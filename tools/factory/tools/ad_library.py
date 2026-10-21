"""`factory ad_library`: who advertises on a term, or for a domain, in a public ad library.

    factory ad_library --idea S --engine (meta|tiktok|linkedin|google_transparency)
                       (--q TERM | --domain D) [--country ALL|FR|..] [--region US] [--num 20]

One SearchAPI call (PRICE_TABLE_EUR: 0.01 EUR) to one library, each searched its own way:

    meta                 Meta Ad Library (meta_ad_library): --q in --country (default ALL)
    tiktok               TikTok Ads Library (tiktok_ads_library, EEA ads only): --q in --country
    linkedin             LinkedIn Ad Library (linkedin_ad_library): --q in --country
    google_transparency  Google Ads Transparency Center (google_ads_transparency_center): the ads
                         of the advertisers verified for --domain, in --region (default US); it
                         has no keyword search

A combination a library cannot run (a --domain for meta, a --region for linkedin...) is refused
before any call. The research JSON is

    {"engine", "query", "total_results",
     "items": [{"advertiser", "page_or_domain", "text", "format", "first_seen", "last_seen",
                "active", "link"}]}

`query` is what was searched, `{"q", "country"}` or `{"domain", "region", "num"}`; `total_results`
is the library's own count; `items` are the first --num ads of the one page fetched. Each item
reads the fields the v1 ad-intel scripts read (meta_ads.py, tiktok_ads.py, linkedin_ads.py,
google_transparency.py). What a library does not give is null: TikTok and LinkedIn give no domain,
LinkedIn no dates, only Meta says whether an ad is active, Google Transparency gives no text.
`page_or_domain` is the landing domain (Meta: of the ad's link or caption, else the page's URL;
Google Transparency: the target domain); `link` is the landing page on Meta, the video or first
image on TikTok, the ad's page on LinkedIn and Google Transparency.
"""

import argparse
from collections.abc import Callable

from factory import tables, toolbase
from factory.http import Client
from factory.providers import searchapi

