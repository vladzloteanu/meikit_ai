import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from factory import costs, ledger

REPO_FIXTURE = Path(__file__).resolve().parents[2] / "ideas" / "_fixture"

STATUS_NAMES = [
    "NEW",
    "TRIAGED",
    "GO",
    "NO-GO",
    "LAUNCHED",
    "RUNNING",
    "REWORK",
    "BUILD",
    "PIVOT",
    "PARK",
    "DROP",
]

IDEA_KEYS = [
    "slug",
    "title",
    "status",
    "created",
    "updated",
    "geo",
    "language",
    "buyer",
    "signer",
    "value_per_customer_eur",
    "cap_eur",
    "founder_hour_rate_eur",
    "repo",
    "local_path",
    "domain",
    "current_experiment",
    "provisional",
    "notes",
    "totals",
]

DEFAULT_STEPS = [
    ("1", "intake", "/idea-new", "15 min"),
    ("2", "triage", "/idea-triage", "60 min"),
    ("3", "challenge", "/idea-challenge", "1 session"),
    ("4", "launch", "/idea-launch", "1 day"),
    ("5", "run", "/idea-status", "5 min/day"),
    ("6", "conversations", "manual", "5 × 20 min"),
    ("7", "verdict", "/idea-verdict", "30 min"),
]

WORKSTREAM_PLAN = """\
# Plan

## Steps

- [x] 1. intake — `/idea-new` — 15 min — 2026-10-14
- [~] 2. triage — `/idea-triage` — 60 min

Prose that mentions - [ ] inline is not a step.
- a plain bullet is not a step either

## Workstream: lp-improve

- [ ] lp-improve.1. design review — `/gstack-design-review` — 30 min
- [!] lp-improve.2. read interviews — `manual` — 1 day — 2026-10-30
"""

TEN_HEADINGS = [
    "Summary",
    "Who pays today",
    "Demand",
    "Complaints",
    "Landscape",
    "AdsInsights conclusions",
    "Triage score",
    "Gate",
    "Open questions for the challenge",
    "Cost and time of this triage",
]


def write_idea_yml(root: Path, slug: str, text: str) -> Path:
    folder = root / "ideas" / slug
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "idea.yml"
    path.write_text(text, encoding="utf-8")
    return path


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- the brief's tests -------------------------------------------------------------------------


def test_load_fixture_idea(root):
    i = ledger.load_idea("_fixture")
    assert i.status == "RUNNING" and i.cap_eur == 300


def test_list_ideas_skips_fixture(root):
    assert all(i.slug != "_fixture" for i in ledger.list_ideas())


def test_plan_next_and_mark(root):
    assert ledger.next_step("_fixture").id == "5"
    s = ledger.mark_step("_fixture", "5", "done", when="2026-10-21")
    assert s.status == "done" and s.done_at == "2026-10-21"
    assert "- [x] 5. run" in (root / "ideas/_fixture/plan.md").read_text()


def test_plan_parse_error_has_line(root):
    p = root / "ideas/_fixture/plan.md"
    p.write_text(p.read_text() + "\n- [x] broken line\n")
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert e.value.line_no > 1


def test_create_idea_writes_files(root):
    ledger.create_idea("demo", "Demo", geo=["FR"], language="fr", cap_eur=300)
    d = root / "ideas/demo"
    assert (d / "idea.yml").exists() and (d / "plan.md").exists() and (d / "costs.jsonl").exists()
    assert ledger.next_step("demo").id == "1"


def test_unknown_idea_message(root):
    with pytest.raises(ledger.IdeaNotFound) as e:
        ledger.load_idea("nope")
    assert "ideas/" in str(e.value)


# --- the fixture idea --------------------------------------------------------------------------


def test_fixture_folder_is_complete():
    for name in ("idea.yml", "plan.md", "intake.md", "brief.md", "costs.jsonl", "learnings.md"):
        assert (REPO_FIXTURE / name).is_file(), name
    assert (REPO_FIXTURE / "research" / ".gitkeep").is_file()


