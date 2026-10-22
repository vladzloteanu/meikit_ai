import dataclasses
import json

import pytest
import yaml

from factory import costs, ledger
from factory.cli import main

TABLE_COLUMNS = ["slug", "status", "step", "exp", "spend/cap", "updated", "next"]
JSON_KEYS = ["slug", "status", "step", "exp", "spend_eur", "cap_eur", "updated", "next"]
FIXTURE_ROW = {
    "slug": "_fixture",
    "status": "RUNNING",
    "step": "5. run",
    "exp": 1,
    "spend_eur": 0.4,
    "cap_eur": 300.0,
    "updated": "2026-10-16",
    "next": "/idea-status",
}


def board_rows(capsys, *flags):
    """The board as `--json` prints it, keyed by slug."""
    assert main(["board", "--json", *flags]) == 0
    return {row["slug"]: row for row in json.loads(capsys.readouterr().out)}


def new_idea(slug="demo", *flags):
    assert main(["idea", "new", slug, "--title", slug.title(), *flags]) == 0


# --- board -------------------------------------------------------------------------------------


def test_board_lists_fixture_only_with_all(root, capsys):
    main(["board"])
    assert "_fixture" not in capsys.readouterr().out
    main(["board", "--all"])
    assert "_fixture" in capsys.readouterr().out


def test_idea_new_then_board(root, capsys):
    assert main(["idea", "new", "demo", "--title", "Demo", "--geo", "FR"]) == 0
    main(["board", "--json"])
    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["slug"] == "demo" and rows[0]["step"].startswith("1.")
    assert rows[0]["next"] == "/idea-new"


def test_board_survives_bad_plan(root, capsys):
    main(["idea", "new", "demo", "--title", "Demo"])
    (root / "ideas/demo/plan.md").write_text("## Steps\n- [x] garbage\n")
    assert main(["board", "--all"]) == 0
    out = capsys.readouterr().out
    assert "invalid" in out and "_fixture" in out


def test_board_json_has_the_documented_keys_and_values(root, capsys):
    row = board_rows(capsys, "--all")["_fixture"]
    assert list(row) == JSON_KEYS
    assert row == FIXTURE_ROW


