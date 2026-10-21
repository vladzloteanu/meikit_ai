"""NeuralBox, the local agent service that holds AdsInsights and provider keys (docs/neuralbox.md).

NeuralBox answers a prompt with an agent that has its MCP tools at hand: POST /respond, with the
key (`nb.api_key`) in an `X-API-Key` header, at `nb.url` (http://127.0.0.1:3076 on this machine);
GET /heartbeat says it is up and lists the tools it holds. A /respond call runs an agent: it takes
seconds to minutes, NeuralBox reports what it cost (`cost_usd`), and it is never retried
(retries=1), since a second attempt would run, and bill, the agent again.

Every request names the factory, as NeuralBox requires: `properties` carries a `project`, a
`user_id` (a 422 without a user id or name) and the `user_email` it checks against its users
(`nb.user_email`; a 403 when it knows no such user with API access). The factory sends a
`user_id` and no `user_name`: given a user name, NeuralBox writes "The current user is: <name>
(email: <email>)" into the agent's instructions; given only an id, it adds no such line. NeuralBox
stops the run after RUN_TIMEOUT_S, before the client gives up at TIMEOUT_S, so the answer of a long
run, with its cost, still arrives.

Every call carries the block, so that NeuralBox can call nothing but the three AdsInsights tools
of WHITELIST. `allowed_tools` names the whitelisted tools the call may use (any other name is
refused before any request), and `disallowed_tools` denies everything else: NeuralBox's thirteen
built-ins (BUILTINS), whatever the heartbeat says; every tool the heartbeat lists, the whitelisted
ones the call does not use included; and, whole, every listed MCP server holding none of the tools
the call uses, and PER_RUN_SERVERS. NeuralBox's permission modes cannot do this (none denies a
tool outside `allowed_tools`), so calls keep `bypassPermissions` and the deny rules are the fence
(docs/neuralbox.md). The heartbeat's tool list is fetched once per client and kept on it; without
it the block cannot be built, so no call is made.

Everything NeuralBox returns passes through `secrets.redact` before it leaves this module: the
answer, the strings of the structured output, the errors, the tool names, the ids (a dry run's
canned answer excepted: it holds no secret, and a dry run loads none). NBResult keeps the names of
the tools called and nothing else of NeuralBox's ToolCall objects, whose inputs and outputs hold
raw tool answers. Once a /respond request has left, an outcome nobody can read (no answer, a 5xx,
an answer that is not a JSON object) raises Unconfirmed, so that the caller counts its cost as
spent. A dry-run client never reads a secret and answers from `fixtures/neuralbox/<name>.json`.
"""

import math
from dataclasses import dataclass, field
from typing import Any

import httpx

from factory import secrets
from factory.http import Client, ProviderError

PROVIDER = "neuralbox"
LOCAL_URL = "http://127.0.0.1:3076"  # where NeuralBox runs on this machine; a dry run's base
TIMEOUT_S = 600.0
RUN_TIMEOUT_S = 540  # NeuralBox's own limit on a run, under TIMEOUT_S
RETRIES = 1
PROJECT = "astrafable"
USER_ID = "astrafable-factory"
PERMISSION_MODE = "bypassPermissions"  # no mode denies by itself: the block does (see above)
# The only tools the factory lets NeuralBox call: AdsInsights' lookups and queries, which read
# aggregates on public advertisers and spend nothing.
WHITELIST = (
    "mcp__tools__LookupAdsInsights",
    "mcp__tools__ListCategories",
    "mcp__tools__QueryAdsInsights",
)
# NeuralBox's own Claude Code built-ins (its BUILTIN_TOOLS, the only non-MCP names it lets a
# caller deny): denied on every call, listed by the heartbeat or not.
BUILTINS = (
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Bash",
    "Glob",
    "Grep",
    "WebSearch",
    "WebFetch",
    "Task",
    "TodoWrite",
    "NotebookEdit",
    "Skill",
)
# MCP servers NeuralBox attaches to runs from its tool config (its src/services/chat_service.py):
# Looker, which its heartbeat never lists, and BrowserAutomation and Chart, which it lists when
# configured. Denied whole on every call, attached or not.
PER_RUN_SERVERS = ("mcp__BrowserAutomation", "mcp__Looker", "mcp__Chart")
DEFAULT_MAX_TURNS = 8
DISCIPLINE = (
    "\n\nIf a tool call fails or a key is missing, say exactly which tool failed. "
    "Never invent numbers. Never print secret values."
)
_JSON_KINDS = {str: "a string", list: "a list", bool: "true or false", int: "a number"}


