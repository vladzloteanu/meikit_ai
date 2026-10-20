import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def factory_root(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty factory root for every test.

    FACTORY_ROOT points at it, so no test can read or overwrite the checkout's real secrets/ or
    ideas/; a test that needs ideas/ asks for `root`.
    """
    path = tmp_path_factory.mktemp("factory_root")
    monkeypatch.setenv("FACTORY_ROOT", str(path))
    return path


@pytest.fixture
def root(factory_root: Path) -> Path:
    """A throwaway factory root.

    FACTORY_ROOT points at it, ideas/ exists, and the repo's ideas/_fixture is copied in once the
    repo has one.
    """
    ideas = factory_root / "ideas"
    ideas.mkdir(exist_ok=True)
    fixture = REPO_ROOT / "ideas" / "_fixture"
    if fixture.is_dir():
        shutil.copytree(fixture, ideas / "_fixture")
    return factory_root