def test_board_table_has_the_documented_columns(root, capsys):
    assert main(["board", "--all"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == TABLE_COLUMNS
    assert set(lines[1]) <= {"-", " "}
    row = "_fixture RUNNING 5. run 1 0/300 2026-10-16 /idea-status"
    assert lines[2].split() == row.split()


def test_board_rows_are_in_slug_order(root, capsys):
    new_idea("beta")
    new_idea("alpha")
    assert list(board_rows(capsys, "--all")) == ["_fixture", "alpha", "beta"]


def test_board_shows_a_finished_plan_and_no_experiment(root, capsys, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    new_idea()
    for step_id in range(1, 8):
        assert main(["plan", "mark", "demo", str(step_id), "done"]) == 0
    capsys.readouterr()
    row = board_rows(capsys)["demo"]
    assert (row["step"], row["next"], row["exp"]) == ("done", None, None)
    assert main(["board"]) == 0
    cells = capsys.readouterr().out.splitlines()[2].split()
    assert cells == ["demo", "NEW", "done", "-", "0/300", "2026-11-02", "-"]


def test_board_spend_is_cash_only(root, capsys):
    main(["costs", "add", "--idea", "_fixture", "--kind", "ads", "--amount-eur", "11.6"])
    row = board_rows(capsys, "--all")["_fixture"]
    assert row["spend_eur"] == 12.0  # 0.4 already there, and the 25 of founder time never counts
    assert main(["board", "--all"]) == 0
    assert "12/300" in capsys.readouterr().out


def test_board_reports_which_plan_line_is_malformed(root, capsys):
    new_idea()
    (root / "ideas/demo/plan.md").write_text("## Steps\n- [x] garbage\n")
    rows = board_rows(capsys, "--all")
    assert (rows["demo"]["step"], rows["demo"]["next"]) == ("plan.md:2 invalid", None)
    assert rows["_fixture"] == FIXTURE_ROW


def test_board_survives_a_malformed_idea_yml(root, capsys):
    new_idea()
    (root / "ideas/demo/idea.yml").write_text("slug: demo\ntitle: Demo\nstatus: LIVE\n")
    rows = board_rows(capsys, "--all")
    assert rows["demo"] == {
        "slug": "demo",
        "status": "idea.yml invalid",
        "step": "1. intake",
        "exp": None,
        "spend_eur": 0.0,
        "cap_eur": None,
        "updated": None,
        "next": "/idea-new",
    }
    assert rows["_fixture"] == FIXTURE_ROW
    assert main(["board", "--all"]) == 0
    assert "idea.yml invalid" in capsys.readouterr().out


def test_board_survives_a_malformed_costs_line(root, capsys):
    new_idea()
    (root / "ideas/demo/costs.jsonl").write_text('{"kind": "api", "amount_eur": 1}\nnot json\n')
    rows = board_rows(capsys, "--all")
    assert (rows["demo"]["spend_eur"], rows["demo"]["cap_eur"]) == (None, 300.0)
    assert rows["_fixture"] == FIXTURE_ROW
    assert main(["board", "--all"]) == 0
    fixture_line, demo_line = capsys.readouterr().out.splitlines()[2:]
    assert " 0/300 " in fixture_line and " ?/300 " in demo_line


def test_board_with_no_ideas(factory_root, capsys):
    assert main(["board", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == []
    assert main(["board"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines()[0].split() == TABLE_COLUMNS
    assert "no ideas" in out


# --- idea new ----------------------------------------------------------------------------------


def test_idea_new_with_only_a_title_takes_the_defaults(root, capsys):
    assert main(["idea", "new", "demo", "--title", "Demo"]) == 0
    idea = ledger.load_idea("demo")
    assert (idea.title, idea.status, idea.geo, idea.language) == ("Demo", "NEW", [], "en")
    assert (idea.cap_eur, idea.founder_hour_rate_eur, idea.provisional) == (300.0, 100.0, False)
    assert capsys.readouterr().out == ""  # a data channel: the confirmation goes to stderr


def test_idea_new_writes_every_field_it_is_given(root):
    argv = ["idea", "new", "demo", "--title", "Demo", "--geo", "FR, US", "--language", "fr"]
    argv += ["--buyer", "salon owners", "--signer", "the owner", "--value-eur", "228"]
    argv += ["--cap-eur", "150", "--rate-eur", "80", "--provisional", "--notes", "a = b"]
    assert main(argv) == 0
    data = yaml.safe_load((root / "ideas/demo/idea.yml").read_text())
    assert (data["geo"], data["language"], data["buyer"], data["signer"]) == (
        ["FR", "US"],
        "fr",
        "salon owners",
        "the owner",
    )
    assert (data["value_per_customer_eur"], data["cap_eur"], data["founder_hour_rate_eur"]) == (
        228.0,
        150.0,
        80.0,
    )
    assert (data["provisional"], data["notes"]) == (True, "a = b")


def test_idea_new_without_a_value_writes_unknown(root):
    assert main(["idea", "new", "demo", "--title", "Demo"]) == 0
    data = yaml.safe_load((root / "ideas/demo/idea.yml").read_text())
    assert data["value_per_customer_eur"] is None and data["value_basis"] == ""


def test_idea_new_accepts_unknown_as_the_value(root):
    assert main(["idea", "new", "demo", "--title", "Demo", "--value-eur", "unknown"]) == 0
    data = yaml.safe_load((root / "ideas/demo/idea.yml").read_text())
    assert data["value_per_customer_eur"] is None


def test_idea_new_refuses_an_existing_slug(root, capsys):
    path = root / "ideas/_fixture/idea.yml"
    before = path.read_text()
    assert main(["idea", "new", "_fixture", "--title", "Other"]) == 1
    err = capsys.readouterr().err
    assert "already exists" in err and len(err.splitlines()) == 1
    assert path.read_text() == before


@pytest.mark.parametrize("slug", ["Bad Slug", "a/b", "x.y"])
def test_idea_new_refuses_a_slug_that_is_not_one(root, capsys, slug):
    assert main(["idea", "new", slug, "--title", "T"]) == 1
    err = capsys.readouterr().err
    assert "slug" in err and len(err.splitlines()) == 1
    assert [p.name for p in (root / "ideas").iterdir()] == ["_fixture"]


@pytest.mark.parametrize(
    ("flag", "value"), [("--cap-eur", "nan"), ("--value-eur", "inf"), ("--rate-eur", "lots")]
)
def test_idea_new_refuses_a_number_that_is_not_one(root, capsys, flag, value):
    assert main(["idea", "new", "demo", "--title", "T", flag, value]) == 2
    assert flag in capsys.readouterr().err
    assert not (root / "ideas/demo").exists()


# --- idea set ----------------------------------------------------------------------------------


def test_idea_set_converts_each_value_to_its_type(root, capsys):
    argv = ["idea", "set", "_fixture", "status=TRIAGED", "geo=FR,US", "cap_eur=250"]
    argv += ["current_experiment=2", "provisional=True", "notes=a=b", "domain=meikit.ai"]
    argv += ["founder_hour_rate_eur=80", "value_per_customer_eur=19.5", "title=New title"]
    assert main(argv) == 0
    idea = ledger.load_idea("_fixture")
    assert (idea.status, idea.geo, idea.cap_eur, idea.current_experiment) == (
        "TRIAGED",
        ["FR", "US"],
        250.0,
        2,
    )
    assert (idea.provisional, idea.notes, idea.domain, idea.title) == (
        True,
        "a=b",
        "meikit.ai",
        "New title",
    )
    assert (idea.founder_hour_rate_eur, idea.value_per_customer_eur) == (80.0, 19.5)
    assert capsys.readouterr().out == ""


def test_idea_set_unknown_or_empty_clears_the_value_and_sets_its_basis(root):
    argv = ["idea", "set", "_fixture", "value_per_customer_eur=unknown"]
    argv += ["value_basis=price 59 (founder) x months unknown"]
    assert main(argv) == 0
    idea = ledger.load_idea("_fixture")
    assert idea.value_per_customer_eur is None
    assert idea.value_basis == "price 59 (founder) x months unknown"
    assert main(["idea", "set", "_fixture", "value_per_customer_eur=319", "value_basis="]) == 0
    idea = ledger.load_idea("_fixture")
    assert idea.value_per_customer_eur == 319.0 and idea.value_basis == ""
    assert main(["idea", "set", "_fixture", "value_per_customer_eur="]) == 0
    assert ledger.load_idea("_fixture").value_per_customer_eur is None


def test_idea_set_an_empty_value_clears_an_optional_field(root):
    assert main(["idea", "set", "_fixture", "domain=meikit.ai", "current_experiment=3"]) == 0
    assert main(["idea", "set", "_fixture", "domain=", "current_experiment=", "geo="]) == 0
    data = yaml.safe_load((root / "ideas/_fixture/idea.yml").read_text())
    assert (data["domain"], data["current_experiment"], data["geo"]) == (None, None, [])


def test_idea_set_saves_through_the_ledger(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    costs.append("_fixture", "ads", "meta", 10.0)
    assert main(["idea", "set", "_fixture", "status=REWORK"]) == 0
    idea = ledger.load_idea("_fixture")
    assert idea.updated == "2026-11-02"
    assert idea.totals["cash_eur"] == 10.4  # recomputed from costs.jsonl


@pytest.mark.parametrize(
    ("assignment", "needle"),
    [
        ("colour=red", "'colour' is not a settable field"),
        ("slug=other", "'slug' is not a settable field"),
        ("totals=1", "'totals' is not a settable field"),
        ("status=LIVE", "status: 'LIVE' is not one of"),
        ("cap_eur=nan", "cap_eur: 'nan' is not a finite number"),
        (
            "value_per_customer_eur=lots",
            "value_per_customer_eur: 'lots' is not a finite number or unknown",
        ),
        ("current_experiment=1.5", "current_experiment: '1.5' is not a whole number"),
        ("provisional=maybe", "provisional: 'maybe' is not true or false"),
        ("status", "'status' is not key=value"),
    ],
)
def test_idea_set_refuses_bad_input_and_writes_nothing(root, capsys, assignment, needle):
    path = root / "ideas/_fixture/idea.yml"
    before = path.read_text()
    assert main(["idea", "set", "_fixture", "notes=changed", assignment]) == 1
    err = capsys.readouterr().err
    assert needle in err and len(err.splitlines()) == 1
    assert path.read_text() == before


def test_idea_set_unknown_idea(root, capsys):
    assert main(["idea", "set", "nope", "status=GO"]) == 1
    assert "ideas/" in capsys.readouterr().err


def test_idea_set_covers_the_fields_that_are_not_computed():
    from factory.tools import idea as idea_command

    fields = {field.name for field in dataclasses.fields(ledger.Idea)}
    assert set(idea_command.SETTABLE) == fields - {"slug", "created", "updated", "totals", "extra"}


# --- plan --------------------------------------------------------------------------------------


def test_plan_mark_and_costs(root, capsys):
    main(["plan", "mark", "_fixture", "5", "done"])
    main(["plan", "next", "_fixture"])
    assert capsys.readouterr().out.startswith("6.")
    main(
        ["costs", "add", "--idea", "_fixture", "--kind", "api", "--amount-eur", "0.5"]
        + ["--provider", "searchapi"]
    )
    main(["costs", "total", "--idea", "_fixture", "--json"])
    assert json.loads(capsys.readouterr().out)["api"] >= 0.5


def test_plan_show_lists_every_step_with_its_status(root, capsys):
    assert main(["plan", "show", "_fixture"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["id", "status", "name", "command", "timebox", "date"]
    assert [line.split()[:2] for line in lines[2:]] == [
        ["1", "done"],
        ["2", "done"],
        ["3", "done"],
        ["4", "done"],
        ["5", "todo"],
        ["6", "todo"],
        ["7", "todo"],
    ]
    assert "2026-10-16" in lines[5]


def test_plan_next_is_one_line(root, capsys):
    assert main(["plan", "next", "_fixture"]) == 0
    assert capsys.readouterr().out == "5. run — /idea-status — 5 min/day\n"


def test_plan_next_says_done_when_nothing_is_left(root, capsys):
    for step_id in "567":
        main(["plan", "mark", "_fixture", step_id, "skipped"])
    capsys.readouterr()
    assert main(["plan", "next", "_fixture"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("done") and len(out.splitlines()) == 1


def test_plan_mark_rewrites_the_line_with_its_status_and_date(root, capsys, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    path = root / "ideas/_fixture/plan.md"
    assert main(["plan", "mark", "_fixture", "5", "doing"]) == 0
    assert "- [~] 5. run — `/idea-status` — 5 min/day\n" in path.read_text()
    main(["plan", "next", "_fixture"])
    assert capsys.readouterr().out.startswith("5.")  # the step in progress is still the next
    assert main(["plan", "mark", "_fixture", "5", "done"]) == 0
    assert "- [x] 5. run — `/idea-status` — 5 min/day — 2026-11-02\n" in path.read_text()
    assert capsys.readouterr().out == ""


def test_plan_mark_takes_only_the_plan_statuses(root, capsys):
    before = (root / "ideas/_fixture/plan.md").read_text()
    assert main(["plan", "mark", "_fixture", "5", "finished"]) == 2
    err = capsys.readouterr().err
    assert "finished" in err and all(status in err for status in ledger.STEP_STATUSES)
    assert (root / "ideas/_fixture/plan.md").read_text() == before


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["mark", "_fixture", "99", "done"], "'99'"),
        (["mark", "nope", "1", "done"], "ideas/"),
        (["next", "nope"], "ideas/"),
        (["show", "nope"], "ideas/"),
    ],
)
def test_plan_commands_refuse_an_unknown_idea_or_step(root, capsys, argv, needle):
    assert main(["plan", *argv]) == 1
    err = capsys.readouterr().err
    assert needle in err and len(err.splitlines()) == 1


@pytest.mark.parametrize("argv", [["show"], ["next"], ["mark", "5", "done"]])
def test_plan_commands_name_the_malformed_line(root, capsys, argv):
    (root / "ideas/_fixture/plan.md").write_text("## Steps\n- [x] garbage\n")
    assert main(["plan", argv[0], "_fixture", *argv[1:]]) == 1
    err = capsys.readouterr().err
    assert "plan.md:2" in err and len(err.splitlines()) == 1


# --- costs -------------------------------------------------------------------------------------


def test_costs_add_appends_one_line_with_what_it_is_given(root, capsys):
    argv = ["costs", "add", "--idea", "_fixture", "--kind", "ads", "--amount-eur", "12.5"]
    argv += ["--provider", "meta", "--phase", "run", "--note", "day 1", "--channel", "meta_feed"]
    assert main(argv) == 0
    line = costs.read_lines("_fixture")[-1]
    assert (line["kind"], line["provider"], line["amount_eur"]) == ("ads", "meta", 12.5)
    assert (line["phase"], line["note"], line["channel"]) == ("run", "day 1", "meta_feed")
    assert len(costs.read_lines("_fixture")) == 4
    assert capsys.readouterr().out == ""


def test_costs_add_needs_only_a_kind_and_an_amount(root):
    argv = ["costs", "add", "--idea", "_fixture", "--kind", "founder_time", "--amount-eur", "-5"]
    assert main(argv) == 0  # a negative line corrects an earlier one
    line = costs.read_lines("_fixture")[-1]
    assert (line["provider"], line["phase"], line["note"], line["channel"]) == ("", "", "", None)
    assert line["amount_eur"] == -5.0


@pytest.mark.parametrize(
    ("kind", "amount", "idea", "code"),
    [
        ("gold", "1", "_fixture", 2),
        ("api", "lots", "_fixture", 2),
        ("api", "nan", "_fixture", 1),
        ("api", "1", "nope", 1),
    ],
)
def test_costs_add_refuses_bad_input_and_writes_nothing(root, capsys, kind, amount, idea, code):
    path = root / "ideas/_fixture/costs.jsonl"
    before = path.read_text()
    argv = ["costs", "add", "--idea", idea, "--kind", kind, "--amount-eur", amount]
    assert main(argv) == code
    assert capsys.readouterr().err != ""
    assert path.read_text() == before
    assert not (root / "ideas/nope").exists()


def test_costs_total_prints_a_line_per_kind_then_cash_and_cap(root, capsys):
    assert main(["costs", "total", "--idea", "_fixture"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "ads             0.00 EUR",
        "api             0.12 EUR",
        "llm             0.28 EUR",
        "domain          0.00 EUR",
        "founder_time   25.00 EUR",
        "other           0.00 EUR",
        "cash            0.40 EUR  (every kind but founder_time)",
        "cap           300.00 EUR",
    ]


def test_costs_total_json_is_the_totals_by_kind_with_cash_and_cap(root, capsys):
    assert main(["costs", "total", "--idea", "_fixture", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "ads": 0.0,
        "api": 0.12,
        "llm": 0.28,
        "domain": 0.0,
        "founder_time": 25.0,
        "other": 0.0,
        "cash_eur": 0.4,
        "cap_eur": 300.0,
    }


def test_costs_total_unknown_idea(root, capsys):
    assert main(["costs", "total", "--idea", "nope"]) == 1
    assert "ideas/" in capsys.readouterr().err


def test_costs_total_names_the_malformed_line(root, capsys):
    with (root / "ideas/_fixture/costs.jsonl").open("a") as f:
        f.write("not json\n")
    assert main(["costs", "total", "--idea", "_fixture"]) == 1
    err = capsys.readouterr().err
    assert "costs.jsonl:4" in err and len(err.splitlines()) == 1