class Unconfirmed(ProviderError):
    """A /respond request left, but what it ran and cost is unknown. `reason` says why: no
    answer (a network error, a timeout), a 5xx, an answer that is not a JSON object."""

    def __init__(self, error: ProviderError, reason: str) -> None:
        super().__init__(error.provider, error.status, error.detail)
        self.reason = reason


class NeuralBoxClient(Client):
    """A Client that also carries the NeuralBox user its calls run as (`nb.user_email`) and the
    tools NeuralBox listed, once `listed_tools` has fetched them."""

    def __init__(self, *args: Any, user_email: str | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_email = user_email
        self.tools: list[str] | None = None


@dataclass(frozen=True)
class NBResult:
    """What a /respond call answered, every string redacted.

    `structured` is the JSON object the schema asked for (None without one); `cost_usd` is None
    when NeuralBox reported no cost; `tools_called` holds the names of the tools that ran, one per
    call, in order; `errors` is what went wrong, one line each: the failures NeuralBox reported,
    and a structured output that is not a JSON object; `tools_denied` names the calls the block
    refused before they ran (a denied MCP tool stays visible to the agent, and NeuralBox lists the
    attempt).
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
    return _object(client, client.get("/heartbeat", fixture="neuralbox/heartbeat"))


def listed_tools(client: Client) -> list[str]:
    """The tools NeuralBox's heartbeat lists: fetched once per NeuralBoxClient, then kept on it.

    Raises ProviderError when the heartbeat cannot be read or lists no tools: without the list,
    the tools outside the whitelist cannot be blocked, so no call may be made.
    """
    cached = getattr(client, "tools", None)
    if cached is not None:
        return cached
    tools = heartbeat(client).get("available_tools")
    if not isinstance(tools, list) or not tools or not all(isinstance(t, str) for t in tools):
        raise ProviderError(
            client.provider,
            200,
            "GET /heartbeat: lists no tools, so the tools outside the whitelist cannot be "
            "blocked: no call made",
        )
    if hasattr(client, "tools"):  # a NeuralBoxClient keeps the list
        client.tools = tools
    return tools


def require_tools(client: Client, tools: list[str]) -> list[str]:
    """The tools NeuralBox lists; ProviderError, before any paid call, when it lacks one of
    `tools`."""
    listed = listed_tools(client)
    missing = [name for name in tools if name not in listed]
    if missing:
        raise ProviderError(
            client.provider, 200, f"GET /heartbeat: lists no {', '.join(missing)}: no call made"
        )
    return listed


def blocked_tools(client: Client, allowed: list[str]) -> list[str]:
    """What a call that may use `allowed` denies: BUILTINS and every tool the heartbeat lists
    but `allowed`, then, whole, every listed MCP server holding none of `allowed`, and
    PER_RUN_SERVERS."""
    listed = listed_tools(client)
    names = [name for name in dict.fromkeys([*BUILTINS, *listed]) if name not in allowed]
    servers = {server for name in listed if (server := _server(name))} | set(PER_RUN_SERVERS)
    kept = {_server(name) for name in allowed}
    return names + sorted(servers - kept)


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

    `allowed_tools` names the tools of WHITELIST the agent may use (none when None or []);
    `schema` asks for structured output; `session_id` resumes a conversation. What is None is left
    out of the request. A dry run answers from `fixture`.

    Every call carries the block (`blocked_tools`): a tool in `allowed_tools` outside WHITELIST
    is a ValueError, raised before any request; a heartbeat that cannot be read, or lists no
    tools, is a ProviderError, and no call is made. A 4xx is a ProviderError (NeuralBox refused
    the call: nothing ran); an outcome nobody can read once the request has left is Unconfirmed.
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
    try:
        response = client.post(
            "/respond",
            {name: value for name, value in body.items() if value is not None},
            fixture=fixture,
        )
    except ProviderError as exc:  # no answer at all: a network error, a timeout
        raise Unconfirmed(exc, "no answer") from None
    return _result(client, _answer(client, response))


def require_success(result: NBResult) -> None:
    """ProviderError when the run went wrong (`result.errors`), its text already redacted."""
    if result.errors:
        raise ProviderError(
            PROVIDER, 200, f"POST /respond: the run failed: {'; '.join(result.errors)}"
        )


def _answer(client: Client, response: httpx.Response) -> dict:
    """The JSON object a /respond answered. A 4xx is a ProviderError: NeuralBox refused the call
    before anything ran. A 5xx, or a 2xx whose body is not a JSON object, is Unconfirmed."""
    if 400 <= response.status_code < 500:
        raise client._error(response, response.text)
    try:
        return _object(client, response)
    except ProviderError as exc:
        reason = f"HTTP {exc.status}" if exc.status and exc.status >= 500 else None
        raise Unconfirmed(exc, reason or "an answer that is not a JSON object") from None


def _result(client: Client, data: dict) -> NBResult:
    """The NBResult of an answer, every string NeuralBox wrote redacted."""
    structured = data.get("structured_output")
    errors = [
        line
        for error in _list(data.get("errors"))
        if isinstance(error, str) and (line := " ".join(error.split()))
    ]
    if structured is not None and not isinstance(structured, dict):
        kind = _JSON_KINDS.get(type(structured), "a number")
        errors.append(f"the structured output is {kind}, not a JSON object")
        structured = None
    calls = [
        call
        for call in _list(data.get("tools_called"))
        if isinstance(call, dict) and isinstance(call.get("name"), str)
    ]
    return NBResult(
        answer=_redact(client, _text(data.get("answer")) or ""),
        structured=_redact(client, structured),
        cost_usd=_cost(data.get("cost_usd")),
        tools_called=_redact(client, [call["name"] for call in calls if not _refused(call)]),
        session_id=_redact(client, _text(data.get("session_id"))),
        request_id=_redact(client, _text(data.get("request_id"))),
        errors=_redact(client, errors),
        tools_denied=_redact(client, [call["name"] for call in calls if _refused(call)]),
    )


def _redact(client: Client, value: Any) -> Any:
    """`value` with `secrets.redact` applied to every string in it, keys included; a dry run's
    canned answer is returned as it is, since a dry run loads no secret."""
    if client.dry_run:
        return value
    if isinstance(value, str):
        return secrets.redact(value)
    if isinstance(value, list):
        return [_redact(client, item) for item in value]
    if isinstance(value, dict):
        return {_redact(client, key): _redact(client, item) for key, item in value.items()}
    return value


def _properties(client: Client) -> dict:
    """Who the call is for, as NeuralBox requires: the project, the user id, the user email."""
    properties = {"project": PROJECT, "user_id": USER_ID}
    user_email = getattr(client, "user_email", None)
    if user_email:
        properties["user_email"] = user_email
    return properties


def _object(client: Client, response: httpx.Response) -> dict:
    """The JSON object of a 2xx `response`; ProviderError for any other status or body."""
    data = client.decode(response)
    if not isinstance(data, dict):
        raise client._error(response, f"not a JSON object: {response.text}")
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
