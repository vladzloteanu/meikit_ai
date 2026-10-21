"""Arctic Shift (arctic-shift.photon-reddit.com): the Reddit archive, read-only, free, no key.

Reddit refuses automated reads, so its posts and comments are searched in Arctic Shift's archive.
`posts_search` is a keyword search of a post's title and text (`query`); `comments_search` a
full-text search of a comment's body (`body`: the words AND-ed, "a phrase", OR, -word). Arctic
Shift runs a text search only within a `subreddit` (or an author): without one it answers 400.
A search returns at most `limit` items (1 to 100), newest first, created after `after` and before
`before`, each an ISO date (or a Unix time). Only the fields the tools read are asked for, so an
item has no `permalink`. A score is what Arctic Shift stored about 36 hours after the item was
posted.

Arctic Shift limits its callers by load: it answers 429, or 422 "Timeout. Maybe slow down a bit",
with the seconds to wait in X-RateLimit-Reset. Client retries both after that wait (at most 300 s)
up to 5 attempts, since the limit can outlast one wait. A search too heavy for its database (a
year of comments in a busy subreddit) gets the same 422 after some seconds, and a retry often
passes once the database is warm; the tools keep each search short (reddit_mentions: 7 days of
comments a call). Calls are paced 1 s apart. A dry-run client answers from
`fixtures/arcticshift/posts_search.json` and `comments_search.json`.
"""

import httpx

from factory.http import Client

BASE_URL = "https://arctic-shift.photon-reddit.com"
PACE_S = 1.0
RETRIES = 5
MAX_LIMIT = 100  # items a search returns at most
POST_FIELDS = "id,author,created_utc,title,selftext,score,num_comments,subreddit"
COMMENT_FIELDS = "id,author,created_utc,body,link_id,score,subreddit"


def client(dry_run: bool = False) -> Client:
    return Client(
        "arcticshift", BASE_URL, pace_s=PACE_S, retries=RETRIES, dry_run=dry_run, retry_on=slow_down
    )


def slow_down(response: httpx.Response) -> bool:
    """Arctic Shift's rate limit (or a heavy query): a 422 "Timeout. Maybe slow down a bit"."""
    return response.status_code == 422 and "slow down" in response.text.lower()


def posts_search(
    client: Client,
    query: str,
    subreddit: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = MAX_LIMIT,
) -> list[dict]:
    """The posts whose title or text holds the words of `query`, newest first."""
    params = {"query": query, **_window(subreddit, after, before, limit), "fields": POST_FIELDS}
    return _items(client.get_json("/api/posts/search", params, fixture="arcticshift/posts_search"))


def comments_search(
    client: Client,
    body: str,
    subreddit: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = MAX_LIMIT,
) -> list[dict]:
    """The comments whose body matches `body`, newest first."""
    params = {"body": body, **_window(subreddit, after, before, limit), "fields": COMMENT_FIELDS}
    answer = client.get_json("/api/comments/search", params, fixture="arcticshift/comments_search")
    return _items(answer)


def _window(subreddit: str | None, after: str | None, before: str | None, limit: int) -> dict:
    return {
        "subreddit": subreddit,
        "after": after,
        "before": before,
        "limit": limit,
        "sort": "desc",
    }


def _items(answer: object) -> list[dict]:
    """The objects of the answer's `data` list; nothing when it has none."""
    data = answer.get("data") if isinstance(answer, dict) else None
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []
