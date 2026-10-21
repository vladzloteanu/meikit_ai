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

Every call carries the block, so that NeuralBox can call nothing but the three AdsInsights
tools of WHITELIST, never a tool that spends or reads Dolead's client data. `allowed_tools`
names the whitelisted tools the call may use (any other name is refused before any request), and
`disallowed_tools` denies everything else: every tool the heartbeat lists, the whitelisted ones
the call does not use included; whole, every listed MCP server holding none of the tools the
call uses; and UNLISTED_SERVERS, which NeuralBox adds to some runs without listing them.
NeuralBox's permission modes cannot do this: none denies a tool outside `allowed_tools` (in
`default`, `acceptEdits` and `plan` its own `can_use_tool` lets through any tool it has no rule
against, and it accepts no other mode), so calls keep `bypassPermissions` and rely on the deny
rules, which hold in every mode. The heartbeat's tool list is fetched once per client and kept on
it; without it the block cannot be built, so no call is made (ProviderError).

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
PERMISSION_MODE = "bypassPermissions"  # no mode denies by itself: the block does (see above)
# The only tools the factory lets NeuralBox call: AdsInsights' lookups and queries, which read
# aggregates on public advertisers and spend nothing.
WHITELIST = (
    "mcp__tools__LookupAdsInsights",
    "mcp__tools__ListCategories",
    "mcp__tools__QueryAdsInsights",
)
# MCP servers NeuralBox adds to a run when configured, without listing them in its heartbeat
# (its src/services/chat_service.py): denied whole, whatever tools they hold.
UNLISTED_SERVERS = ("mcp__BrowserAutomation", "mcp__Looker", "mcp__Chart")
DEFAULT_MAX_TURNS = 8
DISCIPLINE = (
    "\n\nIf a tool call fails or a key is missing, say exactly which tool failed. "
    "Never invent numbers. Never print secret values."
)


class NeuralBoxClient(Client):
    """A Client that also carries the NeuralBox user its calls run as (`nb.user_email`) and the
    tools NeuralBox listed, once `listed_tools` has fetched them."""

    def __init__(self, *args: Any, user_email: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_email = user_email
        self.tools: list[str] | None = None


@dataclass(frozen=True)
class NBResult:
    """What a /respond call answered.

    `structured` is the JSON the schema asked for (None without one); `cost_usd` is None when
    NeuralBox reported no cost; `tools_called` holds the names of the tools that ran, one per
    call, in order; `errors` are the failures NeuralBox reported, one line each (empty when the
    run went well); `tools_denied` names the calls the block refused before they ran (a denied
    MCP tool stays visible to the agent, and NeuralBox lists the attempt).
    """

    answer: str
    structured: dict | None
    cost_usd: float | None
    tools_called: list[str]
    session_id: str | None
    request_id: str | None
    errors: list[str] = field(default_factory=list)
    tools_denied: list[str] = field(default_factory=list)


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


def listed_tools(client: Client) -> list[str]:
    """The tools NeuralBox's heartbeat lists: fetched once per NeuralBoxClient, then kept on it.

    Raises ProviderError when the heartbeat cannot be read or lists no tools: without the list,
    the tools outside the whitelist cannot be blocked, so no call may be made.
    """
    cached = getattr(client, "tools", None)
    if cached is not None:
        return cached
    response = client.get("/heartbeat", fixture="neuralbox/heartbeat")
    tools = _object(client, response).get("available_tools")
    if not isinstance(tools, list) or not tools or not all(isinstance(t, str) for t in tools):
        raise ProviderError(
            client.provider,
            response.status_code,
            "GET /heartbeat: lists no tools, so the tools outside the whitelist cannot be "
            "blocked: no call made",
        )
    if hasattr(client, "tools"):  # a NeuralBoxClient keeps the list
        client.tools = tools
    return tools


def blocked_tools(client: Client, allowed: list[str]) -> list[str]:
    """What a call that may use `allowed` denies: every tool the heartbeat lists but `allowed`,
    then, whole, every listed MCP server holding none of `allowed` and UNLISTED_SERVERS."""
    listed = listed_tools(client)
    servers = {server for name in listed if (server := _server(name))} | set(UNLISTED_SERVERS)
    kept = {_server(name) for name in allowed}
    return [name for name in listed if name not in allowed] + sorted(servers - kept)


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

    `allowed_tools` names the tools of WHITELIST the agent may use, none when None; `schema`
    asks for structured output; `session_id` resumes a conversation. What is None is left out of
    the request. A dry run answers from `fixture`.

    Every call carries the block (`blocked_tools`): a tool in `allowed_tools` outside WHITELIST
    is a ValueError, raised before any request; a heartbeat that cannot be read, or lists no
    tools, is a ProviderError, and no call is made.
    """
    allowed = list(allowed_tools or [])
    outside = [name for name in allowed if name not in WHITELIST]
    if outside:
        raise ValueError(
            f"{', '.join(outside)}: the factory lets NeuralBox use only {', '.join(WHITELIST)}"
        )
    body = {
        "prompt": prompt + DISCIPLINE,
        "allowed_tools": allowed_tools,
        "disallowed_tools": blocked_tools(client, allowed),
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
    calls = [
        call
        for call in _list(data.get("tools_called"))
        if isinstance(call, dict) and isinstance(call.get("name"), str)
    ]
    return NBResult(
        answer=_text(data.get("answer")) or "",
        structured=structured if isinstance(structured, dict) else None,
        cost_usd=_cost(data.get("cost_usd")),
        tools_called=[call["name"] for call in calls if not _refused(call)],
        session_id=_text(data.get("session_id")),
        request_id=_text(data.get("request_id")),
        errors=[
            line
            for error in _list(data.get("errors"))
            if isinstance(error, str) and (line := " ".join(error.split()))
        ],
        tools_denied=[call["name"] for call in calls if _refused(call)],
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


def _refused(call: dict) -> bool:
    """Whether the block refused `call`: its output is Claude Code's own refusal of that tool."""
    output = call.get("output")
    return isinstance(output, str) and output.startswith(
        f"Permission to use {call['name']} has been denied"
    )


def _server(tool: str) -> str | None:
    """`mcp__<server>` for the MCP tool `mcp__<server>__<tool>`; None for a built-in tool."""
    parts = tool.split("__")
    return f"mcp__{parts[1]}" if parts[0] == "mcp" and len(parts) >= 3 and parts[1] else None


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _cost(value: Any) -> float | None:
    """A reported cost in USD: a finite number of 0 or more, else None (not reported)."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value) if math.isfinite(value) and value >= 0 else None
