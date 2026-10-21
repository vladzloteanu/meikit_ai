"""`factory reddit_mentions`: how often Reddit talks about the idea's pain phrases, and where.

    factory reddit_mentions --idea S --terms T ... --subreddits A,B [--since 2025-10-21]
                            [--until 2026-10-21] [--limit 100]

Reddit refuses automated reads, so this searches the Arctic Shift archive (free, no key; v1
reddit_mentions.py): the posts whose title or text holds a term's words, and the comments whose
body does (the comments' search keeps a quoted phrase whole: '"ad account" hacked'), created from
--since to --until, both included (UTC; by default the 12 months up to today). Arctic Shift
searches text only within named subreddits, so --subreddits is required.

Each term, subreddit and kind is searched newest first, 60 days of posts or 7 days of comments a
call (a longer comment search times out in a busy subreddit; v1's windows), until --limit items
(at most 100) are found or the range is done: a year is 7 post calls and 53 comment calls a term
and subreddit, paced 1 s apart. The research JSON is

    {"subreddits", "since", "until", "limit",
     "terms": {term: {"posts", "comments", "by_month": {"YYYY-MM": n},
                      "by_subreddit": {subreddit: n}, "complete",
                      "hits": [{"kind", "subreddit", "title", "url", "score", "created",
                                "snippet"}]}}}

`posts` and `comments` count the items found; `by_month` counts both together by the month (UTC)
they were created, `by_subreddit` by subreddit, the most first. `complete` is false when a search
stopped at --limit: the counts are then lower bounds. `hits` are the term's newest --limit items:
`kind` is post or comment, `url` the item on reddit.com, `created` its day, `snippet` the start of
its text (null for a post with none); a comment has no title. Deleted and removed comments, and
those of bots (AutoModerator, "I am a bot"), are left out, as in v1. Arctic Shift is free: no cost
is logged. The summary is one row per term: `term | posts | comments | top subreddits`.
"""

import argparse
import re
from collections import Counter
from datetime import date, timedelta

from factory import tables, toolbase
from factory.http import Client
from factory.providers import arcticshift

