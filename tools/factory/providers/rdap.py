"""RDAP through rdap.org: whether a domain is registered, free and keyless.

rdap.org redirects a lookup to the registry's own RDAP server (Verisign for .com, Google for .dev,
AFNIC for .fr, Identity Digital for .ai...), which answers 200 for a registered domain and 404 for
a free one. For a TLD with no RDAP server in IANA's bootstrap list (.io, .co, .de on 2026-10-21)
rdap.org answers its own 404, "No RDAP service is available for this resource": that says nothing
about the domain, so it reads `unknown`, never `available`. Client retries a 429 and a 5xx, never
a 404. A dry-run client answers a .com from `fixtures/rdap/taken.json` (a real 200, trimmed) and
any other domain from `fixtures/rdap/available.json` (`{"_status": 404}`).
"""

from factory.http import Client

BASE_URL = "https://rdap.org"
STATUSES = ("available", "taken", "unknown")
_NO_SERVICE = "no rdap service"  # rdap.org's own 404, for a TLD it cannot ask


def client(dry_run: bool = False) -> Client:
    return Client("rdap", BASE_URL, dry_run=dry_run)


def status(client: Client, domain: str) -> str:
    """`taken` (200), `available` (the registry's 404) or `unknown` (anything else) for `domain`."""
    fixture = "rdap/taken" if domain.endswith(".com") else "rdap/available"
    response = client.get(f"/domain/{domain}", fixture=fixture)
    if response.status_code == 200:
        return "taken"
    if response.status_code == 404 and _NO_SERVICE not in response.text.lower():
        return "available"
    return "unknown"
