"""SearchAPI (searchapi.io): live Google SERPs with their ads, and the public ad libraries.

One endpoint, one engine per call: `google`, `meta_ad_library`, `tiktok_ads_library`,
`linkedin_ad_library`, `google_ads_transparency_center`. The key
(`providers.searchapi.api_key`) travels as the `api_key` query parameter of every call, so it is
in every request URL: ProviderError scrubs it from error text and factory.http keeps httpx's
request log off. Once the plan's monthly searches are used up SearchAPI answers 429 to every call
until the period resets: `quota_used_up` makes that fatal, while other 429s are retried. A dry-run
client never reads the key and answers from `fixtures/searchapi/<engine>.json`.
"""

from typing import Any

import httpx

from factory import secrets
from factory.http import Client

BASE_URL = "https://www.searchapi.io/api/v1"
PACE_S = 0.35
TIMEOUT_S = 120.0


def client(dry_run: bool = False) -> Client:
    params = None if dry_run else {"api_key": secrets.get("providers.searchapi.api_key")}
    return Client(
        "searchapi",
        BASE_URL,
        pace_s=PACE_S,
        timeout_s=TIMEOUT_S,
        dry_run=dry_run,
        params=params,
        fatal=quota_used_up,
    )


def quota_used_up(response: httpx.Response) -> bool:
    """SearchAPI's "You have used all of the searches for the month" 429: no retry can help."""
    return response.status_code == 429 and "used all of the searches" in response.text.lower()


def search(client: Client, engine: str, **params: Any) -> dict:
    """GET /search for `engine` with `params` (q, gl, hl, country, domain, region, num, ...)."""
    return client.get_json(
        "/search", params={"engine": engine, **params}, fixture=f"searchapi/{engine}"
    )
