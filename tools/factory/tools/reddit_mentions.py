"""`factory reddit_mentions`: how often Reddit talks about the idea's pain phrases, and where.

    factory reddit_mentions --idea S --terms T ... --subreddits A,B [--since 2025-10-21]
                            [--until 2026-10-21] [--limit 100]

Reddit refuses automated reads, so this searches the Arctic Shift archive (free, no key; v1
reddit_mentions.py): the posts whose title or text holds a term's words, and the comments whose
body does (the comments' search keeps a quoted phrase whole: '"ad account" hacked'), created from
--since to --until, both included (UTC; by default the 12 months up to today). Arctic Shift
searches text only within named subreddits, so --subreddits is required.

Each term, subreddit and kind (posts, comments) is one search: one call over the whole range for
its newest 100 items, and 100 back means more exist, so the search ends there. Arctic Shift
answers 422 "Timeout. Maybe slow down a bit" both to a search too heavy for it and to a caller it
throttles: the search then waits (X-RateLimit-Reset seconds, 30 at most; 3 without one), halves
its window and goes on from the newest half, then older, in windows of the size that answered,
for 8 calls at most. What a search fetched is always kept. The research JSON is

    {"subreddits", "since", "until", "limit",
     "terms": {term: {"posts", "comments", "by_month": {"YYYY-MM": n},
                      "by_subreddit": {subreddit: n}, "complete", "covered_since",
                      "hits": [{"kind", "subreddit", "title", "url", "score", "created",
                                "snippet"}]}}}

`posts` and `comments` count the items fetched; `by_month` counts both together by the month
(UTC) they were created, `by_subreddit` by subreddit, the most first. `covered_since` is the first
day from which every search of the term fetched every match; `complete` says it is --since. When
it is not (a search came back full, or ran out of calls), the counts are lower bounds. `hits` are
the term's newest --limit items: `kind` is post or comment, `url` the item on reddit.com (its
permalink, else its rebuilt path), `created` its day, `snippet` the start of its text (null for a
post with none); a comment has no title. Deleted and removed comments, and those of bots
(AutoModerator, "I am a bot"), are left out, as in v1. Arctic Shift is free: no cost is logged.
The summary is one row per term, `term | posts | comments | top subreddits`, then a line for each
incomplete term.
"""

import argparse
import math
import re
import time
from collections import Counter
from datetime import UTC, date, datetime, timedelta

from factory import tables, toolbase
from factory.http import Client
from factory.providers import arcticshift

TOOL = "reddit_mentions"
PROVIDER = "arcticshift"
REDDIT = "https://www.reddit.com"
KINDS = ("post", "comment")
PAGE = arcticshift.MAX_LIMIT  # a call's items at most: 100 back means more exist
MAX_CALLS = 8  # the calls one search (a term, a subreddit, a kind) makes at most
WAIT_S = 3.0  # the wait after a 422 without X-RateLimit-Reset
MAX_WAIT_S = 30.0  # the longest wait after a 422
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
        default=100,
        help="the most hits of a term kept in the research file (default: %(default)s)",
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


def search(
    client: Client, kind: str, term: str, subreddit: str, start: date, end: date
) -> tuple[list[dict], date]:
    """The items of `kind` (post or comment) matching `term` in `subreddit` created from `start`
    to `end` (excluded), newest first, each once; and the first day from which every match was
    fetched (`start` when all were). One call asks the whole range; a full answer (PAGE items)
    ends the search; a 422 is waited out and the window halved, the newest half first; the
    search goes on, older, in windows of the size that answered, MAX_CALLS calls at most."""
    find = arcticshift.posts_search if kind == "post" else arcticshift.comments_search
    found: dict[str, dict] = {}
    covered = end  # every match created from `covered` to `end` is in `found`
    days = (end - start).days  # the window asked next
    calls = 0
    while covered > start and calls < MAX_CALLS:
        after = max(start, covered - timedelta(days=days))
        calls += 1
        try:
            page = find(
                client,
                term,
                subreddit=subreddit,
                after=after.isoformat(),
                before=covered.isoformat(),
                limit=PAGE,
            )
        except arcticshift.SlowDown as exc:
            window = (covered - after).days
            if window <= 1 or calls >= MAX_CALLS:
                break  # a day cannot be halved; or no call is left to wait for
            time.sleep(WAIT_S if exc.reset_s is None else min(exc.reset_s, MAX_WAIT_S))
            days = math.ceil(window / 2)
            continue
        for item in page:
            if isinstance(item.get("id"), str):
                found.setdefault(item["id"], item)
        if len(page) >= PAGE:  # full: older matches in this window were not returned
            times = [i["created_utc"] for i in page if toolbase.is_time(i.get("created_utc"))]
            if times:
                covered = max(after, _first_full_day(min(times)))
            break
        covered = after
    return list(found.values()), covered


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
    lines = [tables.render(rows, COLUMNS)]
    for term, found in data["terms"].items():
        if found["complete"]:
            continue
        if found["covered_since"] > data["until"]:
            seen = "no day fetched in full"
        else:
            seen = f"every match fetched only from {found['covered_since']} on"
        lines.append(
            f'"{term}": {seen} (a search came back full, or Arctic Shift kept saying slow down), '
            "so its counts are lower bounds"
        )
    return "\n".join(lines)


def _term(
    client: Client, term: str, subreddits: list[str], since: date, end: date, limit: int
) -> dict:
    """One term's entry in the research JSON: its posts and comments in every subreddit."""
    items: dict[tuple[str, str], dict] = {}
    covered_since = since
    for subreddit in subreddits:
        for kind in KINDS:
            found, covered = search(client, kind, term, subreddit, since, end)
            covered_since = max(covered_since, covered)
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
        "complete": covered_since == since,
        "covered_since": covered_since.isoformat(),
        "hits": [_hit(item) for item in newest[:limit]],
    }


def _item(kind: str, raw: dict) -> dict | None:
    """A post or a comment as the term counts it; None for a comment left out (deleted, removed,
    a bot's) and for an item without an id or a creation time."""
    item_id, created = raw.get("id"), raw.get("created_utc")
    if not isinstance(item_id, str) or not toolbase.is_time(created):
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


def _first_full_day(timestamp: float) -> date:
    """The first day (UTC) that starts at or after `timestamp`."""
    moment = datetime.fromtimestamp(timestamp, UTC)
    day = moment.date()
    return day if moment == datetime.combine(day, datetime.min.time(), UTC) else day + timedelta(1)


def _most_first(counts: Counter) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
