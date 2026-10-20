import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from factory import costs, ledger

LINE_KEYS = ["ts", "kind", "provider", "amount_eur", "ref", "phase", "note", "channel"]


def log_path(root: Path, slug: str = "_fixture") -> Path:
    return root / "ideas" / slug / "costs.jsonl"


def file_lines(root: Path, slug: str = "_fixture") -> list[dict]:
    text = log_path(root, slug).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines()]


# --- the brief's tests -------------------------------------------------------------------------


def test_append_and_total(root):
    costs.append("_fixture", "api", "searchapi", 0.05, phase="triage")
    assert costs.total("_fixture", kind="api") >= 0.05


def test_check_cap_raises(root):
    costs.append("_fixture", "ads", "meta", 299.0)
    with pytest.raises(costs.CapExceeded):
        costs.check_cap("_fixture", planned_eur=5.0)
    costs.check_cap("_fixture", planned_eur=5.0, force=True)


def test_founder_time_not_cash(root):
    costs.append("_fixture", "founder_time", "vlad", 1000.0)
    costs.check_cap("_fixture")  # no raise


# --- constants ---------------------------------------------------------------------------------


def test_constants():
    assert costs.KINDS == ["ads", "api", "llm", "domain", "founder_time", "other"]
    assert costs.LINE_KEYS == LINE_KEYS
    assert costs.USD_EUR == 0.92
    assert costs.PRICE_TABLE_EUR == {
        "searchapi": 0.01,
        "seranking": 0.02,
        "firecrawl": 0.01,
        "arcticshift": 0.0,
        "algolia": 0.0,
        "rdap": 0.0,
    }


# --- append ------------------------------------------------------------------------------------


def test_append_writes_the_documented_line(root, monkeypatch):
    monkeypatch.setattr(costs, "_now", lambda: datetime(2026, 10, 21, 9, 5, 7, 123456))
    line = costs.append(
        "_fixture",
        "ads",
        "meta",
        12.34567,
        ref="cmp_1",
        phase="run",
        note="day 1 — é",
        channel="meta_feed",
    )
    assert line == {
        "ts": "2026-10-21T09:05:07",
        "kind": "ads",
        "provider": "meta",
        "amount_eur": 12.3457,
        "ref": "cmp_1",
        "phase": "run",
        "note": "day 1 — é",
        "channel": "meta_feed",
    }
    assert list(line) == LINE_KEYS
    raw = log_path(root).read_text(encoding="utf-8").splitlines()
    assert len(raw) == 4 and json.loads(raw[-1]) == line
    assert list(json.loads(raw[-1])) == LINE_KEYS
    assert "day 1 — é" in raw[-1]  # written as text, not as \u escapes


def test_append_defaults(root):
    line = costs.append("_fixture", "other", "manual", 1)
    assert (line["ref"], line["phase"], line["note"], line["channel"]) == ("", "", "", None)
    assert line["amount_eur"] == 1.0 and isinstance(line["amount_eur"], float)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line["ts"])
    assert file_lines(root)[-1] == line


def test_append_keeps_a_negative_amount_as_a_correction(root):
    costs.append("_fixture", "ads", "meta", 50.0)
    costs.append("_fixture", "ads", "meta", -20.0, note="refund")
    assert costs.total("_fixture", kind="ads") == 30.0


def test_append_rejects_a_kind_that_is_not_known(root):
    for kind in ("Ads", "founder-time", "", "tools"):
        with pytest.raises(ValueError, match="kind"):
            costs.append("_fixture", kind, "x", 1.0)
    assert len(file_lines(root)) == 3


def test_append_rejects_an_amount_that_is_not_a_finite_number(root):
    for amount in (float("nan"), float("inf"), float("-inf"), "1.0", None, True):
        with pytest.raises(ValueError, match="amount"):
            costs.append("_fixture", "api", "x", amount)
    assert len(file_lines(root)) == 3


def test_append_to_an_unknown_idea_creates_nothing(root):
    with pytest.raises(ledger.IdeaNotFound):
        costs.append("nope", "api", "x", 1.0)
    assert not (root / "ideas/nope").exists()


def test_append_creates_a_missing_log(root):
    log_path(root).unlink()
    costs.append("_fixture", "api", "searchapi", 0.01)
    assert len(file_lines(root)) == 1


