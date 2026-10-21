# NeuralBox

NeuralBox is Dolead's agent service: Claude with about 350 MCP tools and the provider keys behind
them, run on this machine at `nb.url` (`http://127.0.0.1:3076`). The factory reaches it for one
thing no other provider gives: AdsInsights, the ad-intelligence base that says which advertisers
hold a market's reach, per country and per network. The triage step reads it through
`factory nb adsinsights`; `factory nb ask` sends any other prompt.

The client is `tools/factory/providers/neuralbox.py`, the command `tools/factory/tools/nb.py`.

## The two commands

    uv run factory nb ask --idea S (--prompt P | --prompt-file F) [--tools A,B] [--schema F.json]
                          [--max-turns 8] [--session ID]
    uv run factory nb adsinsights --idea S --category C --countries FR,US
                                  [--networks facebook,search] [--top 10]

`nb ask` sends one prompt and writes `ideas/<slug>/research/nb_ask_<ts>.json`:

    {"prompt", "answer", "structured", "cost_usd", "tools_called", "tools_denied", "session_id",
     "request_id"}

`--schema` (a JSON Schema object) makes NeuralBox also answer in that shape (`structured`);
`--session` resumes the conversation of an earlier answer's `session_id`; `--tools` names the
tools the agent may use, among the three AdsInsights tools only (see the block below). Without
`--tools` the agent has no tool at all: a plain question to the model.

`nb adsinsights` asks about one market: the category found with `LookupAdsInsights` (and
`ListCategories` when needed), then for each network one `QueryAdsInsights` call on the `company`
tile of its `aggregations` at `sort=all` (total reach, number of advertisers, the top companies'
reach), and one on its `copy` (the ad texts behind the typical hooks). It writes
`ideas/<slug>/research/nb_adsinsights_<ts>.json`:

    {"category_resolved", "countries",
     "networks": [{"network", "total_reach", "advertisers_count",
                   "top_companies": [{"name", "share_pct"}], "caveats"}],
     "typical_hooks", "not_found"}

The networks are facebook, tiktok, snapchat, native, linkedin and search. Reach is per network and
never comparable across networks: never add networks up or compare them. `share_pct` is a
company's share of its network's total reach; a network whose query failed has null figures and a
caveat saying so; `not_found` says no AdsInsights category matched `--category`.

Both take the common flags (`--dry-run`, `--json`, `--out`, `--phase`, `--force`) and
`--selftest`: the heartbeat, then one prompt without tools ("Reply with the single word pong", one
turn), printing `OK neuralbox <tools listed> items; respond cost <x> EUR`. `nb adsinsights
--selftest` first checks that the heartbeat lists its three tools.

## The cost

Every call runs an agent and NeuralBox bills it: its answer reports `cost_usd`. The command logs it
as one `llm` line, provider `neuralbox`, `cost_usd × 0.92` EUR, with NeuralBox's request id as
`ref` (the planned 0.5 EUR when NeuralBox reports no cost). The idea's cap is checked against
0.5 EUR per call before the call is made. Measured on 2026-10-21: the selftest's pong cost
0.0665 USD in 10 s; an `nb adsinsights` call for one country and two networks 0.155 USD in 25 s.

A call is never retried: a second attempt would run, and bill, the agent again. NeuralBox stops a
run after 540 s, before the client gives up at 600 s, so a long run still answers with its cost.
A call NeuralBox refuses (a 4xx) cost nothing and logs nothing. A run it reports failed (its
`errors`: a timeout, the turns used up) logs its cost, writes nothing and exits 1. A 500 or a
network error may have spent money the factory cannot see; NeuralBox's own call log holds it.

## The persistence rule

AdsInsights is kept in an idea only as aggregated conclusions: counts, shares of named
advertisers, typical hooks. So `nb adsinsights` writes the structured answer only, cut to what its
schema describes (anything else NeuralBox returns is dropped), never the answer text, the agent's
reasoning or what the tools returned, and at most five typical hooks. An answer without
structured output is not kept at all. `tools_called` and `tools_denied` hold tool names only,
never the tools' inputs or outputs.

`nb ask` keeps its answer as written. AdsInsights therefore goes through `nb adsinsights`, never
through `nb ask`.

## Who the factory is to NeuralBox

