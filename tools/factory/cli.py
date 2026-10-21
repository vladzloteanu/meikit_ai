"""The `factory` command line: one entry point, one sub-command per tool.

Every tool is a module under `factory.tools`, listed by name in TOOL_MODULES. A tool module
exposes two functions:

    add_parser(sub)  register its sub-command(s) on the argparse sub-parsers action `sub`
    run(args)        do the work for the parsed command line and return the exit code
"""

import argparse
import importlib
import sys

from factory import __version__

# Module names under `factory.tools`, one per tool. Add a new tool's module name here.
TOOL_MODULES: list[str] = [
    "secrets_import_nb",
    "board",
    "idea",
    "plan",
    "costs_cmd",
    "serp_ads",
    "keyword_volume",
    "ad_library",
    "reddit_mentions",
    "hn_mentions",
    "pricing_scan",
    "domain_check",
    "nb",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="factory",
        description="The ideas factory: one research tool per sub-command.",
    )
    parser.add_argument("--version", action="version", version=f"factory {__version__}")
    sub = parser.add_subparsers(dest="tool", metavar="<tool>", title="tools", required=True)
    for name in TOOL_MODULES:
        module = importlib.import_module(f"factory.tools.{name}")
        known = set(sub.choices)
        module.add_parser(sub)
        # Whatever sub-commands the module just registered are run by its `run`.
        for command in set(sub.choices) - known:
            sub.choices[command].set_defaults(_run=module.run)
    return parser


def _exit_code(code: object) -> int:
    """The exit status carried by a SystemExit: None is success, a message is failure."""
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    print(code, file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Run the CLI on `argv` (default: the process arguments) and return the exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:  # argparse exits for --help/--version (0) and usage errors (2)
        return _exit_code(exit_.code)
    return args._run(args)
