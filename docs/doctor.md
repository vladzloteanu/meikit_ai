# Doctor

`uv run factory doctor` says which secrets, accounts and assets exist on this machine, which
channels and recipes they unlock, and what to fix. `/factory` runs it with `--offline` at every
start, `/factory-setup` runs it to prove each asset it creates, and `make check` runs it with
`--offline` after the tests. The command is `tools/factory/tools/doctor.py`; the Vercel CLI's
login is read by `tools/factory/vercel.py`.

## Running it

    uv run factory doctor [--json] [--offline | --live]

| Mode | Does |
|---|---|
| default | every check below: the secrets, free read-only calls (SearchAPI's account, NeuralBox's heartbeat, one Arctic Shift search, RDAP), `vercel whoami`, Vercel's `GET /v2/user`, `gh auth status` and `dig` |
| `--offline` | no network call at all, no API and no CLI that calls one: it reads the secrets, in well under a second, and shows each network check as `skip` |
| `--live` | adds each provider's selftest (`factory <tool> --selftest`, run in-process): real calls that cost a few cents (SearchAPI, SE Ranking, Firecrawl, NeuralBox's one-turn prompt) and log nothing |
| `--json` | prints `{"checks": [{"name", "level", "ok", "detail", "blocks"}], "eligible_channels", "eligible_recipes"}` instead of the table |

It prints a table `check | level | detail`, then `eligible channels: …` and `eligible recipes: …`.
It exits 1 when a check fails, 0 otherwise, warnings included. A detail reports presence only:
no secret value and no Vercel token ever appears in it. A network check makes one attempt with a
20 s timeout (30 s for a command), so a provider that is down costs 20 s, not minutes of retries.

## The checks

In the order they run. "Network: partly" means the check runs offline and adds a call online.

| Check | Network | Not ok | Passes when | Blocks | Fix |
|---|---|---|---|---|---|
| `secrets.master_key` | no | fail | `secrets/master.key` opens `secrets/config.yml.enc` | every tool that reads a key | [secrets.md](secrets.md) |
| `secrets.providers` | partly | fail | the SearchAPI, SE Ranking and Firecrawl keys are set; online, SearchAPI's account (`GET /me`, free) has searches left this month | serp_ads, ad_library, keyword_volume, pricing_scan | `uv run factory secrets-import-nb`; a used-up quota names its reset date |
| `nb.heartbeat` | yes | warn | NeuralBox answers its heartbeat at `nb.url` and lists the AdsInsights tools | nb adsinsights | start NeuralBox ([neuralbox.md](neuralbox.md)) |
| `provider.arcticshift` | yes | warn | one 30-day posts search answers; a throttle is waited out once, 60 s at most | reddit_mentions | none: Arctic Shift is free and `reddit_mentions` waits throttles out |
| `vercel.login` | yes | fail | `vercel whoami` passes | launch | `vercel login` |
| `vercel.scope` | yes | fail | the CLI works in the personal scope (next section) | launch | `vercel switch <username>` |
| `vercel.plan` | yes | warn | the account's plan (`GET /v2/user`) is not Hobby | paid traffic | Hobby forbids commercial use: upgrade to Pro before the first paid traffic |
| `gh.auth` | yes | fail | `gh auth status` passes, so `gh` can create the idea repos | launch | `gh auth login` |
| `domain.meikit` | yes | warn | `meikit.ai` is registered (RDAP) and points at Vercel (`dig +short`: `76.76.21.21` or a `vercel-dns` CNAME) | launch on `<slug>.meikit.ai` | free: buy it, `/factory-setup` step 1; registered but not on Vercel: confirm with the owner or pick another lab domain |
| `assets.meta` | no | warn | `accounts.meta.ad_account_id` is set | meta_feed | `/factory-setup` |
| `assets.google_ads` | no | warn | `accounts.google_ads.customer_id` is set | google_search | `/factory-setup` |
| `assets.stripe` | no | warn | `accounts.stripe.secret_key` is set | pre-order | `/factory-setup` |
| `assets.sending_domain` | no | warn | `accounts.sending_domain.domain` is set | cold_email_b2b | `/factory-setup` |
| `assets.resend` | no | warn | `accounts.resend.account_key` is set | the stand's email sending | `/factory-setup` |
| `assets.turnstile` | no | warn | `accounts.turnstile.site_key` is set | the stand's anti-bot check | `/factory-setup` |

SearchAPI's quota: a used-up month fails `secrets.providers` with "SearchAPI monthly quota used up
(resets <date>); serp_ads and ad_library are blocked", the date being the end of SearchAPI's
billing period (none when SearchAPI answers the used-up 429 itself). A key SearchAPI refuses (401,
403) fails; SearchAPI down or rate-limiting is a warning.

`--live` adds, after these, one selftest per provider: `selftest.searchapi` (`serp_ads`),
`selftest.seranking` (`keyword_volume`) and `selftest.firecrawl` (`pricing_scan`) fail when they
fail; `selftest.neuralbox` (`nb adsinsights`, which also checks the AdsInsights tools are
listed), `selftest.arcticshift` (`reddit_mentions`), `selftest.algolia` (`hn_mentions`) and
`selftest.rdap` (`domain_check`) warn. A selftest that crashes is reported as one row, `crashed:
<exception type>`, and the other checks still run.

## What unlocks each channel and recipe

| Channel | Eligible when |
|---|---|
| `reddit_reply`, `reddit_post`, `linkedin_outreach`, `community_post` | always: a human posts and sends |
| `google_search` | `assets.google_ads` passes |
| `meta_feed` | `assets.meta` passes |
| `cold_email_b2b` | `assets.sending_domain` passes |
| `tiktok` | never yet: it has no asset check |

Every recipe is eligible but `pre-order`, which needs `assets.stripe`: its checkout takes payments.
An asset passes on the presence of its key: whether the account is in good standing (verified ad
account, warmed domain) is for `/factory-setup` to prove.

## The Vercel scope

The factory deploys from Vlad's personal Vercel account, in its personal scope, never a team
scope (design D9). The CLI keeps its scope in `config.json` (`~/Library/Application
Support/com.vercel.cli/`): `currentTeam` is a team id, absent or null in the personal scope.
`vercel.scope` passes when there is no current team on an account that has a personal scope, and
fails on a team naming `vercel switch <username>`, the username read from `GET /v2/user`. That
call is the only one made with the CLI's token (read from `auth.json`, never printed); the doctor
never runs `vercel switch` and writes nothing. `vercel.login` runs first, so the CLI has renewed an
expired token before the doctor reads it.

A team-based Vercel account (`"version": "northstar"` in `GET /v2/user`) has no personal scope:
its CLI always works in a team, the account's default team when `currentTeam` is unset, and
`vercel switch <username>` answers "You cannot set your Personal Account as the scope." (Vercel
CLI 63). On such an account `vercel.scope` always fails, saying so. The account logged in on this
machine is one, and on 2026-10-21 its only team, which is also its default, is a company team: it
has no scope D9 allows. Getting one (a personal team to switch to, or a separate personal login)
and teaching `vercel.scope` to accept it is a setup decision; until then the launch stays blocked.
