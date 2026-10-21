"""What every research tool shares: the common flags, the run of one idea, the error lines.

A research tool (`serp_ads`, `keyword_volume`, `ad_library`, ...) is a module under `factory.tools`.
Its parser takes its own flags plus the ones `add_common` adds, and its `run` reads:

    @toolbase.handle_errors
    def run(args):
        if args.selftest:                         # one minimal real call, no idea needed
            ...
            return toolbase.selftest_ok("searchapi", n)
        keywords = ...                            # read and check the input first
        planned = toolbase.api_cost("searchapi", len(keywords))
        with toolbase.run(args, tool="serp_ads", planned_eur=planned) as r:
            client = searchapi.client(dry_run=r.dry_run)
            try:
                data = ...                        # the provider calls
                r.write(data)
            finally:
                r.log_cost("searchapi", client.calls)
            r.summary(table)
        return 0

Entering `toolbase.run` refuses a missing or unknown idea, and a planned spend that would take the
idea past its cap unless --force, before any key is read or any call made; the cap is checked in a
dry run too. `r.write` puts the research JSON in
`ideas/<slug>/research/<tool>_<YYYYMMDD-HHMMSS>.json` (or --out) through a `.tmp` file renamed
into place, so no half-written file is ever left. `r.log_cost` appends to the idea's costs.jsonl
what the calls cost by `costs.PRICE_TABLE_EUR`, the calls made before a failure included.

A dry run answers from the fixtures and logs nothing. Its file is
`<tool>_<YYYYMMDD-HHMMSS>.dryrun.json` and its JSON starts with `"dry_run": true` (at --out and
on stdout too), so canned data never passes for real research.

Output: the summary, or with --json the research JSON, goes to stdout; what the run did (the file
written, the cost logged) goes to stderr. `handle_errors` turns an unknown idea, the cap, a provider
error, a missing key or a bad input into one line `<tool>: <message>` on stderr and exit code 1
(2 for a usage error), never a traceback.
"""

import argparse
import functools
import json
import os
import sys
from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path
from typing import Self
from urllib.parse import urlsplit

from factory import costs, ledger, paths, secrets
from factory.http import ProviderError

DEFAULT_PHASE = "triage"
STAMP_FORMAT = "%Y%m%d-%H%M%S"
DRY_RUN_SUFFIX = ".dryrun.json"  # a dry run's research file, so it never passes for real research


class ToolError(Exception):
    """The tool cannot do what it was asked. The message is one line; the exit code is 1."""


class UsageError(ToolError):
    """The command line, or an input file it names, cannot be used as given; the exit code is 2."""


# What `handle_errors` reports as one line instead of a traceback.
FAILURES = (ledger.LedgerError, ProviderError, secrets.SecretsError, ToolError)


def add_common(parser: argparse.ArgumentParser) -> None:
    """Add the flags every research tool takes. `--idea` is checked when the run starts, because a
    selftest needs none."""
    parser.add_argument(
        "--idea",
        metavar="SLUG",
        help="the idea the research is for, its folder under ideas/ (required unless --selftest)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="answer from the fixtures: no network, no key read, no cost logged; the research "
        "file is <tool>_<ts>.dryrun.json and says dry_run: true",
    )
    parser.add_argument(
        "--json", action="store_true", help="print the research JSON instead of the summary"
    )
    parser.add_argument(
        "--out",
        type=Path,
        metavar="FILE",
        help="write the research JSON to FILE instead of ideas/<slug>/research/<tool>_<ts>.json",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="make one minimal real call and print `OK <provider> <n> items`; needs no --idea, "
        "writes and logs nothing",
    )
    parser.add_argument(
        "--phase",
        default=DEFAULT_PHASE,
        help="the plan step the cost is logged under (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="run even when the planned cost takes the idea past its cap",
    )


def handle_errors(
    run_tool: Callable[[argparse.Namespace], int],
) -> Callable[[argparse.Namespace], int]:
    """Wrap a tool's `run`: a known failure (FAILURES) is one line `<tool>: <message>` on stderr
    and exit code 1, or 2 for a UsageError. Anything else is a bug and propagates."""

    @functools.wraps(run_tool)
    def run_reporting_errors(args: argparse.Namespace) -> int:
        try:
            return run_tool(args)
        except FAILURES as exc:
            message = str(exc)
            if isinstance(exc, costs.CapExceeded):
                message += "; --force runs anyway"
            print(f"{args.tool}: {' '.join(message.split())}", file=sys.stderr)
            return 2 if isinstance(exc, UsageError) else 1

    return run_reporting_errors


def run(args: argparse.Namespace, tool: str, planned_eur: float = 0.0) -> Run:
    """The run of `tool` for `args.idea`: `with toolbase.run(args, tool="serp_ads") as r:`.

    `planned_eur` is what the run is expected to cost, checked against the idea's cap on entry.
    """
    return Run(args, tool, planned_eur)


