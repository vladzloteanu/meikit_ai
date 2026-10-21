"""The idea ledger: one folder per idea, the single source of truth for where it stands.

`ideas/<slug>/` (spec section 6) holds `idea.yml` (status, dates, buyer, cap, computed totals),
`plan.md` (the steps and workstreams with their status), `learnings.md`, `costs.jsonl` (which
`factory.costs` reads and writes) and whatever the skills and tools add. This module reads and
writes the first three and creates the folder; docs/ledger.md describes the formats.

Every function takes the idea's slug and finds its folder through `paths`, at call time, so
FACTORY_ROOT works as everywhere else. A slug that is not a well-formed slug, or whose folder does
not exist, is refused with IdeaNotFound before anything is read or written: a typo never creates a
stray folder, and a slug can never point outside `ideas/`.

Every error this module raises on purpose is a LedgerError whose message is one line naming the
file (and the line, for plan.md), so a command can print it and exit 1 without a traceback.
"""

import contextlib
import dataclasses
import math
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from factory import paths

# Idea statuses, in the order of spec section 6.
STATUSES: list[str] = [
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

# Plan step statuses, and the character that stands for each between the brackets in plan.md.
MARKERS: dict[str, str] = {"todo": " ", "doing": "~", "done": "x", "skipped": "-", "void": "!"}
STEP_STATUSES: list[str] = list(MARKERS)

FIXTURE_SLUG = "_fixture"
DEFAULT_CAP_EUR = 300.0  # cash per experiment (spec section 4)
DEFAULT_RATE_EUR = 100.0  # founder hour (spec section 4)

# The weekly cycle of spec section 5 as a new idea's plan.md.
DEFAULT_PLAN = """\
# Plan

## Steps

- [ ] 1. intake — `/idea-new` — 15 min
- [ ] 2. triage — `/idea-triage` — 60 min
- [ ] 3. challenge — `/idea-challenge` — 1 session
- [ ] 4. launch — `/idea-launch` — 1 day
- [ ] 5. run — `/idea-status` — 5 min/day
- [ ] 6. conversations — `manual` — 5 × 20 min
- [ ] 7. verdict — `/idea-verdict` — 30 min
"""

_SLUG_RE = re.compile(r"[a-z0-9_][a-z0-9_-]*")
_DAY_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_HEADING_RE = re.compile(r"## +(?P<title>\S.*)")
_STEP_GRAMMAR = "- [ ] <id>. <name> — `<command>` — <timebox>[ — YYYY-MM-DD]"
# A name or a timebox is free text that does not contain the separator " — ".
_STEP_RE = re.compile(
    r"- \[(?P<marker>[ ~x!-])\] (?P<id>[a-z0-9][a-z0-9_-]*(?:\.[0-9]+)?)\. "
    r"(?P<name>(?:(?! — ).)+) — `(?P<command>[^`]+)` — (?P<timebox>(?:(?! — ).)+)"
    r"(?: — (?P<done_at>[0-9]{4}-[0-9]{2}-[0-9]{2}))?"
)
_STATUS_OF_MARKER = {marker: status for status, marker in MARKERS.items()}
_DATED = ("done", "skipped", "void")  # statuses that get today's date when no date is given


class LedgerError(Exception):
    """A ledger operation failed. The message is one line and names the file involved."""


class IdeaNotFound(LedgerError):
    """No idea has this slug: not a slug, or no such folder under ideas/."""

    def __init__(self, slug: str) -> None:
        known = ", ".join(idea_slugs(include_fixture=True)) or "none"
        super().__init__(f"no idea {slug!r} in ideas/ (known: {known})")
        self.slug = slug


class IdeaExists(LedgerError):
    """create_idea was asked for a slug that already has an idea.yml."""

    def __init__(self, slug: str) -> None:
        super().__init__(f"idea {slug!r} already exists: ideas/{slug}/idea.yml")
        self.slug = slug


class IdeaFileError(LedgerError):
    """idea.yml cannot be read: broken YAML, not a mapping, or a value of the wrong kind."""

    def __init__(self, slug: str, reason: str) -> None:
        super().__init__(f"ideas/{slug}/idea.yml: {reason}")
        self.slug = slug
        self.reason = reason


class PlanParseError(LedgerError):
    """A line of plan.md breaks the plan grammar. `str()` holds `plan.md:<line_no>`."""

    def __init__(
        self, line_no: int, text: str, reason: str | None = None, slug: str | None = None
    ) -> None:
        where = f"ideas/{slug}/plan.md" if slug else "plan.md"
        self.reason = reason or f"not a step, expected {_STEP_GRAMMAR}"
        super().__init__(f"{where}:{line_no}: {self.reason}: {text.strip()}")
        self.line_no = line_no
        self.text = text
        self.slug = slug


class StepNotFound(LedgerError):
    """The plan has no step with this id."""

    def __init__(self, slug: str, step_id: str, known: list[str]) -> None:
        super().__init__(
            f"no step {step_id!r} in ideas/{slug}/plan.md (steps: {', '.join(known) or 'none'})"
        )
        self.slug = slug
        self.step_id = step_id


@dataclass
class Idea:
    """The contents of an idea.yml (docs/ledger.md describes each key).

    `totals` is recomputed from costs.jsonl by `save_idea`. `extra` holds the keys of the file that
    are not fields, which `save_idea` writes back after the others.
    """

    slug: str
    title: str
    status: str = "NEW"
    # Looked up at call time, so a test can pin the date by patching `_today`.
    created: str = field(default_factory=lambda: _today())
    updated: str = field(default_factory=lambda: _today())
    geo: list[str] = field(default_factory=list)
    language: str = "en"
    buyer: str = ""
    signer: str = ""
    value_per_customer_eur: float = 0.0
    cap_eur: float = DEFAULT_CAP_EUR
    founder_hour_rate_eur: float = DEFAULT_RATE_EUR
    repo: str | None = None
    local_path: str | None = None
    domain: str | None = None
    current_experiment: int | None = None
    provisional: bool = False
    notes: str = ""
    totals: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)