TOOL = "reddit_mentions"
PROVIDER = "arcticshift"
MAX_TIME = 4102444800  # 2100-01-01: a later Unix time is garbage
REDDIT = "https://www.reddit.com"
WINDOW_DAYS = {"post": 60, "comment": 7}  # days a search covers, by kind (v1)
TOP_SUBREDDITS = 3
COLUMNS = ["term", "posts", "comments", "top subreddits"]
SELFTEST_QUERY = "ad account"
SELFTEST_SUBREDDIT = "FacebookAds"
SELFTEST_DAYS = 30
SELFTEST_LIMIT = 10
# Comments that say nothing about a term (v1).
SKIP_BODIES = {"[deleted]", "[removed]", ""}
BOT = re.compile(
    r"i am a bot|this action was performed automatically|sufficient comment karma", re.IGNORECASE
)
BOT_AUTHORS = {"AutoModerator"}


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="Reddit posts and comments mentioning phrases, by month and subreddit (free)",
        description="Count the Reddit posts and comments that mention each phrase in the given "
        "subreddits (Arctic Shift archive, free), by month and subreddit, with the newest ones.",
    )
    parser.add_argument(
        "--terms",
        nargs="+",
        action="extend",
        metavar="T",
        help="the phrases to count (quote a phrase; the flag repeats)",
    )
    parser.add_argument(
        "--subreddits",
        action="append",
        metavar="A,B",
        help="the subreddits to search, comma-separated, r/ optional (required: Arctic Shift "
        "searches text only within subreddits; the flag repeats)",
    )
    parser.add_argument(
        "--since",
        type=toolbase.iso_date,
        metavar="YYYY-MM-DD",
        help="the first day searched (default: 12 months before --until)",
    )
    parser.add_argument(
        "--until",
        type=toolbase.iso_date,
        metavar="YYYY-MM-DD",
        help="the last day searched, included (default: today)",
    )
    parser.add_argument(
        "--limit",
        type=toolbase.positive_int,
        default=arcticshift.MAX_LIMIT,
        help="the most items a search of one term in one subreddit keeps, and the most hits of a "
        "term (default and at most: %(default)s)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = arcticshift.client(dry_run=args.dry_run)
        after = toolbase.today() - timedelta(days=SELFTEST_DAYS)
        posts = arcticshift.posts_search(
            client,
            SELFTEST_QUERY,
            subreddit=SELFTEST_SUBREDDIT,
            after=after.isoformat(),
            limit=SELFTEST_LIMIT,
        )
        return toolbase.selftest_ok(PROVIDER, len(posts))
    terms = toolbase.unique_terms(args.terms or [])
    if not terms:
        raise toolbase.UsageError("no term: give --terms T ...")
    subreddits = _subreddits(args.subreddits or [])
    since, until = toolbase.date_range(args.since, args.until)
    if args.limit > arcticshift.MAX_LIMIT:
        raise toolbase.UsageError(
            f"--limit is at most {arcticshift.MAX_LIMIT}, the items Arctic Shift returns a call"
        )
    with toolbase.run(args, tool=TOOL) as r:
        client = arcticshift.client(dry_run=r.dry_run)
        data = collect(client, terms, subreddits, since, until, args.limit)
        r.write(data)
        r.summary(summary(data))
    return 0


def collect(
    client: Client, terms: list[str], subreddits: list[str], since: date, until: date, limit: int
) -> dict:
    """The research JSON: each term searched in each subreddit from `since` to `until`."""
    end = until + timedelta(days=1)  # the range is [since, end): --until is included
    return {
        "subreddits": subreddits,
        "since": since.isoformat(),
        "until": until.isoformat(),
        "limit": limit,
        "terms": {term: _term(client, term, subreddits, since, end, limit) for term in terms},
    }


def walk(
    client: Client, kind: str, term: str, subreddit: str, start: date, end: date, limit: int
) -> tuple[list[dict], bool]:
    """Up to `limit` distinct items of `kind` (post or comment) matching `term` in `subreddit`,
    created from `start` to `end` (excluded), searched in windows of WINDOW_DAYS[kind] days,
    newest first; and whether the whole range was searched (false when a window answered all it
    was asked for, so the search stopped at `limit`). An item two windows answer (one created on
    their boundary) is kept once."""
    search = arcticshift.posts_search if kind == "post" else arcticshift.comments_search
    found: dict[str, dict] = {}
    for after, before in windows(start, end, WINDOW_DAYS[kind]):
        want = limit - len(found)
        page = search(
            client,
            term,
            subreddit=subreddit,
            after=after.isoformat(),
            before=before.isoformat(),
            limit=want,
        )
        for item in page:
            if isinstance(item.get("id"), str):
                found.setdefault(item["id"], item)
        if len(page) >= want:
            return list(found.values()), False
    return list(found.values()), True


def windows(start: date, end: date, days: int) -> list[tuple[date, date]]:
    """The days from `start` to `end` (excluded) cut into windows of `days`, anchored at `start`
    (the newest may be shorter), newest first."""
    cuts = []
    day = start
    while day < end:
        cuts.append((day, min(end, day + timedelta(days=days))))
        day += timedelta(days=days)
    return cuts[::-1]


def summary(data: dict) -> str:
    rows = [
        {
            "term": term,
            "posts": found["posts"],
            "comments": found["comments"],
            "top subreddits": ", ".join(
                f"{subreddit} ({n})"
                for subreddit, n in list(found["by_subreddit"].items())[:TOP_SUBREDDITS]
            ),
        }
        for term, found in data["terms"].items()
    ]
    text = tables.render(rows, COLUMNS)
    stopped = [f'"{term}"' for term, found in data["terms"].items() if not found["complete"]]
    if stopped:
        text += (
            f"\nstopped at --limit {data['limit']}: the counts of {', '.join(stopped)} are lower "
            "bounds"
        )
    return text


def _term(
    client: Client, term: str, subreddits: list[str], start: date, end: date, limit: int
) -> dict:
    """One term's entry in the research JSON: its posts and comments in every subreddit."""
    items: dict[tuple[str, str], dict] = {}
    complete = True
    for subreddit in subreddits:
        for kind in WINDOW_DAYS:
            found, done = walk(client, kind, term, subreddit, start, end, limit)
            complete = complete and done
            for raw in found:
                item = _item(kind, raw)
                if item is not None:
                    items[(kind, item["id"])] = item
    newest = sorted(items.values(), key=lambda item: (-item["ts"], item["id"]))
    return {
        "posts": sum(1 for item in newest if item["kind"] == "post"),
        "comments": sum(1 for item in newest if item["kind"] == "comment"),
        "by_month": dict(sorted(Counter(toolbase.month_of(i["ts"]) for i in newest).items())),
        "by_subreddit": _most_first(Counter(item["subreddit"] for item in newest)),
        "complete": complete,
        "hits": [_hit(item) for item in newest[:limit]],
    }


def _item(kind: str, raw: dict) -> dict | None:
    """A post or a comment as the term counts it; None for a comment left out (deleted, removed,
    a bot's) and for an item without an id or a creation time."""
    item_id, created = raw.get("id"), raw.get("created_utc")
    if not isinstance(item_id, str) or not _is_time(created):
        return None
    subreddit = raw.get("subreddit") if isinstance(raw.get("subreddit"), str) else ""
    if kind == "post":
        title, text = raw.get("title"), raw.get("selftext")
        path = f"/r/{subreddit}/comments/{item_id}/"
    else:
        body = raw.get("body")
        title, text = None, body if isinstance(body, str) else ""
        if text.strip() in SKIP_BODIES or BOT.search(text) or raw.get("author") in BOT_AUTHORS:
            return None
        thread = str(raw.get("link_id") or "").removeprefix("t3_")
        path = f"/r/{subreddit}/comments/{thread}/comment/{item_id}/"
    permalink = raw.get("permalink")
    if isinstance(permalink, str) and permalink.startswith("/"):
        path = permalink
    return {
        "kind": kind,
        "id": item_id,
        "ts": created,
        "subreddit": subreddit,
        "title": title,
        "url": REDDIT + path,
        "score": raw.get("score"),
        "text": text if isinstance(text, str) and text.strip() not in SKIP_BODIES else None,
    }


def _hit(item: dict) -> dict:
    return {
        "kind": item["kind"],
        "subreddit": item["subreddit"],
        "title": item["title"],
        "url": item["url"],
        "score": item["score"],
        "created": toolbase.day_of(item["ts"]),
        "snippet": toolbase.snippet(item["text"]),
    }


def _subreddits(values: list[str]) -> list[str]:
    """The subreddits of the comma-separated --subreddits, without r/, each once whatever its
    case. Raises UsageError when there is none."""
    names: list[str] = []
    for value in values:
        for part in value.split(","):
            name = part.strip().lstrip("/")
            if name[:2].lower() == "r/":
                name = name[2:]
            name = name.strip("/ ")
            if name and name.lower() not in {known.lower() for known in names}:
                names.append(name)
    if not names:
        raise toolbase.UsageError(
            "--subreddits is required: Arctic Shift searches text only within subreddits "
            "(--subreddits FacebookAds,PPC)"
        )
    return names


def _most_first(counts: Counter) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _is_time(value: object) -> bool:
    """A Unix time a day can be read from: a number from 1970 to 2100 (not NaN, not a bool)."""
    return isinstance(value, int | float) and not isinstance(value, bool) and 0 <= value < MAX_TIME
