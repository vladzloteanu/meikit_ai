"""`factory secrets-import-nb`: copy the provider keys NeuralBox holds into the factory secrets.

NeuralBox's config is read by running `make -C <nb-root> secrets-cat`, its output captured and
parsed in memory, and NB_API_KEY comes from `<nb-root>/.env`; nothing is ever written inside
<nb-root>. Each value lands at its factory dotpath (MAPPING, ENV_MAPPING) next to the sibling keys
`source: neural_box` and `imported_at: <date>`, and the factory config is re-encrypted with
bin/secrets (spec section 11). Only the dotpaths written are printed, never a value; `--dry-run`
prints the dotpaths and changes nothing.
"""

import argparse
import copy
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from factory import paths, secrets

COMMAND = "secrets-import-nb"
DEFAULT_NB_ROOT = "~/wrk/dolead/neural_box"
SOURCE = "neural_box"

# NeuralBox `make secrets-cat` dotpath -> factory dotpath.
MAPPING = {
    "tools.SearchAPI.api_key": "providers.searchapi.api_key",
    "tools.SEranking.api_token": "providers.seranking.api_token",
    "tools.Apify.api_key": "providers.apify.api_key",
    "tools.Firecrawl.api_key": "providers.firecrawl.api_key",
    "tools.Tavily.api_key": "providers.tavily.api_key",
    "tools.ScreenshotAPI.token": "providers.screenshotapi.token",
    "tools.OpenAI.api_key": "providers.openai.api_key",
    "tools.Legnext.api_key": "providers.legnext.api_key",
    "tools.FalAI.api_key": "providers.fal.api_key",
    "tools.ElevenLabs.api_key": "providers.elevenlabs.api_key",
    "tools.Submagic.api_key": "providers.submagic.api_key",
    "tools.Gemini.vertex_ai": "providers.gemini.vertex_ai",  # the whole mapping
}
# NeuralBox `.env` variable -> factory dotpath.
ENV_MAPPING = {"NB_API_KEY": "nb.api_key"}


class ImportFailed(Exception):
    """The import cannot go on. The message is one line and never quotes a value."""


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="copy NeuralBox's provider keys into the factory secrets",
        description="Copy the provider keys NeuralBox holds into secrets/config.yml.enc, each "
        "next to `source: neural_box`. Prints the dotpaths written, never a value.",
    )
    parser.add_argument(
        "--nb-root",
        default=DEFAULT_NB_ROOT,
        metavar="DIR",
        help="the NeuralBox checkout, only read (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print the dotpaths it would write, change nothing"
    )


def run(args: argparse.Namespace) -> int:
    nb_root = Path(args.nb_root).expanduser()
    root = paths.root()
    try:
        config = copy.deepcopy(secrets.load(root, refresh=True))
        values, missing = collect(nb_root)
        for name in missing:
            print(f"{COMMAND}: skipped {name}: not set in NeuralBox", file=sys.stderr)
        if not values:
            raise ImportFailed(f"nothing to import from {nb_root}")
        if not args.dry_run:
            secrets.save(apply(config, values, date.today()), root)
            _verify(values, root)
    except (secrets.SecretsError, ImportFailed) as exc:
        print(f"{COMMAND}: {exc}", file=sys.stderr)
        return 1
    print("\n".join(values))
    outcome = (
        "dry run, nothing written" if args.dry_run else f"written to {root / secrets.ENCRYPTED}"
    )
    print(f"{COMMAND}: {len(values)} values from NeuralBox, {outcome}", file=sys.stderr)
    return 0


def collect(nb_root: Path) -> tuple[dict[str, Any], list[str]]:
    """{factory dotpath: value} for each mapped value NeuralBox has, and the names it lacks."""
    if not nb_root.is_dir():
        raise ImportFailed(f"no NeuralBox checkout at {nb_root} (pass --nb-root)")
    nb_config = read_nb_config(nb_root)
    values: dict[str, Any] = {}
    missing: list[str] = []
    for source, dotpath in MAPPING.items():
        value = _dig(nb_config, source)
        if _is_blank(value):
            missing.append(source)
        else:
            values[dotpath] = value
    for name, dotpath in ENV_MAPPING.items():
        value = env_value(nb_root / ".env", name)
        if _is_blank(value):
            missing.append(f".env {name}")
        else:
            values[dotpath] = value
    return values, missing


def read_nb_config(nb_root: Path) -> dict:
    """NeuralBox's decrypted config: `make -C <nb_root> secrets-cat`, parsed in memory."""
    shown = f"`make -C {nb_root} secrets-cat`"
    # -s and --no-print-directory keep make's own lines out of the YAML on stdout.
    command = ["make", "-s", "--no-print-directory", "-C", str(nb_root), "secrets-cat"]
    try:
        proc = subprocess.run(command, capture_output=True, stdin=subprocess.DEVNULL)
    except OSError as exc:
        raise ImportFailed(f"cannot run make: {exc.strerror}") from None
    if proc.returncode != 0:
        # stdout may hold part of the config, so only stderr is quoted.
        raise ImportFailed(f"{shown} failed (exit {proc.returncode}): {_tail(proc.stderr)}")
    try:
        documents = [doc for doc in yaml.safe_load_all(proc.stdout) if doc is not None]
    except yaml.YAMLError:
        # The parser's message quotes the offending line, which may hold a value.
        raise ImportFailed(f"{shown} did not print valid YAML") from None
    if len(documents) > 1:
        raise ImportFailed(
            f"{shown} printed {len(documents)} YAML documents (NEURAL_BOX_ENV or ENV set?); "
            "unset them to read the local config"
        )
    if not documents or not isinstance(documents[0], dict):
        raise ImportFailed(f"{shown} did not print a YAML mapping")
    return documents[0]


def env_value(path: Path, name: str) -> str | None:
    """The value given to `name` in a dotenv file (the last assignment wins), or None."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    value = None
    for line in lines:
        line = line.strip()
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        key, sep, raw = line.partition("=")
        if not sep or key.strip() != name:
            continue
        raw = raw.strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
            value = raw[1:-1]
        else:
            value = raw.split(" #", 1)[0].rstrip()
    return value


def apply(config: dict, values: dict[str, Any], today: date) -> dict:
    """`config` with each value at its dotpath, next to `source: neural_box`, `imported_at: today`.

    Updates `config` in place and returns it; sibling keys already there (nb.url) are kept.
    """
    for dotpath, value in values.items():
        *parents, leaf = dotpath.split(".")
        node = config
        for key in parents:
            if not isinstance(node.get(key), dict):
                node[key] = {}
            node = node[key]
        node[leaf] = value
        node["source"] = SOURCE
        node["imported_at"] = today
    return config


def _verify(values: dict[str, Any], root: Path) -> None:
    """Every value reads back from the re-encrypted file (`save` reloaded it)."""
    for dotpath, value in values.items():
        if secrets.get(dotpath, None, root=root) != value:
            raise ImportFailed(
                f"{dotpath} did not read back after encryption; "
                f"restore the previous file with `git checkout {secrets.ENCRYPTED}`"
            )


def _dig(node: Any, dotpath: str) -> Any:
    for part in dotpath.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, (str, dict, list)) and not value)


def _tail(stderr: bytes) -> str:
    lines = [
        line.strip() for line in stderr.decode("utf-8", "replace").splitlines() if line.strip()
    ]
    return " | ".join(lines[-3:])[:300] or "no error output"
