"""`factory costs`: log a cost by hand, or total an idea's spend.

    factory costs add --idea S --kind K --amount-eur N [--provider P] [--phase ..] [--note ..]
                      [--channel ..]
    factory costs total --idea S [--json]

The module is `costs_cmd` because `factory.costs` is the cost ledger itself; the command is
`costs`. `add` appends one line to the idea's costs.jsonl (`costs.append`) and does not check the
cap: the money is already spent, and a wrong line is corrected by adding a negative one. `total`
prints the sum per kind, then the cash (every kind but founder time) and the cap; `--json` prints
`{"<kind>": EUR, ..., "cash_eur": EUR, "cap_eur": EUR}`.
"""

import argparse
import json
import sys

from factory import commands, costs, ledger

COMMAND = "costs"
CASH_NOTE = "(every kind but founder_time)"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="log a cost by hand, or total an idea's spend",
        description="The cost ledger of an idea (ideas/<slug>/costs.jsonl).",
    )
    actions = commands.add_actions(parser)

    add = actions.add_parser(
        "add",
        help="append a cost line",
        description="Append one line to the idea's costs.jsonl. The cap is not checked: the "
        "money is already spent. A wrong line is corrected by adding a negative one.",
    )
    add.add_argument("--idea", required=True, metavar="SLUG", help="the idea the cost belongs to")
    add.add_argument("--kind", required=True, choices=costs.KINDS, help="what was paid for")
    add.add_argument("--amount-eur", required=True, type=float, metavar="N", help="in EUR")
    add.add_argument("--provider", default="", help="who was paid: meta, searchapi, vlad...")
    add.add_argument("--phase", default="", help="the plan step it belongs to: triage, run...")
    add.add_argument("--note", default="", help="free text")
    add.add_argument("--channel", help="the channel, for the cost of running one")
    add.set_defaults(handler=_add)

    total = actions.add_parser(
        "total",
        help="the spend per kind, the cash and the cap",
        description="The spend of an idea per kind, then the cash (every kind but founder_time) "
        "and the cap.",
    )
    total.add_argument("--idea", required=True, metavar="SLUG", help="the idea to total")
    total.add_argument("--json", action="store_true", help="print a JSON object instead of lines")
    total.set_defaults(handler=_total)


def run(args: argparse.Namespace) -> int:
    return commands.run(args)


def _add(args: argparse.Namespace) -> int:
    line = costs.append(
        args.idea,
        args.kind,
        args.provider,
        args.amount_eur,
        phase=args.phase,
        note=args.note,
        channel=args.channel,
    )
    print(f"{args.idea}: logged {line['kind']} {line['amount_eur']} EUR", file=sys.stderr)
    return 0


def _total(args: argparse.Namespace) -> int:
    cap = ledger.load_idea(args.idea).cap_eur
    summary = costs.summary(args.idea)
    if args.json:
        data = {**summary["by_kind"], "cash_eur": summary["cash_eur"], "cap_eur": cap}
        print(json.dumps(data, indent=2))
        return 0
    amounts = [*summary["by_kind"].items(), ("cash", summary["cash_eur"]), ("cap", cap)]
    name_width = max(len(name) for name, _ in amounts)
    amount_width = max(len(f"{amount:.2f}") for _, amount in amounts)
    for name, amount in amounts:
        note = f"  {CASH_NOTE}" if name == "cash" else ""
        print(f"{name:<{name_width}}  {amount:>{amount_width}.2f} EUR{note}")
    return 0
