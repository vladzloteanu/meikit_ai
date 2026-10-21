"""SE Ranking's research API (api4.seranking.com): keyword volumes, and a domain's keywords and ads.

The token (`providers.seranking.api_token`) goes in an `Authorization: Token` header. SE Ranking
answers bursts with 429s, so calls are paced 2.5 s apart and Client retries the 429s. Countries
are SE Ranking's codes, `uk` not `gb`: every call maps its country through `cc`. A dry-run client
never reads the token and answers from `fixtures/seranking/<call>.json`.
"""

from factory import secrets
from factory.http import Client

BASE_URL = "https://api4.seranking.com"
PACE_S = 2.5
TIMEOUT_S = 90.0
BATCH_SIZE = 20  # keywords per analyze-keywords call


def client(dry_run: bool = False) -> Client:
    headers = None
    if not dry_run:
        headers = {"Authorization": f"Token {secrets.get('providers.seranking.api_token')}"}
    return Client(
        "seranking", BASE_URL, headers=headers, pace_s=PACE_S, timeout_s=TIMEOUT_S, dry_run=dry_run
    )


def cc(geo: str) -> str:
    """SE Ranking's country code for `geo`: GB and UK are `uk`, any other code is lowercased."""
    code = geo.strip().lower()
    return "uk" if code in ("gb", "uk") else code


def analyze_keywords(client: Client, cc: str, keywords: list[str]) -> list[dict]:
    """One row per keyword (keyword, volume, cpc, difficulty, competition, intents, history_trend,
    is_data_found), asked 20 keywords per call, rows in the order of the calls."""
    rows: list[dict] = []
    for start in range(0, len(keywords), BATCH_SIZE):
        rows += client.post_json(
            _path(cc, "analyze-keywords"),
            json={"keywords": keywords[start : start + BATCH_SIZE]},
            fixture="seranking/analyze_keywords",
        )
    return rows


def domain_keywords(client: Client, cc: str, domain: str, limit: int = 60) -> list[dict]:
    """The organic keywords `domain` ranks for, with volume and CPC."""
    return client.get_json(
        _path(cc, "keywords"),
        params={"domain": domain, "limit": limit},
        fixture="seranking/domain_keywords",
    )


def domain_advertising(client: Client, cc: str, domain: str) -> list[dict]:
    """The paid keywords `domain` bids on, with volume, CPC and its ad snippets over time."""
    return client.get_json(
        _path(cc, "advertising"), params={"domain": domain}, fixture="seranking/domain_advertising"
    )


def domain_overview(client: Client, cc: str, domain: str) -> dict:
    """`domain`'s organic and paid totals (traffic, keyword counts, traffic value)."""
    return client.get_json(
        _path(cc, "overview"), params={"domain": domain}, fixture="seranking/domain_overview"
    )


def _path(country: str, endpoint: str) -> str:
    return f"/research/{cc(country)}/{endpoint}/"
