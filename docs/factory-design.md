# Ideas Factory — design

**Status:** approved 2026-10-20 (open questions answered, section 16) · **Date:** 2026-10-20 · **Owner:** Vlad Zloteanu
**Repo:** `~/wrk/pers/astrafable` (personal, the control plane) · **Supersedes:** `/idea-validate` in `personal_skills_and_tools`

## 1. Intent

One bootstrapped idea tested per week, for a solo founder or a pair, until one is worth pursuing.
"Tested" means: a real buyer saw a real offer at a real price through a real channel, and the
factory knows what one lead or one payment intent cost. Desk research never ends a run.

The factory is a control plane: Claude Code skills, deterministic tools, recipes, a ledger of
ideas, and a website template. Each idea that reaches launch gets its own GitHub repo, its own
Vercel project and its own secrets, created by the factory from the template. Vlad runs the skills
himself; they must work without the agent that built them in the room. Every run must leave the
factory better than it found it.

### Why v2 exists

v1 (`/idea-validate`, August 2026) had the right thesis and the right gates. In ten weeks it put
three ideas in and none reached paid traffic: one pivoted during research, one built a three-week
rig then stalled, one is still in research. `calibration.csv` has zero rows. The missing piece was
never tooling; it was throughput to the money phase. v2 is designed around that.

## 2. Goals, non-goals, anti-goals

**Goals**
- From pitch to first euro spent (or first outreach sent) in 2 working days; verdict in 7.
- Every test produces one number against one pre-registered threshold, then a verdict in
  {BUILD, PIVOT, PARK, DROP}.
- Paid and unpaid channels measured in the same unit: cost per primary event, all-in, with founder
  time priced.
- The factory improves on every run through calibration rows, learnings and skill edits.
- Costs of every kind (ads, APIs, LLM calls, domains, founder time) live in the idea's ledger.
- An idea with a BUILD verdict graduates as it is: its repo, its secrets, its history. A co-founder
  can be given one idea's repo without the factory's keys.
- Opening a session with `/factory` shows every idea and its state, and lets Vlad continue the
  plan step by step or rework one part of it (a better landing page, an A/B test, a new channel).

**Non-goals**
- Building the product. A BUILD verdict ends the factory's job for that idea.
- Brand work, naming perfection, pixel-perfect design. Good enough to be credible for one week.
- Multi-week ad optimisation. One week, one framing, one readout per experiment.

**Anti-goals (would make this a failure even if it works)**
- A run that ends in a research document with no spend, no outreach and no number.
- A verdict decided after looking at the data, instead of by the rule written before.
- Spending from a company ad account, or leaving company-specific content in this repo.
- Losing the ad account to a policy ban: it is shared by every future idea.
- Skills that only work when the agent that wrote them is driving.
- An idea repo that holds a secret it does not need.

## 3. Decisions already made (Vlad, 2026-10-20)

