import argparse
import json
from datetime import datetime

import pytest

from factory import costs, ledger, toolbase
from factory.http import ProviderError
from factory.secrets import SecretsUnavailable

STAMP = datetime(2026, 10, 21, 10, 12, 3)
NAME = "demo_20261021-101203.json"


def args_for(*argv: str, tool: str = "demo") -> argparse.Namespace:
    """The arguments of a tool that takes only the common flags, as the CLI would parse them."""
    parser = argparse.ArgumentParser(prog=tool)
    toolbase.add_common(parser)
    args = parser.parse_args(argv)
    args.tool = tool  # the CLI's sub-parsers set it
    return args


def make_tool(body=lambda r: None, planned: float = 0.0):
    """A tool whose run is `body(r)` inside `toolbase.run`, wrapped as every tool is."""

    @toolbase.handle_errors
    def tool(args):
        with toolbase.run(args, tool=args.tool, planned_eur=planned) as r:
            body(r)
        return 0

    return tool


def research(root, slug="_fixture"):
    """The names in the idea's research folder, .gitkeep aside, sorted."""
    folder = root / "ideas" / slug / "research"
    return sorted(p.name for p in folder.iterdir() if p.name != ".gitkeep")


@pytest.fixture
def stamp(monkeypatch):
    monkeypatch.setattr(toolbase, "_now", lambda: STAMP)


# --- the common flags --------------------------------------------------------------------------


def test_add_common_adds_the_flags_with_their_defaults():
    args = args_for("--idea", "x")
    assert (args.idea, args.dry_run, args.json, args.out, args.selftest) == (
        "x",
        False,
        False,
        None,
        False,
    )
    assert (args.phase, args.force) == ("triage", False)
    args = args_for("--idea", "x", "--dry-run", "--json", "--out", "o.json", "--phase", "run")
    assert (args.dry_run, args.json, str(args.out), args.phase) == (True, True, "o.json", "run")
    assert args_for("--idea", "x", "--force").force


def test_a_selftest_parses_without_an_idea():
    args = args_for("--selftest")
    assert args.selftest and args.idea is None


# --- entering a run: the idea and the cap ------------------------------------------------------


def test_a_run_without_an_idea_is_a_usage_error(root, capsys):
    ran = []
    assert make_tool(ran.append)(args_for()) == 2
    assert not ran
    assert capsys.readouterr().err == "demo: --idea is required (or --selftest)\n"


def test_an_unknown_idea_is_refused_before_the_run(root, capsys):
    ran = []
    assert make_tool(ran.append)(args_for("--idea", "nope", "--dry-run")) == 1
    err = capsys.readouterr().err
    assert not ran
    assert err.startswith("demo: no idea 'nope' in ideas/") and err.count("\n") == 1


def test_the_cap_is_checked_with_the_planned_cost_even_in_a_dry_run(root, capsys):
    # the fixture idea has spent 0.40 EUR cash against a cap of 300
    ran = []
    assert make_tool(ran.append, planned=299.61)(args_for("--idea", "_fixture", "--dry-run")) == 1
    err = capsys.readouterr().err
    assert not ran
    assert "over its cap of 300.00 EUR" in err and "--force" in err and err.count("\n") == 1
    assert make_tool(ran.append, planned=299.6)(args_for("--idea", "_fixture", "--dry-run")) == 0
    assert len(ran) == 1  # landing exactly on the cap is allowed


def test_force_runs_past_the_cap(root):
    ran = []
    assert make_tool(ran.append, planned=1000.0)(args_for("--idea", "_fixture", "--force")) == 0
    assert len(ran) == 1


def test_the_run_exposes_the_idea_and_the_mode(root):
    seen = []
    make_tool(lambda r: seen.append((r.slug, r.dry_run)))(
        args_for("--idea", "_fixture", "--dry-run")
    )
    assert seen == [("_fixture", True)]


# --- writing the research ----------------------------------------------------------------------


