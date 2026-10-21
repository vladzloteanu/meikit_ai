# NeuralBox

NeuralBox is Dolead's agent service: Claude with about 350 MCP tools and the provider keys behind
them, run on this machine at `nb.url` (`http://127.0.0.1:3076`). The factory reaches it for one
thing no other provider gives: AdsInsights, the ad-intelligence base that says which advertisers
hold a market's reach, per country and per network. The triage step reads it through
`factory nb adsinsights`. `factory nb ask` puts a plain question to the model, with no tool at all.

The client is `tools/factory/providers/neuralbox.py`, the command `tools/factory/tools/nb.py`.

## The two commands

    uv run factory nb ask --idea S (--prompt P | --prompt-file F) [--schema F.json]
                          [--max-turns 8] [--session ID]
    uv run factory nb adsinsights --idea S --category C --countries FR,US
                                  [--networks facebook,search] [--top 10]

`nb ask` sends one prompt with no tool: every tool and server NeuralBox has is denied, the
AdsInsights ones included. It writes `ideas/<slug>/research/nb_ask_<ts>.json`:

    {"prompt", "answer", "structured", "cost_usd", "tools_called", "tools_denied", "session_id",
     "request_id"}

`--schema` (a JSON Schema object) makes NeuralBox also answer in that shape (`structured`).
`--session` resumes the conversation of an earlier answer's `session_id`. `nb ask` keeps its
answer as written, which is why it has no tool: AdsInsights is reachable only through
`nb adsinsights`, which keeps conclusions.

