"""The cost ledger: `ideas/<slug>/costs.jsonl`, one JSON object per line, append-only.

Every tool that spends appends a line here (spec sections 6 and 10) and the cap check reads the sum
back, so a line that is not written is money the cap cannot see. Cash is everything but
`founder_time`: the cap counts cash only, while founder time is priced so unpaid channels compare
with paid ones. A wrong line is corrected by appending a negative one, not by editing the file.

Reading is strict on purpose. A line that is not a JSON object with a text `kind` and a finite
numeric `amount_eur` raises CostsParseError naming its number; skipping it would under-count the
spend and let the cap be passed. Amounts are rounded to 4 decimals, sums too.
"""

import json
import math
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from factory import ledger

KINDS: list[str] = ["ads", "api", "llm", "domain", "founder_time", "other"]
FOUNDER_TIME = "founder_time"

# The keys of a line, in the order they are written.
LINE_KEYS: list[str] = ["ts", "kind", "provider", "amount_eur", "ref", "phase", "note", "channel"]

# Estimated EUR per call by provider, for the tools that are billed per call. They are estimates
# that the retro corrects against the real invoices.
PRICE_TABLE_EUR: dict[str, float] = {
    "searchapi": 0.01,
    "seranking": 0.02,
    "firecrawl": 0.01,
    "arcticshift": 0.0,
    "algolia": 0.0,
    "rdap": 0.0,
}

USD_EUR = 0.92  # NeuralBox reports cost_usd


class CapExceeded(ledger.LedgerError):
    """Spending `planned` more would take the idea's cash spend `total` past its `cap`."""

    def __init__(self, slug: str, total: float, cap: float, planned: float = 0.0) -> None:
        super().__init__(
            f"idea {slug!r}: cash spend would reach {total + planned:.2f} EUR "
            f"({total:.2f} spent + {planned:.2f} planned), over its cap of {cap:.2f} EUR"
        )
        self.slug = slug
        self.total = total
        self.cap = cap
        self.planned = planned


class CostsParseError(ledger.LedgerError):
    """A line of costs.jsonl is not a cost line."""

    def __init__(self, slug: str, line_no: int, reason: str) -> None:
        super().__init__(f"ideas/{slug}/costs.jsonl:{line_no}: {reason}")
        self.slug = slug
        self.line_no = line_no
        self.reason = reason


def append(
    slug: str,
    kind: str,
    provider: str,
    amount_eur: float,
    ref: str = "",
    phase: str = "",
    note: str = "",
    channel: str | None = None,
) -> dict:
    """Append one cost line to the idea's costs.jsonl and return it.

    The line holds the keys of LINE_KEYS in that order: `ts` is the local time to the second,
    `amount_eur` is rounded to 4 decimals, `channel` is null for idea-level costs (founder time
    spent on a channel's execution carries that channel). Raises ValueError for a kind that is not
    in KINDS or an amount that is not a finite number, and IdeaNotFound for a slug with no folder;
    nothing is written then.
    """
    _check_kind(kind)
    amount = _finite(amount_eur, "amount_eur")
    folder = ledger.require_dir(slug)
    line = {
        "ts": _now().isoformat(timespec="seconds"),
        "kind": kind,
        "provider": provider,
        "amount_eur": round(amount, 4),
        "ref": ref,
        "phase": phase,
        "note": note,
        "channel": channel,
    }
    text = json.dumps(line, ensure_ascii=False, allow_nan=False)
    ledger.append_line(folder / "costs.jsonl", text)
    return line


def read_lines(slug: str) -> list[dict]:
    """The idea's cost lines, in file order; blank lines are skipped and a missing file is empty.

    Raises CostsParseError for a line that is not a cost line, IdeaNotFound for an unknown idea.
    """
    path = ledger.require_dir(slug) / "costs.jsonl"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    # Not splitlines(): a note may hold U+2028 or U+0085, which are not line ends in this file.
    return [
        _parse_line(slug, line_no, raw)
        for line_no, raw in enumerate(text.split("\n"), start=1)
        if raw.strip()
    ]


def total(slug: str, kind: str | None = None, phase: str | None = None) -> float:
    """The sum of `amount_eur` over the lines of this `kind` and `phase` (None: any).

    Founder time is included unless `kind` says otherwise; `cash_total` is what counts for the cap.
    """
    if kind is not None:
        _check_kind(kind)
    return _sum(
        line
        for line in read_lines(slug)
        if (kind is None or line["kind"] == kind) and (phase is None or line.get("phase") == phase)
    )


def cash_total(slug: str) -> float:
    """The cash spent: every line except `founder_time`."""
    return _sum(line for line in read_lines(slug) if line["kind"] != FOUNDER_TIME)


def summary(slug: str) -> dict:
    """The `totals` block of idea.yml: cash, founder time and the sum per kind.

    `by_kind` has every kind of KINDS, in that order, then any other kind found in the file.
    """
    lines = read_lines(slug)
    kinds = KINDS + sorted({line["kind"] for line in lines} - set(KINDS))
    by_kind = {kind: _sum(line for line in lines if line["kind"] == kind) for kind in kinds}
    return {
        "cash_eur": _sum(line for line in lines if line["kind"] != FOUNDER_TIME),
        "founder_time_eur": by_kind[FOUNDER_TIME],
        "by_kind": by_kind,
    }


def check_cap(slug: str, planned_eur: float = 0.0, force: bool = False) -> None:
    """Refuse a spend that would take the idea past its cap.

    Raises CapExceeded when the cash spent so far plus `planned_eur` is more than the idea's
    `cap_eur`; landing exactly on the cap is allowed. `force` skips the refusal but not the check
    that the idea exists. Raises IdeaNotFound for an unknown idea, ValueError for a planned amount
    that is not a finite number.
    """
    idea = ledger.load_idea(slug)
    planned = _finite(planned_eur, "planned_eur")
    if force:
        return
    spent = cash_total(slug)
    if round(spent + planned, 4) > round(idea.cap_eur, 4):
        raise CapExceeded(slug, spent, idea.cap_eur, planned)


def _now() -> datetime:
    return datetime.now()


def _check_kind(kind: str) -> None:
    if kind not in KINDS:
        raise ValueError(f"kind {kind!r} is not one of {', '.join(KINDS)}")


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return float(value)


def _sum(lines: Iterable[dict]) -> float:
    return round(math.fsum(line["amount_eur"] for line in lines), 4)


def _parse_line(slug: str, line_no: int, raw: str) -> dict:
    try:
        line = json.loads(raw)
    except ValueError:
        raise CostsParseError(slug, line_no, "not valid JSON") from None
    if not isinstance(line, dict):
        raise CostsParseError(slug, line_no, "not a JSON object")
    if not isinstance(line.get("kind"), str):
        raise CostsParseError(slug, line_no, "kind must be text")
    try:
        _finite(line.get("amount_eur"), "amount_eur")
    except ValueError as exc:
        raise CostsParseError(slug, line_no, str(exc)) from None
    return line