TOOL = "ad_library"
PROVIDER = "searchapi"
# --engine -> SearchAPI's engine
ENGINES = {
    "meta": "meta_ad_library",
    "tiktok": "tiktok_ads_library",
    "linkedin": "linkedin_ad_library",
    "google_transparency": "google_ads_transparency_center",
}
BY_DOMAIN = "google_transparency"  # the one library searched by domain, not by keyword
DEFAULT_COUNTRY = "ALL"  # every keyword library's own default
DEFAULT_REGION = "US"
MAX_NUM = 100  # Google Transparency answers at most 100 ads a call
COLUMNS = ["advertiser", "page_or_domain", "format", "first_seen", "last_seen", "active", "text"]
TEXT_WIDTH = 60
SELFTEST_QUERY = "ad account"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="the ads in a public ad library (Meta, TikTok, LinkedIn, Google Transparency)",
        description="The ads one public ad library shows for a term (Meta, TikTok, LinkedIn) or "
        "for an advertiser's domain (Google Ads Transparency Center): one SearchAPI call, "
        "0.01 EUR.",
    )
    parser.add_argument("--engine", choices=list(ENGINES), help="the library (required)")
    query = parser.add_mutually_exclusive_group()
    query.add_argument("--q", metavar="TERM", help="the term to search (meta, tiktok, linkedin)")
    query.add_argument(
        "--domain", metavar="D", help="the advertiser's domain (google_transparency)"
    )
    parser.add_argument(
        "--country",
        metavar="CC",
        help=f"the country of the ads: ALL, FR, US... (meta, tiktok, linkedin; default: "
        f"{DEFAULT_COUNTRY})",
    )
    parser.add_argument(
        "--region",
        metavar="CC",
        help=f"the region of the ads: US, FR, anywhere... (google_transparency; default: "
        f"{DEFAULT_REGION})",
    )
    parser.add_argument(
        "--num",
        type=toolbase.positive_int,
        default=20,
        help=f"the most ads to keep (default: %(default)s; google_transparency asks for that "
        f"many, at most {MAX_NUM})",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = searchapi.client(dry_run=args.dry_run)
        data = collect(client, "meta", {"q": SELFTEST_QUERY, "country": DEFAULT_COUNTRY}, args.num)
        return toolbase.selftest_ok(PROVIDER, len(data["items"]))
    engine, query = _query(args)
    with toolbase.run(args, tool=TOOL, planned_eur=toolbase.api_cost(PROVIDER, 1)) as r:
        client = searchapi.client(dry_run=r.dry_run)
        try:
            data = collect(client, engine, query, args.num)
            r.write(data)
        finally:
            r.log_cost(PROVIDER, client.calls)
        r.summary(summary(data))
    return 0


def collect(client: Client, engine: str, query: dict, num: int) -> dict:
    """The research JSON of one library call: `engine` searched for `query`, `num` items kept."""
    params = dict(query)
    if str(params.get("country", "")).upper() == "ALL":
        del params["country"]  # all countries is every keyword library's default
    raw = searchapi.search(client, ENGINES[engine], **params)
    ads = _items(raw, "ad_creatives" if engine == BY_DOMAIN else "ads")
    return {
        "engine": engine,
        "query": query,
        "total_results": _total(raw, len(ads)),
        "items": [ITEM_OF[engine](ad) for ad in ads[:num]],
    }


def summary(data: dict) -> str:
    query = data["query"]
    if "q" in query:
        what = f'"{query["q"]}" in {query["country"]}'
    else:
        what = f"{query['domain']} in {query['region']}"
    head = (
        f"{data['engine']}: {data['total_results']} ads for {what}; the first {len(data['items'])}:"
    )
    rows = [
        {
            **item,
            "first_seen": _day(item["first_seen"]),
            "last_seen": _day(item["last_seen"]),
            "active": {True: "yes", False: "no"}.get(item["active"]),  # True, False or None
            "text": _short(item["text"]),
        }
        for item in data["items"]
    ]
    return f"{head}\n{tables.render(rows, COLUMNS)}"


def _query(args: argparse.Namespace) -> tuple[str, dict]:
    """The engine and what to search, once the flags are known to suit the library."""
    engine = args.engine
    if engine is None:
        raise toolbase.UsageError(f"--engine is required: {', '.join(ENGINES)}")
    if engine == BY_DOMAIN:
        if args.q is not None:
            raise toolbase.UsageError(f"{engine} has no keyword search: give --domain D")
        if args.country is not None:
            raise toolbase.UsageError(f"{engine} takes --region, not --country")
        if not args.domain or not args.domain.strip():
            raise toolbase.UsageError(f"{engine} needs --domain D")
        if args.num > MAX_NUM:
            raise toolbase.UsageError(
                f"{engine} answers at most {MAX_NUM} ads a call: --num {args.num} is too many"
            )
        domain = toolbase.domain_of(args.domain) or args.domain.strip()
        return engine, {"domain": domain, "region": args.region or DEFAULT_REGION, "num": args.num}
    if args.domain is not None:
        raise toolbase.UsageError(
            f"{engine} searches by --q TERM; --domain works with {BY_DOMAIN} only"
        )
    if args.region is not None:
        raise toolbase.UsageError(f"{engine} takes --country, not --region")
    if not args.q or not args.q.strip():
        raise toolbase.UsageError(f"{engine} needs --q TERM")
    return engine, {"q": " ".join(args.q.split()), "country": args.country or DEFAULT_COUNTRY}


# --- one item per library, by the field paths of the v1 scripts --------------------------------


def _meta_item(ad: dict) -> dict:
    snapshot = _object(ad.get("snapshot"))
    body = snapshot.get("body")  # documented as {"text": ...}
    text = body.get("text") if isinstance(body, dict) else body
    if not text:  # a carousel or dynamic ad keeps its text in its cards
        cards = snapshot.get("cards")
        text = _object(cards[0] if isinstance(cards, list) and cards else None).get("body")
    return {
        "advertiser": snapshot.get("page_name") or ad.get("page_name"),
        "page_or_domain": toolbase.domain_of(snapshot.get("link_url"))
        or toolbase.domain_of(snapshot.get("caption"))
        or snapshot.get("page_profile_uri"),
        "text": text or snapshot.get("title"),
        "format": snapshot.get("display_format"),
        "first_seen": ad.get("start_date"),
        "last_seen": ad.get("end_date"),
        "active": ad.get("is_active") if isinstance(ad.get("is_active"), bool) else None,
        "link": snapshot.get("link_url"),
    }


def _tiktok_item(ad: dict) -> dict:
    images = ad.get("image_urls") if isinstance(ad.get("image_urls"), list) else []
    return {
        "advertiser": _name(ad.get("advertiser")),
        "page_or_domain": None,
        "text": ad.get("title"),
        "format": ad.get("format"),
        "first_seen": ad.get("first_shown_datetime"),
        "last_seen": ad.get("last_shown_datetime"),
        "active": None,
        "link": ad.get("video_link") or (images[0] if images else None),
    }


def _linkedin_item(ad: dict) -> dict:
    content = _object(ad.get("content"))
    return {
        "advertiser": _name(ad.get("advertiser")),
        "page_or_domain": None,
        # event ads keep their headline outside `content`, document ads have a title
        "text": content.get("headline") or ad.get("headline") or content.get("title"),
        "format": ad.get("ad_type"),
        "first_seen": None,
        "last_seen": None,
        "active": None,
        "link": ad.get("link"),
    }


def _transparency_item(creative: dict) -> dict:
    return {
        "advertiser": _name(creative.get("advertiser")),
        "page_or_domain": toolbase.domain_of(creative.get("target_domain"))
        or creative.get("target_domain"),
        "text": None,
        "format": creative.get("format"),
        "first_seen": creative.get("first_shown_datetime"),
        "last_seen": creative.get("last_shown_datetime"),
        "active": None,
        "link": creative.get("details_link"),
    }


ITEM_OF: dict[str, Callable[[dict], dict]] = {
    "meta": _meta_item,
    "tiktok": _tiktok_item,
    "linkedin": _linkedin_item,
    "google_transparency": _transparency_item,
}


def _items(raw: object, key: str) -> list[dict]:
    """The objects of the list `raw[key]`; nothing when the answer has no such list."""
    value = raw.get(key) if isinstance(raw, dict) else None
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _object(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _name(advertiser: object) -> str | None:
    """An advertiser as the libraries give it: a name, or an object with a `name`."""
    if isinstance(advertiser, dict):
        return advertiser.get("name")
    return advertiser if isinstance(advertiser, str) else None


def _total(raw: object, fallback: int) -> int:
    """`search_information.total_results` as a number (`1,234` too), else `fallback`."""
    info = raw.get("search_information") if isinstance(raw, dict) else None
    total = info.get("total_results") if isinstance(info, dict) else None
    if isinstance(total, str) and total.replace(",", "").strip().isdecimal():
        return int(total.replace(",", ""))
    if isinstance(total, int) and not isinstance(total, bool):
        return total
    if isinstance(total, float) and total.is_integer():  # not nan, not inf
        return int(total)
    return fallback


def _day(timestamp: object) -> str | None:
    return timestamp[:10] if isinstance(timestamp, str) else None


def _short(text: object) -> str | None:
    if not isinstance(text, str):
        return None
    text = " ".join(text.split())
    return text if len(text) <= TEXT_WIDTH else text[: TEXT_WIDTH - 1] + "…"
