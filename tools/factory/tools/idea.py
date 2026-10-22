"""`factory idea`: create an idea, and change the fields of its idea.yml.

    factory idea new <slug> --title T [--geo FR,US] [--language en] [--buyer ..] [--signer ..]
                     [--value-eur N|unknown] [--cap-eur N] [--rate-eur N] [--provisional]
                     [--notes ..]
    factory idea set <slug> key=value [key=value ...]

`new` is `ledger.create_idea` (the folder, the default plan.md, the empty cost ledger) and refuses
a slug that already has an idea. `set` changes the fields in SETTABLE, each value read as its
field's type, and saves through `ledger.save_idea`: the keys and values are all checked before
anything is written, so a call that has one bad pair changes nothing.
"""

import argparse
import math
import sys
from collections.abc import Callable
from typing import Any

from factory import commands, ledger

COMMAND = "idea"


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="create an idea, or change the fields of its idea.yml",
        description="Create an idea (ideas/<slug>/ with its plan and cost ledger), or change the "
        "fields of an existing idea.yml.",
    )
    actions = commands.add_actions(parser)

    new = actions.add_parser(
        "new",
        help="create ideas/<slug>/ for a new idea",
        description="Create ideas/<slug>/: idea.yml (status NEW), the default plan.md, intake.md, "
        "learnings.md, an empty costs.jsonl and research/. Refuses a slug that is already an idea.",
    )
    new.add_argument("slug", help="the folder's name: lowercase letters, digits, - and _")
    new.add_argument("--title", required=True, help="the working title")
    new.add_argument(
        "--geo", type=_countries, metavar="FR,US", help="country codes, comma-separated"
    )
    new.add_argument("--language", help="language of the pages and ads (default: en)")
    new.add_argument("--buyer", help="who pays")
    new.add_argument("--signer", help="who signs the purchase")
    new.add_argument(
        "--value-eur",
        type=optional_number,
        metavar="N|unknown",
        help="first-year gross margin per customer, or unknown (the default)",
    )
    new.add_argument(
        "--cap-eur",
        type=number,
        metavar="N",
        help=f"cash cap in EUR (default: {ledger.DEFAULT_CAP_EUR:.0f})",
    )
    new.add_argument(
        "--rate-eur",
        type=number,
        metavar="N",
        help=f"founder hour in EUR (default: {ledger.DEFAULT_RATE_EUR:.0f})",
    )
    new.add_argument(
        "--provisional",
        action="store_true",
        help="the intake values are placeholders still to confirm",
    )
    new.add_argument("--notes", help="free text")
    new.set_defaults(handler=_new)

    set_ = actions.add_parser(
        "set",
        help="change fields of idea.yml",
        description="Change fields of an idea's idea.yml, all or nothing. Settable: "
        + ", ".join(SETTABLE)
        + ". geo is comma-separated, provisional is true or false, value_per_customer_eur is "
        "a number or unknown, an empty value clears repo, local_path, domain, "
        "current_experiment and value_per_customer_eur.",
    )
    set_.add_argument("slug", help=commands.SLUG_HELP)
    set_.add_argument("assignments", nargs="+", metavar="key=value")
    set_.set_defaults(handler=_set)


def run(args: argparse.Namespace) -> int:
    return commands.run(args)


# --- values ------------------------------------------------------------------------------------
# Each reads the text of a `key=value` and returns the field's value, or raises ValueError.


def number(text: str) -> float:
    """A finite number: what a cap, a rate or a value is. Also the argparse type of those flags."""
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"{text!r} is not a finite number") from None
    if not math.isfinite(value):  # float() reads nan and inf, which no file can hold
        raise ValueError(f"{text!r} is not a finite number")
    return value


def optional_number(text: str) -> float | None:
    """A finite number, or None for an empty text or the word unknown: the value per customer
    before anything supports it. Also the argparse type of --value-eur."""
    if text.strip().lower() in ("", "unknown"):
        return None
    try:
        return number(text)
    except ValueError:
        raise ValueError(f"{text!r} is not a finite number or unknown") from None


def _text(text: str) -> str:
    return text


def _optional_text(text: str) -> str | None:
    return text or None


def _countries(text: str) -> list[str]:
    return [code.strip() for code in text.split(",") if code.strip()]


def _status(text: str) -> str:
    if text not in ledger.STATUSES:
        raise ValueError(f"{text!r} is not one of {', '.join(ledger.STATUSES)}")
    return text


def _optional_int(text: str) -> int | None:
    if not text.strip():
        return None
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{text!r} is not a whole number") from None


def _flag(text: str) -> bool:
    word = text.strip().lower()
    if word not in ("true", "false"):
        raise ValueError(f"{text!r} is not true or false")
    return word == "true"


# The Idea fields `set` can change. `slug` is the folder's name, `created` never changes,
# `updated` and `totals` are written by save_idea, `extra` is the keys that are not fields.
SETTABLE: dict[str, Callable[[str], Any]] = {
    "title": _text,
    "status": _status,
    "geo": _countries,
    "language": _text,
    "buyer": _text,
    "signer": _text,
    "value_per_customer_eur": optional_number,
    "value_basis": _text,
    "cap_eur": number,
    "founder_hour_rate_eur": number,
    "repo": _optional_text,
    "local_path": _optional_text,
    "domain": _optional_text,
    "current_experiment": _optional_int,
    "provisional": _flag,
    "notes": _text,
}


# --- actions -----------------------------------------------------------------------------------


def _new(args: argparse.Namespace) -> int:
    given = {
        "geo": args.geo,
        "language": args.language,
        "buyer": args.buyer,
        "signer": args.signer,
        "value_per_customer_eur": args.value_eur,
        "cap_eur": args.cap_eur,
        "founder_hour_rate_eur": args.rate_eur,
        "provisional": True if args.provisional else None,
        "notes": args.notes,
    }
    fields = {name: value for name, value in given.items() if value is not None}
    idea = ledger.create_idea(args.slug, args.title, **fields)
    print(
        f"created ideas/{idea.slug}/ ({idea.status}, cap {idea.cap_eur:.0f} EUR)", file=sys.stderr
    )
    return 0


def _set(args: argparse.Namespace) -> int:
    changes = dict(_assignment(text) for text in args.assignments)
    idea = ledger.load_idea(args.slug)
    for name, value in changes.items():
        setattr(idea, name, value)
    ledger.save_idea(idea)
    print(f"{args.slug}: {', '.join(args.assignments)}", file=sys.stderr)
    return 0


def _assignment(text: str) -> tuple[str, Any]:
    """The field and value of one `key=value`; ValueError for a pair that cannot be applied."""
    key, equals, value = text.partition("=")
    if not equals:
        raise ValueError(f"{text!r} is not key=value")
    if key not in SETTABLE:
        raise ValueError(f"{key!r} is not a settable field (settable: {', '.join(SETTABLE)})")
    try:
        return key, SETTABLE[key](value)
    except ValueError as exc:
        raise ValueError(f"{key}: {exc}") from None