@dataclass
class Step:
    """One line of plan.md. `done_at` is the date of the line, whatever the status."""

    id: str
    name: str
    command: str
    timebox: str
    status: str
    done_at: str | None
    section: str  # "steps" for `## Steps`, else the name in `## Workstream: <name>`


# --- finding ideas -----------------------------------------------------------------------------


def require_dir(slug: str) -> Path:
    """The folder `ideas/<slug>/`. Raises IdeaNotFound unless `slug` is a slug and it exists."""
    if not (isinstance(slug, str) and _SLUG_RE.fullmatch(slug)):
        raise IdeaNotFound(slug)
    folder = paths.idea_dir(slug)
    if not folder.is_dir():
        raise IdeaNotFound(slug)
    return folder


def idea_slugs(include_fixture: bool = False) -> list[str]:
    """The slugs of the folders under ideas/ that hold an idea.yml, sorted.

    The fixture idea is left out unless `include_fixture`. A board that must survive one broken
    idea.yml iterates these and calls `load_idea` on each; `list_ideas` stops at the first.
    """
    found = sorted(p.parent.name for p in paths.ideas().glob("*/idea.yml"))
    return [s for s in found if _SLUG_RE.fullmatch(s) and (include_fixture or s != FIXTURE_SLUG)]


def list_ideas(include_fixture: bool = False) -> list[Idea]:
    """Every idea sorted by slug, the fixture only on request. Raises on a broken idea.yml."""
    return [load_idea(slug) for slug in idea_slugs(include_fixture)]


# --- idea.yml ----------------------------------------------------------------------------------


def load_idea(slug: str) -> Idea:
    """The idea in `ideas/<slug>/idea.yml`.

    Raises IdeaNotFound for a slug with no idea.yml and IdeaFileError for a file that cannot be
    read: broken YAML, not a mapping, an unknown status, a value of the wrong kind, a `slug` key
    that is not the folder's name. Missing keys take the field's default; keys that are not fields
    go to `extra`. `totals` is what the file says, as of the last `save_idea`.
    """
    path = require_dir(slug) / "idea.yml"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise IdeaNotFound(slug) from None
    return _parse_idea(slug, text)


