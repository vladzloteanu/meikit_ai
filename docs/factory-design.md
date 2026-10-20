# Ideas Factory — design

**Status:** draft for approval · **Date:** 2026-10-20 · **Owner:** Vlad Zloteanu
**Repo:** `~/wrk/pers/astrafable` (personal) · **Supersedes:** `/idea-validate` in `personal_skills_and_tools`

## 1. Intent

One bootstrapped idea tested per week, for a solo founder or a pair, until one is worth pursuing.
"Tested" means: a real buyer saw a real offer at a real price through a real channel, and the
factory knows what one lead or one payment intent cost. Desk research never ends a run.

The factory is a set of Claude Code skills, deterministic tools, a shared test website and a
written method. Vlad will run the skills himself; they must work without the agent that built them
in the room. Every run must leave the factory better than it found it.

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
- Costs of every kind (ads, APIs, LLM calls, domains, founder time) live in the idea's folder.

**Non-goals**
- Building the product. A BUILD verdict ends the factory's job for that idea.
- Brand work, naming perfection, pixel-perfect design. Good enough to be credible for one week.
- Multi-week ad optimisation. One week, one framing, one readout.

**Anti-goals (would make this a failure even if it works)**
- A run that ends in a research document with no spend, no outreach and no number.
- A verdict decided after looking at the data, instead of by the rule written before.
- Spending from a company ad account, or leaving company-specific content in this repo.
- Losing the ad account to a policy ban: it is shared by every future idea.
- Skills that only work when the agent that wrote them is driving.

## 3. Decisions already made (Vlad, 2026-10-20)

| # | Decision |
|---|---|
| D1 | **Ad spend from personal ad accounts** (Meta, Google; TikTok later). **Research and creative APIs through NeuralBox's provider accounts** (SearchAPI, SERanking, Apify, Firecrawl, Tavily, ScreenshotAPI, Gemini, OpenAI, Fal, Legnext, ElevenLabs, Submagic). Every cost is stored inside the idea's metadata. |
| D2 | **Primary metric per test is either cost per payment intent or cost per lead**, declared at launch in `experiment.yml`. |
| D3 | **A domain is bought per idea by default.** `meikit.ai` (unregistered on 2026-10-20) becomes the lab domain; `<slug>.meikit.ai` is the fast path when a name is not ready or brand matters little. |
| D4 | **Non-ads channels are first-class**: replying to people who complain, Reddit posts, direct LinkedIn contact, cold email, communities. Chosen per idea by the same decision table as paid channels. |
| D5 | **The test website is a new design by Claude**, not a fork of the MonMagot rig. Its hard-won lessons carry over (section 9). |
| D6 | The first real idea is supplied by Vlad; the factory is built against it, not against a dummy. |

Governance facts checked today: the Vercel CLI on this machine is scoped to Dolead's team and
MonMagot lives on a SelectionA team, so the factory needs its own Vercel scope (open question Q1).
NeuralBox's Google/Meta/TikTok Ads tools spend from Dolead's accounts and are never used to spend.

## 4. Constraints

- **Company boundary.** Reading `~/wrk/dolead/*` and `~/wrk/cmt/*` is fine. Nothing from this repo
  is ever written into them. No Dolead, SelectionA or CMT client data or brand material lands here.
- **Budget.** Default cap 300 EUR per idea, all-in, declared at intake and enforced at every gate.
  Founder time is priced at a declared hourly rate (default 100 EUR/h) so unpaid channels compare.
- **Founder time.** About 2 hours per week: intake, the challenge session, ad approval, and five
  conversations with the people who converted. P8-style conversations stay mandatory.
- **Legal (FR/EU).** Legal mentions, privacy page, lawful basis for emails, cookie banner, honest
  fake-door disclosure. B2B cold email allowed with relevance and opt-out; B2C cold email is not.
- **Ad platform policy.** No guarantees, no before/after, no fake scarcity, no misleading claims.
  A claims lint runs on every ad and every page before launch.
- **Reddit and LinkedIn etiquette.** The agent finds targets and drafts; a human posts and sends,
  in small batches. No bulk automation on LinkedIn.
- **NeuralBox is LLM-mediated.** A `/respond` call takes about two minutes and costs about 0.30 USD.
  It is used where it holds unique data (AdsInsights) or for exploratory research, never on the
  daily path where a direct API call exists.

## 5. The weekly cycle

