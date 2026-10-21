"""`factory plan`: read an idea's plan.md and move it along.

    factory plan show <slug>                 the steps as a table
    factory plan next <slug>                 the step to do next, on one line
    factory plan mark <slug> <id> <status>   set the status of a step

The next step is the one in progress, else the first not started (`ledger.next_step`). `next`
prints `<id>. <name> — <command> — <timebox>`, or `done: ...` when nothing is left. `mark` rewrites
that step's line of plan.md and nothing else; `done`, `skipped` and `void` also put today's date on
it. `status` is one of `ledger.STEP_STATUSES`.
"""

import argparse
import sys

from factory import commands, ledger, tables

COMMAND = "plan"
COLUMNS = ["id", "status", "name", "command", "timebox", "date"]
NOTHING_LEFT = "done: every step is done, skipped or void"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="show an idea's plan, its next step, or mark a step",
        description="Read an idea's plan.md and move it along.",
    )
    actions = commands.add_actions(parser)

    show = actions.add_parser("show", help="the steps of the plan with their status")
    show.add_argument("slug", help=commands.SLUG_HELP)
    show.set_defaults(handler=_show)

    next_ = actions.add_parser(
        "next",
        help="the step to do next: <id>. <name> — <command> — <timebox>",
        description="The step in progress, else the first not started, on one line: "
        "<id>. <name> — <command> — <timebox>. `done: ...` when nothing is left.",
    )
    next_.add_argument("slug", help=commands.SLUG_HELP)
    next_.set_defaults(handler=_next)

    mark = actions.add_parser(
        "mark",
        help="set the status of a step",
        description="Set the status of one step; only that line of plan.md changes.",
    )
    mark.add_argument("slug", help=commands.SLUG_HELP)
    mark.add_argument("step", metavar="id", help="the step's id, e.g. 2 or lp-improve.1")
    mark.add_argument("status", choices=ledger.STEP_STATUSES)
    mark.set_defaults(handler=_mark)


def run(args: argparse.Namespace) -> int:
    return commands.run(args)


def _show(args: argparse.Namespace) -> int:
    rows = [
        {
            "id": step.id,
            "status": step.status,
            "name": step.name,
            "command": step.command,
            "timebox": step.timebox,
            "date": step.done_at,
        }
        for step in ledger.load_plan(args.slug)
    ]
    print(tables.render(rows, COLUMNS))
    return 0


def _next(args: argparse.Namespace) -> int:
    step = ledger.next_step(args.slug)
    if step is None:
        print(NOTHING_LEFT)
    else:
        print(f"{step.id}. {step.name} — {step.command} — {step.timebox}")
    return 0


def _mark(args: argparse.Namespace) -> int:
    step = ledger.mark_step(args.slug, args.step, args.status)
    when = f" {step.done_at}" if step.done_at else ""
    print(f"{args.slug}: {step.id}. {step.name}: {step.status}{when}", file=sys.stderr)
    return 0
