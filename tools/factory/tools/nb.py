"""`factory nb`: ask NeuralBox, the local agent service that holds AdsInsights (docs/neuralbox.md).

    factory nb ask --idea S (--prompt P | --prompt-file F) [--tools A,B] [--schema F.json]
                   [--max-turns 8] [--session ID]
    factory nb adsinsights --idea S --category C --countries FR,US
                           [--networks facebook,search] [--top 10]

`ask` sends one prompt to NeuralBox (`neuralbox.respond`) and keeps what it answered in
`research/nb_ask_<ts>.json`:

    {"prompt", "answer", "structured", "cost_usd", "tools_called", "tools_denied", "session_id",
     "request_id"}

`prompt` as given (without the DISCIPLINE every request carries), `structured` the JSON that
--schema (a JSON Schema object) asked for, null without one, `tools_called` the names of the
tools that ran, `tools_denied` those the agent tried and the block refused (both commands also
warn of these on stderr). --tools names the tools the agent may use, among the three AdsInsights
tools of the whitelist (`mcp__tools__QueryAdsInsights`...), any other name refused; without it
the agent has no tool at all. --session resumes the conversation of an earlier answer's
`session_id`. The summary is the answer, the structured JSON, the tools.

`adsinsights` asks NeuralBox about the market of one category in some countries: the category
found with LookupAdsInsights (ListCategories when needed), then for each network one
QueryAdsInsights call on the `company` tile of its `aggregations` at `sort=all`, and one on its
`copy` for the ad texts behind the hooks. The agent is given those three tools only
(ADSINSIGHTS_TOOLS) and answers in the shape of ADSINSIGHTS_SCHEMA:

    {"category_resolved", "countries",
     "networks": [{"network", "total_reach", "advertisers_count",
                   "top_companies": [{"name", "share_pct"}], "caveats"}],
     "typical_hooks", "not_found"}

Its research file, `nb_adsinsights_<ts>.json`, holds that structured answer only, cut to what the
schema describes, never the answer text or what the tools returned: AdsInsights is kept as
aggregated conclusions (counts, shares of named advertisers, typical hooks), the persistence rule.
A network whose query failed has null figures and a caveat saying so. The summary is the category
and the countries, one row per network `network | total_reach | advertisers | top companies`, the
hooks and the caveats.

Every call carries the block (`neuralbox.respond`): NeuralBox is told to deny every tool and
server it lists but the call's whitelisted tools, and no call is made when its heartbeat cannot
say which tools those are, or lacks a tool the call needs. At most MAX_HOOKS typical hooks are
kept.

Every call is billed by NeuralBox: the `llm` cost `cost_usd` x USD_EUR is logged with the request
id as `ref` (PLANNED_EUR when NeuralBox reports no cost), and PLANNED_EUR is what the idea's cap is
checked against before the call. A run NeuralBox reports failed (its `errors`), and an
`adsinsights` answer without structured output, logs its cost, writes nothing and exits 1.

--selftest (either action) gets the heartbeat, then sends one prompt without tools ("Reply with
the single word pong", one turn), and prints `OK neuralbox <n> items; respond cost <x> EUR`, n
the tools NeuralBox lists; for `adsinsights` the heartbeat must list ADSINSIGHTS_TOOLS, checked
before the paid call. It writes and logs nothing.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from factory import costs, tables, toolbase
from factory.http import Client
from factory.providers import neuralbox

COMMAND = "nb"
PROVIDER = "neuralbox"
PLANNED_EUR = 0.5  # what one NeuralBox call is expected to cost: the cap is checked with it
NETWORKS = ["facebook", "tiktok", "snapchat", "native", "linkedin", "search"]
REGIONS = ["NAM", "EMEA", "LATAM", "APAC"]
DEFAULT_NETWORKS = "facebook,search"
DEFAULT_TOP = 10
MAX_TOP = 56  # QueryAdsInsights' rows per tile at most
ADSINSIGHTS_TOOLS = list(neuralbox.WHITELIST)  # the only tools the factory lets NeuralBox use
MAX_HOOKS = 5  # typical hooks kept per answer
SELFTEST_PROMPT = "Reply with the single word pong"
TOP_SHOWN = 5  # companies per network in the summary
COLUMNS = ["network", "total_reach", "advertisers", "top companies"]
_COUNTRY = re.compile(r"[A-Z]{2}")

ADSINSIGHTS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "category_resolved": {"type": "string"},
        "countries": {"type": "array", "items": {"type": "string"}},
        "networks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "network": {"type": "string"},
                    "total_reach": {"type": ["number", "null"]},
                    "advertisers_count": {"type": ["integer", "null"]},
                    "top_companies": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "share_pct": {"type": "number"},
                            },
                            "required": ["name", "share_pct"],
                            "additionalProperties": False,
                        },
                    },
                    "caveats": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "network",
                    "total_reach",
                    "advertisers_count",
                    "top_companies",
                    "caveats",
                ],
                "additionalProperties": False,
            },
        },
        "typical_hooks": {"type": "array", "items": {"type": "string"}},
        "not_found": {"type": "boolean"},
    },
    "required": ["category_resolved", "countries", "networks", "typical_hooks", "not_found"],
    "additionalProperties": False,
}

ADSINSIGHTS_PROMPT = """\
Summarise what AdsInsights holds on one market, as aggregated conclusions only.