| Day | Command | Who | Output | Timebox |
|---|---|---|---|---|
| Mon AM | `/idea-new` | Vlad 15 min | `ideas/<slug>/intake.md` (verbatim pitch, geo, buyer, value per customer, cap) | 15 min |
| Mon AM | `/idea-triage` | agent, automatic | `brief.md`: who pays today, prices, demand signals, complaints, triage score | 60 min, 3 EUR |
| Mon PM | `/idea-challenge` | Vlad 45 min with agent | `challenge.md`: forcing questions answered, adversarial read, pivot fan-out scored, GO/NO-GO with one framing, recipe, channels, predictions | 1 session |
| Tue | `/idea-launch` | agent, Vlad approves ads 15 min | domain, site live, QA passed, creatives, campaign specs, channel kits, `experiment.yml` frozen | 1 day |
| Wed–Sun | `/idea-status` | agent daily | `results.md` refreshed: spend, clicks, events, cost per primary, stop-rule check | 5 min/day |
| Next Mon | `/idea-verdict` | agent, Vlad confirms | verdict, calibration row, learnings, write-back | 30 min |
| Every 2 weeks | `/factory-retro` | agent | skill, recipe and tool edits from learnings; fixture dry run | 1 h |

Two ideas overlap: idea N is in traffic while idea N+1 is in intake and challenge. A phase that
overruns its timebox is cut and noted in learnings, not finished.

Gates (a run stops or pivots when one fails):
- Intake: slug, geo, language, buyer, value per customer, cap written down.
- Triage: at least one of {someone pays to acquire this buyer today, a trigger keyword exists,
  recurring complaints exist}. All three absent ends the run at cost zero.
- Challenge: one framing survives with a falsifiable prediction; a price is written; a recipe and
  channels are chosen; the modelled cost per primary event leaves margin against value per customer.
- Launch: page live, QA passed, a test event reached the admin, claims lint clean, legal pages up.
- Verdict: minimum sample reached, or VOID.

## 6. The idea folder contract

`ideas/<slug>/` is the single source of truth for an idea; a run that leaves no files did not happen.

```
ideas/<slug>/
  idea.yml          # status, dates, geo, buyer, value_per_customer_eur, cap_eur, totals (computed)
  intake.md         # verbatim pitch + intake answers, never edited after Monday
  brief.md          # triage output
  challenge.md      # challenge session: questions, answers, adversarial read, framings, decision
  experiment.yml    # the pre-registered test (schema below), frozen at launch
  site.yml          # page content and theme for the stand (section 9)
  channels/         # one kit per channel: campaign spec, ad copy, outreach list, drafts
  creatives/        # generated images/videos, with the prompt and cost of each
  costs.jsonl       # every cost line: {ts, kind, provider, amount_eur, ref, phase, note}
  results.md        # daily readout, regenerated by /idea-status
  verdict.md        # BUILD / PIVOT / PARK / DROP with the numbers and the reason
  learnings.md      # append-only, written by every command
  conversations/    # notes from the calls with people who converted
```

`experiment.yml`:

```yaml
slug: dog-grooming-scheduler
framing: "Online booking page for independent dog groomers in FR, 19 EUR/month"
recipe: fake-door-saas            # see section 7
primary_metric: cost_per_intent   # or cost_per_lead
value_per_customer_eur: 228       # 12 months × 19
cap_eur: 300
founder_hour_rate_eur: 100
channels: [google_search, meta_feed, reddit_reply]
predictions: {cpc_eur: 0.9, ctr_pct: 4, lp_cvr_pct: 6, cost_per_primary_eur: 15}
thresholds:
  pass_cost_per_primary_max_eur: 25   # must leave ≥3× margin on one-shot value, ≥1/3 of LTV on recurring
  min_clicks: 300
  min_primary_events: 20
  void_below_clicks: 100
stop_rules:
  - "spend ≥ cap"
  - "clicks ≥ 150 and primary events = 0"
  - "ad account warning or rejection"
window: {start: 2026-10-28, end: 2026-11-02}
```

`costs.jsonl` kinds: `ads`, `api`, `llm`, `domain`, `founder_time`, `other`. Tools append their own
lines (NeuralBox returns `cost_usd` per call; provider tools use a per-call price table). `idea.yml`
totals are recomputed by `/idea-status`.

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