def test_write_puts_the_json_in_research_named_after_the_tool_and_time(root, stamp, capsys):
    written = []
    make_tool(lambda r: written.append(r.write({"a": 1, "é": [1, 2]})))(
        args_for("--idea", "_fixture")
    )
    path = root / "ideas/_fixture/research" / NAME
    assert written == [path]
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1, "é": [1, 2]}
    assert research(root) == [NAME]  # no .tmp left behind
    out, err = capsys.readouterr()
    assert out == ""
    assert err == f"demo: wrote ideas/_fixture/research/{NAME}\n"


def test_a_second_run_in_the_same_second_does_not_overwrite_the_first(root, stamp):
    tool = make_tool(lambda r: r.write({"n": 1}))
    assert tool(args_for("--idea", "_fixture")) == 0
    assert tool(args_for("--idea", "_fixture")) == 0
    assert research(root) == ["demo_20261021-101203-2.json", NAME]


def test_write_goes_to_out_when_given(root, tmp_path):
    out = tmp_path / "elsewhere" / "result.json"
    assert (
        make_tool(lambda r: r.write({"n": 1}))(args_for("--idea", "_fixture", "--out", str(out)))
        == 0
    )
    assert json.loads(out.read_text(encoding="utf-8")) == {"n": 1}
    assert research(root) == [] and sorted(p.name for p in out.parent.iterdir()) == ["result.json"]


def test_a_failed_write_leaves_no_file_and_no_tmp(root, capsys, monkeypatch):
    def full_disk(src, dst):
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(toolbase.os, "replace", full_disk)
    assert make_tool(lambda r: r.write({"n": 1}))(args_for("--idea", "_fixture")) == 1
    assert research(root) == []
    err = capsys.readouterr().err
    assert "cannot write" in err and "No space left on device" in err and err.count("\n") == 1


def test_summary_prints_unless_json_and_json_prints_the_research(root, capsys):
    def body(r):
        r.write({"k": "v"})
        r.summary("the table")

    assert make_tool(body)(args_for("--idea", "_fixture")) == 0
    assert capsys.readouterr().out == "the table\n"
    assert make_tool(body)(args_for("--idea", "_fixture", "--json")) == 0
    assert json.loads(capsys.readouterr().out) == {"k": "v"}


# --- logging the cost --------------------------------------------------------------------------


def test_the_costs_are_logged_with_the_research_file_as_ref(root, stamp, capsys):
    def body(r):
        r.write({"n": 1})
        r.log_cost("searchapi", 3)
        r.log_api_calls("seranking", 2)
        r.log("llm", "neuralbox", 0.276, ref="req-1", note="one respond call")
        r.log_cost("searchapi", 0)  # no call, no line

    before = len(costs.read_lines("_fixture"))
    assert make_tool(body)(args_for("--idea", "_fixture", "--phase", "challenge")) == 0
    lines = costs.read_lines("_fixture")[before:]
    assert [(x["kind"], x["provider"], x["amount_eur"], x["ref"], x["phase"]) for x in lines] == [
        ("api", "searchapi", 0.03, NAME, "challenge"),
        ("api", "seranking", 0.04, NAME, "challenge"),
        ("llm", "neuralbox", 0.276, "req-1", "challenge"),
    ]
    assert [x["note"] for x in lines] == [
        "3 searchapi calls at 0.01 EUR",
        "2 seranking calls at 0.02 EUR",
        "one respond call",
    ]
    err = capsys.readouterr().err
    assert err.startswith(f"demo: wrote ideas/_fixture/research/{NAME}; 0.35 EUR (")
    assert err.rstrip().endswith(") logged")


def test_a_dry_run_logs_nothing_and_reports_what_it_would_cost(root, capsys):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")

    def body(r):
        r.write({})
        r.log_cost("searchapi", 2)
        r.log("llm", "neuralbox", 1.0)

    assert make_tool(body)(args_for("--idea", "_fixture", "--dry-run")) == 0
    assert log.read_text(encoding="utf-8") == before
    err = capsys.readouterr().err
    assert err.startswith("demo: dry run: wrote ideas/_fixture/research/demo_")
    assert "1.02 EUR (2 searchapi calls at 0.01 EUR)" in err and err.rstrip().endswith("not logged")