def test_a_note_with_unicode_line_separators_stays_one_line(root):
    costs.append("_fixture", "other", "manual", 1.0, note="a\u2028b\u0085c\x0cd")
    assert len(log_path(root).read_text(encoding="utf-8").split("\n")) == 5  # 4 lines + the end
    assert costs.read_lines("_fixture")[-1]["note"] == "a\u2028b\u0085c\x0cd"
    assert costs.total("_fixture", kind="other") == 1.0


def test_append_ends_an_unterminated_last_line_first(root):
    path = log_path(root)
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    costs.append("_fixture", "api", "searchapi", 0.01)
    assert len(file_lines(root)) == 4


# --- totals ------------------------------------------------------------------------------------


def test_total_cash_total_and_filters(root):
    costs.append("_fixture", "api", "searchapi", 0.05, phase="triage")
    costs.append("_fixture", "ads", "meta", 10.0, phase="run")
    assert costs.total("_fixture") == 35.45  # everything, founder time included
    assert costs.cash_total("_fixture") == 10.45  # founder time excluded
    assert costs.total("_fixture", kind="api") == 0.17
    assert costs.total("_fixture", kind="founder_time") == 25.0
    assert costs.total("_fixture", phase="triage") == 0.45
    assert costs.total("_fixture", kind="api", phase="triage") == 0.17
    assert costs.total("_fixture", kind="ads", phase="triage") == 0.0
    assert costs.total("_fixture", phase="no-such-phase") == 0.0


def test_totals_are_rounded_floats(root):
    for _ in range(10):
        costs.append("_fixture", "api", "searchapi", 0.1)
    assert costs.total("_fixture", kind="api") == 1.12  # not 1.1200000000000001
    assert isinstance(costs.total("_fixture", kind="domain"), float)


def test_total_rejects_a_kind_that_is_not_known(root):
    with pytest.raises(ValueError, match="kind"):
        costs.total("_fixture", kind="founder-time")


def test_summary_is_the_totals_block_of_idea_yml(root):
    summary = costs.summary("_fixture")
    assert summary == {
        "cash_eur": 0.4,
        "founder_time_eur": 25.0,
        "by_kind": {
            "ads": 0.0,
            "api": 0.12,
            "llm": 0.28,
            "domain": 0.0,
            "founder_time": 25.0,
            "other": 0.0,
        },
    }
    assert list(summary) == ["cash_eur", "founder_time_eur", "by_kind"]
    assert list(summary["by_kind"]) == costs.KINDS


def test_an_empty_or_missing_log_totals_zero(root):
    ledger.create_idea("demo", "Demo")
    assert costs.total("demo") == 0.0 and costs.cash_total("demo") == 0.0
    assert costs.summary("demo") == {
        "cash_eur": 0.0,
        "founder_time_eur": 0.0,
        "by_kind": dict.fromkeys(costs.KINDS, 0.0),
    }
    log_path(root, "demo").unlink()
    assert costs.total("demo") == 0.0


def test_blank_lines_are_skipped(root):
    path = log_path(root)
    path.write_text(path.read_text(encoding="utf-8") + "\n   \n\n", encoding="utf-8")
    assert costs.total("_fixture") == 25.4
    assert len(costs.read_lines("_fixture")) == 3


def test_totals_of_an_unknown_idea_are_refused(root):
    for call in (costs.total, costs.cash_total, costs.summary, costs.read_lines):
        with pytest.raises(ledger.IdeaNotFound):
            call("nope")


@pytest.mark.parametrize(
    ("bad", "reason"),
    [
        ("not json", "JSON"),
        ("[1, 2]", "object"),
        ('{"kind": "api"}', "amount_eur"),
        ('{"kind": "api", "amount_eur": "0.1"}', "amount_eur"),
        ('{"kind": "api", "amount_eur": true}', "amount_eur"),
        ('{"kind": "api", "amount_eur": NaN}', "amount_eur"),
        ('{"amount_eur": 0.1}', "kind"),
        ('{"kind": 3, "amount_eur": 0.1}', "kind"),
    ],
)
def test_a_bad_line_is_an_error_naming_its_number(root, bad, reason):
    path = log_path(root)
    path.write_text(path.read_text(encoding="utf-8") + bad + "\n", encoding="utf-8")
    with pytest.raises(costs.CostsParseError) as e:
        costs.total("_fixture")
    message = str(e.value)
    assert "ideas/_fixture/costs.jsonl:4" in message and reason in message
    assert "\n" not in message
    assert isinstance(e.value, ledger.LedgerError)
    assert e.value.line_no == 4


