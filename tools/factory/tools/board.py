"""`factory board`: one row per idea, where it stands and what to run next.

Columns: `slug | status | step | exp | spend/cap | updated | next`. `step` is the id and name of the
idea's next plan step (`done` when none is left), `next` the command that runs it, `exp` the
current experiment, `spend/cap` the cash spent (founder time left out) over the cash cap, in whole
EUR, `updated` the date of the last change to idea.yml. `--json` prints the same as a list of
dicts with numbers as numbers; what a row cannot say is null there and `-` or `?` in the table.

The board does not stop at a broken idea: an idea.yml, plan.md or costs.jsonl that the ledger
refuses (a LedgerError) shows in its row, not as a traceback. An idea.yml that cannot be read shows
`idea.yml invalid` in `status` (its cap, experiment and date unknown), a plan.md that cannot be
read `plan.md:<line> invalid` in `step`, a costs.jsonl that cannot be read `?` for the spend. Each
is judged on its own, so the rest of the row is still filled in.
"""

import argparse
import json

from factory import costs, ledger, tables

COMMAND = "board"
COLUMNS = ["slug", "status", "step", "exp", "spend/cap", "updated", "next"]
NO_IDEAS = "no ideas yet: factory idea new <slug> --title T"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="one row per idea: status, next step, spend against cap",
        description="One row per idea: where it stands, the next step of its plan and the command "
        "that runs it, the cash spent against its cap.",
    )
    parser.add_argument("--json", action="store_true", help="print a JSON list instead of a table")
    parser.add_argument(
        "--all", action="store_true", help=f"include the {ledger.FIXTURE_SLUG} dry-run idea"
    )


def run(args: argparse.Namespace) -> int:
    rows = [row_of(slug) for slug in ledger.idea_slugs(include_fixture=args.all)]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    print(tables.render([_cells(row) for row in rows], COLUMNS))
    if not rows:
        print(NO_IDEAS)
    return 0


def row_of(slug: str) -> dict:
    """The board row of one idea, with the keys of the `--json` output.

    A part of the idea that the ledger refuses to read (a LedgerError) is reported in the row, as
    the module docstring says, not raised.
    """
    try:
        idea = ledger.load_idea(slug)
    except ledger.LedgerError:
        idea = None
    step, command = _next_step(slug)
    return {
        "slug": slug,
        "status": idea.status if idea else "idea.yml invalid",
        "step": step,
        "exp": idea.current_experiment if idea else None,
        "spend_eur": _spend(slug),
        "cap_eur": idea.cap_eur if idea else None,
        "updated": idea.updated if idea else None,
        "next": command,
    }


def _next_step(slug: str) -> tuple[str, str | None]:
    """The `step` and `next` cells: "<id>. <name>" and its command, or why there is none."""
    try:
        step = ledger.next_step(slug)
    except ledger.PlanParseError as exc:
        return f"plan.md:{exc.line_no} invalid", None
    except ledger.LedgerError:
        return "plan.md invalid", None
    if step is None:
        return "done", None
    return f"{step.id}. {step.name}", step.command


def _spend(slug: str) -> float | None:
    try:
        return costs.cash_total(slug)
    except ledger.LedgerError:
        return None


def _cells(row: dict) -> dict:
    """The text of a row's cells in the table: `-` for what is empty, `?` for what is unknown."""
    spend = "?" if row["spend_eur"] is None else f"{row['spend_eur']:.0f}"
    cap = "?" if row["cap_eur"] is None else f"{row['cap_eur']:.0f}"
    cells = {key: "-" if value is None else value for key, value in row.items()}
    cells["spend/cap"] = f"{spend}/{cap}"
    return cells
