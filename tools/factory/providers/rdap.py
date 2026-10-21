"""RDAP through rdap.org: whether a domain is registered, free and keyless.

rdap.org answers a lookup by redirecting it to the registry's own RDAP server (Verisign for .com,
Google for .dev, AFNIC for .fr, Identity Digital for .ai...), which answers 200 for a registered
domain and 404 for a free one. For a TLD with no RDAP server in IANA's bootstrap list (.io, .co,
.de on 2026-10-21) rdap.org answers a 404 itself: that says nothing about the domain. So a 404
reads `available` only when the redirect was followed to another host, a registry's answer, and
`unknown` when rdap.org answered it, whatever its body says. Client follows the redirect, retries
a 429 and a 5xx, never a 404. A dry-run client answers a .com from `fixtures/rdap/taken.json` (a
real 200, trimmed) and any other domain from `fixtures/rdap/available.json` (`{"_status": 404}`,
which stands for a registry's 404).
"""

import httpx

from factory.http import Client

BASE_URL = "https://rdap.org"
STATUSES = ("available", "taken", "unknown")


def client(dry_run: bool = False) -> Client:
    return Client("rdap", BASE_URL, dry_run=dry_run)


def status(client: Client, domain: str) -> str:
    """`taken` (200), `available` (a registry's 404) or `unknown` (anything else) for `domain`."""
    fixture = "rdap/taken" if domain.endswith(".com") else "rdap/available"
    response = client.get(f"/domain/{domain}", fixture=fixture)
    if response.status_code == 200:
        return "taken"
    if response.status_code == 404 and (client.dry_run or registry_answered(response)):
        return "available"
    return "unknown"


def registry_answered(response: httpx.Response) -> bool:
    """Whether a registry's RDAP server gave `response`: rdap.org redirected the lookup to another
    host, and that host answered."""
    return bool(response.history) and response.url.host != httpx.URL(BASE_URL).host
