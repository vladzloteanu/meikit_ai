"""Arctic Shift (arctic-shift.photon-reddit.com): the Reddit archive, read-only, free, no key.

Reddit refuses automated reads, so its posts and comments are searched in Arctic Shift's archive.
`posts_search` is a keyword search of a post's title and text (`query`); `comments_search` a
full-text search of a comment's body (`body`: the words AND-ed, "a phrase", OR, -word). Arctic
Shift runs a text search only within a `subreddit` (or an author): without one it answers 400.
A search returns at most `limit` items (1 to 100), newest first, created after `after` and before
`before`, each an ISO date (or a Unix time). Items come whole: Arctic Shift's `fields` cannot ask
for `permalink` (400 "'permalink' is not a valid field"), the item's link on reddit.com. A score
is what Arctic Shift stored about 36 hours after the item was posted.

Arctic Shift answers 422 "Timeout. Maybe slow down a bit" both to a caller it throttles and to a
search too heavy for its database (a year of comments in a busy subreddit), with the wait in
X-RateLimit-Reset. Only the time it took tells them apart: a throttle answers at once, a heavy
search after its 5 s or more of trying (v1). Client does not retry that 422: the search raises
SlowDown, saying how long the answer took (`throttled` when under 5 s) and the wait asked for,
and the tool decides (reddit_mentions waits out a throttle and asks again, and halves a range
that timed out). Client retries a 429 and a 5xx. Calls are paced 1 s apart. A dry-run client
answers from `fixtures/arcticshift/posts_search.json` and `comments_search.json`.
"""

import httpx

from factory import http
from factory.http import Client, ProviderError

BASE_URL = "https://arctic-shift.photon-reddit.com"
PACE_S = 1.0
MAX_LIMIT = 100  # items a search returns at most
SLOW_S = 5.0  # a 422 that took this long or more is a search timing out, not a throttle


class SlowDown(ProviderError):
    """Arctic Shift's 422 "Timeout. Maybe slow down a bit": too many searches, or one too heavy.

    `took_s` is how long the answer took and `throttled` says it came under SLOW_S: a throttle,
    not a timeout. `reset_s` is the wait asked for in X-RateLimit-Reset, in seconds (a Unix time
    is read as the seconds until it), None when there is none.
    """

    def __init__(self, response: httpx.Response) -> None:
        request = response.request
        target = request.url.raw_path.decode("ascii", "replace")  # path and query string
        detail = f"{request.method} {target}: {response.text}"
        super().__init__("arcticshift", response.status_code, detail)
        self.reset_s = http.wait_seconds(response.headers)
        try:
            self.took_s = response.elapsed.total_seconds()
        except RuntimeError:  # a response httpx did not time (a dry run's)
            self.took_s = 0.0

    @property
    def throttled(self) -> bool:
        return self.took_s < SLOW_S


def client(dry_run: bool = False) -> Client:
    return Client("arcticshift", BASE_URL, pace_s=PACE_S, dry_run=dry_run)


def slow_down(response: httpx.Response) -> bool:
    """Arctic Shift's heavy-search or throttle answer: a 422 "Timeout. Maybe slow down a bit"."""
    return response.status_code == 422 and "slow down" in response.text.lower()


def posts_search(
    client: Client,
    query: str,
    subreddit: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = MAX_LIMIT,
) -> list[dict]:
    """The posts whose title or text holds the words of `query`, newest first. Raises SlowDown
    for Arctic Shift's 422, ProviderError for any other failure."""
    params = {"query": query, **_window(subreddit, after, before, limit)}
    return _search(client, "/api/posts/search", params, "arcticshift/posts_search")


def comments_search(
    client: Client,
    body: str,
    subreddit: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = MAX_LIMIT,
) -> list[dict]:
    """The comments whose body matches `body`, newest first. Raises SlowDown for Arctic Shift's
    422, ProviderError for any other failure."""
    params = {"body": body, **_window(subreddit, after, before, limit)}
    return _search(client, "/api/comments/search", params, "arcticshift/comments_search")


def _search(client: Client, path: str, params: dict, fixture: str) -> list[dict]:
    response = client.get(path, params, fixture=fixture)
    if slow_down(response):
        raise SlowDown(response)
    return _items(client.decode(response))


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