| # | Decision |
|---|---|
| D1 | **Ad spend from personal ad accounts** (Meta, Google; TikTok later). **Research and creative APIs through NeuralBox's provider accounts** (SearchAPI, SERanking, Apify, Firecrawl, Tavily, ScreenshotAPI, Gemini, OpenAI, Fal, Legnext, ElevenLabs, Submagic). Every cost is stored inside the idea's ledger. |
| D2 | **Primary metric per experiment is either cost per payment intent or cost per lead**, declared in the experiment file. |
| D3 | **Lab domain first.** `meikit.ai` (unregistered on 2026-10-20, to be bought during setup) is the lab domain. The first three runs default to `<slug>.meikit.ai` with the root verified once in Meta; a dedicated domain is bought only when brand trust is part of the test (consumer `.fr`) or after a BUILD. Amended by Q6, 2026-10-20. |
| D4 | **Non-ads channels are first-class**: replying to people who complain, Reddit posts, direct LinkedIn contact, cold email, communities. Chosen per idea by the same decision table as paid channels. |
| D5 | **The test website is a new design by Claude**, not a fork of the MonMagot rig. Its hard-won lessons carry over (section 9). |
| D6 | The first real idea is supplied by Vlad; the factory is built against it, not against a dummy. |
| D7 | **Every deployed project lives in its own GitHub repo with only the secrets it needs.** The factory instantiates it from a template and keeps the ledger; the idea repo holds the site and its own encrypted secrets. |
| D8 | **`/factory` is the entry point.** It lists the ideas with their status, lets Vlad pick one or start a new one, then either runs the next step of that idea's plan or reworks one part of it. |
| D9 | **Vercel: Vlad's personal account**, the login already on this machine, in its personal scope. Never a team scope. Hobby terms forbid commercial use, so `/factory-doctor` reads the plan and warns before the first launch; upgrading to Pro is Vlad's call. |
| D10 | **Operator is Vlad as an individual.** Legal pages, the fake-door disclosure and Stripe name him as a natural person; a company can replace him later by editing `operator` in the factory secrets. |
| D11 | **Ad and payment assets do not exist yet and are created later** (personal Meta Business Manager and ad account, Google Ads, Stripe, warmed sending domain). A `/factory-setup` checklist walks through creating each one and stores its keys. Until an asset exists, `/factory-doctor` removes its channels from the eligible set, so the first idea's week one runs on unpaid channels plus whatever account is live by then. |
| D12 | **Consent posture: informative banner, pixels on** (MonMagot's posture), re-decided per geo if a run targets a stricter market. |
| D13 | **First idea: an AI watchdog for ad accounts** (section 18). The factory is built against it. |

Governance facts checked today: the Vercel CLI on this machine is scoped to Dolead's team and
MonMagot lives on a SelectionA team, so the factory switches the CLI to the personal scope and
the doctor refuses to run against any team (D9). NeuralBox's Google/Meta/TikTok Ads tools spend
from Dolead's accounts and are never used to spend.

## 4. Constraints

- **Company boundary.** Reading `~/wrk/dolead/*` and `~/wrk/cmt/*` is fine. Nothing from this repo
  is ever written into them. No Dolead, SelectionA or CMT client data or brand material lands here.
- **Budget.** Default cap 300 EUR per experiment, **cash only** (ads, APIs, LLM calls, domains,
  tools), declared at intake and enforced at every gate; `idea.yml` tracks the cumulative cash across
  experiments. Founder time is priced at a declared hourly rate (default 100 EUR/h) so unpaid
  channels compare, but it never counts against the cash cap. Fixed founder time (intake, challenge,
  verdict) is idea-level overhead; only channel execution time (posting, sending, replying) enters
  that channel's cost per primary event.
- **Founder time.** About 2 hours per week: intake, the challenge session, ad approval, and five
  conversations with the people who converted. Those conversations stay mandatory.
- **Legal (FR/EU).** Legal mentions, privacy page, lawful basis for emails, cookie banner, honest
  fake-door disclosure. B2B cold email allowed with relevance and opt-out; B2C cold email is not.
- **Ad platform policy.** No guarantees, no before/after, no fake scarcity, no misleading claims.
  A claims lint runs on every ad and every page before launch.
- **Reddit and LinkedIn etiquette.** The agent finds targets and drafts; a human posts and sends,
  in small batches. No bulk automation on LinkedIn.
- **NeuralBox is LLM-mediated.** A `/respond` call takes about two minutes and costs about 0.30 USD.
  It is used where it holds unique data (AdsInsights) or for exploratory research, never on the
  daily path where a direct API call exists.
- **Secrets isolation.** The factory's master key never enters an idea repo; an idea's master key
  opens only that idea's secrets.
- **AdsInsights data.** Only aggregated, category-level benchmarks and conclusions may be written
  into an idea's files (advertiser counts, reach shares of named public advertisers, typical hooks).
  No client-level rows, no raw exports, no Dolead internal identifiers. The `nb` tool's AdsInsights
  mode returns a structured summary and `/idea-triage` writes conclusions, never the payload.
- **Channel prerequisites.** A channel is eligible for an experiment only when its asset exists and
  is in good standing (ad account verified, warmed sending domain, Reddit or LinkedIn account with
  history, Stripe live for deposits). `/factory-doctor` checks them and the challenge session only
  picks eligible channels.

## 5. Plans, steps and workstreams

Every idea has a `plan.md`: the weekly cycle instantiated as numbered steps, each with a status
(todo, doing, done, skipped, void), the command that runs it, its gate and its timebox. `/factory`
reads it to show where the idea stands and to offer the next step.

### The default plan (one week)

| Step | Command | Who | Output | Timebox |
|---|---|---|---|---|
| 1 Intake | `/idea-new` | Vlad 15 min | `intake.md` (verbatim pitch, geo, buyer, value per customer, cap) | 15 min |
| 2 Triage | `/idea-triage` | agent, automatic | `brief.md`: who pays today, prices, demand signals, complaints, triage score | 60 min, 3 EUR |
| 3 Challenge | `/idea-challenge` | Vlad 45 min with agent | `challenge.md`: forcing questions answered, adversarial read, pivot fan-out scored, GO/NO-GO with one framing, recipe, channels, predictions | 1 session |
| 4 Launch | `/idea-launch` | agent, Vlad approves ads 15 min | idea repo created from the template, domain, site live, QA passed, creatives, campaign specs, channel kits, experiment 1 frozen | 1 day |
| 5 Run | `/idea-status` daily | agent | `results/1.md` refreshed: spend, clicks, events, cost per primary, stop-rule check; today's outreach batch; converters to call | 5 min/day |
| 6 Conversations | Vlad | Vlad | notes in `conversations/` | 5 × 20 min |
| 7 Verdict | `/idea-verdict` | agent, Vlad confirms | verdict, calibration row, learnings, write-back | 30 min |

Gates (a step fails and the plan stops or pivots when one is not met):
- Intake: slug, geo, language, buyer, value per customer, cap written down.
- Triage: at least one of {someone pays to acquire this buyer today, a trigger keyword exists,
  recurring complaints exist}. All three absent ends the run at cost zero. *Amended 2026-10-22,
  after the Codex challenge of the triage skill: three signals scored 0–2 or U (unknown) — P the
  buyer's problem seen in their actions, C commercial evidence, R an unpaid route to reach the
  buyer; PASS when R ≥ 1 and (P = 2, or C = 2, or P ≥ 1 and C ≥ 1 from independent sources);
  STOP (status `DROP`) only after the minimum coverage finds the decisive evidence absent;
  INCONCLUSIVE otherwise. Adjacent advertising and search volume never pass on their own. The
  skill `.claude/skills/idea-triage/SKILL.md` is the reference.*
- Challenge: one framing survives with a falsifiable prediction; a price is written; a recipe and
  channels are chosen; the modelled cost per primary event leaves margin against value per customer.
- Launch: page live, QA passed, a test event reached the admin, claims lint clean, legal pages up.
- Verdict: minimum sample reached, or VOID.

Two ideas overlap: idea N is in step 5 while idea N+1 is in steps 1 to 3. A step that overruns its
timebox is cut and noted in learnings, not finished.

### Workstreams (reworking a part of the plan)

A workstream is an optional block of steps inserted into an idea's plan after launch, when Vlad
wants to improve a part rather than move on. Each has a recipe under `workstreams/<name>.md`, and
each one that changes what is measured ends by pre-registering a new experiment
(`experiments/<n>.yml`) so the readout stays honest.

| Workstream | What it does | Ends with |
|---|---|---|
| `lp-improve` | design review of the live page, converter interviews read, a new variant written and reviewed | experiment n+1 on variant B, or an A/B test |
| `ab-test` | two variants served 50/50 by cookie, per-variant thresholds and minimum sample | experiment n+1 with per-variant readout |
| `new-creatives` | new angles and formats from the winners and losers of the week | same experiment, new ad set, noted in results |
| `new-channel` | add a channel kit (for example outreach next to search ads) | experiment n+1 or an addendum with its own thresholds |
| `re-triage` | refresh the brief after new facts | updated `brief.md` |
| `re-challenge` | run the challenge again on a new framing | new GO/NO-GO; the plan restarts at launch |
| `pivot` | carry the surviving framing into a new launch with the same channel setup | new experiment |

## 6. The idea ledger (`ideas/<slug>/` in the factory)

The factory's folder for an idea is the single source of truth for everything except the site code,
which lives in the idea's own repo (section 9). A run that leaves no files did not happen.

```
ideas/<slug>/
  idea.yml          # status, phase, dates, geo, buyer, value_per_customer_eur, cap_eur,
                    # repo (github url), local_path, domain, current_experiment, totals (computed)
  plan.md           # the steps and workstreams with their status (section 5)
  intake.md         # verbatim pitch + intake answers, never edited after step 1
  brief.md          # triage output
  challenge.md      # challenge session: questions, answers, adversarial read, framings, decision
  experiments/      # 1.yml, 2.yml … each pre-registered and frozen at its launch (schema below)
  results/          # 1.md, 2.md … daily readouts per experiment, regenerated by /idea-status
  channels/         # one kit per channel: campaign spec, ad copy, outreach list, drafts
  creatives/        # generated images/videos, with the prompt and cost of each
  costs.jsonl       # every cost line: {ts, kind, provider, amount_eur, ref, phase, note}
  verdict.md        # BUILD / PIVOT / PARK / DROP with the numbers and the reason
  learnings.md      # append-only, written by every command
  conversations/    # notes from the calls with people who converted
```

Idea statuses: `NEW`, `TRIAGED`, `GO`, `NO-GO`, `LAUNCHED`, `RUNNING`, `REWORK`, `BUILD`, `PIVOT`,
`PARK`, `DROP`. `/factory` shows them on the board.

`experiments/<n>.yml`:

```yaml
n: 1
slug: dog-grooming-scheduler
framing: "Online booking page for independent dog groomers in FR, 19 EUR/month"
recipe: fake-door-saas            # see section 7
primary_metric: cost_per_intent   # or cost_per_lead
value_per_customer_eur: 228       # 12 months × 19
cap_eur: 300
founder_hour_rate_eur: 100
channels: [google_search, meta_feed, reddit_reply]
variants: [a]                     # [a, b] for an A/B test, split 50/50 by cookie
predictions: {cpc_eur: 0.9, ctr_pct: 4, lp_cvr_pct: 6, cost_per_primary_eur: 15}
primary_to_customer_rate: 0.33    # recipe prior (section 7), replaced by calibration over runs
thresholds:
  # allowed CAC = value_per_customer / 3; pass max = allowed CAC × primary_to_customer_rate
  # here: 228 / 3 = 76 → 76 × 0.33 ≈ 25
  pass_cost_per_primary_max_eur: 25
  sample_unit: clicks                 # clicks for traffic recipes, contacts_reached for outreach
  min_sample: 300                     # per variant when there are two
  min_primary_events: 20
  void_below_sample: 100
stop_rules:
  - "spend ≥ cap"
  - "clicks ≥ 150 and primary events = 0"
  - "ad account warning or rejection"
window: {start: 2026-10-28, end: 2026-11-02}
```

`costs.jsonl` kinds: `ads`, `api`, `llm`, `domain`, `founder_time`, `other`. Tools append their own
lines (NeuralBox returns `cost_usd` per call; provider tools use a per-call price table). `idea.yml`
totals are recomputed by `/idea-status`. `founder_time` lines carry a `channel` field when the time
was channel execution, and none when it was idea-level overhead.

**Value per customer** is first-year gross margin per customer, declared at intake (recurring:
monthly price × gross margin × 12, never more than 12 months). **Allowed CAC** is one third of it.
**The pass threshold** is allowed CAC × the recipe's primary-to-customer prior, so a pass means the
modelled CAC leaves a 3× margin. The prior comes from the recipe table and is replaced by the
calibration median once five rows exist for that recipe.

## 7. Recipes (what a test is)

A recipe is a test design: what the page offers, what counts as the primary event, which channels
fit, the minimum sample and the default thresholds. Chosen in the challenge session from this table.

| Recipe | Page offer | Primary event | Fits |
|---|---|---|---|
| `fake-door-saas` | product page with price and "Start" button; checkout step says private beta, leave email, optional refundable deposit | intent (click at stated price) | software, subscriptions, B2C/B2B self-serve |
| `pre-order` | product page with price and real checkout (Stripe payment link, refundable) | payment | physical or digital products with a clear unit price |
| `concierge-b2b` | offer page with price, "Book a call" | lead (qualified call booked) | services, B2B, anything sold with a conversation |
| `cold-email-b2b` | same offer page; traffic from outreach only | lead (reply with interest) | identifiable B2B buyers, lists buildable |
| `complaint-response` | page as above; traffic from replies to people complaining in public | lead or intent | any idea where the pain is written down in public |
| `waitlist-b2c` | email capture, no price | lead | last resort, only when a price cannot be stated yet |

What exactly counts, per recipe:

| Recipe | Primary event fires when | Sample unit | Minimum sample / events | VOID below | Primary → customer prior |
|---|---|---|---|---|---|
| `fake-door-saas` | the checkout step (price shown again, private-beta disclosure) is submitted with an email; `cta_click` on the priced page is a secondary event. A paid refundable deposit fires `payment` on top and is reported separately | clicks | 300 / 20 | 100 clicks | 0.33 |
| `pre-order` | Stripe checkout completed (refundable) | clicks | 300 / 10 | 100 clicks | 0.8 |
| `concierge-b2b` | a call is booked with a work email | clicks | 300 / 15 | 100 clicks | 0.3 |
| `cold-email-b2b` | a reply expressing interest (classified by the agent, confirmed by Vlad) | contacts reached (delivered) | 100 / 10 | 40 reached | 0.15 |
| `complaint-response` | lead or intent on the page, from a tracked reply link | replies posted | 40 / 8 | 15 posted | 0.2 |
| `waitlist-b2c` | email submitted | clicks | 300 / 30 | 100 clicks | 0.05 |

Every primary event carries an email (or a reply thread), so every converter can be called; the
conversation requirement in the verdict is therefore always satisfiable.

Rules that hold for every recipe:
- A price is shown unless the recipe is `waitlist-b2c`. No price, no launch.
- The page states honestly that the product is in private beta or pre-launch (fake-door disclosure).
- The primary event fires server-side and is forwarded to the ad platforms (Meta Conversions API first).
- The minimum sample, the primary events and the VOID floor are the recipe's (table above), per
  variant in an A/B test. The window is a target; the cap is the hard stop (section 12).
- Conversations with converters are part of the recipe, not an afterthought.

## 8. Acquisition channels

Each channel has a kit template under `channels/<name>/` in the factory: how to build the list or
campaign, cost unit, tracking, compliance, and the stop rules. The challenge session picks 2 to 3.

| Channel | Cost unit | Tracking | Notes |
|---|---|---|---|
| `google_search` | EUR (personal Google Ads) | gclid + utm | first choice when solution-aware or trigger keywords exist; exact/phrase match; 2–3 RSAs |
| `meta_feed` | EUR (personal Meta) | fbclid + utm + CAPI | problem-unaware audiences; 3 angles × 2 formats, kill losers at 48 h |
| `tiktok` | EUR | ttclid + utm | later; needs a personal TikTok Ads account |
| `reddit_reply` | founder minutes | per-thread tracked link | agent finds complaints (Arctic Shift, SearchAPI); drafts genuinely helpful replies; human posts |
| `reddit_post` | founder minutes | tracked link | one honest post per fitting subreddit, written to its rules |
| `linkedin_outreach` | founder minutes | reply log + tracked link | agent builds the list (Apify, NeuralBox domain-owner identification) and a 3-touch sequence; human sends ≤20/day |
| `cold_email_b2b` | founder minutes + sending tool | tracked link + reply log | sent from the factory's shared, pre-warmed sending domain (a factory asset set up during the build, never an idea's own domain); per-idea sender identity; an idea pauses at bounce > 5 % or complaint > 0.3 % to protect the shared asset; relevance + opt-out; never B2C |
| `community_post` | founder minutes | tracked link | Facebook groups, Discord/Slack, Indie Hackers, Product Hunt, Show HN |

