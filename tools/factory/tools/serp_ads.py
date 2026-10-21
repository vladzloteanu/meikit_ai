"""`factory serp_ads`: who buys Google ads on the idea's keywords, and who ranks under them.

    factory serp_ads --idea S (--keywords K ... | --keywords-file F) [--gl us] [--hl en] [--num 10]

One SearchAPI `google` search per keyword (PRICE_TABLE_EUR: 0.01 EUR each) reads the live SERP,
its ads and its organic results. The research JSON is

    {"gl", "hl",
     "queries": {keyword: {"n_ads",
                           "ads": [{"position", "title", "domain", "link", "snippet", "sitelinks"}],
                           "organic": [{"p", "domain", "title", "url"}]}},
     "advertisers": {domain: the number of keywords it has an ad on}}

with the fields of the v1 `serp_harvest.py`. A domain is a host without `www.`; an ad's sitelinks
are `{"title", "snippet", "link"}`; the advertisers run from the most keywords to the fewest. What
the SERP does not give is null. The summary is one row per keyword: `keyword | n_ads | advertisers`.

The keywords file holds one keyword per line; blank lines and lines starting with `#` are skipped.
A keyword given twice, whatever its case, is searched once.
"""

import argparse
from collections import Counter
from pathlib import Path

from factory import tables, toolbase
from factory.http import Client
from factory.providers import searchapi

TOOL = "serp_ads"
PROVIDER = "searchapi"
ENGINE = "google"
COLUMNS = ["keyword", "n_ads", "advertisers"]
SELFTEST_QUERY = "ad account security"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="live Google SERPs of keywords: who advertises, who ranks",
        description="One live Google search per keyword (SearchAPI, 0.01 EUR each): its ads, its "
        "organic results, and which advertisers come back across the keywords.",
    )
    keywords = parser.add_mutually_exclusive_group()
    keywords.add_argument(
        "--keywords",
        nargs="+",
        action="extend",
        metavar="K",
        help="the keywords, one search each (quote a phrase; the flag repeats)",
    )
    keywords.add_argument(
        "--keywords-file",
        type=Path,
        metavar="F",
        help="a file of keywords, one per line (# starts a comment line)",
    )
    parser.add_argument("--gl", default="us", help="Google's country (default: %(default)s)")
    parser.add_argument("--hl", default="en", help="Google's language (default: %(default)s)")
    parser.add_argument(
        "--num",
        type=toolbase.positive_int,
        default=10,
        help="results per SERP (default: %(default)s; Google answers 10 whatever is asked)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = searchapi.client(dry_run=args.dry_run)
        serp = search_keyword(client, SELFTEST_QUERY, "us", "en", 10)
        return toolbase.selftest_ok(PROVIDER, len(serp["ads"]) + len(serp["organic"]))
    keywords = _keywords(args)
    planned = toolbase.api_cost(PROVIDER, len(keywords))
    with toolbase.run(args, tool=TOOL, planned_eur=planned) as r:
        client = searchapi.client(dry_run=r.dry_run)
        try:
            data = collect(client, keywords, args.gl, args.hl, args.num)
            r.write(data)
        finally:
            r.log_cost(PROVIDER, client.ok_calls)
        r.summary(summary(data))
    return 0


def collect(client: Client, keywords: list[str], gl: str, hl: str, num: int) -> dict:
    """The research JSON: one search per keyword, then the advertisers across them."""
    queries = {keyword: search_keyword(client, keyword, gl, hl, num) for keyword in keywords}
    return {"gl": gl, "hl": hl, "queries": queries, "advertisers": advertisers(queries)}


def search_keyword(client: Client, keyword: str, gl: str, hl: str, num: int) -> dict:
    """The SERP of one keyword as the research JSON holds it: `{"n_ads", "ads", "organic"}`."""
    raw = searchapi.search(client, ENGINE, q=keyword, gl=gl, hl=hl, num=num)
    ads = [_ad(ad) for ad in _items(raw, "ads")]
    organic = [_organic(result) for result in _items(raw, "organic_results")]
    return {"n_ads": len(ads), "ads": ads, "organic": organic}


def advertisers(queries: dict) -> dict[str, int]:
    """{domain: the number of keywords with an ad of it}, the most keywords first, then by name."""
    counts = Counter(
        domain
        for serp in queries.values()
        for domain in {ad["domain"] for ad in serp["ads"]}
        if domain
    )
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def summary(data: dict) -> str:
    rows = [
        {
            "keyword": keyword,
            "n_ads": serp["n_ads"],
            "advertisers": ", ".join(
                dict.fromkeys(ad["domain"] for ad in serp["ads"] if ad["domain"])
            ),
        }
        for keyword, serp in data["queries"].items()
    ]
    return tables.render(rows, COLUMNS)


def read_keywords_file(path: Path) -> list[str]:
    """The keywords of a file, one per line, without blank lines and `#` lines."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise toolbase.UsageError(f"cannot read {path}: {exc.strerror or exc}") from None
    except UnicodeDecodeError:
        raise toolbase.UsageError(f"{path} is not UTF-8 text") from None
    return [
        line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]


def _keywords(args: argparse.Namespace) -> list[str]:
    if args.keywords_file is not None:
        keywords = toolbase.unique_terms(read_keywords_file(args.keywords_file))
        if not keywords:
            raise toolbase.UsageError(f"no keyword in {args.keywords_file}")
        return keywords
    keywords = toolbase.unique_terms(args.keywords or [])
    if not keywords:
        raise toolbase.UsageError("no keyword: give --keywords K ... or --keywords-file F")
    return keywords


def _items(raw: object, key: str) -> list[dict]:
    """The objects of the list `raw[key]`; nothing when the answer has no such list."""
    value = raw.get(key) if isinstance(raw, dict) else None
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _ad(ad: dict) -> dict:
    domain = (
        toolbase.domain_of(ad.get("domain"))
        or toolbase.domain_of(ad.get("link"))
        or toolbase.domain_of(ad.get("displayed_link"))
    )
    return {
        "position": ad.get("position"),
        "title": ad.get("title"),
        "domain": domain,
        "link": ad.get("link"),
        "snippet": ad.get("snippet"),
        "sitelinks": _sitelinks(ad.get("sitelinks")),
    }


def _sitelinks(sitelinks: object) -> list[dict]:
    """An ad's sitelinks, the expanded ones then the inline ones."""
    groups = (
        [sitelinks.get("expanded"), sitelinks.get("inline")] if isinstance(sitelinks, dict) else []
    )
    return [
        {"title": link.get("title"), "snippet": link.get("snippet"), "link": link.get("link")}
        for group in groups
        if isinstance(group, list)
        for link in group
        if isinstance(link, dict)
    ]


def _organic(result: dict) -> dict:
    return {
        "p": result.get("position"),
        "domain": toolbase.domain_of(result.get("domain"))
        or toolbase.domain_of(result.get("link")),
        "title": result.get("title"),
        "url": result.get("link"),
    }
