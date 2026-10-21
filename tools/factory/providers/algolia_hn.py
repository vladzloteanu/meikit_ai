"""The HN Algolia API (hn.algolia.com): Hacker News stories and comments, free, no key.

`search_by_date` returns the newest items matching `query` with one tag (`story` or `comment`)
created strictly between two Unix times: Algolia ANDs the words, reads the last one as a prefix
("worktre" finds "worktree") and a "quoted phrase" as a phrase. Typos are not tolerated, so a
count means the words themselves (v1 hn_mentions.py). The answer holds `hits` (at most
`hits_per_page`, 1000 on this index) and `nbHits`, the number of matches. Calls are paced 0.2 s
apart. A dry-run client answers from `fixtures/algolia/search_by_date.json`, whatever the tag.
"""

from factory.http import Client

BASE_URL = "https://hn.algolia.com/api/v1"
PACE_S = 0.2
MAX_HITS = 1000  # hitsPerPage at most on the HN index


def client(dry_run: bool = False) -> Client:
    return Client("algolia", BASE_URL, pace_s=PACE_S, dry_run=dry_run)


def search_by_date(
    client: Client, query: str, tag: str, since_ts: int, until_ts: int, hits_per_page: int = 100
) -> dict:
    """GET /search_by_date: the `tag` items matching `query` created after `since_ts` and before
    `until_ts`, newest first."""
    params = {
        "query": query,
        "tags": tag,
        "numericFilters": f"created_at_i>{since_ts},created_at_i<{until_ts}",
        "hitsPerPage": hits_per_page,
        "typoTolerance": "false",
    }
    return client.get_json("/search_by_date", params, fixture="algolia/search_by_date")