Channel choice is a decision table, not taste: solution-aware searches → search ads; problem-unaware
consumers → Meta; identifiable B2B buyers → outreach before ads; pain written in public → replies.
Founder minutes are converted to EUR at the intake rate so every channel yields a comparable cost
per primary event.

## 9. The stand: a template, instantiated per idea

The stand is a Next.js App Router site kept as a GitHub **template repository** (`stand-template`,
developed from a sibling checkout of the factory). `/idea-launch` creates `vladzloteanu/<slug>`
from it, writes the idea's content, creates the Vercel project and database, attaches the domain
and deploys. One repo, one Vercel project, one database, one set of secrets per idea. Lessons kept
from MonMagot: fire the conversion at capture, not at double opt-in; store utm and click ids on the
lead row and fall back to them when the cookie is gone.

- **Pages:** landing, offer/pricing (inline or `/pricing`), checkout or booking step, thanks, legal
  mentions, privacy, cookies, contact. Legal pages are generated from the operator entity.
- **Content:** `site.yml` in the idea repo holds headline, subhead, three proof points, offer
  (price, unit, what is included, CTA), FAQ, and a theme (palette, font pair) so pages do not all
  look alike. A second entry under `variants:` is served 50/50 by cookie when an A/B test is on.
- **Events (canonical):** `page_view`, `scroll_50`, `cta_click`, `checkout_view`, `intent`,
  `lead`, `payment`, `share`. Every event carries the variant, utm and click ids.
