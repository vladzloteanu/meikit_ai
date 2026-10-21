"""`factory reddit_mentions`: how often Reddit talks about the idea's pain phrases, and where.

    factory reddit_mentions --idea S --terms T ... --subreddits A,B [--since 2025-10-21]
                            [--until 2026-10-21] [--limit 100] [--max-wait-s 300]

Reddit refuses automated reads, so this searches the Arctic Shift archive (free, no key; v1
reddit_mentions.py): the posts whose title or text holds a term's words, and the comments whose
body does (the comments' search keeps a quoted phrase whole: '"ad account" hacked'), created from
--since to --until, both included (UTC; by default the 12 months up to today). Arctic Shift
searches text only within named subreddits, so --subreddits is required.

Each term, subreddit and kind (posts, comments) is one search: one call over the whole range for
its newest 100 items, and 100 back means more exist, so the search ends there. Arctic Shift
answers 422 "Timeout. Maybe slow down a bit" both to a caller it throttles and to a search too
heavy for it; the time the answer took tells them apart. A throttle (under 5 s) is waited out in
full, X-RateLimit-Reset seconds (120 at most, 3 without one), and the same window asked again. A
timeout (5 s or more) halves the window: its reset is waited out, the newest half asked, then the
older ranges in windows of the size that answered. A search makes 8 calls at most and waits 240 s
at most in all; when either runs out it stops, and what it fetched is kept. So does a search
Arctic Shift refuses after the client's retries (a 429, a 5xx) or a network error ends: its
failure is recorded on its term, and the run goes on with the next search. A run waits
--max-wait-s at most across all its searches, the time the client spent retrying a call that
failed counted in: once a wait would pass it, the searches left are skipped. The run fails (exit
1, no research file) only when no search at all was answered. The research JSON is

    {"subreddits", "since", "until", "limit", "max_wait_s", "waited_s", "skipped_searches",
     "terms": {term: {"posts", "comments", "by_month": {"YYYY-MM": n},
                      "by_subreddit": {subreddit: n}, "complete", "covered_since", "skipped",
                      "error", "calls", "waited_s",
                      "hits": [{"kind", "subreddit", "title", "url", "score", "created",
                                "snippet"}]}}}

`posts` and `comments` count the items fetched; `by_month` counts both together by the month
(UTC) they were created, `by_subreddit` by subreddit, the most first. `covered_since` is the first
day from which every search of the term fetched every match; `complete` says it is --since. When
it is not (a search came back full, failed, ran out of calls or waiting time, or was skipped), the
counts are lower bounds. `skipped` says some of the term's searches were not made, the run's
waiting budget spent; `error` is the message of the first of its searches that failed (null when
none did), one line and never quoting a secret. `calls` and `waited_s` are what the term's
searches cost in Arctic Shift calls and in seconds waiting on its resets and on the client's
retries, what makes a run slow; at the top, `waited_s` is the run's and `skipped_searches` counts
the searches skipped. `hits` are the term's newest --limit items: `kind`
is post or comment, `url` the item on reddit.com (its permalink, else its rebuilt path), `created`
its day, `snippet` the start of its text (null for a post with none); a comment has no title.
Deleted and removed comments, and those of bots (AutoModerator, "I am a bot"), are left out, as in
v1. Arctic Shift is free: no cost is logged.
The summary is one row per term, `term | posts | comments | top subreddits`, then a line for each
term that is incomplete or waited on Arctic Shift, one for each whose search failed, and one
saying how many searches were skipped.
The selftest is one posts search; a throttle is waited out once (60 s at most) and the call made
once more.
"""

import argparse
import math
import re
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from factory import tables, toolbase
from factory.http import Client, ProviderError
from factory.providers import arcticshift

