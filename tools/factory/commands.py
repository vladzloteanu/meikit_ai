"""What the commands that work on the ledger (`idea`, `plan`, `costs`) share.

Each registers one command whose verbs are its actions (`idea new`, `plan mark`, `costs total`):
`add_actions` gives it the sub-parsers, each action's parser names its function with
`set_defaults(handler=...)`, and the module's `run` is `commands.run`. A handler takes the parsed
arguments and returns the exit code; what it prints as data goes to stdout, what it reports about
what it did goes to stderr, so a command's stdout is the same with or without a mutation before it.
"""

import argparse
import sys

from factory import ledger

SLUG_HELP = "the idea's slug: its folder under ideas/"


def add_actions(parser: argparse.ArgumentParser) -> argparse._SubParsersAction:
    """The sub-parsers of a command, one per action; the action is required."""
    return parser.add_subparsers(dest="action", metavar="<action>", title="actions", required=True)


def run(args: argparse.Namespace) -> int:
    """Call the handler of the action on the command line and return its exit code.

    A LedgerError (an unknown idea or step, a malformed file) or a ValueError (a bad value) raised
    on the way is one line on stderr, `<command> <action>: <message>`, and exit code 1.
    """
    try:
        return args.handler(args)
    except (ledger.LedgerError, ValueError) as exc:
        print(f"{args.tool} {args.action}: {exc}", file=sys.stderr)
        return 1