- **Storage:** Postgres provisioned through the Vercel Marketplace per idea (builder picks via the
  marketplace skill; Neon unless discovery says otherwise). Tables: visits, events, leads, intents,
  payments.
- **Pixels:** one Meta pixel (dataset) and one set of Google Ads conversion actions **per idea**,
  created in the personal accounts at launch. Server-side forwarding to Meta Conversions API;
  Google enhanced conversions when the account allows.
- **Admin:** `/admin`, basic auth from the idea's secrets. Visits by source, events funnel per
  variant, leads, intents, payments, cost per primary against the prediction. `/api/stats`
  serves the same numbers to the factory's `/idea-status` under a per-idea stats token.
- **Anti-bot:** Cloudflare Turnstile on forms (free tier).
- **Email:** confirmation and "we are live" emails through Resend on the idea's own domain.
- **Design:** built fresh with the frontend-design skill; credible, fast, mobile-first. Design
  review and QA before every launch.
- **Template drift:** the idea repo records the template version it was created from; a
  `stand_sync` tool applies later template fixes to a running idea when wanted (builder's design).

Domains: `<slug>.meikit.ai` by default for the first three runs (D3): the root is bought once
during setup, its DNS lives at the registrar with a wildcard pointed to Vercel, and attaching a
subdomain to an idea's project is one command. A dedicated domain, when a test needs one, is bought
with `vercel domains buy` when Vercel sells the TLD, else at Porkbun with DNS pointed to Vercel.

## 10. Tools layer (in the factory)

`tools/` holds deterministic CLIs, Python 3.14 with `uv`, `httpx`, no LLM in the loop. Every tool
takes `--idea <slug>`, appends its cost to the idea's `costs.jsonl`, supports `--dry-run`, and has
`--selftest`. Keys come from the factory's `secrets/config.yml.enc` (section 11), never from the
environment of a Dolead repo.

| Group | Tools | Provider |
|---|---|---|
| demand | `serp_ads` (live SERP with ads), `keyword_volume` (domain-anchored volume + CPC), `ad_library` (Meta, TikTok, Google Transparency counts and creatives) | SearchAPI, SERanking |
| voice of customer | `reddit_mentions`, `hn_mentions`, `reviews_harvest` (app stores, G2 via Apify) | Arctic Shift, Algolia, Apify |
| landscape | `pricing_scan` (extract prices from competitor pages), `site_screenshot`, `domain_owner` | Firecrawl, ScreenshotAPI, NeuralBox |
| unique data | `nb` (NeuralBox `/respond` client with structured output, tool whitelist, cost logging, and the no-fabricated-numbers clause) | NeuralBox |
| creative | `image_gen` (Gemini/OpenAI/Legnext via NeuralBox accounts), `claims_lint` | NeuralBox accounts |
| launch | `domain_check` (RDAP), `domain_buy`, `repo_create` (from the template, with the idea's secrets), `vercel_project` (create, link, env, domain), `stand_deploy`, `stand_smoke`, `stand_sync` | gh, Vercel CLI |
| ads | `meta_campaign` (create or spec-only), `google_campaign`, `ads_spend` (daily readout) | personal accounts |
| outreach | `list_build`, `outreach_draft`, `tracked_link` | Apify, stand |
| measure | `idea_stats` (pulls `/api/stats` of the idea), `verdict_engine`, `calibration_append`, `costs_total` | idea repo, local files |
| board | `ledger` (reads every `idea.yml` and `plan.md`, renders the board for `/factory`) | local files |

Ads automation is staged: the first runs produce a campaign spec plus creatives and Vlad creates
the campaign in the ads UI in ten minutes, pasting the campaign id back; API creation on the
personal accounts is added once the accounts and app credentials exist. Spend readout is API-first
(Meta Insights, Google Ads reports) with CSV import as fallback.

v1 assets migrate here: the 19 `ad-intel` scripts become `tools/` modules reading keys from
secrets; the `naming` skill and `check-availability.sh` come along; `dev-tool-traction` scripts
join the voice-of-customer group; the three `business_ideas/` folders move to `ideas/` with their
status preserved. The old `/idea-validate` command gets a pointer here.

## 11. Secrets: two layers

Same scheme in both layers as `cmt_agents/bin/secrets`: `bin/secrets` (OpenSSL AES-256-CBC, PBKDF2
100k, YAML validated), `secrets/config.yml.enc` committed, `secrets/master.key` gitignored (chmod
600), `.gitattributes` textconv for decrypted diffs, `make secrets-init | secrets-edit | secrets-cat`.

**Factory secrets** (`astrafable/secrets/config.yml.enc`): everything that spends, researches or
creates, plus the keys to operate each idea.

```yaml
operator: {name, address, email, siren}          # legal pages and fake-door disclosure
nb: {url: http://127.0.0.1:3076, api_key, user_email}
providers: {searchapi, seranking, apify, firecrawl, tavily, screenshotapi, gemini, openai, legnext, fal, elevenlabs, submagic}
accounts:
  github: {owner}                                # repo creation uses the logged-in gh CLI; token optional
  vercel: {scope}                                # the personal scope; the logged-in Vercel CLI does the work
  meta: {business_id, ad_account_id, system_user_token, app_id, app_secret}
  google_ads: {customer_id, developer_token, oauth}
  stripe: {secret_key}
  porkbun: {api_key, secret}
  resend: {account_key}                          # to mint per-domain sending keys
ideas:
  <slug>: {master_key, stats_token}              # the only way into that idea's secrets
```

**Idea secrets** (`<slug>/secrets/config.yml.enc`, decrypted in memory by the site from the
`MASTER_KEY` Vercel env var): only what that site needs to run.

```yaml
database_url
admin: {user, password}
stats_token
meta: {pixel_id, capi_token}                     # this idea's dataset only
google: {conversion_ids_and_labels}
resend: {api_key, from}                          # key scoped to this domain
turnstile: {site_key, secret_key}
stripe: {payment_link}                           # when the recipe uses it
```

Provider keys that come from NeuralBox are copied once with `make secrets-cat` run in the
NeuralBox checkout and annotated `source: neural_box` in the YAML, so a later switch to own keys is
a one-line change. Nothing is ever written into the NeuralBox tree. No factory key is ever copied
into an idea repo.

## 12. Measurement and verdicts

`/idea-status` pulls spend (ads APIs or CSV), events (the idea's `/api/stats`), outreach logs and
founder time, computes clicks, CTR, CPC, conversion rate and cost per primary event per variant,
compares them with the predictions, checks the stop rules and writes `results/<n>.md`. It never
changes a frozen experiment file.

The engine is deterministic in two stages.

**Stage 1, status of the experiment** (computed, no human input):
- **VOID**: tracking broken, ads never served, or sample below the recipe's VOID floor.
- **PASS**: minimum sample and minimum events reached, cost per primary ≤ threshold.
- **FAIL**: minimum sample reached and cost per primary > threshold; or a stop rule fired with the
  sample above the VOID floor.
- **EXTEND**: the window ended with the sample between the VOID floor and the minimum, and cash
  remains under the cap. The window extends automatically, once, until the minimum or the cap.
- **INCONCLUSIVE**: cap reached with the sample between the VOID floor and the minimum. The cost
  per primary is still reported.

**Stage 2, verdict label** (computed from the status and the predictions; one human override):
- PASS and at least one converter conversation produced the buyer's own words and a buying
  question → **BUILD**. PASS without conversations → the verdict waits up to three days for them,
  then BUILD if they happen, otherwise PIVOT with "offer reached buyers we could not talk to".
- FAIL with CTR ≥ 0.7× predicted and CPC ≤ 1.5× predicted and page conversion < 0.5× predicted
  → **PIVOT** (the offer, not the market): experiment n+1 in the same folder, one new framing,
  same channel setup, its own cap declared.
- FAIL otherwise, or INCONCLUSIVE → **DROP**.
- **PARK** is the only human override: it may replace a DROP when Vlad writes the trigger to watch
  and the reason; `verdict.md` records it as an override of the computed label.
- VOID → fix and re-run as experiment n+1; nothing is interpreted.

The verdict appends a row to `docs/calibration.csv` (predicted vs actual CPC, CTR, CVR, cost per
primary, channel, recipe, buyer type, geo, variant). After five rows the default predictions in the
recipes are replaced by the medians.

## 13. The learning loop

- Every command appends dated lines to `ideas/<slug>/learnings.md`: tool gaps, timings, costs,
  surprises, things a human had to do by hand.
- `/factory-retro` reads learnings, costs and calibration across ideas and proposes concrete edits
  to skills, recipes, workstreams, channel kits, the template and tools, with the reason; applies
  the approved ones; runs the fixture.
- `/factory-doctor` checks before any run: master key present, NeuralBox heartbeat, provider
  selftests, Vercel CLI logged in and in the personal scope (never a team), plan read and the Hobby
  warning shown, `gh` can create repos, `meikit.ai` resolves to Vercel, each configured asset
  reachable (ad accounts, Stripe, Resend, sending domain), each running idea's `/api/stats`
  answering. Its output is the eligible channel set for the next challenge session.
- `ideas/_fixture/` is a dummy idea with canned data so every skill and tool can be dry-run without
  spending; the retro and any skill edit end with a fixture run.
- `docs/learnings.md` holds the durable, cross-idea lessons; `CLAUDE.md` stays short and points to
  `docs/` for every big topic.

## 14. Skills (commands) and what each must do

All are project skills in `.claude/skills/<name>/SKILL.md`, invocable as `/<name>`, written to be
run by Vlad alone. Each has a checklist, reads only the files it needs, and ends with the learnings
append and a one-screen summary. `CLAUDE.md` tells a new session to start with `/factory`.

- **`/factory`** (entry point): render the board from the ledger (slug, status, current step,
  experiment number, spend against cap, last activity, next step), ask Vlad to pick an idea or
  start a new one, then offer two paths: **follow** (run the next step of `plan.md`) or **rework**
  (pick a workstream from section 5, insert it into the plan, run its first step). Also shows the
  running ideas that need a daily `/idea-status` or converter calls.
- **`/idea-new`**: capture the pitch verbatim, ask the intake questions one at a time (geo,
  language, buyer, who signs, value per customer, cap, founder rate), create the ledger folder and
  `plan.md`, run the cheap checks on any factual claim in the pitch.
- **`/idea-triage`**: build the four keyword buckets (solution-aware, problem-aware, trigger,
  adjacent budget), run the demand, landscape and voice-of-customer tools, query AdsInsights through
  NeuralBox when the category matches, and write `brief.md` with a triage score and a "who pays
  today" table. Time and cost capped.
- **`/idea-challenge`**: run the office-hours forcing questions on the brief's facts, dispatch an
  adversarial reader (steelman, the most revealing thing said, one wrong claim with the evidence
  that would prove it, a 48-hour test), fan out 4–6 framings along segment, job, price shape,
  channel and buyer side, score them on triage data, and end with GO on one framing plus recipe,
  channels, price and predictions, or NO-GO. Uses `/gstack-office-hours` and `/gstack-plan-ceo-review`
  rather than re-implementing them.
- **`/idea-launch`**: working title and domain; repo created from the template with the idea's own
  secrets; `site.yml` written and reviewed; creatives generated and claims-linted; campaign specs
  and outreach kits produced; Vercel project, database and domain attached; deployed; QA and
  design review passed; test event verified in admin; experiment file frozen; Vlad approves the ads
  and channel kits; campaigns go live; first outreach batch prepared.
- **`/idea-status`**: section 12. Also drafts the day's outreach batch and flags converters to call.
- **`/idea-verdict`**: section 12, plus write-back of `verdict.md`, `idea.yml`, `plan.md`,
  calibration, and the conversation notes.
- **`/factory-retro`**, **`/factory-doctor`**: section 13.
- **`/factory-setup`**: the one-time asset checklist (D11), resumable. For each asset: why the
  factory needs it, the exact steps to create it in the provider's UI, which key to paste where, and
  the doctor check that proves it works. Assets: `meikit.ai` purchase and wildcard DNS; Vercel
  personal scope and plan; Meta Business Manager, ad account, pixel dataset and system user;
  Google Ads account, developer token and conversion access; Stripe as an individual; Resend;
  Turnstile; Porkbun API; the shared cold-email sending domain and its warm-up.
- **`/factory-scout`** (later): propose three candidate ideas per week from structural signals
  (fast-growing advertisers, one-star reviews, "alternatives to X" demand, public complaints) in the
  intake format. *Amended 2026-10-22: the method is proposed in `docs/idea-sourcing.md` (money
  first, then pain; P/C/R plus hassle and fit; a pilot run by hand); the command is built only
  after Vlad validates that pilot. Since 2026-10-23 the candidates live in the store `scout/`
  (Claude, Codex and Gemini rounds, blind challenge, refusals that bind later rounds).*

## 15. Left to the builder

- Exact Next.js structure, component library, theming mechanism, variant assignment, and the
  admin's look.
- Postgres provider via the marketplace skill; schema details and migrations tooling.
- Python package layout under `tools/`, shared HTTP client, retry and 429 pacing (SERanking
  needs 2.5 s between calls), price table for API costs.
- Which ad-intel scripts merge into one module and which stay as they are.
- Meta Conversions API and Google conversion wiring details; enhanced conversions can wait.
- How `stand_sync` propagates template fixes to a running idea.
- Fixture content and the dry-run mechanics; `plan.md` format and how `/factory` parses it.
- Order of implementation, as long as the first real idea can run end to end by its launch day.

## 16. Open questions, answered (Vlad, 2026-10-20)

| Q | Answer | Folded into |
|---|---|---|
| Q1 Vercel scope | a personal Vercel account | D9 |
| Q2 Operator entity | Vlad as a person, to start | D10 |
| Q3 Assets today | none yet; they will be created later | D11, `/factory-setup`, doctor gating |
| Q4 Consent posture | informative banner | D12 |
| Q5 First idea | the ad-account watchdog (section 18) | D13 |
| Q6 Domain default | accept `<slug>.meikit.ai` for the first three runs | D3 amended |

## 17. My calls (reject any)

- Python 3.14 + `uv` for tools; Next.js App Router on Vercel for the stand; Postgres from the
  marketplace per idea; Resend for email; Turnstile for anti-bot.
- The stand is a GitHub template repository; idea repos are private under Vlad's GitHub account.
- One Meta pixel and one Google conversion set **per idea**, so an idea repo never holds another
  idea's token.
- Staged ads automation: spec plus manual creation first, API creation once accounts exist.
- Founder rate default 100 EUR/h; cap default 300 EUR; minimum sample 300 clicks or 20 primary
  events, per variant when A/B testing.
- Commands live in `.claude/skills/`, recipes, workstreams and channel kits as plain markdown
  under `recipes/`, `workstreams/` and `channels/`, big topics under `docs/`, short `CLAUDE.md`
  pointing at them.
- v1 assets migrate into this repo; the old command is marked superseded.
- From the builder review: the cap is cash only and per experiment; founder overhead is idea-level
  and only channel execution time enters a channel's cost per primary; the pass threshold is
  allowed CAC (value per customer / 3) × the recipe's primary-to-customer prior; `intent` fires on
  the submitted checkout step with an email, never on the first button; outreach recipes count
  contacts reached, not clicks; the verdict engine is a two-stage deterministic rule with PARK as
  the only human override; cold email sends from one shared, warmed factory domain with protective
  stop rules; AdsInsights output is persisted as aggregated conclusions only.

## 18. The first run: an AI watchdog for ad accounts

Vlad's pitch, verbatim (2026-10-20):

> We got hacked at Dolead - our facebook account was stolen (from a phishing on one of our
> admins - that opened an infected file); so my point: what if you could have a AI security stuff
> - that would alert you if anything weird is happening with your ad accounts? pivot: it can also
> help you do the right settings

What the pitch gives the factory, and what it does not yet:

- **The pain is real and written down in public.** "Ad account hacked" is a recurring complaint on
  Reddit, in Meta's own community forums and on X, which makes `complaint-response` and
  `reddit_reply` natural first channels, and the trigger-keyword bucket ("facebook ad account
  hacked", "unauthorized ads on my account", "business manager hacked") is a search-ads candidate
  once a Google Ads account exists.
- **Two framings are already on the table**: the watchdog (detect and alert on anomalies: new
  admins, payment method changes, new campaigns, spend spikes, country or page changes, permission
  grants) and the posture pivot (audit and fix the settings before the incident). The challenge
  session scores them with the triage data and keeps one for experiment 1.
- **Still to be decided at intake**: the buyer (agency owner, in-house performance marketer, SMB
  founder running ads alone), geo and language, the price shape (per ad account per month is the
  obvious one) and the value per customer, the cap. The buyer choice also decides the recipe:
  `fake-door-saas` for self-serve, `concierge-b2b` or `cold-email-b2b` for agencies.
- **The origin story stays out of the test.** The incident at Dolead is the motivation, not
  content: no Dolead name, detail or screenshot appears in any page, ad or outreach (section 4).

Build order follows from it: the ledger, intake and triage tools first so the brief exists before
the challenge session with Vlad; then the stand and the unpaid channel kits, because week one of
this idea cannot buy traffic (D11); paid-channel tooling lands as the accounts do.