Rules that hold for every recipe:
- A price is shown unless the recipe is `waitlist-b2c`. No price, no launch.
- The page states honestly that the product is in private beta or pre-launch (fake-door disclosure).
- The primary event fires server-side and is forwarded to the ad platforms (Meta Conversions API first).
- Minimum sample: 300 clicks or 20 primary events or the cap; below 100 clicks the run is VOID.
- Conversations with converters are part of the recipe, not an afterthought.

## 8. Acquisition channels

Each channel has a kit template under `channels/<name>/` in the repo: how to build the list or
campaign, cost unit, tracking, compliance, and the stop rules. The challenge session picks 2 to 3.

| Channel | Cost unit | Tracking | Notes |
|---|---|---|---|
| `google_search` | EUR (personal Google Ads) | gclid + utm | first choice when solution-aware or trigger keywords exist; exact/phrase match; 2–3 RSAs |
| `meta_feed` | EUR (personal Meta) | fbclid + utm + CAPI | problem-unaware audiences; 3 angles × 2 formats, kill losers at 48 h |
| `tiktok` | EUR | ttclid + utm | later; needs a personal TikTok Ads account |
| `reddit_reply` | founder minutes | per-thread tracked link | agent finds complaints (Arctic Shift, SearchAPI); drafts genuinely helpful replies; human posts |
| `reddit_post` | founder minutes | tracked link | one honest post per fitting subreddit, written to its rules |
| `linkedin_outreach` | founder minutes | reply log + tracked link | agent builds the list (Apify, NeuralBox domain-owner identification) and a 3-touch sequence; human sends ≤20/day |
| `cold_email_b2b` | founder minutes + sending tool | tracked link + reply log | separate sending domain; relevance + opt-out; never B2C |
| `community_post` | founder minutes | tracked link | Facebook groups, Discord/Slack, Indie Hackers, Product Hunt, Show HN |

Channel choice is a decision table, not taste: solution-aware searches → search ads; problem-unaware
consumers → Meta; identifiable B2B buyers → outreach before ads; pain written in public → replies.
Founder minutes are converted to EUR at the intake rate so every channel yields a comparable cost
per primary event.

## 9. The stand (shared test website)

One multi-tenant Next.js app on Vercel serves every idea; the hostname selects the idea's `site.yml`.
One deploy, one admin, one event schema across ideas. Lessons kept from MonMagot: fire the
conversion at capture, not at double opt-in; store utm and click ids on the lead row and fall back
to them when the cookie is gone.

- **Pages per idea:** landing, offer/pricing (inline or `/pricing`), checkout or booking step,
  thanks, legal mentions, privacy, cookies, contact. Legal pages are generated from the operator
  entity in secrets.
- **Content:** `site.yml` holds headline, subhead, three proof points, offer (price, unit, what is
  included, CTA), FAQ, and a theme (palette, font pair) so pages do not all look alike. Variants are
  additional `site.yml` entries selected by path, for later A/B.
- **Events (canonical):** `page_view`, `scroll_50`, `cta_click`, `checkout_view`, `intent`,
  `lead`, `payment`, `share`. Every event carries the idea slug, the variant, utm and click ids.
- **Storage:** Postgres provisioned through the Vercel Marketplace (builder picks via the
  marketplace skill; Neon unless discovery says otherwise). Tables: visits, events, leads, intents,
  payments; `idea_slug` on every row.
- **Pixels:** one Meta pixel and one Google Ads conversion set for the whole stand; the slug travels
  on the event and per-idea custom conversions are defined by hostname. Server-side forwarding to
  Meta Conversions API; Google enhanced conversions when the account exists.
- **Admin:** `/admin`, basic auth from secrets. Per idea: visits by source, events funnel, leads,
  intents, payments, spend (from `costs.jsonl` and ad APIs), cost per primary, prediction deltas.
  `/api/stats/<slug>` serves the same numbers to `/idea-status`.
- **Anti-bot:** Cloudflare Turnstile on forms (free tier).
- **Email:** confirmation and "we are live" emails through Resend on a dedicated subdomain.
- **Design:** built fresh with the frontend-design skill; credible, fast, mobile-first. Design
  review and QA before every launch.

Domains: `vercel domains buy` when the TLD is sold by Vercel, else manual purchase at Porkbun with
DNS pointed to Vercel; `<slug>.meikit.ai` otherwise. Adding a domain to the stand is one command.

## 10. Tools layer

`tools/` holds deterministic CLIs, Python 3.14 with `uv`, `httpx`, no LLM in the loop. Every tool
takes `--idea <slug>`, appends its cost to `costs.jsonl`, supports `--dry-run`, and has `--selftest`.
Keys come from `secrets/config.yml.enc` (section 11), never from the environment of a Dolead repo.

