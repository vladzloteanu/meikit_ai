import sys
import types

from factory import cli
from factory.cli import main


def test_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "factory 0.1.0"


def test_unknown_command_exits_2():
    assert main(["no-such-tool"]) == 2


def test_help_lists_tools(capsys):
    main(["--help"])
    out = capsys.readouterr().out
    assert "factory" in out
    assert "tool" in out


def test_help_exits_0(capsys):
    assert main(["--help"]) == 0


def test_no_command_exits_2():
    assert main([]) == 2


def test_registered_tool_is_listed_and_run(monkeypatch, capsys):
    seen = {}

    def add_parser(sub):
        parser = sub.add_parser("hello", help="say hello")
        parser.add_argument("--name", default="world")

    def run(args):
        seen["name"] = args.name
        return 7

    fake = types.SimpleNamespace(add_parser=add_parser, run=run)
    monkeypatch.setitem(sys.modules, "factory.tools.hello", fake)
    monkeypatch.setattr(cli, "TOOL_MODULES", ["hello"])

    assert main(["--help"]) == 0
    assert "hello" in capsys.readouterr().out
    assert main(["hello", "--name", "vlad"]) == 7
    assert seen == {"name": "vlad"}


def test_exit_code_passes_a_system_exit_status_through():
    assert [cli._exit_code(code) for code in (None, 0, 2)] == [0, 0, 2]


def test_exit_code_prints_a_message_and_fails(capsys):
    assert cli._exit_code("boom") == 1
    assert capsys.readouterr().err == "boom\n"
