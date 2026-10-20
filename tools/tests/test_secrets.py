import copy
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path
from urllib.parse import quote

import pytest
import yaml

from factory import secrets
from factory.cli import main
from factory.secrets import SecretMissing, SecretsUnavailable

REPO_ROOT = Path(__file__).resolve().parents[2]
SEARCHAPI_KEY = "abcdefgh12345"


def make_root(tmp_path: Path, config: dict | None = None) -> Path:
    """A factory root at tmp_path: the repo's bin/secrets, a new master key, `config` encrypted."""
    (tmp_path / "secrets").mkdir(parents=True)
    (tmp_path / "bin").mkdir()
    shutil.copy2(REPO_ROOT / "bin" / "secrets", tmp_path / "bin" / "secrets")
    # bin/secrets validates YAML with <root>/.venv/bin/python: hand it this one, which has pyyaml.
    python = tmp_path / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    python.chmod(0o755)
    if config is None:
        config = {
            "providers": {"searchapi": {"api_key": SEARCHAPI_KEY}},
            "nb": {"url": "http://127.0.0.1:3076"},
        }
    script = tmp_path / "bin/secrets"
    subprocess.run(
        [script, "generate-key", tmp_path / "secrets/master.key"], check=True, capture_output=True
    )
    (tmp_path / "secrets/config.yml").write_text(yaml.safe_dump(config))
    subprocess.run(
        [
            script,
            "encrypt",
            tmp_path / "secrets/config.yml",
            tmp_path / "secrets/config.yml.enc",
            tmp_path / "secrets/master.key",
        ],
        check=True,
        capture_output=True,
    )
    (tmp_path / "secrets/config.yml").unlink()
    return tmp_path


@pytest.fixture(autouse=True)
def private_tmp(tmp_path_factory, monkeypatch) -> Path:
    """Temp files (the plaintext `secrets.save` hands to bin/secrets) land here, not in TMPDIR."""
    path = tmp_path_factory.mktemp("tmpdir")
    monkeypatch.setattr(tempfile, "tempdir", str(path))
    return path


@pytest.fixture
def no_subprocess(monkeypatch):
    def refuse(args, *rest, **kwargs):
        raise AssertionError(f"unexpected subprocess: {args!r}")

    monkeypatch.setattr(subprocess, "run", refuse)


# --- factory.secrets ---------------------------------------------------------------------------


def test_load_and_get(tmp_path):
    root = make_root(tmp_path)
    assert secrets.load(root)["nb"]["url"] == "http://127.0.0.1:3076"
    assert secrets.get("providers.searchapi.api_key", root=root) == SEARCHAPI_KEY