| Group | Tools | Provider |
|---|---|---|
| demand | `serp_ads` (live SERP with ads), `keyword_volume` (domain-anchored volume + CPC), `ad_library` (Meta, TikTok, Google Transparency counts and creatives) | SearchAPI, SERanking |
| voice of customer | `reddit_mentions`, `hn_mentions`, `reviews_harvest` (app stores, G2 via Apify) | Arctic Shift, Algolia, Apify |
| landscape | `pricing_scan` (extract prices from competitor pages), `site_screenshot`, `domain_owner` | Firecrawl, ScreenshotAPI, NeuralBox |
| unique data | `nb` (NeuralBox `/respond` client with structured output, tool whitelist, cost logging, and the no-fabricated-numbers clause) | NeuralBox |
| creative | `image_gen` (Gemini/OpenAI/Legnext via NeuralBox accounts), `claims_lint` | NeuralBox accounts |
| launch | `domain_check` (RDAP), `domain_buy`, `stand_add_domain`, `stand_deploy`, `stand_smoke` | Vercel CLI |
| ads | `meta_campaign` (create or spec-only), `google_campaign`, `ads_spend` (daily readout) | personal accounts |
| outreach | `list_build`, `outreach_draft`, `tracked_link` | Apify, stand |
| measure | `idea_stats`, `verdict_engine`, `calibration_append`, `costs_total` | stand, local files |

Ads automation is staged: the first runs produce a campaign spec plus creatives and Vlad creates
the campaign in the ads UI in ten minutes, pasting the campaign id back; API creation on the
personal accounts is added once the accounts and app credentials exist. Spend readout is API-first
(Meta Insights, Google Ads reports) with CSV import as fallback.

v1 assets migrate here: the 19 `ad-intel` scripts become `tools/` modules reading keys from
secrets; the `naming` skill and `check-availability.sh` come along; `dev-tool-traction` scripts
join the voice-of-customer group; the three `business_ideas/` folders move to `ideas/` with their
status preserved. The old `/idea-validate` command gets a pointer here.

## 11. Secrets

Same scheme as `cmt_agents/bin/secrets`: `bin/secrets` (OpenSSL AES-256-CBC, PBKDF2 100k, YAML
validated), `secrets/config.yml.enc` committed, `secrets/master.key` gitignored (chmod 600),
`.gitattributes` textconv for decrypted diffs, `make secrets-init | secrets-edit | secrets-cat`.
The stand reads `MASTER_KEY` from Vercel env and decrypts in memory.

`config.yml` shape:

```yaml
operator: {name, address, email, siren}          # legal pages and fake-door disclosure
nb: {url: http://127.0.0.1:3076, api_key, user_email}
providers: {searchapi, seranking, apify, firecrawl, tavily, screenshotapi, gemini, openai, legnext, fal, elevenlabs, submagic, resend, turnstile}
accounts:
  vercel: {team, token}
  meta: {ad_account_id, pixel_id, capi_token, app_id, app_secret}
  google_ads: {customer_id, conversion_ids, developer_token, oauth}
  stripe: {secret_key, payment_link_base}
  porkbun: {api_key, secret}
stand: {admin_user, admin_password, database_url}
```

Provider keys that come from NeuralBox are copied once with `make secrets-cat` run in the
NeuralBox checkout and annotated `source: neural_box` in the YAML, so a later switch to own keys is
a one-line change. Nothing is ever written into the NeuralBox tree.

## 12. Measurement and verdicts

`/idea-status` pulls spend (ads APIs or CSV), events (stand API), outreach logs and founder time,
computes clicks, CTR, CPC, conversion rate and cost per primary event, compares them with the
predictions, checks the stop rules and writes `results.md`. It never changes `experiment.yml`.

`/idea-verdict` applies the pre-registered rule:
- **VOID** below `void_below_clicks`, or when tracking was broken, or when ads never served.
- **PASS → BUILD** when cost per primary ≤ threshold at minimum sample, and at least one
  conversation produced the buyer's own words and a buying question.
- **PIVOT** when clicks were cheap and CTR fine but the page did not convert (the offer, not the
  market), carrying one new framing into the next week with the same channel setup.
- **DROP** when clicks were expensive and conversion poor.
- **PARK** when the market is right and the time is wrong, with the trigger to watch.