1. Find the exact AdsInsights category for {category} with LookupAdsInsights \
(what="categories"), and with ListCategories if the lookup does not settle it. If no category \
matches, answer not_found true, category_resolved "", no networks and no typical_hooks, and stop.
2. Call QueryAdsInsights with section="aggregations", tile="company", sort="all", \
countries={countries}, categories=[<the category found>], top={top}, once for each network \
in {networks}.
3. Call QueryAdsInsights with section="copy", copy_kind="all", sort="all" and the same \
countries and category, once for each of those networks, to read the ad texts.

For each network report total_reach (the company tile's total_reach), advertisers_count (its \
distinct count), top_companies (each row's name, and share_pct = 100 x reach / total_reach with \
one decimal) and caveats (the answer's query.caveats, and any hint that the window was widened \
or the slice is not covered). A network whose query fails or holds nothing: total_reach and \
advertisers_count null, no top_companies, and a caveat saying what happened. Reach is never \
comparable across networks: never add networks up or compare them. typical_hooks: up to 5 \
recurring angles of the ad texts read in step 3 (the promise, the offer, the urgency...), each \
in a few words of your own. countries: the countries queried.

Never copy rows, whole ad texts, URLs or IDs into the answer: counts, shares of named \
advertisers and typical hooks only."""


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="ask NeuralBox (local agent with AdsInsights): a prompt, or a market's ad summary",
        description="Ask NeuralBox, the local agent service that holds AdsInsights and the "
        "provider keys. Every call runs an agent and is billed (docs/neuralbox.md).",
    )
    actions = parser.add_subparsers(
        dest="action", metavar="<action>", title="actions", required=True
    )

    ask = actions.add_parser(
        "ask",
        help="send one prompt and keep the answer",
        description="Send one prompt to NeuralBox and keep its answer, the structured JSON a "
        "--schema asked for, and the names of the tools it called.",
    )
    prompt = ask.add_mutually_exclusive_group()
    prompt.add_argument("--prompt", metavar="P", help="the prompt (required unless --selftest)")
    prompt.add_argument("--prompt-file", type=Path, metavar="F", help="a file holding the prompt")
    ask.add_argument(
        "--tools",
        action="append",
        metavar="A,B",
        help="the tools the agent may use, comma-separated, among "
        f"{', '.join(neuralbox.WHITELIST)} (default: none); the flag repeats",
    )
    ask.add_argument(
        "--schema",
        type=Path,
        metavar="F.json",
        help="a JSON Schema object: the answer also comes back as JSON of that shape",
    )
    ask.add_argument(
        "--max-turns",
        type=toolbase.positive_int,
        default=neuralbox.DEFAULT_MAX_TURNS,
        metavar="N",
        help="the agent's turns at most (default: %(default)s)",
    )
    ask.add_argument("--session", metavar="ID", help="resume an earlier answer's session_id")
    toolbase.add_common(ask)
    ask.set_defaults(handler=_ask)

    ads = actions.add_parser(
        "adsinsights",
        help="a market's advertisers and their shares per network, from AdsInsights",
        description="Ask NeuralBox's AdsInsights about one category in some countries: per "
        "network the total reach, the number of advertisers, the top companies' shares, the "
        "caveats, and the typical hooks. Only these conclusions are kept.",
    )
    ads.add_argument(
        "--category",
        metavar="C",
        help="the market in words (home security): NeuralBox finds its AdsInsights category "
        "(required unless --selftest)",
    )
    ads.add_argument(
        "--countries",
        metavar="FR,US",
        help=f"country codes or regions ({', '.join(REGIONS)}), comma-separated (required "
        "unless --selftest)",
    )
    ads.add_argument(
        "--networks",
        default=DEFAULT_NETWORKS,
        metavar="A,B",
        help=f"comma-separated, among {', '.join(NETWORKS)} (default: %(default)s)",
    )
    ads.add_argument(
        "--top",
        type=_top,
        default=DEFAULT_TOP,
        metavar="N",
        help=f"the top companies per network, 1 to {MAX_TOP} (default: %(default)s)",
    )
    toolbase.add_common(ads)
    ads.set_defaults(handler=_adsinsights)


@toolbase.handle_errors
def run(args: argparse.Namespace) -> int:
    return args.handler(args)


def _ask(args: argparse.Namespace) -> int:
    if args.selftest:
        return _selftest(args, required=[])
    prompt = _prompt(args)
    tools = _tools(args.tools)
    schema = _schema(args.schema)
    with toolbase.run(args, tool="nb_ask", planned_eur=PLANNED_EUR) as r:
        client = neuralbox.client(dry_run=r.dry_run)
        _require_listed(client, tools or [])
        result = neuralbox.respond(
            client,
            prompt,
            allowed_tools=tools,
            schema=schema,
            max_turns=args.max_turns,
            session_id=args.session,
        )
        _warn_denied(result)
        _log_cost(r, result, "ask")
        _require_success(result)
        r.write(
            {
                "prompt": prompt,
                "answer": result.answer,
                "structured": result.structured,
                "cost_usd": result.cost_usd,
                "tools_called": result.tools_called,
                "tools_denied": result.tools_denied,
                "session_id": result.session_id,
                "request_id": result.request_id,
            }
        )
        r.summary(ask_summary(result))
    return 0


def _adsinsights(args: argparse.Namespace) -> int:
    if args.selftest:
        return _selftest(args, required=ADSINSIGHTS_TOOLS)
    category = _category(args.category)
    countries = _countries(args.countries)
    networks = _networks(args.networks)
    prompt = ADSINSIGHTS_PROMPT.format(
        category=json.dumps(category, ensure_ascii=False),
        countries=json.dumps(countries),
        networks=", ".join(networks),
        top=args.top,
    )
    with toolbase.run(args, tool="nb_adsinsights", planned_eur=PLANNED_EUR) as r:
        client = neuralbox.client(dry_run=r.dry_run)
        _require_listed(client, ADSINSIGHTS_TOOLS)
        result = neuralbox.respond(
            client,
            prompt,
            allowed_tools=ADSINSIGHTS_TOOLS,
            schema=ADSINSIGHTS_SCHEMA,
            max_turns=adsinsights_turns(len(networks)),
            fixture="neuralbox/adsinsights",
        )
        _warn_denied(result)
        _log_cost(r, result, "adsinsights")
        _require_success(result)
        if result.structured is None:
            raise toolbase.ToolError(
                f"{PROVIDER}: no structured output: the answer is not kept "
                "(AdsInsights is kept as conclusions only)"
            )
        data = conclusions(ADSINSIGHTS_SCHEMA, result.structured)
        if isinstance(data.get("typical_hooks"), list):
            data["typical_hooks"] = data["typical_hooks"][:MAX_HOOKS]
        r.write(data)
        r.summary(adsinsights_summary(data, category, countries))
    return 0


def adsinsights_turns(networks: int) -> int:
    """The agent's turns for `networks` networks: a lookup or two, two queries a network (when
    it makes them one at a time) and the answer, never under the default 8."""
    return max(neuralbox.DEFAULT_MAX_TURNS, 4 + 2 * networks)


def conclusions(schema: dict, value: Any) -> Any:
    """`value` cut to what `schema` describes: an object keeps its declared properties only, an
    array its items, each cut the same way; a value of the wrong shape is emptied (null for an
    object or a scalar, [] for an array), so nothing the schema does not describe is kept."""
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict):
            return None
        properties = schema.get("properties", {})
        return {
            key: conclusions(properties[key], item)
            for key, item in value.items()
            if key in properties
        }
    if kind == "array":
        if not isinstance(value, list):
            return []
        return [conclusions(schema.get("items", {}), item) for item in value]
    return value if value is None or isinstance(value, str | int | float | bool) else None


def ask_summary(result: neuralbox.NBResult) -> str:
    parts = [result.answer]
    if result.structured is not None:
        parts.append("structured:\n" + json.dumps(result.structured, indent=2, ensure_ascii=False))
    if result.tools_called:
        parts.append(f"tools called: {', '.join(dict.fromkeys(result.tools_called))}")
    return "\n".join(parts)


def adsinsights_summary(data: dict, category: str, countries: list[str]) -> str:
    where = ", ".join(countries)
    if data.get("not_found"):
        return (
            f"no AdsInsights category matches {json.dumps(category, ensure_ascii=False)} ({where})"
        )
    networks = [network for network in data.get("networks") or [] if isinstance(network, dict)]
    rows = [
        {
            "network": network.get("network"),
            "total_reach": _reach(network.get("total_reach")),
            "advertisers": network.get("advertisers_count"),
            "top companies": ", ".join(
                _share(company)
                for company in (network.get("top_companies") or [])[:TOP_SHOWN]
                if isinstance(company, dict)
            ),
        }
        for network in networks
    ]
    lines = [
        f"{data.get('category_resolved') or category} in {where}",
        tables.render(rows, COLUMNS),
    ]
    hooks = [hook for hook in data.get("typical_hooks") or [] if isinstance(hook, str)]
    if hooks:
        lines.append(f"typical hooks: {'; '.join(hooks)}")
    caveats = [
        f"  {network.get('network')}: {caveat}"
        for network in networks
        for caveat in network.get("caveats") or []
        if isinstance(caveat, str)
    ]
    if caveats:
        lines += ["caveats:", *caveats]
    return "\n".join(lines)


def _selftest(args: argparse.Namespace, required: list[str]) -> int:
    """The heartbeat, the `required` tools in its list, then one prompt without tools."""
    client = neuralbox.client(dry_run=args.dry_run)
    tools = _require_listed(client, required)
    result = neuralbox.respond(client, SELFTEST_PROMPT, max_turns=1)
    _require_success(result)
    if not result.answer.strip():
        raise toolbase.ToolError(
            f"{PROVIDER}: the selftest's respond call came back without an answer"
        )
    cost = (
        "not reported" if result.cost_usd is None else f"{result.cost_usd * costs.USD_EUR:.4f} EUR"
    )
    print(f"OK {PROVIDER} {len(tools)} items; respond cost {cost}")
    return 0


def _log_cost(r: toolbase.Run, result: neuralbox.NBResult, action: str) -> None:
    """Log the call's `llm` cost: what NeuralBox reported, in EUR; the planned cost without one."""
    if result.cost_usd is None:
        amount = PLANNED_EUR
        note = f"nb {action}, cost not reported: the planned {PLANNED_EUR:g} EUR"
    else:
        amount = result.cost_usd * costs.USD_EUR
        note = f"nb {action}, {result.cost_usd:g} USD"
    r.log("llm", PROVIDER, amount, ref=result.request_id or "", note=note)