def test_fixture_idea_fields(root):
    i = ledger.load_idea("_fixture")
    assert (i.slug, i.title, i.status) == ("_fixture", "Fixture idea (dry runs only)", "RUNNING")
    assert i.geo == ["FR"] and i.language == "fr"
    assert i.buyer == "independent dog groomers"
    assert (i.value_per_customer_eur, i.cap_eur, i.founder_hour_rate_eur) == (228.0, 300.0, 100.0)
    assert (i.repo, i.local_path, i.domain) == (None, None, None)
    assert i.current_experiment == 1 and i.provisional is False
    assert i.extra == {}


def test_fixture_plan_has_four_steps_done_in_october_2026(root):
    steps = ledger.load_plan("_fixture")
    assert [(s.id, s.name, s.command, s.timebox) for s in steps] == DEFAULT_STEPS
    assert [s.status for s in steps] == ["done"] * 4 + ["todo"] * 3
    assert all(re.fullmatch(r"2026-10-\d\d", s.done_at) for s in steps[:4])
    assert all(s.done_at is None for s in steps[4:])


def test_fixture_costs_are_the_three_documented_lines(root):
    lines = costs.read_lines("_fixture")
    assert [
        (line["kind"], line["provider"], line["amount_eur"], line["channel"]) for line in lines
    ] == [
        ("api", "searchapi", 0.12, None),
        ("llm", "neuralbox", 0.28, None),
        ("founder_time", "vlad", 25.0, None),
    ]
    assert all(re.fullmatch(r"2026-10-\d\dT\d\d:\d\d:\d\d", line["ts"]) for line in lines)
    assert all(list(line) == costs.LINE_KEYS for line in lines)
    assert len((root / "ideas/_fixture/costs.jsonl").read_text().splitlines()) == 3


def test_fixture_stored_totals_match_its_costs(root):
    assert ledger.load_idea("_fixture").totals == costs.summary("_fixture")


def test_fixture_brief_has_the_triage_template_headings(root):
    text = read(root / "ideas/_fixture/brief.md")
    headings = re.findall(r"^## (.+?)\s*$", text, flags=re.MULTILINE)
    for heading in TEN_HEADINGS:
        assert heading in headings


def test_fixture_intake_is_a_two_paragraph_pitch(root):
    text = read(root / "ideas/_fixture/intake.md")
    assert text.startswith("# Intake — Fixture idea (dry runs only)\n")
    assert "## Pitch (verbatim)" in text


def test_fixture_learnings_has_a_header_and_one_dated_line(root):
    lines = read(root / "ideas/_fixture/learnings.md").splitlines()
    assert lines[0] == "# Learnings — _fixture"
    entries = [line for line in lines if line.startswith("- ")]
    assert len(entries) == 1 and re.match(r"- 2026-10-\d\d /\S+: .+", entries[0])


def test_fixture_names_no_company_client_or_person():
    # The fixture ships in every checkout and is copied by every dry run: nothing real in it.
    forbidden = re.compile(
        r"dolead|selectiona|\bcmt\b|code modulo|zloteanu|google|facebook|\bmeta\b|linkedin|reddit",
        re.IGNORECASE,
    )
    for path in REPO_FIXTURE.rglob("*"):
        if path.suffix in {".md", ".yml", ".jsonl"}:
            assert not forbidden.search(read(path)), path.name


def test_fixture_idea_yml_is_in_the_form_save_idea_writes(root, monkeypatch):
    path = root / "ideas/_fixture/idea.yml"
    before = read(path)
    monkeypatch.setattr(ledger, "_today", lambda: yaml.safe_load(before)["updated"])
    ledger.save_idea(ledger.load_idea("_fixture"))
    assert read(path) == before


# --- statuses, listing -------------------------------------------------------------------------


def test_statuses_are_the_eleven_in_spec_order():
    assert ledger.STATUSES == STATUS_NAMES
    assert ledger.STEP_STATUSES == ["todo", "doing", "done", "skipped", "void"]


def test_idea_slugs_lists_folders_with_an_idea_yml(root):
    ledger.create_idea("beta", "Beta")
    ledger.create_idea("alpha", "Alpha")
    (root / "ideas" / "stray").mkdir()  # no idea.yml: not an idea
    write_idea_yml(root, "Not A Slug", "slug: x\ntitle: x\n")  # not a slug: never listed
    assert ledger.idea_slugs() == ["alpha", "beta"]
    assert ledger.idea_slugs(include_fixture=True) == ["_fixture", "alpha", "beta"]