def save_idea(idea: Idea) -> None:
    """Write `idea` to its idea.yml.

    `updated` becomes today and `totals` is recomputed from costs.jsonl (on `idea` too). The keys
    follow the order of the fields, `extra` last. The file is rewritten from data, so comments in
    it are not kept, and replaced in one step: a crash leaves the old file or the new one. Raises
    ValueError for a status that is not one of STATUSES, IdeaNotFound when the idea has no folder
    and IdeaFileError when a value would not load back (a `cap_eur` of nan or of text): what is
    written is read by the same reader as `load_idea` first, so one bad value never makes the idea
    unreadable, and the file is then left as it was.
    """
    _check_status(idea.status)
    folder = require_dir(idea.slug)
    idea.updated = _today()
    idea.totals = _totals(idea.slug)
    _write_text(folder / "idea.yml", _dump_checked(idea))


def create_idea(slug: str, title: str, **fields: Any) -> Idea:
    """Create `ideas/<slug>/` for a new idea and return it, as saved.

    `fields` are any other Idea fields (`geo`, `cap_eur`, `created`...). The folder gets idea.yml,
    the default plan.md, intake.md with its header, learnings.md with its header, an empty
    costs.jsonl and research/. A file already in the folder is kept, not overwritten; idea.yml is
    written last, so an interrupted create leaves a folder that is not yet an idea. Raises
    ValueError for a slug that is not a slug or a bad status, IdeaFileError for a value that would
    not load back (as `save_idea` does), both before creating anything, TypeError for an unknown
    field and IdeaExists when the idea already has an idea.yml.
    """
    if not (isinstance(slug, str) and _SLUG_RE.fullmatch(slug)):
        raise ValueError(
            f"slug {slug!r} must be lowercase letters, digits, - and _, not starting with -"
        )
    idea = Idea(slug=slug, title=title, **fields)
    _check_status(idea.status)
    _dump_checked(idea)
    folder = paths.idea_dir(slug)
    if (folder / "idea.yml").exists():
        raise IdeaExists(slug)
    (folder / "research").mkdir(parents=True, exist_ok=True)
    for name, text in (
        ("plan.md", DEFAULT_PLAN),
        ("intake.md", f"# Intake — {' '.join(title.split())}\n\n"),
        ("learnings.md", _learnings_header(slug)),
        ("costs.jsonl", ""),
        ("research/.gitkeep", ""),
    ):
        _write_new(folder / name, text)
    save_idea(idea)
    return idea


# --- learnings.md ------------------------------------------------------------------------------


def append_learning(slug: str, command: str, text: str) -> None:
    """Append `- YYYY-MM-DD <command>: <text>` to the idea's learnings.md.

    The entry is one line (the text's whitespace is collapsed). The file is created with its
    header when it is missing.
    """
    path = require_dir(slug) / "learnings.md"
    if not path.exists():
        _write_new(path, _learnings_header(slug))
    append_line(path, f"- {_today()} {command}: {' '.join(text.split())}")


def append_line(path: Path, line: str) -> None:
    """Append `line` and a newline to the text file `path`, creating it when need be.

    A last line left without its newline (by a hand edit) is ended first, so two entries never
    share a line. The new line goes out in a single write.
    """
    with path.open("ab+") as f:
        size = f.seek(0, os.SEEK_END)
        lead = b""
        if size:
            f.seek(size - 1)
            lead = b"" if f.read(1) == b"\n" else b"\n"
        f.write(lead + line.encode("utf-8") + b"\n")


# --- plan.md -----------------------------------------------------------------------------------


def load_plan(slug: str) -> list[Step]:
    """The steps of the idea's plan.md, in file order.

    One step per line, `- [<m>] <id>. <name> — `<command>` — <timebox>[ — YYYY-MM-DD]`, under a
    `## Steps` or `## Workstream: <name>` heading; any other line is ignored unless it starts with
    `- [`, which must be a step. Raises PlanParseError (with the line number) for a line that
    breaks the grammar, a step outside those sections or a repeated id.
    """
    path = _plan_path(slug)
    return [step for _, step in _parse_plan(slug, _read_plan(slug, path))]


def next_step(slug: str) -> Step | None:
    """The step in progress (the first `doing`), else the first `todo`, in file order.

    None when every step is done, skipped or void.
    """
    steps = load_plan(slug)
    for wanted in ("doing", "todo"):
        for step in steps:
            if step.status == wanted:
                return step
    return None