def test_a_bad_line_is_never_skipped_in_the_cap_check(root):
    path = log_path(root)
    path.write_text(path.read_text(encoding="utf-8") + "garbage\n", encoding="utf-8")
    with pytest.raises(costs.CostsParseError):
        costs.check_cap("_fixture", planned_eur=1.0)


def test_lines_with_extra_or_missing_optional_keys_still_count(root):
    path = log_path(root)
    path.write_text(
        path.read_text(encoding="utf-8")
        + '{"kind": "ads", "amount_eur": 5, "extra": "kept"}\n'
        + '{"ts": "x", "kind": "mystery", "amount_eur": 2.5}\n',
        encoding="utf-8",
    )
    assert costs.total("_fixture", kind="ads") == 5.0
    assert costs.cash_total("_fixture") == 7.9  # the unknown kind counts as cash
    assert costs.summary("_fixture")["by_kind"]["mystery"] == 2.5
    assert costs.summary("_fixture")["cash_eur"] == 7.9


# --- the cap -----------------------------------------------------------------------------------


def test_check_cap_message_names_slug_total_and_cap(root):
    costs.append("_fixture", "ads", "meta", 299.0)
    with pytest.raises(costs.CapExceeded) as e:
        costs.check_cap("_fixture", planned_eur=5.0)
    err = e.value
    assert (err.slug, err.total, err.cap, err.planned) == ("_fixture", 299.4, 300.0, 5.0)
    message = str(err)
    assert "_fixture" in message and "299.40" in message and "300.00" in message
    assert "cap" in message and "5.00" in message and "\n" not in message
    assert isinstance(err, ledger.LedgerError)


def test_cap_exceeded_can_be_built_from_the_three_values():
    err = costs.CapExceeded("demo", 310.0, 300.0)
    assert (err.slug, err.total, err.cap, err.planned) == ("demo", 310.0, 300.0, 0.0)
    assert "demo" in str(err) and "310.00" in str(err) and "300.00" in str(err)


def test_check_cap_allows_spending_exactly_up_to_the_cap(root):
    costs.append("_fixture", "ads", "meta", 299.0)  # 299.40 spent
    costs.check_cap("_fixture", planned_eur=0.6)  # lands on 300.00: allowed
    with pytest.raises(costs.CapExceeded):
        costs.check_cap("_fixture", planned_eur=0.6001)


def test_check_cap_compares_rounded_amounts(root):
    ledger.create_idea("demo", "Demo", cap_eur=0.3)
    costs.append("demo", "api", "searchapi", 0.1)
    costs.check_cap("demo", planned_eur=0.2)  # 0.1 + 0.2 is 0.30000000000000004 in floats
    with pytest.raises(costs.CapExceeded):
        costs.check_cap("demo", planned_eur=0.2001)


def test_check_cap_with_nothing_planned_refuses_a_spent_cap(root):
    costs.append("_fixture", "ads", "meta", 300.0)  # 300.40 spent against 300
    with pytest.raises(costs.CapExceeded):
        costs.check_cap("_fixture")


def test_check_cap_reads_the_cap_from_idea_yml(root):
    idea = ledger.load_idea("_fixture")
    idea.cap_eur = 1.0
    ledger.save_idea(idea)
    costs.check_cap("_fixture", planned_eur=0.6)  # 0.40 + 0.60 = 1.00: allowed
    with pytest.raises(costs.CapExceeded) as e:
        costs.check_cap("_fixture", planned_eur=0.7)
    assert e.value.cap == 1.0


def test_check_cap_rejects_a_planned_amount_that_is_not_a_finite_number(root):
    # NaN compares false with everything: unchecked, it would pass any spend.
    for planned in (float("nan"), float("inf"), "5", None):
        with pytest.raises(ValueError, match="planned_eur"):
            costs.check_cap("_fixture", planned_eur=planned)


def test_check_cap_of_an_unknown_idea_is_refused_even_with_force(root):
    for force in (False, True):
        with pytest.raises(ledger.IdeaNotFound):
            costs.check_cap("nope", planned_eur=1.0, force=force)