The verdict appends a row to `docs/calibration.csv` (predicted vs actual CPC, CTR, CVR, cost per
primary, channel, recipe, buyer type, geo). After five rows the default predictions in the recipes
are replaced by the medians.

## 13. The learning loop

- Every command appends dated lines to `ideas/<slug>/learnings.md`: tool gaps, timings, costs,
  surprises, things a human had to do by hand.
- `/factory-retro` reads learnings, costs and calibration across ideas and proposes concrete edits
  to skills, recipes, channel kits and tools, with the reason; applies the approved ones; runs the
  fixture.
- `/factory-doctor` checks before any run: master key present, NeuralBox heartbeat, provider
  selftests, Vercel scope is the factory's team, ad accounts reachable, stand healthy.
- `ideas/_fixture/` is a dummy idea with canned data so every skill and tool can be dry-run without
  spending; the retro and any skill edit end with a fixture run.
- `docs/learnings.md` holds the durable, cross-idea lessons; `CLAUDE.md` stays short and points to
  `docs/` for every big topic.

## 14. Skills (commands) and what each must do

All are project skills in `.claude/skills/<name>/SKILL.md`, invocable as `/<name>`, written to be
run by Vlad alone. Each has a checklist, reads only the files it needs, and ends with the learnings
append and a one-screen summary.

- **`/idea-new`**: capture the pitch verbatim, ask the intake questions one at a time (geo,
  language, buyer, who signs, value per customer, cap, founder rate), create the folder, run the
  cheap checks on any factual claim in the pitch.
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
- **`/idea-launch`**: working title and domain, `site.yml` written and reviewed, creatives
  generated and claims-linted, campaign specs and outreach kits produced, domain bought and attached,
  stand deployed, QA and design review passed, test event verified in admin, `experiment.yml`
  frozen, Vlad approves the ads and channel kits, campaigns go live, first outreach batch prepared.
- **`/idea-status`**: section 12. Also drafts the day's outreach batch and flags converters to call.
- **`/idea-verdict`**: section 12, plus write-back of `verdict.md`, `idea.yml`, calibration, and the
  conversation notes.
- **`/factory-retro`**, **`/factory-doctor`**: section 13.
- **`/factory-scout`** (later): propose three candidate ideas per week from structural signals
  (fast-growing advertisers, one-star reviews, "alternatives to X" demand, public complaints) in the
  intake format.

## 15. Left to the builder

- Exact Next.js structure, component library, theming mechanism, and the admin's look.
- Postgres provider via the marketplace skill; schema details and migrations tooling.
- Python package layout under `tools/`, shared HTTP client, retry and 429 pacing (SERanking
  needs 2.5 s between calls), price table for API costs.
- Which ad-intel scripts merge into one module and which stay as they are.
- Meta Conversions API and Google conversion wiring details; enhanced conversions can wait.
- Fixture content and the dry-run mechanics.
- Order of implementation, as long as the first real idea can run end to end by its launch day.

## 16. Open questions for Vlad

- **Q1 Vercel scope.** A new personal Pro team for the factory (about 20 USD/month; Hobby forbids
  commercial use), or an existing non-Dolead team?
- **Q2 Operator entity.** Who is the legal operator on the legal pages and on Stripe: Vlad as an
  individual, or a company? Needed before any traffic.
- **Q3 Ad accounts today.** Do a personal Meta Business Manager and a personal Google Ads account
  already exist? New accounts take days to verify and warm up, which sets the first launch date.
- **Q4 Consent posture.** Default is MonMagot's: informative banner, pixels on, re-decided per geo.
  Strict CNIL posture (pixels only after consent) is safer and costs signal. Which one?
- **Q5 The first idea.**

## 17. My calls (reject any)

- Python 3.14 + `uv` for tools; Next.js App Router on Vercel for the stand; Postgres from the
  marketplace; Resend for email; Turnstile for anti-bot.
- One multi-tenant stand rather than one project per idea.
- One Meta pixel and one Google conversion set across ideas, slug on every event.
- Staged ads automation: spec plus manual creation first, API creation once accounts exist.
- Founder rate default 100 EUR/h; cap default 300 EUR; minimum sample 300 clicks or 20 primary events.
- Commands live in `.claude/skills/`, recipes and channel kits as plain markdown under `recipes/`
  and `channels/`, big topics under `docs/`, short `CLAUDE.md` pointing at them.
- v1 assets migrate into this repo; the old command is marked superseded.