def _require_listed(client: Client, tools: list[str]) -> list[str]:
    """The tools NeuralBox lists (fetched once per client), refusing to go on, before the paid
    call, when it lists none or lacks one of `tools`."""
    listed = neuralbox.listed_tools(client)
    missing = [name for name in tools if name not in listed]
    if missing:
        raise toolbase.ToolError(f"{PROVIDER}: the heartbeat lists no {', '.join(missing)}")
    return listed


def _warn_denied(result: neuralbox.NBResult) -> None:
    """One stderr line naming the tools the agent tried and the block refused, if any."""
    if result.tools_denied:
        denied = ", ".join(dict.fromkeys(result.tools_denied))
        print(f"{COMMAND}: the block denied the agent {denied}", file=sys.stderr)


def _require_success(result: neuralbox.NBResult) -> None:
    if result.errors:
        raise toolbase.ToolError(f"{PROVIDER}: the run failed: {'; '.join(result.errors)}")


def _prompt(args: argparse.Namespace) -> str:
    if args.prompt_file is not None:
        try:
            prompt = args.prompt_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise toolbase.UsageError(
                f"cannot read {args.prompt_file}: {exc.strerror or exc}"
            ) from None
        except ValueError:  # not UTF-8
            raise toolbase.UsageError(f"{args.prompt_file} is not UTF-8 text") from None
    elif args.prompt is not None:
        prompt = args.prompt
    else:
        raise toolbase.UsageError("give --prompt P or --prompt-file F")
    if not prompt.strip():
        raise toolbase.UsageError("the prompt is empty")
    return prompt