def mark_step(slug: str, step_id: str, status: str, when: str | None = None) -> Step:
    """Set the status of step `step_id` and return the step as rewritten.

    Only that line of plan.md changes. Its date is `when` (YYYY-MM-DD) when given. Without it,
    `done`, `skipped` and `void` carry today's date (the step's own, if it already had that
    status) and `todo` and `doing` carry none. Raises StepNotFound for an id the plan does not
    have and ValueError for a status that is not one of STEP_STATUSES or a date that is not
    YYYY-MM-DD; the file is then untouched.
    """
    if status not in MARKERS:
        raise ValueError(f"status {status!r} is not one of {', '.join(STEP_STATUSES)}")
    if when is not None and not _valid_day(when):
        raise ValueError(f"when must be a date written YYYY-MM-DD, got {when!r}")
    path = _plan_path(slug)
    text = _read_plan(slug, path)
    parsed = _parse_plan(slug, text)
    found = next(((n, s) for n, s in parsed if s.id == step_id), None)
    if found is None:
        raise StepNotFound(slug, step_id, [s.id for _, s in parsed])
    line_no, step = found
    if when is None and status in _DATED:
        when = step.done_at if step.status == status and step.done_at else _today()
    marked = dataclasses.replace(step, status=status, done_at=when)
    lines = text.split("\n")
    carriage_return = "\r" if lines[line_no - 1].endswith("\r") else ""
    lines[line_no - 1] = _format_step(marked) + carriage_return
    _write_text(path, "\n".join(lines))
    return marked


def _plan_path(slug: str) -> Path:
    return require_dir(slug) / "plan.md"


