"""Where the factory's files live.

The factory root is the checkout this package runs from, or the directory named by the
FACTORY_ROOT environment variable (tests point it at a temp dir). It is looked up on every
call, never at import time, so setting or monkeypatching FACTORY_ROOT after import takes
effect. That is why these are functions and not module constants: call `paths.root()`,
`paths.ideas()`, `paths.docs()` and `paths.secrets_dir()` at the point of use.
"""

import os
from pathlib import Path


def root() -> Path:
    """FACTORY_ROOT when set and non-empty, else the checkout holding this package."""
    override = os.environ.get("FACTORY_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2]


def ideas() -> Path:
    return root() / "ideas"


def docs() -> Path:
    return root() / "docs"


def secrets_dir() -> Path:
    return root() / "secrets"


def idea_dir(slug: str) -> Path:
    return ideas() / slug


def research_dir(slug: str) -> Path:
    return idea_dir(slug) / "research"
