"""Firecrawl (api.firecrawl.dev): a web page as markdown, one billed scrape a call.

`scrape` asks for the page's main content only (navigation, headers and footers left out) as
markdown, and returns Firecrawl's `data`: `markdown`, and `metadata` with the page's `title` (a
string, or a list when the page has several), `sourceURL` and `statusCode`. The key
(`providers.firecrawl.api_key`) goes in an `Authorization: Bearer` header. A dry-run client never
reads the key and answers from `fixtures/firecrawl/scrape.json`.
"""

from factory import secrets
from factory.http import Client

BASE_URL = "https://api.firecrawl.dev/v1"


def client(dry_run: bool = False) -> Client:
    headers = None
    if not dry_run:
        headers = {"Authorization": f"Bearer {secrets.get('providers.firecrawl.api_key')}"}
    return Client("firecrawl", BASE_URL, headers=headers, dry_run=dry_run)


def scrape(client: Client, url: str) -> dict:
    """POST /scrape: the page at `url` as `{"markdown", "metadata"}` ({} if the answer has none)."""
    answer = client.post_json(
        "/scrape",
        json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
        fixture="firecrawl/scrape",
    )
    data = answer.get("data") if isinstance(answer, dict) else None
    return data if isinstance(data, dict) else {}