`nb adsinsights` asks about one market. It finds the category with `LookupAdsInsights` (and
`ListCategories` when needed). Then, for each network, it makes one `QueryAdsInsights` call on
the `company` tile of `aggregations` at `sort=all` (total reach, number of advertisers, the top
companies' reach), and one on `copy` (the ad texts behind the typical hooks). It writes
`ideas/<slug>/research/nb_adsinsights_<ts>.json`:

    {"category_resolved", "countries",
     "networks": [{"network", "total_reach", "advertisers_count",
                   "top_companies": [{"name", "share_pct"}], "caveats"}],
     "typical_hooks", "not_found"}

- The networks are facebook, tiktok, snapchat, native, linkedin and search.
- Reach is per network and never comparable across networks: never add networks up or compare
  them.
- `share_pct` is a company's share of its network's total reach.
- A network whose query failed has null figures and a caveat saying so.
- `not_found` says no AdsInsights category matched `--category`.

Both commands take the common flags (`--dry-run`, `--json`, `--out`, `--phase`, `--force`) and
`--selftest`. The selftest fetches the heartbeat, then sends one prompt with no tool ("Reply with
the single word pong", one turn), and prints
`OK neuralbox <tools listed> items; respond cost <x> EUR`. `nb adsinsights --selftest` first
checks that the heartbeat lists its three tools.

## The cost

Every call runs an agent, and NeuralBox bills it: its answer reports `cost_usd`. The command logs
it as one `llm` line, provider `neuralbox`, `cost_usd × 0.92` EUR, with NeuralBox's request id as
`ref`. Before each call, the idea's cap is checked against a planned 0.5 EUR. That same 0.5 EUR
is logged in two cases:

- NeuralBox reports no cost.
- The request left and its outcome is unknown: no answer (a network error, the client's 600 s
  timeout), a 5xx, or an answer that is not a JSON object. The line's note then reads
  `unconfirmed: <reason>`, so the cap counts the call as spent.

A call NeuralBox refuses (a 4xx) costs nothing and logs nothing. So does a call that never
leaves, because the heartbeat failed (see "The block"). A run NeuralBox reports failed (its
`errors`: a timeout, the turns used up, a structured output that is not a JSON object) logs its
reported cost, writes nothing and exits 1.

A call is never retried, since a second attempt would run, and bill, the agent again. NeuralBox
stops a run after 540 s, before the client gives up at 600 s, so a long run still answers with its
cost.

Measured on 2026-10-21:

| Call | Cost | Time |
|------|------|------|
| Selftest, before the block | 0.0612 EUR (0.0665 USD) | 10 s |
| Selftest, with the block, final code | 0.0337 EUR | 6 s |
| `nb adsinsights`, one country, two networks, before the block | 0.155 USD | 25 s |

## The persistence rule

AdsInsights is kept in an idea only as aggregated conclusions: counts, shares of named
advertisers, typical hooks. `nb adsinsights` therefore writes the structured answer only:

- cut to what its schema describes, anything else NeuralBox returns being dropped;
- every string cut at 200 characters;
- at most five typical hooks;
- never the answer text, the agent's reasoning or what the tools returned.

An answer without a structured JSON object is not kept at all. `tools_called` and `tools_denied`
hold tool names only, never the tools' inputs or outputs. `nb ask` reaches no AdsInsights tool,
so its verbatim answer holds only what the model writes.

## Secrets and what NeuralBox sees

Everything NeuralBox returns passes through `secrets.redact` before the factory keeps it, prints
it or raises it: the answer, every string of the structured output, the errors, the tool names
and the ids. Every failure is one `ProviderError` line on stderr, redacted the same way. A dry
run is the only exception: it answers from canned fixtures and loads no secret. `redact` replaces
with `***` any string of 8 characters or more that the factory config holds, so it catches the
key and the user email.

NeuralBox does see the user email. It receives `nb.user_email` with every call, checks it, and
keeps it in its own call log. It also writes "The current user is: <user_name> (email: <email>)"
into the agent's instructions whenever a request carries a `user_name`. The factory sends a
`user_id` instead, and NeuralBox then adds no user line (its `src/services/chat_service.py`). The
model of a factory run is therefore not handed the address. Redaction stays as the safety net.

## Who the factory is to NeuralBox

NeuralBox refuses a call that does not say whom it is for. Every request carries `properties`:

- `project: astrafable`;
- `user_id: astrafable-factory` (a 422 without a user id or name);
- `user_email`, the secret `nb.user_email`: a user NeuralBox knows, with API access. Any other
  address is a 403: "Email domain not allowed" outside its allowed domains, "User not found"
  inside them.

The key is `nb.api_key`, copied from NeuralBox's `.env` by `uv run factory secrets-import-nb`. It
travels in the `X-API-Key` header only.

`nb.user_email` was `astrafable@local` until 2026-10-21, when NeuralBox refused it ("Email domain
not allowed"). It was then set, through `secrets.save`, to Vlad's Dolead work address, the
`DEV_EMAIL` of NeuralBox's `.env`. Its value is stored only in `secrets/config.yml.enc`, and sent
only to NeuralBox, as above.

## The block

The factory lets NeuralBox call three tools and nothing else, the whitelist:

- `mcp__tools__LookupAdsInsights`
- `mcp__tools__ListCategories`
- `mcp__tools__QueryAdsInsights`

They read AdsInsights' aggregates on public advertisers and spend nothing. `nb adsinsights` uses
the three. `nb ask` and the selftest use none: they send an empty `allowed_tools`. The client
refuses any other tool before sending anything (`neuralbox.respond`), whoever calls it.

Every call carries the block. `allowed_tools` names the whitelisted tools the call uses, as
`/heartbeat` lists them (a bare name like `QueryAdsInsights` is a 400 "Unknown tool").
`disallowed_tools` denies everything else:

- NeuralBox's thirteen Claude Code built-ins: `Read`, `Write`, `Edit`, `MultiEdit`, `Bash`,
  `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Task`, `TodoWrite`, `NotebookEdit`, `Skill`. They
  are denied on every call, whatever the heartbeat lists.
- Every tool `/heartbeat` lists (357 on 2026-10-21), including the whitelisted ones a call does
  not use.
- Whole, every listed MCP server holding none of the call's tools (`mcp__FacebookAds`,
  `mcp__GoogleAds`, `mcp__HubSpot`...). A tool added to one of them later is therefore denied
  too.
- Whole, the three servers NeuralBox attaches to runs from its tool config:
  - `mcp__Looker` is attached whenever NeuralBox's config declares it, which it does today, and
    is never listed in the heartbeat.
  - `mcp__BrowserAutomation` lists sixteen tools when configured.
  - `mcp__Chart` lists its tools when configured with external rendering.

The client fetches the tool list once per run (`GET /heartbeat`) and keeps it. If the heartbeat
cannot be read or lists no tools, the block cannot be built, so no call is made: one line on
stderr, exit 1, nothing spent. A run whose whitelisted tools the heartbeat does not list stops
there too, before the paid call.

**Why a deny list and not a permission mode.** The safer design would be a permission mode that
denies any tool missing from `allowed_tools`, without `bypassPermissions`. NeuralBox has none.

- It accepts four modes: `default`, `acceptEdits`, `bypassPermissions` and `plan`. Anything else,
  `dontAsk` included, is a 422.
- In every mode but `bypassPermissions`, a tool missing from `allowed_tools` goes to NeuralBox's
  own `can_use_tool` (its `filesystem_guard`). That guard lets through any tool it has no specific
  rule against: it ends in `return _allow(input_data)`. So no mode denies, and none hangs either.
- Under `bypassPermissions`, `allowed_tools` alone denies nothing (NeuralBox's `docs/agents.md`,
  "Whitelists").

The deny rules of `disallowed_tools` do hold under `bypassPermissions`, as measured below. So
calls keep `bypassPermissions`, and the deny list is the fence.

**What was measured** (2026-10-21, real calls, on no idea's ledger):

| What was denied | What the agent was asked | What happened | Cost |
|-----------------|--------------------------|---------------|------|
| `WebSearch`, a built-in in the block | Search the web with `WebSearch` | It answered "WEBSEARCH NOT AVAILABLE. There is no tool named WebSearch in this session" and called no tool. A denied built-in is gone from the agent's tools. | 0.098 EUR |
| `mcp__SearchAPI__GetLocations`, by name and by server | Call it | It tried, and Claude Code refused the call before it ran: "Permission to use mcp__SearchAPI__GetLocations has been denied." Nothing was fetched. A denied MCP tool can stay visible to the agent. | 0.0415 EUR |
| `mcp__SearchAPI`, the whole server only, none of its tools by name | Call `mcp__SearchAPI__GetLocations` | The same refusal. A whole-server entry is enough. This is what guards Looker, which the heartbeat never lists. | 0.0893 EUR |

NeuralBox lists a refused attempt among the tools called. The client moves it to `tools_denied`,
and the command warns on stderr: `nb: the block denied the agent <tool>`.

**What the block does not cover:**

- **External MCP servers configured in NeuralBox's `extensions.mcp_servers`.** NeuralBox attaches
  them to every run and never lists them, so the factory cannot know their names to deny them.
  None is configured today. One added there later would be open to the agent.
- **Agents started by an agent tool.** `Workflow` and the like may start other agents, and whether
  those agents are held to the same deny rules is not verified. Claude Code applies a session's
  deny rules per tool call, but no call has tested an agent started this way.
- **Built-ins NeuralBox does not let a caller deny.** These are `ToolSearch`, the session and
  agent tools (`Workflow`, `ListAgents`, `ScheduleWakeup`, `CronCreate`...) and the MCP resource
  readers. NeuralBox refuses any non-`mcp__` name outside its thirteen built-ins (400). None of
  them spends or reaches Dolead's accounts or data by itself, and NeuralBox's own tool servers
  serve tools only, no resources.

## What never to ask it

The block refuses these tools, within the limits above. Still, never ask for them:

- **Spending.** NeuralBox's Google, Meta and TikTok Ads tools act on Dolead's ad accounts. The
  factory spends only from its own accounts: never ask NeuralBox to create, change, launch or pay
  for anything.
- **Dolead client data.** Its ad-account, CRM, lead and reporting tools, Looker included, hold the
  data of Dolead's clients. Never ask for it, and never put it into an idea file. AdsInsights'
  aggregates on public advertisers are the only Dolead-held data the factory keeps, and only as
  `nb adsinsights`' conclusions.
- **Secrets.** Every prompt ends with the same three rules: say exactly which tool failed, never
  invent numbers, never print secret values.
