import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A throwaway factory root.

    FACTORY_ROOT points at tmp_path, ideas/ exists, and the repo's ideas/_fixture
    is copied in once the repo has one.
    """
    monkeypatch.setenv("FACTORY_ROOT", str(tmp_path))
    ideas = tmp_path / "ideas"
    ideas.mkdir(exist_ok=True)
    fixture = REPO_ROOT / "ideas" / "_fixture"
    if fixture.is_dir():
        shutil.copytree(fixture, ideas / "_fixture")
    return tmp_path
