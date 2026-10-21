"""`factory keyword_volume`: how many people search the idea's keywords, and what a click costs.

    factory keyword_volume --idea S --cc us (--keywords K ... | --buckets-file F) [--language en]

SE Ranking's analyze-keywords gives each keyword its monthly volume, CPC, paid competition (0 to 1),
organic difficulty (0 to 100), intents and 12-month trend, 20 keywords per call (PRICE_TABLE_EUR:
0.02 EUR a call). The buckets file sorts the keywords by how close the searcher is to buying:

    {"solution_aware": [...], "problem_aware": [...], "trigger": [...], "adjacent_budget": [...]}

any of the four, each a list of keywords, no keyword in two of them. The research JSON is

    {"cc", "language",
     "keywords": {keyword: {"volume", "cpc", "competition", "difficulty", "intents", "trend_12m",
                            "found", "bucket"}},
     "buckets": {bucket: {"volume_sum", "n", "cpc_median"}}}

A keyword SE Ranking has no data for stays in `keywords` with `found: false`, null figures, no
intents and no trend. A bucket's figures count only its found keywords, `n` of them; every bucket
of the file is listed, an empty one too. `bucket` is null for --keywords, and `buckets` empty.
`trend_12m` is the monthly volumes, oldest first. `cc` is SE Ranking's country (`uk` for GB);
`language` is the language the keywords are written in, recorded with them: SE Ranking's volumes
are per country. The summary is one row per bucket, then the 15 keywords searched the most (when
any has data), then the keywords without data.
"""

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

from factory import tables, toolbase
from factory.providers import seranking

TOOL = "keyword_volume"
PROVIDER = "seranking"
BUCKETS = ["solution_aware", "problem_aware", "trigger", "adjacent_budget"]
TOP = 15
BUCKET_COLUMNS = ["bucket", "found", "volume_sum", "cpc_median"]
KEYWORD_COLUMNS = ["keyword", "bucket", "volume", "cpc", "competition", "difficulty"]
SELFTEST_KEYWORD = "crm software"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        TOOL,
        help="monthly search volume, CPC and trend of keywords, by bucket",
        description="Monthly volume, CPC, competition, difficulty, intents and 12-month trend of "
        "each keyword in one country (SE Ranking, 20 keywords per call at 0.02 EUR), summed by "
        "bucket.",
    )
    parser.add_argument(
        "--cc",
        metavar="CC",
        help="the country of the volumes: us, fr, gb (asked as uk)... (required unless --selftest)",
    )
    keywords = parser.add_mutually_exclusive_group()
    keywords.add_argument(
        "--keywords",
        nargs="+",
        action="extend",
        metavar="K",
        help="the keywords, without buckets (quote a phrase; the flag repeats)",
    )
    keywords.add_argument(
        "--buckets-file",
        type=Path,
        metavar="F.json",
        help=f"a JSON object of keyword lists by bucket: {', '.join(BUCKETS)}",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="the language the keywords are written in, recorded with the results "
        "(default: %(default)s)",
    )
    toolbase.add_common(parser)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    if args.selftest:
        client = seranking.client(dry_run=args.dry_run)
        rows = seranking.analyze_keywords(client, "us", [SELFTEST_KEYWORD])
        return toolbase.selftest_ok(PROVIDER, len(rows))
    if not args.cc or not args.cc.strip():
        raise toolbase.UsageError("--cc is required: the country of the volumes (us, fr, gb...)")
    buckets = _buckets(args)
    keywords = [keyword for words in buckets.values() for keyword in words]
    planned = toolbase.api_cost(PROVIDER, math.ceil(len(keywords) / seranking.BATCH_SIZE))
    with toolbase.run(args, tool=TOOL, planned_eur=planned) as r:
        client = seranking.client(dry_run=r.dry_run)
        cc = seranking.cc(args.cc)
        try:
            rows = seranking.analyze_keywords(client, cc, keywords)
            data, not_asked = collect(cc, args.language, buckets, rows)
            if not_asked:
                listed = ", ".join(repr(keyword) for keyword in not_asked)
                print(
                    f"{TOOL}: SE Ranking answered for {len(not_asked)} keyword"
                    f"{'' if len(not_asked) == 1 else 's'} not asked, ignored: {listed}",
                    file=sys.stderr,
                )
            r.write(data)
        finally:
            r.log_cost(PROVIDER, client.calls)
        r.summary(summary(data))
    return 0


def collect(
    cc: str, language: str, buckets: dict[str | None, list[str]], rows: list
) -> tuple[dict, list[str]]:
    """The research JSON for the keywords of `buckets` from SE Ranking's `rows`, and the keywords
    of the rows that answer no keyword asked.

    A row answers the keyword it names whatever its case and spacing; the first row wins.
    """
    by_key: dict[str, dict] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("keyword"), str):
            by_key.setdefault(toolbase.term_key(row["keyword"]), row)
    keywords = {
        keyword: _figures(by_key.get(toolbase.term_key(keyword)), bucket)
        for bucket, words in buckets.items()
        for keyword in words
    }
    asked = {toolbase.term_key(keyword) for keyword in keywords}
    not_asked = [row["keyword"] for key, row in by_key.items() if key not in asked]
    figures = {
        bucket: _bucket_figures([keywords[keyword] for keyword in words])
        for bucket, words in buckets.items()
        if bucket is not None
    }
    data = {"cc": cc, "language": language, "keywords": keywords, "buckets": figures}
    return data, not_asked


