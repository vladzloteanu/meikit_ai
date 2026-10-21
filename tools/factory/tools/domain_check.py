"""`factory domain_check`: which domains of a name are free, by RDAP.

    factory domain_check --idea S --name N [--tlds com,io,ai,dev,fr]

One RDAP lookup per TLD through rdap.org, free and keyless (v1 check-availability.sh): `taken`
when the registry holds the domain (200), `available` when it does not (404), `unknown` for any
other answer, rdap.org's own 404 for a TLD it has no RDAP server for (.io, .co, .de) included.
The research JSON is

    {"name", "domains": {domain: status}, "lab": "<name>.meikit.ai"}

`lab` is the idea's default address on the lab domain (spec D3): a subdomain, nothing to buy.
The name is one domain label (letters, digits and inner hyphens), lowercased. Nothing is spent
and no cost is logged. The summary is one row per domain, `domain | status`, then the lab address.
"""

import argparse
import re

from factory import tables, toolbase
from factory.providers import rdap

TOOL = "domain_check"
PROVIDER = "rdap"
LAB_DOMAIN = "meikit.ai"
DEFAULT_TLDS = "com,io,ai,dev,fr"
COLUMNS = ["domain", "status"]
SELFTEST_DOMAIN = "example.com"  # registered for good: a working lookup says taken
_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="whether <name>.<tld> is registered, by RDAP (free)",
        description="Look up <name>.<tld> for each TLD in RDAP (rdap.org, free): taken, "
        "available or unknown, and name the idea's lab address on the lab domain.",
    )
    parser.add_argument("--name", metavar="N", help="the name to check, without TLD (required)")
    parser.add_argument(
        "--tlds",
        default=DEFAULT_TLDS,
        metavar="A,B",
        help="the TLDs to look up, comma-separated (default: %(default)s)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        status = rdap.status(rdap.client(dry_run=args.dry_run), SELFTEST_DOMAIN)
        if status != "taken":
            raise toolbase.ToolError(f"rdap: {SELFTEST_DOMAIN} came back {status}, not taken")
        return toolbase.selftest_ok(PROVIDER, 1)
    name = _name(args.name)
    tlds = _tlds(args.tlds)
    with toolbase.run(args, tool=TOOL) as r:
        client = rdap.client(dry_run=r.dry_run)
        data = {
            "name": name,
            "domains": {f"{name}.{tld}": rdap.status(client, f"{name}.{tld}") for tld in tlds},
            "lab": f"{name}.{LAB_DOMAIN}",
        }
        r.write(data)
        r.summary(summary(data))
    return 0


def summary(data: dict) -> str:
    rows = [{"domain": domain, "status": status} for domain, status in data["domains"].items()]
    return f"{tables.render(rows, COLUMNS)}\nlab: {data['lab']}"


def _name(value: str | None) -> str:
    if value is None or not value.strip():
        raise toolbase.UsageError("--name is required: the name to check, without TLD")
    name = value.strip().lower()
    if not _LABEL.fullmatch(name):
        raise toolbase.UsageError(
            f"not a domain name label: {value.strip()!r} (letters, digits and inner hyphens, "
            "no TLD)"
        )
    return name


def _tlds(value: str) -> list[str]:
    """The TLDs of a comma-separated list, lowercased, without a leading dot, each once."""
    tlds: list[str] = []
    for part in value.split(","):
        tld = part.strip().lower().removeprefix(".")
        if not tld:
            continue
        if not _LABEL.fullmatch(tld):
            raise toolbase.UsageError(f"not a TLD: {part.strip()!r}")
        if tld not in tlds:
            tlds.append(tld)
    if not tlds:
        raise toolbase.UsageError("no TLD: give --tlds com,io,...")
    return tlds