def test_get_missing_raises(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(SecretMissing) as e:
        secrets.get("providers.nope.key", root=root)
    assert "providers.nope.key" in str(e.value)
    assert e.value.dotpath == "providers.nope.key"


def test_load_without_key_names_setup(tmp_path, no_subprocess):
    (tmp_path / "secrets").mkdir()
    with pytest.raises(SecretsUnavailable) as e:
        secrets.load(tmp_path, refresh=True)
    assert "make secrets-init" in str(e.value)
    assert "\n" not in str(e.value)


def test_redact_hides_values(tmp_path):
    root = make_root(tmp_path)
    secrets.load(root, refresh=True)
    assert SEARCHAPI_KEY not in secrets.redact(f"key={SEARCHAPI_KEY} ok", root=root)


def test_load_without_enc_names_encrypt(tmp_path, no_subprocess):
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets/master.key").write_text("0" * 64 + "\n")
    with pytest.raises(SecretsUnavailable) as e:
        secrets.load(tmp_path, refresh=True)
    assert "bin/secrets encrypt" in str(e.value)
    assert "\n" not in str(e.value)


def test_lost_key_beside_an_enc_still_names_setup(tmp_path):
    root = make_root(tmp_path)
    (root / "secrets/master.key").unlink()
    with pytest.raises(SecretsUnavailable) as e:
        secrets.load(root, refresh=True)
    assert "make secrets-init" in str(e.value)
    assert "\n" not in str(e.value)


def test_wrong_key_is_unavailable_and_quotes_no_value(tmp_path):
    root = make_root(tmp_path)
    (root / "secrets/master.key").write_text("f" * 64 + "\n")
    with pytest.raises(SecretsUnavailable) as e:
        secrets.load(root, refresh=True)
    assert SEARCHAPI_KEY not in "".join(traceback.format_exception(e.value))


def test_invalid_yaml_quotes_no_content(tmp_path, monkeypatch):
    (tmp_path / "secrets").mkdir()
    (tmp_path / "secrets/master.key").write_text("0" * 64 + "\n")
    (tmp_path / "secrets/config.yml.enc").write_bytes(b"ciphertext")
    broken = b"providers:\n  searchapi: {api_key: TOPSECRETVALUE: [\n"
    monkeypatch.setattr(
        subprocess, "run", lambda args, *a, **k: subprocess.CompletedProcess(args, 0, broken, b"")
    )
    with pytest.raises(SecretsUnavailable) as e:
        secrets.load(tmp_path, refresh=True)
    assert "line" in str(e.value)
    assert "TOPSECRETVALUE" not in "".join(traceback.format_exception(e.value))


def test_load_decrypts_once_per_root(tmp_path, monkeypatch):
    a = make_root(tmp_path / "a")
    b = make_root(tmp_path / "b", {"nb": {"url": "http://b.test"}})
    calls = []
    real_run = subprocess.run

    def counting_run(args, *rest, **kwargs):
        calls.append(args)
        return real_run(args, *rest, **kwargs)

    monkeypatch.setattr(subprocess, "run", counting_run)
    assert secrets.load(a, refresh=True)["nb"]["url"] == "http://127.0.0.1:3076"
    assert secrets.load(b)["nb"]["url"] == "http://b.test"
    secrets.load(a)
    secrets.get("nb.url", root=b)
    secrets.redact("text", root=a)
    assert len(calls) == 2
    secrets.load(a, refresh=True)
    assert len(calls) == 3


def test_root_defaults_to_the_factory_root(root):
    make_root(root)
    assert secrets.get("providers.searchapi.api_key") == SEARCHAPI_KEY


def test_get_treats_empty_values_as_not_set(tmp_path):
    root = make_root(
        tmp_path,
        {
            "nb": {"url": "http://127.0.0.1:3076", "api_key": ""},
            "providers": {"gemini": {"vertex_ai": {}}},
            "operator": {"name": None},
        },
    )
    for dotpath in (
        "nb.api_key",
        "providers.gemini.vertex_ai",
        "operator.name",
        "nb.url.host",
        "nope",
    ):
        with pytest.raises(SecretMissing):
            secrets.get(dotpath, root=root)
        assert secrets.get(dotpath, None, root=root) is None
    assert secrets.get("nb.url", "unused", root=root) == "http://127.0.0.1:3076"


def test_redact_is_a_no_op_without_secrets(tmp_path):
    assert secrets.redact("nothing to hide here", root=tmp_path) == "nothing to hide here"


def test_redact_longest_first_and_encoded_forms(tmp_path):
    pem = "-----BEGIN KEY-----\nMIIEsecretbody\n-----END KEY-----\n"
    root = make_root(
        tmp_path,
        {
            "a": "abcdefgh",
            "b": "abcdefgh12345",
            "short": "1234567",
            "slashy": "key/with+plus=",
            "pem": pem,
        },
    )
    url_encoded = quote("key/with+plus=", safe="")
    text = f"x abcdefgh12345 y abcdefgh z 1234567 u {url_encoded} j {json.dumps(pem)}"
    assert secrets.redact(text, root=root) == 'x *** y *** z 1234567 u *** j "***"'


def test_save_failure_keeps_the_file_and_leaves_no_plaintext(tmp_path, private_tmp):
    root = make_root(tmp_path)
    enc = (root / "secrets/config.yml.enc").read_bytes()
    # A YAML validator that fails and quotes the file, as the parser does on bad input.
    (root / ".venv/bin/python").write_text(
        f"#!/bin/sh\necho 'quoted: {SEARCHAPI_KEY}' >&2\nexit 1\n"
    )
    with pytest.raises(secrets.SecretsError) as e:
        secrets.save({"providers": {"searchapi": {"api_key": SEARCHAPI_KEY}}}, root)
    assert "Refusing to encrypt" in str(e.value)
    assert SEARCHAPI_KEY not in "".join(traceback.format_exception(e.value))
    assert list(private_tmp.iterdir()) == []
    assert (root / "secrets/config.yml.enc").read_bytes() == enc


# --- factory secrets-import-nb -----------------------------------------------------------------

PEM = "-----BEGIN PRIVATE KEY-----\nnb-gemini-0012\n-----END PRIVATE KEY-----\n"
NB_CONFIG = {
    "tools": {
        "SearchAPI": {"api_key": "nb-searchapi-0001"},
        "SEranking": {"api_token": "nb-seranking-0002"},
        "Apify": {"api_key": "nb-apify-0003"},
        "Firecrawl": {"api_key": "nb-firecrawl-0004"},
        "Tavily": {"api_key": "nb-tavily-0005"},
        "ScreenshotAPI": {"token": "nb-screenshotapi-0006"},
        "OpenAI": {"api_key": "nb-openai-0007"},
        "Legnext": {"api_key": "nb-legnext-0008"},
        "FalAI": {"api_key": "nb-falai-0009"},
        "ElevenLabs": {"api_key": "nb-elevenlabs-0010", "default_tts_model": "nb-tts-model"},
        "Submagic": {"api_key": "nb-submagic-0011"},
        "Gemini": {
            "vertex_ai": {
                "project_id": "nb-gcp-project",
                "region_name": "nb-region-1",
                "service_account": {"private_key": PEM},
            }
        },
        "Unmapped": {"api_key": "nb-unmapped-9999"},
    },
    "mongodb": {"uri": "mongodb://nb-mongo-9998"},
}
NB_API_KEY = "nb-api-key-0013"
NB_ENV = f"# NeuralBox local env\nDEV_EMAIL=dev@example.test\nNB_API_KEY={NB_API_KEY}\n"
EXPECTED = {
    "providers.searchapi.api_key": "nb-searchapi-0001",
    "providers.seranking.api_token": "nb-seranking-0002",
    "providers.apify.api_key": "nb-apify-0003",
    "providers.firecrawl.api_key": "nb-firecrawl-0004",
    "providers.tavily.api_key": "nb-tavily-0005",
    "providers.screenshotapi.token": "nb-screenshotapi-0006",
    "providers.openai.api_key": "nb-openai-0007",
    "providers.legnext.api_key": "nb-legnext-0008",
    "providers.fal.api_key": "nb-falai-0009",
    "providers.elevenlabs.api_key": "nb-elevenlabs-0010",
    "providers.submagic.api_key": "nb-submagic-0011",
    "providers.gemini.vertex_ai": NB_CONFIG["tools"]["Gemini"]["vertex_ai"],
    "nb.api_key": NB_API_KEY,
}
FACTORY_CONFIG = {
    "operator": {"name": "Vlad Zloteanu"},
    "nb": {"url": "http://127.0.0.1:3076", "api_key": "", "user_email": "astrafable@local"},
    "providers": {"searchapi": {"api_key": ""}, "gemini": {"vertex_ai": {}}},
}


def leaves(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from leaves(value)
    else:
        yield node


NB_VALUES = [*leaves(NB_CONFIG), NB_API_KEY]


def make_nb_root(
    path: Path, config: dict = NB_CONFIG, env: str = NB_ENV, recipe: str = "@cat nb-config.yml"
) -> Path:
    """A stand-in NeuralBox checkout: `make secrets-cat` prints `config`, `.env` has NB_API_KEY."""
    path.mkdir(parents=True)
    (path / "Makefile").write_text(
        f"secrets-cat:\n\t@echo '# config.local.yml.enc (dev)' >&2\n\t{recipe}\n"
    )
    (path / "nb-config.yml").write_text(yaml.safe_dump(config))
    (path / ".env").write_text(env)
    return path


def snapshot(path: Path) -> dict:
    """Every entry under `path` with its bytes and mtime: equal snapshots, nothing written."""
    entries = {".": (None, path.stat().st_mtime_ns)}
    for entry in path.rglob("*"):
        entries[str(entry.relative_to(path))] = (
            entry.read_bytes() if entry.is_file() else None,
            entry.stat().st_mtime_ns,
        )
    return entries


@pytest.fixture
def nb_root(tmp_path_factory):
    return make_nb_root(tmp_path_factory.mktemp("dolead") / "neural_box")


def test_import_nb_writes_values_next_to_source(root, nb_root, private_tmp, capsys):
    make_root(root, FACTORY_CONFIG)
    before = snapshot(nb_root)
    days = {date.today().isoformat()}
    assert main(["secrets-import-nb", "--nb-root", str(nb_root)]) == 0
    days.add(date.today().isoformat())
    out, err = capsys.readouterr()
    assert out.splitlines() == list(EXPECTED)
    for value in NB_VALUES:
        assert value not in out + err
    for dotpath, value in EXPECTED.items():
        parent = dotpath.rsplit(".", 1)[0]
        assert secrets.get(dotpath, root=root) == value
        assert secrets.get(f"{parent}.source", root=root) == "neural_box"
        assert str(secrets.get(f"{parent}.imported_at", root=root)) in days
    config = secrets.load(root, refresh=True)
    assert set(config["providers"]["searchapi"]) == {"api_key", "source", "imported_at"}
    assert set(config["providers"]["gemini"]) == {"vertex_ai", "source", "imported_at"}
    assert config["nb"]["url"] == "http://127.0.0.1:3076"
    assert config["nb"]["user_email"] == "astrafable@local"
    assert config["operator"] == {"name": "Vlad Zloteanu"}
    dumped = yaml.safe_dump(config)
    for unmapped in ("nb-unmapped-9999", "nb-mongo-9998", "nb-tts-model"):
        assert unmapped not in dumped
    assert snapshot(nb_root) == before
    assert list(private_tmp.iterdir()) == []
    assert not (root / "secrets/config.yml").exists()


def test_import_nb_dry_run_changes_nothing(root, nb_root, capsys):
    make_root(root, FACTORY_CONFIG)
    enc = (root / "secrets/config.yml.enc").read_bytes()
    before = snapshot(nb_root)
    assert main(["secrets-import-nb", "--nb-root", str(nb_root), "--dry-run"]) == 0
    out, err = capsys.readouterr()
    assert out.splitlines() == list(EXPECTED)
    for value in NB_VALUES:
        assert value not in out + err
    assert (root / "secrets/config.yml.enc").read_bytes() == enc
    assert secrets.get("nb.api_key", None, root=root) is None
    assert snapshot(nb_root) == before


def test_import_nb_without_factory_key_names_setup(root, tmp_path_factory, capsys):
    (root / "secrets").mkdir()
    marker = tmp_path_factory.mktemp("marker") / "secrets-cat-ran"
    nb = make_nb_root(
        tmp_path_factory.mktemp("dolead") / "neural_box",
        recipe=f"@touch {marker}; cat nb-config.yml",
    )
    assert main(["secrets-import-nb", "--nb-root", str(nb)]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "make secrets-init" in err
    assert not marker.exists()  # NeuralBox is not read when the factory side cannot take the values


def test_import_nb_skips_what_neuralbox_lacks(root, tmp_path_factory, capsys):
    make_root(root, FACTORY_CONFIG)
    config = copy.deepcopy(NB_CONFIG)
    del config["tools"]["Submagic"]
    config["tools"]["Tavily"]["api_key"] = ""
    nb = make_nb_root(
        tmp_path_factory.mktemp("dolead") / "neural_box", config, env="DEV_EMAIL=dev@example.test\n"
    )
    assert main(["secrets-import-nb", "--nb-root", str(nb)]) == 0
    out, err = capsys.readouterr()
    skipped = {"providers.tavily.api_key", "providers.submagic.api_key", "nb.api_key"}
    assert out.splitlines() == [dotpath for dotpath in EXPECTED if dotpath not in skipped]
    assert "tools.Submagic.api_key" in err and "tools.Tavily.api_key" in err and "NB_API_KEY" in err
    assert secrets.get("nb.api_key", None, root=root) is None
    assert "source" not in secrets.load(root)["nb"]


def test_import_nb_reports_a_failed_make_without_its_output(root, tmp_path_factory, capsys):
    make_root(root, FACTORY_CONFIG)
    nb = make_nb_root(
        tmp_path_factory.mktemp("dolead") / "neural_box", recipe="@cat nb-config.yml; exit 3"
    )
    enc = (root / "secrets/config.yml.enc").read_bytes()
    assert main(["secrets-import-nb", "--nb-root", str(nb)]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "secrets-cat" in err and "exit" in err
    for value in NB_VALUES:
        assert value not in err
    assert (root / "secrets/config.yml.enc").read_bytes() == enc


def test_import_nb_needs_the_checkout(root, capsys):
    make_root(root, FACTORY_CONFIG)
    assert main(["secrets-import-nb", "--nb-root", str(root / "no-such-checkout")]) == 1
    assert "no-such-checkout" in capsys.readouterr().err


@pytest.mark.parametrize(
    "line",
    [
        f"NB_API_KEY={NB_API_KEY}",
        f'export NB_API_KEY="{NB_API_KEY}"',
        f"NB_API_KEY = '{NB_API_KEY}'",
        f"NB_API_KEY={NB_API_KEY}  # local key",
    ],
)
def test_env_value_reads_dotenv_lines(tmp_path, line):
    from factory.tools import secrets_import_nb

    env = tmp_path / ".env"
    env.write_text(f"# comment\nNB_API_KEY_OLD=stale-value\nOTHER=1\n{line}\n")
    assert secrets_import_nb.env_value(env, "NB_API_KEY") == NB_API_KEY
    assert secrets_import_nb.env_value(env, "MISSING_NAME") is None
    assert secrets_import_nb.env_value(tmp_path / "absent.env", "NB_API_KEY") is None
