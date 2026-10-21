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

    {"prompt", "answer", "structured", "cost_usd", "tools_called", "session_id", "request_id"}

`--schema` (a JSON Schema object) makes NeuralBox also answer in that shape (`structured`);
`--session` resumes the conversation of an earlier answer's `session_id`; `--tools` names the
tools the agent is given (see the whitelist below).

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
reasoning or what the tools returned. An answer without structured output is not kept at all.
`tools_called` holds tool names only, never the tools' inputs or outputs.

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

## The whitelist

`allowed_tools` names the tools the agent is given, as NeuralBox's `/heartbeat` lists them.
`nb adsinsights` gives three: `mcp__tools__LookupAdsInsights`, `mcp__tools__ListCategories` and
`mcp__tools__QueryAdsInsights`. `nb ask --tools` takes any. NeuralBox refuses a bare name
(`QueryAdsInsights`) with a 400 "Unknown tool": only its built-ins (`Read`, `WebSearch`...) and
`mcp__<server>__<tool>` names pass.

The whitelist steers the agent but does not fence it. Every call runs in `bypassPermissions` mode,
where NeuralBox's `allowed_tools` pre-approves the tools it names and denies none (NeuralBox's
`docs/agents.md`, "Whitelists"). An agent could still reach a tool off the list, so what keeps the
factory safe is what it asks. The `tools_called` of an answer show what the agent did use.

## What never to ask it

- **Spending.** NeuralBox's Google, Meta and TikTok Ads tools act on Dolead's ad accounts. The
  factory spends only from its own accounts: never ask NeuralBox to create, change, launch or pay
  for anything.
- **Dolead client data.** Its ad-account, CRM, lead and reporting tools hold the data of Dolead's
  clients. Never ask for it, and never put it into an idea file. AdsInsights' aggregates on public
  advertisers are the only Dolead-held data the factory keeps, and only as `nb adsinsights`'
  conclusions.
- **Secrets.** Every prompt ends with the same three rules: say exactly which tool failed, never
  invent numbers, never print secret values.
