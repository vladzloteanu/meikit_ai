"""The factory's secrets: one encrypted YAML file, read by dotpath, never printed.

`secrets/config.yml.enc` holds every key the factory spends, researches or creates with (spec
section 11). `bin/secrets` (OpenSSL AES-256-CBC, PBKDF2 100k) is the only way to decrypt or
encrypt it, with the key in `secrets/master.key`. The decrypted config lives in memory only,
cached per factory root; the one plaintext file this module ever writes is the private temp file
`save` hands to `bin/secrets encrypt`, deleted as soon as that returns.

Secret values must never reach stdout, logs, exceptions, research files or git: no message raised
here quotes one, and `redact` scrubs them from text that might hold one (a provider's error body).
"""

import json
import os
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

from factory import paths

# Relative to the factory root.
SCRIPT = Path("bin/secrets")
KEY = Path("secrets/master.key")
ENCRYPTED = Path("secrets/config.yml.enc")

# `redact` leaves shorter strings alone: they are too common in ordinary text to be told apart.
REDACT_MIN_LEN = 8
REDACTED = "***"


class _Missing:
    def __repr__(self) -> str:
        return "MISSING"


MISSING: Any = _Missing()
"""`get`'s default default: raise SecretMissing instead of returning a value."""


class SecretsError(Exception):
    """A secrets operation failed. The message is one line and never quotes a secret value."""


class SecretsUnavailable(SecretsError):
    """The factory config cannot be read: no key, no .enc, a wrong key or a broken file."""


class SecretMissing(SecretsError):
    """The config has no value (absent, null or empty) at `dotpath`."""

    def __init__(self, dotpath: str) -> None:
        super().__init__(f"secret not set: {dotpath} (add it with `make secrets-edit`)")
        self.dotpath = dotpath


_cache: dict[Path, dict] = {}


def load(root: Path | None = None, *, refresh: bool = False) -> dict:
    """The decrypted factory config of `root` (default `paths.root()`), cached per root.

    The first call for a root runs `bin/secrets decrypt`; later calls return the same dict until
    `refresh=True`. Treat it as read-only: deep-copy it to change it, then `save` the copy.
    Raises SecretsUnavailable, before running anything, naming `make secrets-init` when the key is
    missing and `bin/secrets encrypt` when the .enc is; a failed decryption carries bin/secrets'
    stderr, which holds no values.
    """
    root = _root(root)
    cache_key = root.resolve()
    if not refresh and cache_key in _cache:
        return _cache[cache_key]
    key, encrypted = root / KEY, root / ENCRYPTED
    if not key.is_file():
        raise SecretsUnavailable(_no_key(key, encrypted))
    if not encrypted.is_file():
        raise SecretsUnavailable(
            f"no {encrypted}: copy secrets/config.yml.example to secrets/config.yml, fill it in, "
            "run `bin/secrets encrypt`, then delete secrets/config.yml"
        )
    proc = _bin_secrets(root, "decrypt", encrypted, key)
    if proc.returncode != 0:
        raise SecretsUnavailable(
            f"bin/secrets could not decrypt {encrypted}: {_one_line(proc.stderr)}"
        )
    try:
        config = yaml.safe_load(proc.stdout)
    except yaml.YAMLError as exc:
        # The parser's message quotes the offending line, which may hold a value: keep its number.
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark is not None else ""
        raise SecretsUnavailable(
            f"{encrypted} is not valid YAML{where}; fix it with `make secrets-edit`"
        ) from None
    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise SecretsUnavailable(
            f"{encrypted} does not hold a YAML mapping; fix it with `make secrets-edit`"
        )
    _cache[cache_key] = config
    return config


def get(dotpath: str, default: Any = MISSING, *, root: Path | None = None) -> Any:
    """The value at `dotpath` (e.g. `providers.searchapi.api_key`) in the factory config.

    A value that is absent, null, "" or an empty mapping or list is not set: `get` then returns
    `default` when one is given, else raises SecretMissing. Never print what this returns.
    """
    node: Any = load(root)
    for part in dotpath.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    if _is_blank(node):
        if default is MISSING:
            raise SecretMissing(dotpath)
        return default
    return node


def redact(text: str, *, root: Path | None = None) -> str:
    """`text` with every string of 8+ characters found in the factory config replaced by `***`.

    Each value is also caught URL-encoded and JSON-escaped, the forms in which a key usually shows
    up in an error message, and longer values go first so no fragment of one survives. Returns
    `text` unchanged when the secrets cannot be loaded.
    """
    try:
        config = load(root)
    except SecretsUnavailable:
        return text
    for needle in _needles(config):
        text = text.replace(needle, REDACTED)
    return text


def save(config: dict, root: Path | None = None) -> None:
    """Encrypt `config` as the factory config of `root` with `bin/secrets encrypt`, then reload.

    The plaintext exists only in a private temp file (mode 0600, outside the repo) while
    bin/secrets runs, and is deleted whatever happens. bin/secrets checks the key and validates the
    YAML before it overwrites the .enc; git holds the previous version.
    """
    root = _root(root)
    key, encrypted = root / KEY, root / ENCRYPTED
    if not key.is_file():
        raise SecretsUnavailable(_no_key(key, encrypted))
    fd, plaintext = tempfile.mkstemp(prefix="factory-secrets-", suffix=".yml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
        proc = _bin_secrets(root, "encrypt", plaintext, encrypted, key)
    except yaml.YAMLError:
        raise SecretsError(
            "the config holds a value YAML cannot represent; nothing was written"
        ) from None
    finally:
        os.unlink(plaintext)
    if proc.returncode != 0:
        # bin/secrets relays the YAML parser, which quotes content: keep its own `Error:` lines.
        errors = [
            line
            for line in proc.stderr.decode("utf-8", "replace").splitlines()
            if line.startswith("Error:")
        ]
        raise SecretsError(
            f"bin/secrets could not encrypt {encrypted}: {' | '.join(errors) or 'no error message'}"
        )
    load(root, refresh=True)


def _root(root: Path | None) -> Path:
    return Path(root) if root is not None else paths.root()


def _no_key(key: Path, encrypted: Path) -> str:
    if encrypted.is_file():
        return (
            f"no {key}: copy it from the machine that encrypted {encrypted.name}; "
            "`make secrets-init` would create a new key, which cannot open the existing file"
        )
    return f"no {key}: run `make secrets-init`"


def _bin_secrets(root: Path, *args: Path | str) -> subprocess.CompletedProcess[bytes]:
    script = root / SCRIPT
    try:
        return subprocess.run([script, *args], capture_output=True, stdin=subprocess.DEVNULL)
    except OSError as exc:
        raise SecretsUnavailable(f"cannot run {script}: {exc.strerror}") from None


def _one_line(stderr: bytes) -> str:
    lines = [
        line.strip() for line in stderr.decode("utf-8", "replace").splitlines() if line.strip()
    ]
    return " | ".join(lines)[:300] or "no error message"


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, (str, dict, list)) and not value)


def _needles(config: dict) -> list[str]:
    needles: set[str] = set()
    for value in _strings(config):
        if len(value) >= REDACT_MIN_LEN:
            needles.update((value, quote(value, safe=""), json.dumps(value)[1:-1]))
    return sorted(needles, key=len, reverse=True)


def _strings(node: Any) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)
