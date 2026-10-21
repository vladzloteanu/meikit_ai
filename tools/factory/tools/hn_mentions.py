"""`factory hn_mentions`: how often Hacker News talks about the idea's pain phrases.

    factory hn_mentions --idea S --terms T ... [--since 2025-10-21] [--until 2026-10-21]
                        [--limit 100]

The HN Algolia API (free, no key; v1 hn_mentions.py) is searched for each term twice, stories
then comments, created from --since to --until, both included (UTC; by default the 12 months up
to today), the newest --limit of each (at most 1000), without typo tolerance. Algolia ANDs the
words, reads the last one as a prefix and a "quoted phrase" as a phrase. The research JSON is

    {"since", "until", "limit",
     "terms": {term: {"stories", "comments", "by_month": {"YYYY-MM": n}, "complete",
                      "hits": [{"kind", "title", "url", "score", "created", "snippet"}]}}}

`stories` and `comments` are Algolia's counts of the matches. `complete` is false when more
matched than the --limit fetched: `by_month` (stories and comments together, by the month they
were created) and `hits` then cover the newest only. `hits` are the term's newest --limit items:
`kind` story or comment, `title` the story's (a comment's thread), `url` the item on
news.ycombinator.com, `score` its points (null for a comment), `created` its day, `snippet` the
start of its text without HTML (links as their address, as in v1). Algolia is free: no cost is
logged. The summary is one row per term: `term | stories | comments`.
"""

import argparse
import html
import re
from collections import Counter
from datetime import UTC, date, datetime, time, timedelta

from factory import tables, toolbase
from factory.http import Client
from factory.providers import algolia_hn

