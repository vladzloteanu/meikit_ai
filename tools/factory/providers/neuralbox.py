"""NeuralBox, the local agent service that holds AdsInsights and provider keys (docs/neuralbox.md).

NeuralBox answers a prompt with an agent that has its MCP tools at hand: POST /respond, with the
key (`nb.api_key`) in an `X-API-Key` header, at `nb.url` (http://127.0.0.1:3076 on this machine);
GET /heartbeat says it is up and lists the tools it holds. A /respond call runs an agent: it takes
seconds to minutes, NeuralBox reports what it cost (`cost_usd`), and it is never retried
(retries=1), since a second attempt would run, and bill, the agent again.

Every request names the factory, as NeuralBox requires: `properties` carries a `project` and a
`user_name` (refused with a 422 without them) and the `user_email` it checks against its users
(`nb.user_email`; refused with a 403 when it knows no such user with API access). NeuralBox
stops the run after RUN_TIMEOUT_S, before the client gives up at TIMEOUT_S, so the answer of a
long run, with its cost, still arrives.

`respond` appends DISCIPLINE to every prompt and asks for structured output when given a JSON
schema. Its NBResult keeps the names of the tools called and nothing else of NeuralBox's
ToolCall objects, whose inputs and outputs hold raw tool answers. A dry-run client never reads a
secret and answers from `fixtures/neuralbox/<name>.json`.
"""

import math
from dataclasses import dataclass, field
from typing import Any

from factory import secrets
from factory.http import Client, ProviderError

PROVIDER = "neuralbox"
LOCAL_URL = "http://127.0.0.1:3076"  # where NeuralBox runs on this machine; a dry run's base
TIMEOUT_S = 600.0
RUN_TIMEOUT_S = 540  # NeuralBox's own limit on a run, under TIMEOUT_S
RETRIES = 1
PROJECT = "astrafable"
USER_NAME = "astrafable-factory"
PERMISSION_MODE = "bypassPermissions"
DEFAULT_MAX_TURNS = 8
DISCIPLINE = (
    "\n\nIf a tool call fails or a key is missing, say exactly which tool failed. "
    "Never invent numbers. Never print secret values."
)


class NeuralBoxClient(Client):
    """A Client that also carries the NeuralBox user its calls run as (`nb.user_email`)."""

    def __init__(self, *args: Any, user_email: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_email = user_email


@dataclass(frozen=True)
class NBResult:
    """What a /respond call answered.

    `structured` is the JSON the schema asked for (None without one); `cost_usd` is None when
    NeuralBox reported no cost; `tools_called` holds tool names only, one per call, in order;
    `errors` are the failures NeuralBox reported, one line each (empty when the run went well).
    """

    answer: str
    structured: dict | None
    cost_usd: float | None
    tools_called: list[str]
    session_id: str | None
    request_id: str | None
    errors: list[str] = field(default_factory=list)


def client(dry_run: bool = False) -> Client:
    """The NeuralBox client: `nb.url`, `nb.api_key` and `nb.user_email` from the secrets."""
    if dry_run:
        return NeuralBoxClient(
            PROVIDER, LOCAL_URL, timeout_s=TIMEOUT_S, retries=RETRIES, dry_run=True
        )
    return NeuralBoxClient(
        PROVIDER,
        secrets.get("nb.url"),
        headers={"X-API-Key": secrets.get("nb.api_key")},
        timeout_s=TIMEOUT_S,
        retries=RETRIES,
        user_email=secrets.get("nb.user_email"),
    )


def heartbeat(client: Client) -> dict:
    """GET /heartbeat: NeuralBox's status, versions and `available_tools` (free, no key needed)."""
    response = client.get("/heartbeat", fixture="neuralbox/heartbeat")
    return _object(client, response)


def respond(
    client: Client,
    prompt: str,
    *,
    allowed_tools: list[str] | None = None,
    schema: dict | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    session_id: str | None = None,
    fixture: str = "neuralbox/respond",
) -> NBResult:
    """POST /respond: run `prompt` (DISCIPLINE appended) and return what NeuralBox answered.

    `allowed_tools` names the tools the agent is given, as /heartbeat lists them
    (`mcp__tools__QueryAdsInsights`); `schema` asks for structured output; `session_id` resumes
    a conversation. What is None is left out of the request. A dry run answers from `fixture`.
    """
    body = {
        "prompt": prompt + DISCIPLINE,
        "allowed_tools": allowed_tools,
        "permission_mode": PERMISSION_MODE,
        "max_turns": max_turns,
        "timeout": RUN_TIMEOUT_S,
        "output_format": None if schema is None else {"type": "json_schema", "schema": schema},
        "properties": _properties(client),
        "session_id": session_id,
    }
    response = client.post(
        "/respond",
        {name: value for name, value in body.items() if value is not None},
        fixture=fixture,
    )
    data = _object(client, response)
    structured = data.get("structured_output")
    return NBResult(
        answer=_text(data.get("answer")) or "",
        structured=structured if isinstance(structured, dict) else None,
        cost_usd=_cost(data.get("cost_usd")),
        tools_called=[
            call["name"]
            for call in _list(data.get("tools_called"))
            if isinstance(call, dict) and isinstance(call.get("name"), str)
        ],
        session_id=_text(data.get("session_id")),
        request_id=_text(data.get("request_id")),
        errors=[
            line
            for error in _list(data.get("errors"))
            if isinstance(error, str) and (line := " ".join(error.split()))
        ],
    )


def _properties(client: Client) -> dict:
    """Who the call is for, as NeuralBox requires: the project, the user name, the user email."""
    properties = {"project": PROJECT, "user_name": USER_NAME}
    user_email = getattr(client, "user_email", None)
    if user_email:
        properties["user_email"] = user_email
    return properties


def _object(client: Client, response: Any) -> dict:
    """The JSON object of a 2xx `response`; ProviderError for any other status or body."""
    data = client.decode(response)
    if not isinstance(data, dict):
        request = response.request
        raise ProviderError(
            client.provider,
            response.status_code,
            f"{request.method} {request.url.raw_path.decode('ascii', 'replace')}: "
            f"not a JSON object: {response.text}",
        )
    return data


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _cost(value: Any) -> float | None:
    """A reported cost in USD: a finite number of 0 or more, else None (not reported)."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if math.isfinite(value) and value >= 0 else None