NeuralBox refuses a call that does not say whom it is for. Every request carries `properties`:
`project: astrafable`, `user_name: astrafable-factory` (without these two: 422), and `user_email`,
the secret `nb.user_email`: a user NeuralBox knows, with API access. It refuses any other address
with a 403 ("Email domain not allowed" outside its allowed domains, "User not found" inside them).
The key is `nb.api_key` (copied from NeuralBox's `.env` by `uv run factory secrets-import-nb`) and
travels in the `X-API-Key` header only.

`nb.user_email` was `astrafable@local` until 2026-10-21, when NeuralBox refused it ("Email domain
not allowed"). It was then set, through `secrets.save`, to Vlad's Dolead work address, the
`DEV_EMAIL` of NeuralBox's `.env`. The value lives in `secrets/config.yml.enc` only.

## The block

NeuralBox can call nothing for the factory but three tools, the whitelist:
`mcp__tools__LookupAdsInsights`, `mcp__tools__ListCategories` and `mcp__tools__QueryAdsInsights`.
They read AdsInsights' aggregates on public advertisers and spend nothing. `nb adsinsights` uses
the three; `nb ask --tools` takes some of them and refuses any other name (exit 2); without
`--tools`, and in the selftest, a call uses none. The client refuses any other tool too
(`neuralbox.respond`), whoever calls it.

Every call carries the block. `allowed_tools` names the whitelisted tools the call uses, as
NeuralBox's `/heartbeat` lists them. NeuralBox refuses a bare name like `QueryAdsInsights` (400
"Unknown tool"). `disallowed_tools` denies everything else:

- every tool `/heartbeat` lists (357 on 2026-10-21), the whitelisted ones the call does not use
  included;
- every listed MCP server holding none of the tools the call uses (`mcp__FacebookAds`,
  `mcp__GoogleAds`, `mcp__HubSpot`...), whole, so a tool added to it later is denied too;
- the MCP servers NeuralBox adds to some runs without listing them (`mcp__BrowserAutomation`,
  `mcp__Looker`, `mcp__Chart`), whole.

The client fetches the tool list once per run (`GET /heartbeat`) and keeps it. When the heartbeat
cannot be read or lists no tools, the block cannot be built, so no call is made: one line on
stderr, exit 1, nothing spent. A run whose whitelisted tools the heartbeat does not list stops
there too, before the paid call.

**Why a deny list and not a permission mode.** The safer design would deny any tool missing from
`allowed_tools` through the permission mode alone, without `bypassPermissions`. NeuralBox has no
such mode. It accepts four (`default`, `acceptEdits`, `bypassPermissions`, `plan`; anything else,
`dontAsk` included, is a 422). In every mode but `bypassPermissions`, a tool missing from
`allowed_tools` goes to NeuralBox's own `can_use_tool` (its `filesystem_guard`). That guard lets
through any tool it has no specific rule against: it ends in `return _allow(input_data)`. So no
mode denies, and none hangs either. Under `bypassPermissions`, `allowed_tools` alone denies
nothing (NeuralBox's `docs/agents.md`, "Whitelists"). The deny rules of `disallowed_tools` hold in
every mode, so calls keep `bypassPermissions` and the deny list is the fence.

**How a denied tool behaves**, measured on 2026-10-21:

- *A built-in in the block is gone from the agent's tools.* Asked to use `WebSearch`, the agent
  answered "WEBSEARCH NOT AVAILABLE. There is no tool named WebSearch in this session", and
  called no tool (0.098 EUR).
- *A denied MCP tool can stay visible to the agent, but its call is refused before it runs.*
  Told to call `mcp__SearchAPI__GetLocations`, the agent tried. The tool's output was "Permission
  to use mcp__SearchAPI__GetLocations has been denied.", and nothing was fetched (0.0415 EUR).
  NeuralBox lists such an attempt among the tools called. The client moves it to `tools_denied`
  instead, and the command warns on stderr: `nb: the block denied the agent <tool>`.

**What the block cannot reach.** Some Claude Code built-ins are tools NeuralBox neither lists
nor lets a caller deny: `ToolSearch`, its session and agent tools (`Workflow`, `ListAgents`,
`ScheduleWakeup`, `CronCreate`...), and its MCP resource readers. NeuralBox refuses any
non-`mcp__` name outside its own thirteen built-ins (400). None of them spends or reaches Dolead's
accounts or data by itself. The tools that do (NeuralBox's MCP tools, `Bash`, `WebFetch`,
`WebSearch`) are all on the deny list, and NeuralBox's own tool servers serve tools only, no
resources.

## What never to ask it

The block makes these calls impossible; still, never ask for them:

- **Spending.** NeuralBox's Google, Meta and TikTok Ads tools act on Dolead's ad accounts. The
  factory spends only from its own accounts: never ask NeuralBox to create, change, launch or pay
  for anything.
- **Dolead client data.** Its ad-account, CRM, lead and reporting tools hold the data of Dolead's
  clients. Never ask for it, and never put it into an idea file. AdsInsights' aggregates on public
  advertisers are the only Dolead-held data the factory keeps, and only as `nb adsinsights`'
  conclusions. `nb ask` keeps its answer as written, so AdsInsights questions go through
  `nb adsinsights`, even though `nb ask --tools` can reach the same tools.
- **Secrets.** Every prompt ends with the same three rules: say exactly which tool failed, never
  invent numbers, never print secret values.
