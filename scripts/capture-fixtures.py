"""Capture the providers' dry-run fixtures with one real call each (real keys, real cost).

    uv run python scripts/capture-fixtures.py [--only searchapi|seranking]

The calls are listed in tools/factory/fixtures/README.md: 5 SearchAPI searches and 4 SE Ranking
calls. A fixture is written only from a 2xx answer, trimmed to 10 result items. A SearchAPI answer
keeps only `search_parameters` (without any key), `search_information` and its result lists, so
`search_metadata`, which echoes the request URL with the key, never reaches a file. The text goes
through `secrets.redact` before it is written. Every written file is then checked for every secret
value: a file holding one is deleted and the script exits 1. A 429 (a used-up quota, or rate
limits that outlast the retries) prints the provider's message on stderr and exits 1 before any
file is touched. Nothing here prints a secret value: only shapes, counts and dotpaths.
"""

import argparse
import functools
import json
import sys
from collections.abc import Callable, Iterator
from typing import Any
from urllib.parse import quote

from factory import secrets
from factory.http import FIXTURES, ProviderError
from factory.providers import searchapi, seranking

MAX_ITEMS = 10
SEARCHAPI_KEEP = (
    "search_parameters",
    "search_information",
    "ads",
    "organic_results",
    "ad_creatives",
)
SEARCHAPI_CALLS = {
    "google": {"q": "facebook ad account hacked", "gl": "us"},
    "meta_ad_library": {"q": "ad account security", "country": "ALL"},
    "tiktok_ads_library": {"q": "ad account hacked"},
    "google_ads_transparency_center": {"domain": "hootsuite.com", "region": "US", "num": 5},
    "linkedin_ad_library": {"q": "ad account security"},
}
SERANKING_CC = "us"
SERANKING_DOMAIN = "hootsuite.com"
SERANKING_KEYWORDS = ["facebook ad account hacked", "business manager hacked"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture the providers' dry-run fixtures.")
    parser.add_argument("--only", choices=["searchapi", "seranking"])
    args = parser.parse_args(argv)
    try:
        captured, failed = capture(args.only)
    except ProviderError as exc:  # a 429: stop before touching any file
        print(f"{exc}\nno fixture written", file=sys.stderr)
        return 1
    except secrets.SecretsError as exc:
        print(exc, file=sys.stderr)
        return 1
    leaked = write(captured)
    return 1 if failed or leaked else 0


def capture(only: str | None) -> tuple[dict[str, Any], list[str]]:
    """Each call's trimmed 2xx answer by fixture name, and the names of the calls that failed.

    A 429 is raised: the caller stops before anything is written.
    """
    calls: dict[str, Callable[[], Any]] = {}
    if only in (None, "searchapi"):
        sapi = searchapi.client()
        for engine, params in SEARCHAPI_CALLS.items():
            calls[f"searchapi/{engine}"] = functools.partial(
                searchapi.search, sapi, engine, **params
            )
    if only in (None, "seranking"):
        ser = seranking.client()
        calls["seranking/analyze_keywords"] = functools.partial(
            seranking.analyze_keywords, ser, SERANKING_CC, SERANKING_KEYWORDS
        )
        for name in ("domain_keywords", "domain_advertising", "domain_overview"):
            calls[f"seranking/{name}"] = functools.partial(
                getattr(seranking, name), ser, SERANKING_CC, SERANKING_DOMAIN
            )
    captured: dict[str, Any] = {}
    failed: list[str] = []
    for name, call in calls.items():
        try:
            data = call()
        except ProviderError as exc:
            if exc.status == 429:
                raise
            print(f"FAIL {name}: {exc}", file=sys.stderr)
            failed.append(name)
            continue
        print(f"got   {name}: {shape(data)}")
        captured[name] = trim(name, data)
    return captured, failed


def trim(name: str, data: Any) -> Any:
    """At most 10 result items; for SearchAPI only the parts the tools read, and no key."""
    if not name.startswith("searchapi/"):
        return data[:MAX_ITEMS] if isinstance(data, list) else data
    kept = {}
    for part in SEARCHAPI_KEEP:
        if part not in data:
            continue
        value = data[part]
        if part == "search_parameters":
            value = {k: v for k, v in value.items() if "key" not in k.lower()}
        elif isinstance(value, list):
            value = value[:MAX_ITEMS]
        kept[part] = value
    return kept


def write(captured: dict[str, Any]) -> list[str]:
    """Write each fixture redacted, then delete any written file still holding a secret value.

    Returns the names of the deleted fixtures.
    """
    config = secrets.load()
    values = [(p, v) for p, v in strings(config) if len(v) >= secrets.REDACT_MIN_LEN]
    for name, data in captured.items():
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        found = [path for path, value in values if value in text]
        if found:
            print(f"note  {name}: redacting the values of {', '.join(found)}")
        file = FIXTURES / f"{name}.json"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(secrets.redact(text), encoding="utf-8")
        print(f"wrote fixtures/{name}.json: {shape(data)}")
    # Every form `secrets.redact` replaces: raw, URL-encoded and JSON-escaped.
    forms = {f for _, v in values for f in (v, quote(v, safe=""), json.dumps(v)[1:-1])}
    leaked = []
    for name in captured:
        file = FIXTURES / f"{name}.json"
        if any(form in file.read_text(encoding="utf-8") for form in forms):
            file.unlink()
            leaked.append(name)
            print(f"secret value found: deleted fixtures/{name}.json", file=sys.stderr)
    print("secret check:", "FAILED" if leaked else "OK")
    return leaked


def strings(node: Any, path: str = "") -> Iterator[tuple[str, str]]:
    """(dotpath, value) for every string in the config."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from strings(value, f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from strings(value, f"{path}[{index}]")


def shape(data: Any) -> str:
    """List lengths and dict keys, never values."""
    if isinstance(data, list):
        return f"list[{len(data)}]"
    if isinstance(data, dict):
        parts = (f"{k}[{len(v)}]" if isinstance(v, (list, dict)) else k for k, v in data.items())
        return "{" + ", ".join(parts) + "}"
    return type(data).__name__


if __name__ == "__main__":
    sys.exit(main())