def _tools(values: list[str] | None) -> list[str] | None:
    """The --tools names, each once, in order; None when the flag is not given."""
    if values is None:
        return None
    names: list[str] = []
    for value in values:
        for part in value.split(","):
            name = part.strip()
            if name and name not in names:
                names.append(name)
    if not names:
        raise toolbase.UsageError(f"--tools names no tool (among {', '.join(neuralbox.WHITELIST)})")
    for name in names:
        if name not in neuralbox.WHITELIST:
            raise toolbase.UsageError(
                f"--tools: {name!r} is not a tool the factory lets NeuralBox use "
                f"(only {', '.join(neuralbox.WHITELIST)})"
            )
    return names


def _schema(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise toolbase.UsageError(f"cannot read {path}: {exc.strerror or exc}") from None
    except ValueError as exc:  # not JSON, or not UTF-8
        raise toolbase.UsageError(f"{path} is not valid JSON: {exc}") from None
    if not isinstance(schema, dict):
        raise toolbase.UsageError(f"{path} must hold a JSON Schema, a JSON object")
    return schema


def _category(text: str | None) -> str:
    category = " ".join((text or "").split())
    if not category:
        raise toolbase.UsageError("--category is required: the market in words (home security)")
    return category


def _countries(text: str | None) -> list[str]:
    """The --countries codes, uppercased, each once; regions (EMEA...) are codes too."""
    if text is None:
        raise toolbase.UsageError(
            "--countries is required: country codes or regions, comma-separated (FR,US)"
        )
    codes: list[str] = []
    for part in text.split(","):
        code = part.strip().upper()
        if not code:
            continue
        if not (_COUNTRY.fullmatch(code) or code in REGIONS):
            raise toolbase.UsageError(
                f"{part.strip()!r} is not a country code (FR, US...) or a region "
                f"({', '.join(REGIONS)})"
            )
        if code not in codes:
            codes.append(code)
    if not codes:
        raise toolbase.UsageError("--countries names no country (FR,US)")
    return codes


def _networks(text: str) -> list[str]:
    names: list[str] = []
    for part in text.split(","):
        name = part.strip().lower()
        if not name:
            continue
        if name not in NETWORKS:
            raise toolbase.UsageError(f"unknown network {name!r} (networks: {', '.join(NETWORKS)})")
        if name not in names:
            names.append(name)
    if not names:
        raise toolbase.UsageError(f"--networks names no network ({', '.join(NETWORKS)})")
    return names


def _top(text: str) -> int:
    """argparse type: the companies per network, 1 to MAX_TOP."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number") from None
    if not 1 <= value <= MAX_TOP:
        raise argparse.ArgumentTypeError(f"{text!r} is not from 1 to {MAX_TOP}")
    return value


def _reach(value: object) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        return None
    return f"{value:,.0f}"


def _share(company: dict) -> str:
    name = company.get("name")
    share = company.get("share_pct")
    if isinstance(share, bool) or not isinstance(share, int | float) or not math.isfinite(share):
        return str(name)
    return f"{name} {share:.1f}%"
