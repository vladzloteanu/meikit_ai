import os
from pathlib import Path

from factory import paths

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_defaults_to_the_checkout(monkeypatch):
    monkeypatch.delenv("FACTORY_ROOT", raising=False)
    assert paths.root() == REPO_ROOT
    assert (paths.root() / "pyproject.toml").is_file()


def test_root_follows_factory_root_at_call_time(monkeypatch, tmp_path):
    monkeypatch.setenv("FACTORY_ROOT", str(tmp_path / "a"))
    assert paths.root() == tmp_path / "a"
    monkeypatch.setenv("FACTORY_ROOT", str(tmp_path / "b"))
    assert paths.root() == tmp_path / "b"


def test_empty_factory_root_means_the_checkout(monkeypatch):
    monkeypatch.setenv("FACTORY_ROOT", "")
    assert paths.root() == REPO_ROOT


def test_derived_paths(root):
    assert paths.ideas() == root / "ideas"
    assert paths.docs() == root / "docs"
    assert paths.secrets_dir() == root / "secrets"
    assert paths.idea_dir("watchdog") == root / "ideas" / "watchdog"
    assert paths.research_dir("watchdog") == root / "ideas" / "watchdog" / "research"


def test_root_fixture_isolates_the_factory(root):
    assert os.environ["FACTORY_ROOT"] == str(root)
    assert paths.root() == root
    assert (root / "ideas").is_dir()