TOOL = "reddit_mentions"
PROVIDER = "arcticshift"
REDDIT = "https://www.reddit.com"
KINDS = ("post", "comment")
PAGE = arcticshift.MAX_LIMIT  # a call's items at most: 100 back means more exist
MAX_CALLS = 8  # the calls one search (a term, a subreddit, a kind) makes at most
MAX_WAITED_S = 240.0  # the seconds one search waits on Arctic Shift at most, in all
WAIT_S = 3.0  # the wait after a 422 without X-RateLimit-Reset
MAX_WAIT_S = 120.0  # the longest single wait after a 422
MAX_RUN_WAIT_S = 300.0  # the default --max-wait-s: the seconds a whole run waits at most
SELFTEST_MAX_WAIT_S = 60.0  # the longest wait before the selftest's one retry
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
    parser.add_argument(
        "--max-wait-s",
        type=_seconds,
        default=MAX_RUN_WAIT_S,
        metavar="S",
        help="the seconds the whole run may wait on Arctic Shift's throttle; once a wait would "
        "pass them, the searches left are skipped (default: %(default)g)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = arcticshift.client(dry_run=args.dry_run)
        return toolbase.selftest_ok(PROVIDER, len(_selftest_search(client)))
    terms = toolbase.unique_terms(args.terms or [])
    if not terms:
        raise toolbase.UsageError("no term: give --terms T ...")
    subreddits = _subreddits(args.subreddits or [])
    since, until = toolbase.date_range(args.since, args.until)
    with toolbase.run(args, tool=TOOL) as r:
        client = arcticshift.client(dry_run=r.dry_run)
        data = collect(client, terms, subreddits, since, until, args.limit, args.max_wait_s)
        errors = [found["error"] for found in data["terms"].values() if found["error"]]
        if errors and not client.ok_calls:  # nothing fetched to keep: the first failure, exit 1
            raise toolbase.ToolError(f"{errors[0]} (no search answered)")
        r.write(data)
        r.summary(summary(data))
    return 0


def collect(
    client: Client,
    terms: list[str],
    subreddits: list[str],
    since: date,
    until: date,
    limit: int,
    max_wait_s: float = MAX_RUN_WAIT_S,
) -> dict:
    """The research JSON: each term searched in each subreddit from `since` to `until`, the run
    waiting `max_wait_s` at most on Arctic Shift in all."""
    end = until + timedelta(days=1)  # the range is [since, end): --until is included
    budget = WaitBudget(max_wait_s)
    found = {term: _term(client, term, subreddits, since, end, limit, budget) for term in terms}
    return {
        "subreddits": subreddits,
        "since": since.isoformat(),
        "until": until.isoformat(),
        "limit": limit,
        "max_wait_s": max_wait_s,
        "waited_s": round(budget.waited_s, 1),
        "skipped_searches": budget.skipped,
        "terms": found,
    }


@dataclass
class WaitBudget:
    """The waiting one run may do on Arctic Shift across all its searches, and what it did."""

    max_s: float
    waited_s: float = 0.0
    spent: bool = False  # a wait would have passed max_s: the searches left are skipped
    skipped: int = 0  # the searches skipped

    def allows(self, wait: float) -> bool:
        return not self.spent and self.waited_s + wait <= self.max_s

    def charge(self, seconds: float) -> None:
        """Count `seconds` waited; past `max_s`, the budget is spent."""
        self.waited_s += seconds
        if self.waited_s > self.max_s:
            self.spent = True


@dataclass
class Search:
    """What one search (a term, a subreddit, a kind) found and cost."""

    items: list[dict]  # newest first, each once
    covered: date  # the first day from which every match was fetched
    calls: int = 0
    waited_s: float = 0.0
    error: str | None = None  # the failure that ended the search, if one did


def search(
    client: Client,
    kind: str,
    term: str,
    subreddit: str,
    start: date,
    end: date,
    budget: WaitBudget | None = None,
) -> Search:
    """The items of `kind` (post or comment) matching `term` in `subreddit` created from `start`
    to `end` (excluded), and what finding them cost. One call asks the whole range; a full answer
    (PAGE items) ends the search. A throttled 422 is waited out in full and the same window asked
    again; a 422 that timed out is waited out and the window halved, the newest half first, the
    search then going on older in windows of the size that answered. MAX_CALLS calls and
    MAX_WAITED_S seconds of waiting at most: whichever runs out first ends the search. A wait
    the run's `budget` cannot cover ends it too, and marks the budget spent. So does any other
    failure of a call (refused after the client's retries, a network error): it is the search's
    `error`, and the call's wall-clock, which holds the retries' sleeps, counts as waited."""
    budget = budget if budget is not None else WaitBudget(MAX_WAITED_S)
    find = arcticshift.posts_search if kind == "post" else arcticshift.comments_search
    found: dict[str, dict] = {}
    covered = end  # every match created from `covered` to `end` is in `found`
    days = (end - start).days  # the window asked next
    calls, waited, error = 0, 0.0, None
    while covered > start and calls < MAX_CALLS:
        after = max(start, covered - timedelta(days=days))
        calls += 1
        started = time.monotonic()
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
            wait = _wait(exc, MAX_WAIT_S)
            if calls >= MAX_CALLS or waited + wait > MAX_WAITED_S:
                break  # no call left, or no time left to wait
            if not exc.throttled:  # a timeout: ask half the window
                if window <= 1:
                    break  # a day cannot be halved
                days = math.ceil(window / 2)
            if not budget.allows(wait):
                budget.spent = True  # the run cannot wait any more
                break
            time.sleep(wait)
            waited += wait
            budget.charge(wait)
            continue
        except ProviderError as exc:
            error = str(exc)
            retried = time.monotonic() - started  # the client's attempts and their backoffs
            waited += retried
            budget.charge(retried)
            break
        for item in page:
            if isinstance(item.get("id"), str):
                found.setdefault(item["id"], item)
        if len(page) >= PAGE:  # full: older matches in this window were not returned
            times = [i["created_utc"] for i in page if toolbase.is_time(i.get("created_utc"))]
            if times:
                covered = max(after, _first_full_day(min(times)))
            break
        covered = after
    return Search(list(found.values()), covered, calls, waited, error)


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
        cost = f"{found['calls']} calls, {found['waited_s']:g} s waited on Arctic Shift"
        if found["skipped"] and not found["calls"]:
            lines.append(f'"{term}": not searched: the run\'s waiting budget was spent')
        elif not found["complete"]:
            if found["covered_since"] > data["until"]:
                seen = "no day fetched in full"
            else:
                seen = f"every match fetched only from {found['covered_since']} on"
            lines.append(
                f'"{term}": {seen}, so its counts are lower bounds (a search came back full, '
                f"failed, ran out of calls or waiting time, or was skipped; {cost})"
            )
        elif found["waited_s"]:
            lines.append(
                f'"{term}": complete after {found["calls"]} calls and {found["waited_s"]:g} s '
                "waited on Arctic Shift"
            )
        if found["error"]:
            lines.append(f'"{term}": a search failed: {found["error"]}')
    if data["skipped_searches"]:
        lines.append(
            f"{data['skipped_searches']} searches skipped: the run waited {data['waited_s']:g} s "
            f"on Arctic Shift and --max-wait-s {data['max_wait_s']:g} could not cover another wait"
        )
    return "\n".join(lines)


def _term(
    client: Client,
    term: str,
    subreddits: list[str],
    since: date,
    end: date,
    limit: int,
    budget: WaitBudget,
) -> dict:
    """One term's entry in the research JSON: its posts and comments in every subreddit, the
    searches the run's `budget` no longer allows skipped (nothing found, no day covered), the
    first failure among its searches as `error`."""
    items: dict[tuple[str, str], dict] = {}
    covered_since = since
    calls, waited, skipped, error = 0, 0.0, False, None
    for subreddit in subreddits:
        for kind in KINDS:
            if budget.spent:
                budget.skipped += 1
                skipped, covered_since = True, end
                continue
            found = search(client, kind, term, subreddit, since, end, budget)
            covered_since = max(covered_since, found.covered)
            calls += found.calls
            waited += found.waited_s
            error = error or found.error
            for raw in found.items:
                item = _item(kind, raw)
                if item is not None:
                    items[(kind, item["id"])] = item
    newest = sorted(items.values(), key=lambda item: (-item["ts"], item["id"]))
    return {
        "posts": sum(1 for item in newest if item["kind"] == "post"),
        "comments": sum(1 for item in newest if item["kind"] == "comment"),
        "by_month": dict(sorted(Counter(toolbase.month_of(i["ts"]) for i in newest).items())),
        "by_subreddit": _most_first(Counter(item["subreddit"] for item in newest)),
        "complete": covered_since == since and error is None,
        "covered_since": covered_since.isoformat(),
        "skipped": skipped,
        "error": error,
        "calls": calls,
        "waited_s": round(waited, 1),
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


def _wait(exc: arcticshift.SlowDown, longest: float) -> float:
    """The seconds to wait after Arctic Shift's 422: its reset, `longest` at most, WAIT_S without
    one."""
    return WAIT_S if exc.reset_s is None else min(exc.reset_s, longest)


def _selftest_search(client: Client) -> list[dict]:
    """The selftest's one posts search; a throttle is waited out once (SELFTEST_MAX_WAIT_S at
    most) and the search made once more. A second refusal is a ToolError saying the wait."""
    after = (toolbase.today() - timedelta(days=SELFTEST_DAYS)).isoformat()

    def once() -> list[dict]:
        return arcticshift.posts_search(
            client, SELFTEST_QUERY, subreddit=SELFTEST_SUBREDDIT, after=after, limit=SELFTEST_LIMIT
        )

    try:
        return once()
    except arcticshift.SlowDown as exc:
        if not exc.throttled:
            raise  # a timeout: waiting does not help
        wait = _wait(exc, SELFTEST_MAX_WAIT_S)
    time.sleep(wait)
    try:
        return once()
    except arcticshift.SlowDown as exc:
        raise toolbase.ToolError(
            f"{exc} (refused again after waiting {wait:g} s on a throttle)"
        ) from None


def _seconds(text: str) -> float:
    """argparse type: a number of seconds, 0 or more."""
    try:
        value = float(text)
    except ValueError:
        value = math.nan
    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError(f"{text!r} is not a number of seconds")
    return value


def _first_full_day(timestamp: float) -> date:
    """The first day (UTC) that starts at or after `timestamp`."""
    moment = datetime.fromtimestamp(timestamp, UTC)
    day = moment.date()
    return day if moment == datetime.combine(day, datetime.min.time(), UTC) else day + timedelta(1)


def _most_first(counts: Counter) -> dict[str, int]:
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