TOOL = "hn_mentions"
PROVIDER = "algolia"
MAX_TIME = 4102444800  # 2100-01-01: a later Unix time is garbage
HN_ITEM = "https://news.ycombinator.com/item?id="
TAGS = {"story": "stories", "comment": "comments"}  # Algolia's tag -> the count it makes
DEFAULT_LIMIT = 100
COLUMNS = ["term", "stories", "comments"]
SELFTEST_QUERY = "ad account"
SELFTEST_LIMIT = 10
_ANCHOR = re.compile(r'<a\s+href="([^"]*)"[^>]*>.*?</a>', re.DOTALL)


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="Hacker News stories and comments mentioning phrases, by month (free)",
        description="Count the Hacker News stories and comments that mention each phrase (HN "
        "Algolia API, free), by month, with the newest ones.",
    )
    parser.add_argument(
        "--terms",
        nargs="+",
        action="extend",
        metavar="T",
        help="the phrases to count (quote a phrase; the flag repeats)",
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
        default=DEFAULT_LIMIT,
        help=f"the most stories, and comments, fetched per term, and the most hits of a term "
        f"(default: %(default)s, at most {algolia_hn.MAX_HITS})",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = algolia_hn.client(dry_run=args.dry_run)
        since, until = toolbase.date_range(None, None)
        found = algolia_hn.search_by_date(
            client,
            SELFTEST_QUERY,
            "story",
            *_unix_range(since, until),
            hits_per_page=SELFTEST_LIMIT,
        )
        return toolbase.selftest_ok(PROVIDER, len(_hits(found)))
    terms = toolbase.unique_terms(args.terms or [])
    if not terms:
        raise toolbase.UsageError("no term: give --terms T ...")
    since, until = toolbase.date_range(args.since, args.until)
    if args.limit > algolia_hn.MAX_HITS:
        raise toolbase.UsageError(
            f"--limit is at most {algolia_hn.MAX_HITS}, the hits Algolia returns a call"
        )
    with toolbase.run(args, tool=TOOL) as r:
        client = algolia_hn.client(dry_run=r.dry_run)
        data = collect(client, terms, since, until, args.limit)
        r.write(data)
        r.summary(summary(data))
    return 0


def collect(client: Client, terms: list[str], since: date, until: date, limit: int) -> dict:
    """The research JSON: each term's stories and comments from `since` to `until`."""
    unix_range = _unix_range(since, until)
    return {
        "since": since.isoformat(),
        "until": until.isoformat(),
        "limit": limit,
        "terms": {term: _term(client, term, unix_range, limit) for term in terms},
    }


def summary(data: dict) -> str:
    rows = [{"term": term, **found} for term, found in data["terms"].items()]
    text = tables.render(rows, COLUMNS)
    partial = [f'"{term}"' for term, found in data["terms"].items() if not found["complete"]]
    if partial:
        text += (
            f"\nnot every match fetched (--limit {data['limit']}): the by_month and hits of "
            f"{', '.join(partial)} cover the newest only"
        )
    return text


def _term(client: Client, term: str, unix_range: tuple[int, int], limit: int) -> dict:
    """One term's entry in the research JSON: a stories search, then a comments search."""
    entry: dict = {}
    items: dict[str, dict] = {}
    complete = True
    for tag, count in TAGS.items():
        found = algolia_hn.search_by_date(client, term, tag, *unix_range, hits_per_page=limit)
        hits = _hits(found)
        matches = found.get("nbHits") if isinstance(found, dict) else None
        if not isinstance(matches, int) or isinstance(matches, bool):
            matches = len(hits)
        entry[count] = matches
        complete = complete and matches <= len(hits)
        for hit in hits:
            item = _item(tag, hit)
            if item is not None:  # an item both searches answer is one item
                items.setdefault(item["id"], item)
    newest = sorted(items.values(), key=lambda item: (-item["ts"], item["id"]))
    return {
        **entry,
        "by_month": dict(sorted(Counter(toolbase.month_of(i["ts"]) for i in newest).items())),
        "complete": complete,
        "hits": [_hit(item) for item in newest[:limit]],
    }


def _hits(found: object) -> list[dict]:
    hits = found.get("hits") if isinstance(found, dict) else None
    return [hit for hit in hits if isinstance(hit, dict)] if isinstance(hits, list) else []


def _item(tag: str, hit: dict) -> dict | None:
    """A story or a comment as the term counts it; None for a hit without an id or a time. What
    it is comes from its own tags, else from the tag searched."""
    item_id, created = hit.get("objectID"), hit.get("created_at_i")
    if not isinstance(item_id, str) or not _is_time(created):
        return None
    tags = hit.get("_tags") if isinstance(hit.get("_tags"), list) else []
    kind = next((name for name in TAGS if name in tags), tag)
    story = kind == "story"
    return {
        "kind": kind,
        "id": item_id,
        "ts": created,
        "title": hit.get("title") if story else hit.get("story_title"),
        "score": hit.get("points") if story else None,
        "text": _plain(hit.get("story_text") if story else hit.get("comment_text")),
    }


def _hit(item: dict) -> dict:
    return {
        "kind": item["kind"],
        "title": item["title"],
        "url": f"{HN_ITEM}{item['id']}",
        "score": item["score"],
        "created": toolbase.day_of(item["ts"]),
        "snippet": toolbase.snippet(item["text"]),
    }


def _plain(text: object) -> str | None:
    """HN's HTML as text (v1): a link as its address, a paragraph as a blank line, no tags."""
    if not isinstance(text, str):
        return None
    text = _ANCHOR.sub(lambda m: f" {m.group(1)} ", text)
    text = text.replace("<p>", "\n\n")
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def _unix_range(since: date, until: date) -> tuple[int, int]:
    """The Unix times of the midnight (UTC) starting `since` and of the one ending `until`."""
    start = datetime.combine(since, time(), UTC)
    end = datetime.combine(until + timedelta(days=1), time(), UTC)
    return int(start.timestamp()), int(end.timestamp())


def _is_time(value: object) -> bool:
    """A Unix time a day can be read from: a number from 1970 to 2100 (not NaN, not a bool)."""
    return isinstance(value, int | float) and not isinstance(value, bool) and 0 <= value < MAX_TIME
