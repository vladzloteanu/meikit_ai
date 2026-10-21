"""`factory pricing_scan`: what competitors charge, and how, read from their pages.

    factory pricing_scan --idea S --urls U ...

Firecrawl scrapes each page's main content as markdown, one call a page (PRICE_TABLE_EUR:
0.01 EUR each, billed for the scrapes it answers), and the page is read for its offer. The
research JSON is

    {"pages": [{"url", "title", "headline", "prices": [str], "cta", "offer_shape"}]}

`title` is the page's title; `headline` its first heading of the highest level (its H1 when it
has one); `prices` every distinct price written on it, in order, as written (`$29/mo`, `19 € par
mois`, `29 EUR`); `cta` the text of its first call-to-action link (Start free trial, Book a demo,
Essai gratuit...); `offer_shape` is `subscription` (a price per month or year), `quote` (no price,
and a quote or a sales contact asked), `one_shot` (prices, none recurring) or `unknown`. What a
page does not give is null. A URL without a scheme is read as https; a page given twice is asked
once. The summary is one row per page: `url | offer_shape | prices | cta`.
"""

import argparse
import re
from urllib.parse import urlsplit

from factory import tables, toolbase
from factory.http import Client
from factory.providers import firecrawl

TOOL = "pricing_scan"
PROVIDER = "firecrawl"
COLUMNS = ["url", "offer_shape", "prices", "cta"]
SELFTEST_URL = "https://example.com"

# A price: a currency then an amount, or an amount then a currency, then what it is per, all on
# one line (a space may be a no-break one: `19\u202f€`). An amount written before its currency
# starts after neither a digit nor a letter (not `026 150 €` inside `2026 150 €`). A `$` or `£`
# after it is not followed by a digit, even after a space (`Tier 1 $9` holds `$9`, not `1 $`);
# a `€` only not at once, since French writes the amount first and a number may follow
# (`19 € 1er mois offert`, `99 € 49 €` an old and a new price; `Plan 2 €19/mois` holds `€19`).
_SP = r"[ \t\u00a0\u202f]"
_THOUSANDS = rf"(?:[,.]|{_SP})\d{{3}}"  # 1,299  1.299  1 299
_AMOUNT = rf"(?:\d{{1,3}}{_THOUSANDS}+(?:[.,]\d{{1,2}})?|\d+(?:[.,]\d{{1,2}})?)"
_CURRENCY_AFTER = rf"(?:€(?!\d)|[$£](?!{_SP}?\d)|(?:EUR|USD|GBP)\b)"
_UNIT = (
    r"(?:months?|mois|mos?|years?|yrs?|année|annum|an|weeks?|semaine|users?|seats?"
    r"|utilisateurs?|licen[cs]es?)\b"
)
_PER = rf"(?:{_SP}?/{_SP}?{_UNIT}|{_SP}(?:per|par|a){_SP}{_UNIT})"
PRICE = re.compile(
    rf"(?:[$€£]{_SP}?{_AMOUNT}|(?<!\w){_AMOUNT}{_SP}?{_CURRENCY_AFTER})"
    rf"(?:{_SP}?(?:HT|TTC)\b)?(?:{_PER}{{1,2}})?",
    re.IGNORECASE,
)
# What makes a price a subscription, in the price itself or right after it.
RECURRING = re.compile(
    r"/\s?(?:mo|month|mois|yr|year|an|année)s?\b"
    r"|\b(?:per|a|par|each|every|chaque|le)\s(?:month|mois|year|an|année|annum)\b"
    r"|\b(?:monthly|yearly|annually|mensuel(?:le)?s?|annuel(?:le)?s?)\b",
    re.IGNORECASE,
)
AFTER_PRICE = 40  # characters after a price read for what it recurs by
# What those characters hold that is not read: a link's target (`](https://x.example/an-overview)`,
# its text kept) and a bare URL, either cut short by the window's end.
_LINK_TARGET_OR_URL = re.compile(r"\]\([^)\n]*\)?|https?://\S*")
# A negation earlier in the same clause: "no monthly fees", "sans abonnement mensuel".
NEGATION = re.compile(
    r"\b(?:no|not|non|without|never|zero|sans|pas\s+d[e']?|aucun(?:e)?)\b[^.;:!?\n]{0,20}$",
    re.IGNORECASE,
)
QUOTE = re.compile(r"\b(?:quotes?|devis|(?:contact|talk\s+to)\s+(?:our\s+)?sales)\b", re.IGNORECASE)
# The words of a link that asks to act; French verbs by their stem (essayer, essayez...).
CTA = re.compile(
    r"\b(?:start(?:ed)?|try|trial|sign\s*up|register|book|request|schedule|demo"
    r"|(?:contact|talk\s+to)\s+(?:us|sales)|buy|order|subscribe|join|download"
    r"|essa\w*|commenc\w*|démarr\w*|inscri\w*|demand\w*|réserv\w*|contactez|nous\s+contacter"
    r"|achet\w*|command\w*|abonn\w*|télécharg\w*|devis|démo)\b",
    re.IGNORECASE,
)
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$", re.MULTILINE)
_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\([^)\n]*\)")
_IMAGE = re.compile(r"!\[[^\]\n]*\]\([^)\n]*\)")


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="competitor pages: their prices, offer shape, headline and call to action",
        description="Scrape competitor pages (Firecrawl, 0.01 EUR a page) and read their prices, "
        "offer shape (subscription, one-shot, quote), headline and call to action.",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        action="extend",
        metavar="U",
        help="the pages, one scrape each (https:// is assumed; the flag repeats)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = firecrawl.client(dry_run=args.dry_run)
        page = firecrawl.scrape(client, SELFTEST_URL)
        return toolbase.selftest_ok(PROVIDER, 1 if page.get("markdown") else 0)
    urls = _urls(args.urls or [])
    with toolbase.run(args, tool=TOOL, planned_eur=toolbase.api_cost(PROVIDER, len(urls))) as r:
        client = firecrawl.client(dry_run=r.dry_run)
        try:
            data = collect(client, urls)
            r.write(data)
        finally:
            r.log_cost(PROVIDER, client.ok_calls)  # the scrapes Firecrawl answered
        r.summary(summary(data))
    return 0