def read_buckets(path: Path) -> dict[str | None, list[str]]:
    """{bucket: keywords} of a buckets file, the buckets in BUCKETS order, the keywords in file
    order with each kept once. Raises UsageError, naming the file, for a file that cannot be read,
    is not a JSON object of known buckets each holding a list of keywords, puts one keyword in two
    buckets, or holds no keyword at all."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise toolbase.UsageError(f"cannot read {path}: {exc.strerror or exc}") from None
    except ValueError as exc:  # not JSON, or not UTF-8
        raise toolbase.UsageError(f"{path} is not valid JSON: {exc}") from None
    if not isinstance(data, dict):
        raise toolbase.UsageError(
            f"{path} must hold a JSON object of keyword lists by bucket ({', '.join(BUCKETS)})"
        )
    for name in data:
        if name not in BUCKETS:
            raise toolbase.UsageError(
                f"{path}: unknown bucket {name!r} (buckets: {', '.join(BUCKETS)})"
            )
    buckets: dict[str | None, list[str]] = {}
    bucket_of: dict[str, str] = {}
    for bucket in (name for name in BUCKETS if name in data):
        words = data[bucket]
        if not isinstance(words, list) or not all(isinstance(word, str) for word in words):
            raise toolbase.UsageError(f"{path}: {bucket} must be a list of keywords")
        buckets[bucket] = toolbase.unique_terms(words)
        for keyword in buckets[bucket]:
            other = bucket_of.setdefault(toolbase.term_key(keyword), bucket)
            if other != bucket:
                raise toolbase.UsageError(f"{path}: {keyword!r} is in both {other} and {bucket}")
    if not bucket_of:
        raise toolbase.UsageError(f"{path} holds no keyword")
    return buckets


def summary(data: dict) -> str:
    keywords = data["keywords"]
    parts = []
    if data["buckets"]:
        asked = Counter(figures["bucket"] for figures in keywords.values())
        rows = [
            {
                "bucket": bucket,
                "found": f"{figures['n']}/{asked[bucket]}",
                "volume_sum": figures["volume_sum"],
                "cpc_median": figures["cpc_median"],
            }
            for bucket, figures in data["buckets"].items()
        ]
        parts.append(tables.render(rows, BUCKET_COLUMNS))
    searched = [
        (keyword, figures)
        for keyword, figures in keywords.items()
        if figures["found"] and _is_number(figures["volume"])
    ]
    searched.sort(key=lambda item: (-item[1]["volume"], item[0]))
    if searched:
        top = [{"keyword": keyword, **figures} for keyword, figures in searched[:TOP]]
        columns = [c for c in KEYWORD_COLUMNS if c != "bucket" or data["buckets"]]
        parts.append(f"top {TOP} keywords by volume:\n{tables.render(top, columns)}")
    missing = [keyword for keyword, figures in keywords.items() if not figures["found"]]
    if missing:
        parts.append(
            f"no data in SE Ranking ({data['cc']}) for {len(missing)} of {len(keywords)} "
            f"keywords: {', '.join(missing)}"
        )
    return "\n\n".join(parts)


def _buckets(args: argparse.Namespace) -> dict[str | None, list[str]]:
    """{bucket: keywords} to ask: the buckets file's, or the --keywords under the bucket None."""
    if args.buckets_file is not None:
        return read_buckets(args.buckets_file)
    keywords = toolbase.unique_terms(args.keywords or [])
    if not keywords:
        raise toolbase.UsageError("no keyword: give --keywords K ... or --buckets-file F.json")
    return {None: keywords}


def _figures(row: dict | None, bucket: str | None) -> dict:
    """A keyword's entry in the research JSON, from its SE Ranking row (None: no row)."""
    if row is None or not _found(row):
        return {
            "volume": None,
            "cpc": None,
            "competition": None,
            "difficulty": None,
            "intents": [],
            "trend_12m": [],
            "found": False,
            "bucket": bucket,
        }
    intents = row.get("intents")
    return {
        "volume": row.get("volume"),
        "cpc": row.get("cpc"),
        "competition": row.get("competition"),
        "difficulty": row.get("difficulty"),
        "intents": list(intents) if isinstance(intents, list) else [],
        "trend_12m": _trend(row.get("history_trend")),
        "found": True,
        "bucket": bucket,
    }


def _found(row: dict) -> bool:
    if "is_data_found" in row:
        return bool(row["is_data_found"])
    return row.get("volume") is not None


def _trend(history: object) -> list:
    """The last 12 monthly volumes of `history_trend`, oldest first: SE Ranking documents an object
    `{"YYYY-MM-01": volume}`; a list is taken as already in order."""
    if isinstance(history, dict):
        return [history[month] for month in sorted(history)][-12:]
    if isinstance(history, list):
        return history[-12:]
    return []


def _bucket_figures(entries: list[dict]) -> dict:
    found = [entry for entry in entries if entry["found"]]
    cpcs = [entry["cpc"] for entry in found if _is_number(entry["cpc"])]
    return {
        "volume_sum": sum(entry["volume"] for entry in found if _is_number(entry["volume"])),
        "n": len(found),
        "cpc_median": round(statistics.median(cpcs), 2) if cpcs else None,
    }


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)