def test_list_ideas_returns_ideas_in_slug_order(root):
    ledger.create_idea("beta", "Beta")
    ledger.create_idea("alpha", "Alpha")
    assert [i.slug for i in ledger.list_ideas()] == ["alpha", "beta"]
    assert [i.slug for i in ledger.list_ideas(include_fixture=True)] == [
        "_fixture",
        "alpha",
        "beta",
    ]


def test_list_ideas_with_no_ideas_folder_is_empty(factory_root):
    assert ledger.list_ideas() == []


# --- idea.yml: load ----------------------------------------------------------------------------


def test_load_idea_fills_defaults_for_a_minimal_file(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    write_idea_yml(root, "demo", "slug: demo\ntitle: Demo\n")
    i = ledger.load_idea("demo")
    assert (i.status, i.language, i.cap_eur, i.founder_hour_rate_eur) == ("NEW", "en", 300.0, 100.0)
    assert (i.created, i.updated) == ("2026-11-02", "2026-11-02")
    assert (i.geo, i.buyer, i.signer, i.notes, i.value_per_customer_eur) == ([], "", "", "", 0.0)
    assert (i.repo, i.local_path, i.domain, i.current_experiment) == (None, None, None, None)
    assert i.provisional is False and i.totals == {} and i.extra == {}


def test_load_idea_reads_unquoted_dates_as_text(root):
    write_idea_yml(
        root, "demo", "slug: demo\ntitle: Demo\ncreated: 2026-08-10\nupdated: 2026-08-11\n"
    )
    i = ledger.load_idea("demo")
    assert (i.created, i.updated) == ("2026-08-10", "2026-08-11")


def test_load_idea_takes_the_folder_name_when_slug_and_title_are_missing(root):
    write_idea_yml(root, "demo", "status: PARK\n")
    i = ledger.load_idea("demo")
    assert (i.slug, i.title, i.status) == ("demo", "demo", "PARK")


def test_load_idea_reads_numbers_geo_and_flags_leniently(root):
    write_idea_yml(
        root,
        "demo",
        "slug: demo\ntitle: Demo\ngeo: FR, US\ncap_eur: '250'\nvalue_per_customer_eur: 19\n"
        "current_experiment: '2'\nprovisional: true\nrepo: ''\n",
    )
    i = ledger.load_idea("demo")
    assert i.geo == ["FR", "US"]
    assert i.cap_eur == 250.0 and isinstance(i.cap_eur, float)
    assert i.value_per_customer_eur == 19.0 and isinstance(i.value_per_customer_eur, float)
    assert i.current_experiment == 2 and i.provisional is True and i.repo is None


@pytest.mark.parametrize(
    ("text", "needle"),
    [
        ("", "mapping"),
        ("- a\n- b\n", "mapping"),
        ("slug: [unclosed\n", "YAML"),
        ("slug: demo\ntitle: T\nstatus: LIVE\n", "status"),
        ("slug: demo\ntitle: T\ncap_eur: lots\n", "cap_eur"),
        ("slug: demo\ntitle: T\ncap_eur: true\n", "cap_eur"),
        ("slug: other\ntitle: T\n", "slug"),
        ("slug: demo\ntitle: T\nprovisional: 'false'\n", "provisional"),
        ("slug: demo\ntitle: T\ncurrent_experiment: first\n", "current_experiment"),
        ("slug: demo\ntitle: T\ngeo: {a: 1}\n", "geo"),
    ],
)
def test_load_idea_rejects_a_malformed_file(root, text, needle):
    write_idea_yml(root, "demo", text)
    with pytest.raises(ledger.IdeaFileError) as e:
        ledger.load_idea("demo")
    message = str(e.value)
    assert "ideas/demo/idea.yml" in message and needle in message
    assert "\n" not in message
    assert isinstance(e.value, ledger.LedgerError)


@pytest.mark.parametrize("slug", ["", "..", "../outside", "a/b", "Demo", "-x", "x y"])
def test_load_idea_treats_a_slug_that_is_not_a_slug_as_unknown(root, slug):
    (root / "outside").mkdir()  # what "../outside" would reach from ideas/
    (root / "outside" / "idea.yml").write_text("slug: outside\ntitle: Outside\n", encoding="utf-8")
    with pytest.raises(ledger.IdeaNotFound):
        ledger.load_idea(slug)


def test_idea_not_found_lists_the_known_ideas(root):
    ledger.create_idea("demo", "Demo")
    with pytest.raises(ledger.IdeaNotFound) as e:
        ledger.load_idea("demp")
    message = str(e.value)
    assert "'demp'" in message and "ideas/" in message
    assert "demo" in message and "_fixture" in message
    assert e.value.slug == "demp"
    assert "\n" not in message


def test_idea_not_found_without_an_ideas_folder(factory_root):
    with pytest.raises(ledger.IdeaNotFound, match="ideas/"):
        ledger.load_idea("anything")


def test_a_folder_without_idea_yml_is_not_an_idea(root):
    (root / "ideas" / "half").mkdir()
    with pytest.raises(ledger.IdeaNotFound):
        ledger.load_idea("half")


# --- idea.yml: save ----------------------------------------------------------------------------


def test_save_idea_bumps_updated_and_recomputes_totals(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    costs.append("_fixture", "ads", "meta", 10.0)
    i = ledger.load_idea("_fixture")
    assert i.updated != "2026-11-02" and i.totals["cash_eur"] == 0.4
    i.status = "REWORK"
    ledger.save_idea(i)
    assert i.updated == "2026-11-02"
    again = ledger.load_idea("_fixture")
    assert (again.status, again.updated) == ("REWORK", "2026-11-02")
    assert again.totals == {
        "cash_eur": 10.4,
        "founder_time_eur": 25.0,
        "by_kind": {
            "ads": 10.0,
            "api": 0.12,
            "llm": 0.28,
            "domain": 0.0,
            "founder_time": 25.0,
            "other": 0.0,
        },
    }
    assert i.totals == again.totals


def test_idea_yml_keys_are_in_the_field_order(root):
    ledger.create_idea("demo", "Demo", geo=["FR"])
    data = yaml.safe_load(read(root / "ideas/demo/idea.yml"))
    assert list(data) == IDEA_KEYS
    assert isinstance(data["created"], str) and isinstance(data["updated"], str)
    assert data["geo"] == ["FR"] and data["provisional"] is False and data["repo"] is None


def test_save_idea_keeps_unknown_keys_after_the_known_ones(root):
    path = root / "ideas/_fixture/idea.yml"
    path.write_text(read(path) + "v1_status: PIVOT\nlabels: [a, b]\n", encoding="utf-8")
    i = ledger.load_idea("_fixture")
    assert i.extra == {"v1_status": "PIVOT", "labels": ["a", "b"]}
    i.notes = "edited"
    ledger.save_idea(i)
    data = yaml.safe_load(read(path))
    assert list(data) == IDEA_KEYS + ["v1_status", "labels"]
    assert data["v1_status"] == "PIVOT" and data["labels"] == ["a", "b"]
    assert data["notes"] == "edited"
    assert "extra" not in data


def test_save_idea_refuses_a_status_that_is_not_one_of_the_eleven(root):
    before = read(root / "ideas/_fixture/idea.yml")
    i = ledger.load_idea("_fixture")
    i.status = "LIVE"
    with pytest.raises(ValueError, match="status"):
        ledger.save_idea(i)
    assert read(root / "ideas/_fixture/idea.yml") == before


def test_save_idea_refuses_a_missing_folder_and_creates_nothing(root):
    with pytest.raises(ledger.IdeaNotFound):
        ledger.save_idea(ledger.Idea(slug="ghost", title="Ghost"))
    assert not (root / "ideas/ghost").exists()


def test_save_idea_keeps_non_ascii_text_readable(root):
    i = ledger.load_idea("_fixture")
    i.notes = "café — déjà vu"
    ledger.save_idea(i)
    assert "café — déjà vu" in read(root / "ideas/_fixture/idea.yml")
    assert ledger.load_idea("_fixture").notes == "café — déjà vu"


def test_writes_leave_no_temp_files(root):
    ledger.mark_step("_fixture", "5", "done")
    ledger.save_idea(ledger.load_idea("_fixture"))
    ledger.append_learning("_fixture", "/idea-status", "x")
    assert not [n for n in os.listdir(root / "ideas/_fixture") if n.endswith(".tmp")]


# --- idea.yml: create --------------------------------------------------------------------------


def test_create_idea_files_in_detail(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-10-21")
    i = ledger.create_idea("demo", "Demo", geo=["FR"], language="fr", cap_eur=300)
    d = root / "ideas/demo"
    assert read(d / "plan.md") == ledger.DEFAULT_PLAN
    assert read(d / "intake.md").startswith("# Intake — Demo\n")
    assert read(d / "learnings.md").startswith("# Learnings — demo\n")
    assert read(d / "costs.jsonl") == ""
    assert (d / "research").is_dir() and (d / "research" / ".gitkeep").is_file()
    assert (i.status, i.created, i.updated, i.cap_eur) == ("NEW", "2026-10-21", "2026-10-21", 300)
    assert (i.geo, i.language, i.founder_hour_rate_eur) == (["FR"], "fr", 100.0)
    assert i == ledger.load_idea("demo")
    assert i.totals == costs.summary("demo")


def test_create_idea_accepts_every_idea_field(root):
    i = ledger.create_idea(
        "demo",
        "Demo",
        status="GO",
        created="2026-08-01",
        geo=["FR", "US"],
        language="fr",
        buyer="agency owners",
        signer="the owner",
        value_per_customer_eur=228,
        cap_eur=150,
        founder_hour_rate_eur=80,
        repo="https://example.test/demo",
        local_path="/tmp/demo",
        domain="demo.example",
        current_experiment=2,
        provisional=True,
        notes="n",
    )
    again = ledger.load_idea("demo")
    assert again == i
    assert (again.status, again.created, again.cap_eur, again.provisional) == (
        "GO",
        "2026-08-01",
        150.0,
        True,
    )


def test_create_idea_can_set_keys_that_are_not_fields(root):
    ledger.create_idea("demo", "Demo", extra={"v1_status": "PIVOT"})
    assert ledger.load_idea("demo").extra == {"v1_status": "PIVOT"}
    assert yaml.safe_load(read(root / "ideas/demo/idea.yml"))["v1_status"] == "PIVOT"


def test_create_idea_refuses_an_existing_idea(root):
    before = read(root / "ideas/_fixture/idea.yml")
    with pytest.raises(ledger.IdeaExists) as e:
        ledger.create_idea("_fixture", "Other")
    assert "ideas/_fixture" in str(e.value) and e.value.slug == "_fixture"
    assert isinstance(e.value, ledger.LedgerError)
    assert read(root / "ideas/_fixture/idea.yml") == before


def test_create_idea_keeps_files_already_in_the_folder(root):
    d = root / "ideas/demo"
    d.mkdir()
    (d / "intake.md").write_text("# mine\n", encoding="utf-8")
    (d / "v1").mkdir()
    ledger.create_idea("demo", "Demo")
    assert read(d / "intake.md") == "# mine\n"
    assert (d / "v1").is_dir() and (d / "idea.yml").is_file() and (d / "plan.md").is_file()


@pytest.mark.parametrize("slug", ["", "..", "a/b", "Demo", "-x", "x y", "x.y", "é"])
def test_create_idea_refuses_a_bad_slug_and_creates_nothing(root, slug):
    with pytest.raises(ValueError, match="slug"):
        ledger.create_idea(slug, "T")
    assert [p.name for p in (root / "ideas").iterdir()] == ["_fixture"]


def test_create_idea_with_a_bad_status_creates_nothing(root):
    with pytest.raises(ValueError, match="status"):
        ledger.create_idea("demo", "Demo", status="LIVE")
    assert not (root / "ideas/demo").exists()


def test_create_idea_rejects_an_unknown_field_and_creates_nothing(root):
    with pytest.raises(TypeError, match="colour"):
        ledger.create_idea("demo", "Demo", colour="red")
    assert not (root / "ideas/demo").exists()


# --- plan.md -----------------------------------------------------------------------------------


def test_default_plan_is_the_seven_steps_all_todo(root):
    ledger.create_idea("demo", "Demo")
    steps = ledger.load_plan("demo")
    assert [(s.id, s.name, s.command, s.timebox) for s in steps] == DEFAULT_STEPS
    assert {s.status for s in steps} == {"todo"}
    assert {s.done_at for s in steps} == {None}
    assert {s.section for s in steps} == {"steps"}
    assert "- [ ] 6. conversations — `manual` — 5 × 20 min\n" in ledger.DEFAULT_PLAN
    assert ledger.DEFAULT_PLAN.count("- [ ] ") == 7


def test_load_plan_reads_steps_and_workstreams(root):
    ledger.create_idea("demo", "Demo")
    (root / "ideas/demo/plan.md").write_text(WORKSTREAM_PLAN, encoding="utf-8")
    steps = ledger.load_plan("demo")
    assert steps == [
        ledger.Step("1", "intake", "/idea-new", "15 min", "done", "2026-10-14", "steps"),
        ledger.Step("2", "triage", "/idea-triage", "60 min", "doing", None, "steps"),
        ledger.Step(
            "lp-improve.1",
            "design review",
            "/gstack-design-review",
            "30 min",
            "todo",
            None,
            "lp-improve",
        ),
        ledger.Step(
            "lp-improve.2", "read interviews", "manual", "1 day", "void", "2026-10-30", "lp-improve"
        ),
    ]


def test_next_step_is_the_first_doing_else_the_first_todo(root):
    ledger.create_idea("demo", "Demo")
    plan = root / "ideas/demo/plan.md"
    plan.write_text(WORKSTREAM_PLAN, encoding="utf-8")
    assert ledger.next_step("demo").id == "2"  # doing wins
    ledger.mark_step("demo", "2", "done")
    assert ledger.next_step("demo").id == "lp-improve.1"  # then the first todo, file order
    ledger.mark_step("demo", "lp-improve.1", "skipped")
    assert ledger.next_step("demo") is None  # only done, skipped and void steps remain


def test_next_step_prefers_a_later_doing_step_over_an_earlier_todo(root):
    ledger.mark_step("_fixture", "6", "doing")
    assert ledger.next_step("_fixture").id == "6"


def test_next_step_of_an_empty_plan_is_none(root):
    (root / "ideas/_fixture/plan.md").write_text("# Plan\n\n## Steps\n", encoding="utf-8")
    assert ledger.load_plan("_fixture") == []
    assert ledger.next_step("_fixture") is None


def test_mark_step_changes_only_its_line(root):
    path = root / "ideas/_fixture/plan.md"
    before = read(path).split("\n")
    ledger.mark_step("_fixture", "5", "doing")
    after = read(path).split("\n")
    changed = [n for n, (a, b) in enumerate(zip(before, after, strict=True)) if a != b]
    assert len(changed) == 1
    assert after[changed[0]] == "- [~] 5. run — `/idea-status` — 5 min/day"


def test_mark_step_keeps_windows_line_endings(root):
    path = root / "ideas/_fixture/plan.md"
    path.write_bytes(read(path).replace("\n", "\r\n").encode("utf-8"))
    ledger.mark_step("_fixture", "5", "done", when="2026-10-21")
    raw = path.read_bytes()
    assert raw.count(b"\r\n") == raw.count(b"\n")
    assert "- [x] 5. run — `/idea-status` — 5 min/day — 2026-10-21\r\n".encode() in raw
    assert ledger.next_step("_fixture").id == "6"


@pytest.mark.parametrize(
    ("status", "when", "marker", "date"),
    [
        ("done", None, "x", "2026-11-02"),
        ("skipped", None, "-", "2026-11-02"),
        ("void", None, "!", "2026-11-02"),
        ("doing", None, "~", None),
        ("todo", None, " ", None),
        ("done", "2026-10-30", "x", "2026-10-30"),
        ("doing", "2026-10-30", "~", "2026-10-30"),
    ],
)
def test_mark_step_marker_and_date(root, monkeypatch, status, when, marker, date):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-11-02")
    step = ledger.mark_step("_fixture", "5", status, when=when)
    assert (step.id, step.status, step.done_at) == ("5", status, date)
    suffix = f" — {date}" if date else ""
    assert f"- [{marker}] 5. run — `/idea-status` — 5 min/day{suffix}\n" in read(
        root / "ideas/_fixture/plan.md"
    )
    assert ledger.load_plan("_fixture")[4] == step


def test_reopening_a_step_clears_its_date(root):
    step = ledger.mark_step("_fixture", "4", "todo")
    assert (step.status, step.done_at) == ("todo", None)
    assert "- [ ] 4. launch — `/idea-launch` — 1 day\n" in read(root / "ideas/_fixture/plan.md")


def test_marking_a_done_step_done_again_keeps_its_date(root):
    step = ledger.mark_step("_fixture", "4", "done")
    assert step.done_at == "2026-10-16"
    step = ledger.mark_step("_fixture", "4", "done", when="2026-10-17")
    assert step.done_at == "2026-10-17"


def test_mark_step_in_a_workstream(root):
    ledger.create_idea("demo", "Demo")
    (root / "ideas/demo/plan.md").write_text(WORKSTREAM_PLAN, encoding="utf-8")
    step = ledger.mark_step("demo", "lp-improve.1", "skipped", when="2026-10-22")
    assert step.section == "lp-improve" and step.status == "skipped"
    expected = "- [-] lp-improve.1. design review — `/gstack-design-review` — 30 min — 2026-10-22\n"
    assert expected in read(root / "ideas/demo/plan.md")


def test_mark_step_rejects_bad_input_and_leaves_the_file_alone(root):
    path = root / "ideas/_fixture/plan.md"
    before = read(path)
    with pytest.raises(ledger.StepNotFound) as e:
        ledger.mark_step("_fixture", "9", "done")
    assert "'9'" in str(e.value) and "ideas/_fixture/plan.md" in str(e.value)
    assert isinstance(e.value, ledger.LedgerError)
    with pytest.raises(ValueError, match="status"):
        ledger.mark_step("_fixture", "5", "finished")
    for when in ("21/10/2026", "2026-13-01", "20261021", ""):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            ledger.mark_step("_fixture", "5", "done", when=when)
    assert read(path) == before


def test_mark_step_of_an_unknown_idea_creates_nothing(root):
    with pytest.raises(ledger.IdeaNotFound):
        ledger.mark_step("nope", "1", "done")
    assert not (root / "ideas/nope").exists()


@pytest.mark.parametrize(
    "bad",
    [
        "- [x] broken line",
        "- [X] 8. run — `/idea-status` — 5 min/day",
        "- [?] 8. run — `/idea-status` — 5 min/day",
        "- [] 8. run — `/idea-status` — 5 min/day",
        "- [ ]8. run — `/idea-status` — 5 min/day",
        "- [ ] 8 run — `/idea-status` — 5 min/day",
        "- [ ] . run — `/idea-status` — 5 min/day",
        "- [ ] 8. run — /idea-status — 5 min/day",
        "- [ ] 8. run — `` — 5 min/day",
        "- [ ] 8. run - `/idea-status` - 5 min/day",
        "- [ ] 8. run — `/idea-status`",
        "- [ ] 8. run — `/idea-status` — ",
        "- [ ] 8. run — `/idea-status` — 5 min/day — 21-10-2026",
        "- [ ] 8. run — `/idea-status` — 5 min/day — 2026-13-45",
        "- [ ] 8. run — `/idea-status` — 5 min/day — 2026-10-21 — 2026-10-22",
        "- [ ] a.b. run — `/idea-status` — 5 min/day",
    ],
)
def test_a_step_line_that_does_not_match_the_grammar_is_an_error(root, bad):
    path = root / "ideas/_fixture/plan.md"
    path.write_text(read(path) + bad + "\n", encoding="utf-8")
    line_no = len(read(path).splitlines())
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert e.value.line_no == line_no and e.value.text == bad
    message = str(e.value)
    assert f"plan.md:{line_no}" in message and "ideas/_fixture/" in message
    assert "\n" not in message
    assert isinstance(e.value, ledger.LedgerError)


def test_a_trailing_date_that_is_not_a_date_is_an_error(root):
    path = root / "ideas/_fixture/plan.md"
    path.write_text(read(path) + "- [x] 8. extra — `/x` — 1 min — 2026-13-45\n", encoding="utf-8")
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert "2026-13-45 is not a date" in str(e.value)


def test_parse_error_without_a_slug_still_names_the_line():
    error = ledger.PlanParseError(7, "- [x] oops")
    assert "plan.md:7" in str(error) and "- [x] oops" in str(error)
    assert (error.line_no, error.text) == (7, "- [x] oops")


def test_a_step_before_any_section_heading_is_an_error(root):
    path = root / "ideas/_fixture/plan.md"
    path.write_text("# Plan\n\n- [ ] 1. intake — `/idea-new` — 15 min\n", encoding="utf-8")
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert e.value.line_no == 3 and "section" in str(e.value)


def test_a_step_under_another_heading_is_an_error(root):
    path = root / "ideas/_fixture/plan.md"
    path.write_text(
        "## Steps\n\n- [ ] 1. intake — `/idea-new` — 15 min\n\n## Notes\n\n"
        "- [ ] 2. triage — `/idea-triage` — 60 min\n",
        encoding="utf-8",
    )
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert e.value.line_no == 7 and "section" in str(e.value)


def test_a_duplicate_step_id_is_an_error(root):
    path = root / "ideas/_fixture/plan.md"
    path.write_text(read(path) + "- [ ] 5. again — `/idea-status` — 1 min\n", encoding="utf-8")
    line_no = len(read(path).splitlines())
    with pytest.raises(ledger.PlanParseError) as e:
        ledger.load_plan("_fixture")
    assert e.value.line_no == line_no and "duplicate" in str(e.value) and "'5'" in str(e.value)


def test_lines_that_are_not_steps_are_ignored(root):
    path = root / "ideas/_fixture/plan.md"
    extra = (
        "\nSome prose with - [ ] in the middle.\n"
        "  - [ ] an indented checklist item\n"
        "- a plain bullet\n"
        "### A sub heading\n"
        "> a quote\n"
    )
    path.write_text(read(path) + extra, encoding="utf-8")
    assert [s.id for s in ledger.load_plan("_fixture")] == [str(n) for n in range(1, 8)]


def test_load_plan_of_a_missing_file_is_a_ledger_error(root):
    (root / "ideas/_fixture/plan.md").unlink()
    with pytest.raises(ledger.LedgerError, match=r"ideas/_fixture/plan\.md"):
        ledger.load_plan("_fixture")


def test_load_plan_of_an_unknown_idea(root):
    with pytest.raises(ledger.IdeaNotFound):
        ledger.load_plan("nope")


# --- learnings.md ------------------------------------------------------------------------------


def test_append_learning_appends_one_dated_line(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-10-21")
    path = root / "ideas/_fixture/learnings.md"
    before = read(path)
    ledger.append_learning("_fixture", "/idea-status", "first line\nsecond  line")
    assert read(path) == before + "- 2026-10-21 /idea-status: first line second line\n"


def test_append_learning_creates_the_file_with_a_header(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-10-21")
    path = root / "ideas/_fixture/learnings.md"
    path.unlink()
    ledger.append_learning("_fixture", "/idea-triage", "no ads for the trigger bucket")
    assert read(path) == (
        "# Learnings — _fixture\n\n- 2026-10-21 /idea-triage: no ads for the trigger bucket\n"
    )


def test_append_learning_ends_an_unterminated_last_line_first(root, monkeypatch):
    monkeypatch.setattr(ledger, "_today", lambda: "2026-10-21")
    path = root / "ideas/_fixture/learnings.md"
    path.write_text("# Learnings — _fixture\n\n- 2026-10-01 /idea-new: by hand", encoding="utf-8")
    ledger.append_learning("_fixture", "/idea-triage", "x")
    assert read(path).splitlines()[2:] == [
        "- 2026-10-01 /idea-new: by hand",
        "- 2026-10-21 /idea-triage: x",
    ]


def test_append_learning_for_a_missing_idea_creates_nothing(root):
    with pytest.raises(ledger.IdeaNotFound):
        ledger.append_learning("nope", "/idea-status", "x")
    assert not (root / "ideas/nope").exists()


# --- module structure --------------------------------------------------------------------------


@pytest.mark.parametrize("module", ["factory.ledger", "factory.costs"])
def test_each_module_imports_on_its_own(module):
    # ledger and costs use each other: importing either first must work.
    command = [sys.executable, "-I", "-c", f"import {module}"]
    subprocess.run(command, check=True, capture_output=True)