def _read_plan(slug: str, path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", newline="")  # newline="": keep CRLF as it is
    except FileNotFoundError:
        raise LedgerError(f"ideas/{slug}/plan.md not found") from None


def _parse_plan(slug: str, text: str) -> list[tuple[int, Step]]:
    """The steps of a plan.md text with their 1-based line numbers."""
    steps: list[tuple[int, Step]] = []
    seen: set[str] = set()
    section: str | None = None
    for line_no, raw in enumerate(text.split("\n"), start=1):
        line = raw.rstrip()
        heading = _HEADING_RE.fullmatch(line)
        if heading:
            section = _section_of(heading["title"])
            continue
        if not line.startswith("- ["):
            continue
        match = _STEP_RE.fullmatch(line)
        if match is None:
            raise PlanParseError(line_no, raw.rstrip("\r"), slug=slug)
        problem = None
        if section is None:
            problem = 'step outside a "## Steps" or "## Workstream: <name>" section'
        elif match["id"] in seen:
            problem = f"duplicate step id {match['id']!r}"
        elif match["done_at"] and not _valid_day(match["done_at"]):
            problem = f"{match['done_at']} is not a date"
        if problem:
            raise PlanParseError(line_no, raw.rstrip("\r"), reason=problem, slug=slug)
        seen.add(match["id"])
        step = Step(
            id=match["id"],
            name=match["name"].strip(),
            command=match["command"],
            timebox=match["timebox"].strip(),
            status=_STATUS_OF_MARKER[match["marker"]],
            done_at=match["done_at"],
            section=section,
        )
        steps.append((line_no, step))
    return steps


def _section_of(title: str) -> str | None:
    """The section a `## <title>` heading opens: "steps", a workstream's name, or None."""
    if title == "Steps":
        return "steps"
    if title.startswith("Workstream:") and title[len("Workstream:") :].strip():
        return title[len("Workstream:") :].strip()
    return None


def _format_step(step: Step) -> str:
    line = f"- [{MARKERS[step.status]}] {step.id}. {step.name} — `{step.command}` — {step.timebox}"
    return f"{line} — {step.done_at}" if step.done_at else line


def _valid_day(text: str) -> bool:
    if not _DAY_RE.fullmatch(text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


# --- idea.yml: reading and writing -------------------------------------------------------------


def _parse_idea(slug: str, text: str) -> Idea:
    """The idea in the text of an idea.yml: the reader of `load_idea`, and of `_dump_checked`."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise IdeaFileError(slug, _yaml_problem(exc)) from None
    if not isinstance(data, dict):
        raise IdeaFileError(slug, "does not hold a YAML mapping")
    return _idea_from_mapping(slug, data)


def _idea_from_mapping(slug: str, data: dict) -> Idea:
    if "slug" in data and data["slug"] != slug:
        raise IdeaFileError(slug, f"slug {data['slug']!r} is not the folder's name {slug!r}")
    values: dict[str, Any] = {}
    for name, convert in _CONVERTERS.items():
        if data.get(name) is not None:
            values[name] = convert(slug, name, data[name])
    totals = data.get("totals")
    return Idea(
        slug=slug,
        title=values.pop("title", "") or slug,
        totals=dict(totals) if isinstance(totals, dict) else {},
        extra={k: v for k, v in data.items() if k not in _KNOWN_KEYS},
        **values,
    )


def _text(slug: str, name: str, value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise IdeaFileError(slug, f"{name} must be text, got {value!r}")
    return str(value)


def _optional_text(slug: str, name: str, value: Any) -> str | None:
    return _text(slug, name, value) or None


def _day(slug: str, name: str, value: Any) -> str:
    # YAML reads an unquoted 2026-10-14 as a date, and 2026-10-14 09:30:00 as a datetime.
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return _text(slug, name, value)


def _status(slug: str, name: str, value: Any) -> str:
    if value not in STATUSES:
        raise IdeaFileError(slug, f"status {value!r} is not one of {', '.join(STATUSES)}")
    return value


def _geo(slug: str, name: str, value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list) and all(isinstance(code, str) for code in value):
        return list(value)
    raise IdeaFileError(slug, f"geo must be a list of country codes (quote NO), got {value!r}")


def _number(slug: str, name: str, value: Any) -> float:
    number = None
    if isinstance(value, str | int | float) and not isinstance(value, bool):
        with contextlib.suppress(ValueError):
            number = float(value)
    if number is None or not math.isfinite(number):
        raise IdeaFileError(slug, f"{name} must be a number, got {value!r}")
    return number


def _optional_int(slug: str, name: str, value: Any) -> int | None:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().isdecimal():
        return int(value)
    raise IdeaFileError(slug, f"{name} must be a whole number, got {value!r}")


def _flag(slug: str, name: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise IdeaFileError(slug, f"{name} must be true or false, got {value!r}")
    return value


# The Idea fields read from idea.yml, each with its converter; `slug` and `totals` are special.
_CONVERTERS: dict[str, Callable[[str, str, Any], Any]] = {
    "title": _text,
    "status": _status,
    "created": _day,
    "updated": _day,
    "geo": _geo,
    "language": _text,
    "buyer": _text,
    "signer": _text,
    "value_per_customer_eur": _number,
    "cap_eur": _number,
    "founder_hour_rate_eur": _number,
    "repo": _optional_text,
    "local_path": _optional_text,
    "domain": _optional_text,
    "current_experiment": _optional_int,
    "provisional": _flag,
    "notes": _text,
}
_KNOWN_KEYS = {"slug", "totals", *_CONVERTERS}


def _yaml_problem(exc: yaml.YAMLError) -> str:
    mark = getattr(exc, "problem_mark", None)
    where = f" at line {mark.line + 1}" if mark is not None else ""
    problem = " ".join(str(getattr(exc, "problem", None) or "syntax error").split())
    return f"not valid YAML{where}: {problem}"


def _dump(idea: Idea) -> str:
    data = {f.name: getattr(idea, f.name) for f in dataclasses.fields(idea) if f.name != "extra"}
    for key, value in idea.extra.items():
        data.setdefault(key, value)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def _dump_checked(idea: Idea) -> str:
    """The idea.yml text for `idea`, once the reader of `load_idea` has accepted it."""
    text = _dump(idea)
    try:
        _parse_idea(idea.slug, text)
    except IdeaFileError as exc:
        raise IdeaFileError(
            idea.slug, f"not written, it would not load back: {exc.reason}"
        ) from None
    return text


def _check_status(status: str) -> None:
    if status not in STATUSES:
        raise ValueError(f"status {status!r} is not one of {', '.join(STATUSES)}")


def _totals(slug: str) -> dict:
    # costs imports this module at load time, so this module imports costs only when it needs it.
    from factory import costs

    return costs.summary(slug)


def _learnings_header(slug: str) -> str:
    return f"# Learnings — {slug}\n\n"


# --- files -------------------------------------------------------------------------------------


def _today() -> str:
    return date.today().isoformat()


def _write_text(path: Path, text: str) -> None:
    """Replace `path` with `text` in one step: a crash leaves the old file or the new one."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _write_new(path: Path, text: str) -> None:
    """Write `text` to `path` unless a file is already there."""
    with contextlib.suppress(FileExistsError), path.open("x", encoding="utf-8") as f:
        f.write(text)
