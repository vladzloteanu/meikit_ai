"""The Vercel CLI's login on this machine, read for the doctor. Nothing here changes Vercel.

The CLI keeps its state in CONFIG_DIR (`~/Library/Application Support/com.vercel.cli`):
`auth.json` holds the login's `token`; `config.json` holds the scope, `currentTeam` (a team id, or
absent or null in the personal scope), and `cachedTeamSlugs`, the slugs of the teams the CLI has
used (`{team id: {"slug", "savedAt"}}`). The token is read for one call, GET /v2/user, and goes
nowhere else: it is never printed, logged or put in an error message. Nothing here runs
`vercel switch` or writes a file.

A team-based ("northstar") Vercel account has no personal scope: its CLI always works in a team,
the account's default team when `currentTeam` is unset, and refuses `vercel switch <username>`
("You cannot set your Personal Account as the scope.", Vercel CLI 63). `user_plan` says whether
the account is one (docs/doctor.md).
"""

import json
from pathlib import Path

import httpx

from factory.http import Client, ProviderError

CONFIG_DIR = Path.home() / "Library" / "Application Support" / "com.vercel.cli"
AUTH_FILE = "auth.json"
CONFIG_FILE = "config.json"
API_URL = "https://api.vercel.com"
USER_PATH = "/v2/user"
TIMEOUT_S = 20.0
NORTHSTAR = "northstar"  # the `version` of a team-based account in GET /v2/user
REDACTED = "***"


class VercelError(Exception):
    """The Vercel login cannot be read: no token, or GET /v2/user did not answer with a user.
    The message is one line and never holds the token."""


def cli_auth() -> dict | None:
    """The CLI's login: `{"token", "current_team"}` (`current_team` None in the personal scope);
    None when auth.json is missing or holds no token. The token is a secret: never print it."""
    token = _read(AUTH_FILE).get("token")
    if not isinstance(token, str) or not token.strip():
        return None
    return {"token": token, "current_team": _read(CONFIG_FILE).get("currentTeam") or None}


def current_scope() -> tuple[str, str | None]:
    """The CLI's scope from config.json alone (no token, no call): `("personal", None)` when
    `currentTeam` is absent or null, else `("team", slug)`, the slug from `cachedTeamSlugs`, or
    the team id when the CLI has cached none."""
    config = _read(CONFIG_FILE)
    team = config.get("currentTeam")
    if not team:
        return ("personal", None)
    cached = config.get("cachedTeamSlugs")
    entry = cached.get(team) if isinstance(cached, dict) else None
    slug = entry.get("slug") if isinstance(entry, dict) else None
    return ("team", slug if isinstance(slug, str) and slug else str(team))


def user_plan() -> dict:
    """The logged-in account by GET /v2/user, with the CLI's token: `{"username", "plan",
    "northstar"}`, `plan` as Vercel names it (`hobby`, `pro`...) or None, `northstar` whether the
    account is team-based. One call, no retry. Raises VercelError when there is no login, or
    when the call fails or names no user."""
    auth = cli_auth()
    if auth is None:
        raise VercelError("the Vercel CLI is not logged in: run `vercel login`")
    token = auth["token"]
    headers = {"Authorization": f"Bearer {token}"}
    try:
        with Client("vercel", API_URL, headers=headers, timeout_s=TIMEOUT_S, retries=1) as client:
            response = client.get(USER_PATH)
    except ProviderError as exc:  # no answer: a network error or a timeout
        raise VercelError(_without(str(exc), token)) from None
    if not response.is_success:
        reason = _error_reason(response)
        raise VercelError(_without(f"GET {USER_PATH}: HTTP {response.status_code}{reason}", token))
    user = _json(response).get("user")
    user = user if isinstance(user, dict) else {}
    username = user.get("username")
    if not isinstance(username, str) or not username:
        raise VercelError(f"GET {USER_PATH}: the answer names no user")
    billing = user.get("billing")
    plan = billing.get("plan") if isinstance(billing, dict) else None
    return {
        "username": username,
        "plan": plan if isinstance(plan, str) and plan else None,
        "northstar": user.get("version") == NORTHSTAR,
    }


def _read(name: str) -> dict:
    """The JSON object in CONFIG_DIR/`name`; {} when the file is missing, unreadable or not one."""
    try:
        data = json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _json(response: httpx.Response) -> dict:
    try:
        data = response.json()
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _error_reason(response: httpx.Response) -> str:
    """` (<code>: <message>)` from Vercel's error answer, empty when it gives neither."""
    error = _json(response).get("error")
    if not isinstance(error, dict):
        return ""
    words = [str(error[key]) for key in ("code", "message") if error.get(key)]
    return f" ({': '.join(words)})" if words else ""


def _without(text: str, token: str) -> str:
    """`text` on one line, the token replaced wherever it appears."""
    return " ".join(text.replace(token, REDACTED).split())