def test_a_cost_logged_before_a_failure_is_kept_and_reported(root, capsys):
    def body(r):
        r.log_cost("searchapi", 2)
        raise ProviderError("searchapi", 500, "boom")

    before = costs.total("_fixture", kind="api")
    assert make_tool(body)(args_for("--idea", "_fixture")) == 1
    assert costs.total("_fixture", kind="api") == round(before + 0.02, 4)
    assert costs.read_lines("_fixture")[-1]["ref"] == ""  # nothing was written
    assert capsys.readouterr().err.splitlines() == [
        "demo: 0.02 EUR (2 searchapi calls at 0.01 EUR) logged before the failure",
        "demo: searchapi: HTTP 500: boom",
    ]
    assert research(root) == []


# --- failures ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("error", "code", "needle"),
    [
        (
            ProviderError("searchapi", 429, "You have used all of the searches for the month"),
            1,
            "demo: searchapi: HTTP 429: You have used all of the searches for the month",
        ),
        (SecretsUnavailable("no secrets/master.key: run `make secrets-init`"), 1, "secrets-init"),
        (toolbase.ToolError("cannot write x.json"), 1, "demo: cannot write x.json"),
        (toolbase.UsageError("--idea is required"), 2, "demo: --idea is required"),
    ],
)
def test_a_known_failure_is_one_line_on_stderr(root, capsys, error, code, needle):
    @toolbase.handle_errors
    def tool(args):
        raise error

    assert tool(args_for()) == code
    out, err = capsys.readouterr()
    assert out == "" and needle in err and err.count("\n") == 1


def test_an_unknown_idea_raised_anywhere_is_one_line(root, capsys):
    @toolbase.handle_errors
    def tool(args):
        raise ledger.IdeaNotFound("nope")

    assert tool(args_for()) == 1
    assert capsys.readouterr().err.startswith("demo: no idea 'nope' in ideas/")


def test_an_unexpected_error_is_not_swallowed(root):
    @toolbase.handle_errors
    def tool(args):
        raise KeyError("a bug")

    with pytest.raises(KeyError):
        tool(args_for())


# --- helpers -----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "domain"),
    [
        ("https://www.Example.com/a?b=1", "example.com"),
        ("www.brindlewick-recovery.example", "brindlewick-recovery.example"),
        ("kestrelmark.example", "kestrelmark.example"),
        ("https://help.adplatform.example › business › help", "help.adplatform.example"),
        ("http://user@shop.example:8080/x", "shop.example"),
        ("Learn more", None),
        ("", None),
        (None, None),
    ],
)
def test_domain_of(text, domain):
    assert toolbase.domain_of(text) == domain


def test_unique_terms_collapse_whitespace_and_keep_the_first_spelling():
    assert toolbase.unique_terms(["  ad  account ", "Ad Account", "", "  ", "b"]) == [
        "ad account",
        "b",
    ]
    assert toolbase.term_key(" Ad  Account ") == toolbase.term_key("ad account")


def test_api_cost_is_calls_times_the_price():
    assert toolbase.api_cost("searchapi", 3) == 0.03
    assert toolbase.api_cost("seranking", 2) == 0.04
    assert toolbase.api_cost("seranking", 0) == 0.0


def test_selftest_ok_prints_the_line_and_succeeds(capsys):
    assert toolbase.selftest_ok("seranking", 2) == 0
    assert capsys.readouterr().out == "OK seranking 2 items\n"


@pytest.mark.parametrize("text", ["0", "-1", "two"])
def test_positive_int_refuses_what_is_not_one_or_more(text):
    with pytest.raises(argparse.ArgumentTypeError):
        toolbase.positive_int(text)
    assert toolbase.positive_int("20") == 20