class Run:
    """One run of a research tool for one idea (see the module docstring).

    `slug` and `dry_run` come from the command line; `written` is the research file once written.
    """

    def __init__(self, args: argparse.Namespace, tool: str, planned_eur: float = 0.0) -> None:
        self.args = args
        self.tool = tool
        self.planned_eur = planned_eur
        self.slug: str | None = args.idea
        self.dry_run: bool = args.dry_run
        self.written: Path | None = None
        self._spend: list[tuple[float, str]] = []  # (amount_eur, note) of each cost of the run

    def __enter__(self) -> Self:
        if not self.slug:
            raise UsageError("--idea is required (or --selftest)")
        # Loads the idea first: an unknown slug is IdeaNotFound, --force or not.
        costs.check_cap(self.slug, self.planned_eur, force=self.args.force)
        return self

    def __exit__(self, exc_type: type[BaseException] | None, *exc_info: object) -> None:
        if exc_type is None:
            done = f"wrote {_shown(self.written)}" if self.written else "wrote nothing"
            if self._spend:
                done += f"; {self._spent()} {'not logged' if self.dry_run else 'logged'}"
            print(f"{self.tool}: {'dry run: ' if self.dry_run else ''}{done}", file=sys.stderr)
        elif self._spend and not self.dry_run:
            print(f"{self.tool}: {self._spent()} logged before the failure", file=sys.stderr)

    def write(self, data: dict) -> Path:
        """Write `data` as the research JSON and return its path; with --json, also print it.

        The file is `ideas/<slug>/research/<tool>_<YYYYMMDD-HHMMSS>.json` (`-2`, `-3`... added
        when a run of the same second has it already), or --out. In a dry run it ends in
        `.dryrun.json` instead (--out keeps the path given) and the JSON starts with
        `"dry_run": true`. It is written to a `.tmp` beside it and renamed into place: no
        half-written file is ever left. Raises ToolError when it cannot be written.
        """
        if self.dry_run:
            data = {"dry_run": True, **data}
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path = self.args.out if self.args.out is not None else self._research_path()
        try:
            _write_atomic(path, text)
        except OSError as exc:
            raise ToolError(f"cannot write {_shown(path)}: {exc.strerror or exc}") from None
        self.written = path
        if self.args.json:
            sys.stdout.write(text)
        return path

    def summary(self, text: str) -> None:
        """Print the human summary, unless --json (then the research JSON is what is printed)."""
        if not self.args.json:
            print(text)

    def log_cost(self, provider: str, calls: int) -> None:
        """Log the `api` cost of `calls` calls to `provider`: calls × PRICE_TABLE_EUR[provider].

        The line's `ref` is the research file once written (empty before), its note says how many
        calls at what price. No call, no line; a dry run logs nothing.
        """
        if calls <= 0:
            return
        price = costs.PRICE_TABLE_EUR[provider]
        note = f"{calls} {provider} call{'' if calls == 1 else 's'} at {price} EUR"
        self.log("api", provider, api_cost(provider, calls), ref=self._ref(), note=note)

    log_api_calls = log_cost

    def log(
        self, kind: str, provider: str, amount_eur: float, ref: str = "", note: str = ""
    ) -> None:
        """Append one cost line to the idea's costs.jsonl under --phase (`costs.append`), for the
        costs that are not calls by the price table (an `llm` call with its request id as `ref`).
        A dry run logs nothing: the cost is only reported."""
        if not self.dry_run:
            costs.append(
                self.slug, kind, provider, amount_eur, ref=ref, phase=self.args.phase, note=note
            )
        self._spend.append((amount_eur, note))

    def _research_path(self) -> Path:
        folder = paths.research_dir(self.slug)
        stamp = _now().strftime(STAMP_FORMAT)
        suffix = DRY_RUN_SUFFIX if self.dry_run else ".json"
        path = folder / f"{self.tool}_{stamp}{suffix}"
        n = 2
        while path.exists():
            path = folder / f"{self.tool}_{stamp}-{n}{suffix}"
            n += 1
        return path

    def _ref(self) -> str:
        """The research file as a cost line names it: its name in research/, else its path."""
        if self.written is None:
            return ""
        if self.written.parent == paths.research_dir(self.slug):
            return self.written.name
        return str(self.written)

    def _spent(self) -> str:
        total = sum(amount for amount, _ in self._spend)
        notes = ", ".join(note for _, note in self._spend if note)
        return f"{total:.2f} EUR ({notes})" if notes else f"{total:.2f} EUR"


def api_cost(provider: str, calls: int) -> float:
    """What `calls` calls to `provider` cost by PRICE_TABLE_EUR, rounded to 4 decimals."""
    return round(calls * costs.PRICE_TABLE_EUR[provider], 4)


def selftest_ok(provider: str, n: int) -> int:
    """Print a selftest's success line, `OK <provider> <n> items`, and return exit code 0."""
    print(f"OK {provider} {n} items")
    return 0


def positive_int(text: str) -> int:
    """argparse type: a whole number, 1 or more."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number") from None
    if value < 1:
        raise argparse.ArgumentTypeError(f"{text!r} is not 1 or more")
    return value


def term_key(term: str) -> str:
    """What two spellings of one keyword share: its words, casefolded."""
    return " ".join(term.split()).casefold()


def unique_terms(values: Iterable[str]) -> list[str]:
    """The values with their whitespace collapsed, the empty ones dropped and each kept once, in
    order; of spellings that differ only in case, the first is kept."""
    seen: set[str] = set()
    terms = []
    for value in values:
        term = " ".join(value.split())
        if term and term_key(term) not in seen:
            seen.add(term_key(term))
            terms.append(term)
    return terms


def domain_of(text: str | None) -> str | None:
    """The host of a URL or bare domain, lowercased and without `www.`; None when there is none.

    `https://www.Example.com/a?b` and `www.example.com` are both `example.com`; what follows the
    first space is ignored (`help.x.com › business`); a host without a dot (`Learn`) is no domain.
    """
    if not isinstance(text, str) or not text.split():
        return None
    first = text.split()[0]
    try:
        host = urlsplit(first if "//" in first else f"//{first}").hostname
    except ValueError:
        return None
    if not host or "." not in host:
        return None
    return host.removeprefix("www.")


def _now() -> datetime:
    return datetime.now()


def _write_atomic(path: Path, text: str) -> None:
    """Replace `path` with `text` in one step: a crash leaves no file or the whole file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _shown(path: Path) -> str:
    """`path` relative to the factory root when it is inside it."""
    try:
        return str(path.relative_to(paths.root()))
    except ValueError:
        return str(path)