def collect(client: Client, urls: list[str]) -> dict:
    """The research JSON: one scrape per page, each page read for its offer."""
    return {"pages": [page(url, firecrawl.scrape(client, url)) for url in urls]}


def page(url: str, scraped: dict) -> dict:
    """What the page at `url` offers, from Firecrawl's `data` for it."""
    markdown = scraped.get("markdown")
    markdown = markdown if isinstance(markdown, str) else ""
    prices = extract_prices(markdown)
    return {
        "url": url,
        "title": _title(scraped.get("metadata")),
        "headline": headline(markdown),
        "prices": prices,
        "cta": cta(markdown),
        "offer_shape": guess_offer_shape(prices, markdown),
    }


def extract_prices(md: str) -> list[str]:
    """Every distinct price written in `md`, in order, as written (its spaces made plain):
    `$29`, `$29/mo`, `29 €`, `29€/mois`, `€29 per month`, `29 EUR`, `19 € HT par mois`. A word
    before the amount (`From`, `à partir de`) is not part of it."""
    prices: list[str] = []
    for match in PRICE.finditer(md):
        price = " ".join(match.group(0).split())
        if price not in prices:
            prices.append(price)
    return prices


def guess_offer_shape(prices: list[str], md: str) -> str:
    """`subscription` when a price says per month or per year (`/mo`, `month`, `mois`, `/yr`...),
    in itself or in the 40 characters after it in `md`, unless a negation comes first there ("no
    monthly fees"); `quote` when there is no price and the page asks for a quote or a sales
    contact (`quote`, `devis`, `contact sales`); `one_shot` for prices none of which recurs;
    `unknown` otherwise. What the page says elsewhere does not count, nor do the links' targets
    and the URLs after a price (`/an-overview` is no year)."""
    after = (
        _LINK_TARGET_OR_URL.sub(" ", md[match.end() : match.end() + AFTER_PRICE])
        for match in PRICE.finditer(md)
        if " ".join(match.group(0).split()) in prices
    )
    if any(_recurs(price) for price in prices) or any(_recurs(text) for text in after):
        return "subscription"
    if not prices and QUOTE.search(md):
        return "quote"
    return "one_shot" if prices else "unknown"


def headline(md: str) -> str | None:
    """The first heading of the highest level in `md` (its H1 when it has one), as plain text."""
    headings = [(len(m.group(1)), _plain(m.group(2))) for m in _HEADING.finditer(md)]
    headings = [(level, text) for level, text in headings if text]
    if not headings:
        return None
    top = min(level for level, _ in headings)
    return next(text for level, text in headings if level == top)


def cta(md: str) -> str | None:
    """The text of the first link in `md` that asks to act: start, try, sign up, book a demo,
    contact sales, buy, subscribe, essai, commencer, devis..."""
    for match in _LINK.finditer(md):
        text = _plain(match.group(1))
        if text and CTA.search(text):
            return text
    return None


def summary(data: dict) -> str:
    rows = [{**page, "prices": ", ".join(page["prices"])} for page in data["pages"]]
    return tables.render(rows, COLUMNS)


def _recurs(text: str) -> bool:
    """Whether `text` says per month or per year, with no negation before it in its clause."""
    return any(not NEGATION.search(text[: m.start()]) for m in RECURRING.finditer(text))


def _urls(values: list[str]) -> list[str]:
    """The pages to scrape: https:// added to a URL without a scheme, each page once."""
    urls: list[str] = []
    for value in values:
        url = value.strip()
        if url and "://" not in url:
            url = f"https://{url}"
        try:
            scheme = urlsplit(url).scheme
        except ValueError:  # https://[x
            scheme = ""
        if " " in url or scheme not in ("http", "https") or not toolbase.domain_of(url):
            raise toolbase.UsageError(f"not a web page address: {value.strip()!r}")
        if url not in urls:
            urls.append(url)
    if not urls:
        raise toolbase.UsageError("no URL: give --urls U ...")
    return urls


def _title(metadata: object) -> str | None:
    """The page's title from Firecrawl's metadata: a string, or the first of a list of them."""
    title = metadata.get("title") if isinstance(metadata, dict) else None
    if isinstance(title, list):
        title = next((t for t in title if isinstance(t, str) and t.strip()), None)
    if not isinstance(title, str):
        return None
    return " ".join(title.split()) or None


def _plain(text: str) -> str:
    """Markdown inline text as plain text: images dropped, links to their text, no emphasis."""
    text = _IMAGE.sub("", text)
    text = _LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"[*_`]+", "", text)
    return " ".join(text.split())
