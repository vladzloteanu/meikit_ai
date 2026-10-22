---
name: idea-triage
description: Automatic triage of an intaken idea — reuses the intake evidence, verifies the buyer's problem in their own actions, the commercial evidence and an unpaid route to reach them, checks the promise against the platforms' documentation, records every decisive observation with its provenance, scores P/C/R (U for unknown) and writes brief.md with a PASS/STOP/INCONCLUSIVE gate and the open questions for the challenge. Step 2 of the weekly plan, agent-run, 60 minutes and 3 EUR at most.
---

# /idea-triage — triage (step 2, agent-run, 60 min, 3 EUR)

The triage answers one question with evidence: is there enough to spend a challenge session and a
first unpaid test on this idea? Three signals: **P**, the buyer's problem seen in their own
actions; **C**, commercial evidence (an offer sold for this job, or buyers spending on it); **R**,
an unpaid route to reach that buyer this week. The brief is organized around the four decisions
the challenge (step 3) must make — buyer and trigger, job and framing, unpaid channel, price and
purchase unit — not around a description of a market. Nothing here argues the idea; the challenge
does that with this brief in hand. Vlad is not present: the triage runs alone, stops with
unknowns, and never fills a section to look complete.

## Before you start (5 minutes)

1. **The idea.** `uv run factory board` shows it at `2. triage`. Read `ideas/<slug>/idea.yml`
   (buyer, signer, geo, language, `value_basis`), `ideas/<slug>/intake.md` (pitch, firsthand
   evidence, evidence card or homework, hypothesis or decisions, prepared test, claims checked,
   unknowns, the queries carried forward) and every file already in `ideas/<slug>/research/`.
   `## Private context` never reaches `brief.md`, a web search or a prompt.
2. **Budget and clock.** `uv run factory costs total --idea <slug> --json`, note `cash_eur`. The
   triage may add 3 EUR at most, and nothing without a decision the call can change. Note the
   start time: new research stops at minute 47, the brief is written by minute 60.
3. **Providers.** `uv run factory doctor --offline` once. A provider the doctor marks `fail`
   (SearchAPI quota used up, NeuralBox down) is not tried during the run: its tool rows in the
   brief say `pending: <reason> — rerun: <command>` and the signal that depended on it is `U`,
   never 0. The doctor also lists the eligible channels: those are the routes R can use.
4. **The decision frame, before any call.** Write at the top of your notes: the buyer and job
   from the intake, the proposed offer and test price, the eligible unpaid channels, and the single
   finding most likely to change the challenge's decision. Before every search and every paid
   call, one line: "finding X would change decision Y". No decision behind it, no call.

## The sequence (the minutes are a budget, not a promise)

- **5–20, buyer problem and route.** Classify the intake's evidence first, do not recount it: for
  each incident, the buyer's role, the platform, the stage (before or after the problem; recovery
  or prevention), the action taken (what they did, not what they feel), spending, contactability,
  and which other records it is independent of; deduplicate by thread or incident. Reuse: an
  unchanged search is never rerun. New searches only for what the intake left open, in the places
  this buyer actually appears:
  `uv run factory reddit_mentions --idea <slug> --terms "<phrase>" [--terms …] --subreddits <a,b,c> --since <12 months ago> --max-wait-s 60`
  once (when it throttles, the session's web search inside those communities replaces it; counts
  marked `complete: false` are lower bounds of matches), `uv run factory hn_mentions --idea <slug> --terms "<phrase>"`
  only when this buyer posts on Hacker News. Then the route, one eligible channel at a time: the
  communities (their rules on promotion, the live threads of the last 30 days where this buyer
  asks), the directories, agency sites and public LinkedIn profiles (a sample of people who fit),
  the job boards; fill the route table with counts and sources.
- **20–30, offers, advertising, spending, substitutes.** The session's web search for who sells
  this job today (prevention and recovery, service and software, direct and adjacent);
  `uv run factory pricing_scan --idea <slug> --urls <3–5 pages>` (0.01 EUR a page) for the price,
  the unit, the commitment, the scope; the public ad libraries read by web search (Google Ads
  Transparency Center, Meta Ad Library, LinkedIn Ad Library pages) for an inspected ad record:
  advertiser, network, date, country, promise, destination; the free substitutes and the
  platforms' own features with their coverage of the job (what they do, what they miss); the
  strongest counter-evidence to the proposed framing. When SearchAPI is up:
  `uv run factory serp_ads --idea <slug> --gl <cc> --hl <xx> --keywords <representative buyer and job queries, not the highest volume>`,
  then for the sellers found `uv run factory ad_library --idea <slug> --engine google_transparency --domain <domain> --region <CC>`
  and `uv run factory ad_library --idea <slug> --engine meta --q "<advertiser name>" --country <CC>`
  (`linkedin` likewise with `--q` and `--country`), at most five ad-library calls in all.
- **30–42, promise verification.** For each claim the offer would make (platform × event ×
  visibility × permission needed × latency × automatic action), the platform's own documentation
  read through web search: `supported`, `partial`, `unsupported` or `undocumented`, with the page
  and its date; polling a state is not receiving an event; "up to n minutes" is not "every
  change". A claim that cannot be supported is written as a limit for the challenge, never
  softened.
- **42–47, the strongest remaining gap.** One optional call against a named unresolved question:
  `uv run factory nb adsinsights --idea <slug> --category "<the market in words>" --countries <CC,CC> --networks facebook,search`
  (0.5 EUR) only when a category plausibly matches this buyer and this job and the answer would
  change a framing; check the resolved category before using anything; `not_found` or a generic
  category ("cybersecurity", "marketing software") → "no matching category" and nothing else is
  asked of NeuralBox. `uv run factory keyword_volume --idea <slug> --cc <cc> --buckets-file ideas/<slug>/research/buckets.json --language <xx>`
  only when SearchAPI is up and search is a candidate channel: the buckets come from observed
  buyer language, tagged by buyer, job, trigger and purchase stage, an empty bucket is allowed, an
  invented query is labelled `hypothesis`, and no bucket is ever summed into a "market".
- **47–60, write.** The brief, the signals, the gate, the open questions, the closeout. What is
  not done is `pending` or `U`, said as such.

## Evidence record

Every decisive observation in the brief carries: the source (URL or research file), the retrieval
date, the event date, the buyer's role, the geo when known, the job, the action, its class
(`behavior`, `measured cost`, `complaint`, `opinion`, `offer`, `ad record`), direct or adjacent
fit, which other records it is independent of, and its limitation. A count carries its query, its
window, its sources, its completeness (`complete: false` is a lower bound of matches, never
prevalence), its deduplication rule, and screened against relevant hits. A loss is a reported
case with gross fraudulent spend, refund and net kept apart, never "typical". A thing not found is
written "not found in this sweep: <queries>, <sources>, <date>". Dry-run files never support a
score.

## Signals and gate

| Signal | 0 | 1 | 2 | U |
|---|---|---|---|---|
| **P** buyer problem and action | a completed, dated search of the target buyer and job found no qualifying observation | one firsthand account from the target buyer of a concrete loss, workaround or action | two independent target buyers with the same job, at least one describing an action, not a concern | the coverage, the venue or the source cannot be verified |
| **C** commercial evidence | a completed search found no relevant offer and no spending for this job | a current offer for this buyer and job, with a price or an explicit quote process | firsthand buyer evidence of payment or of a budget allocated to this job | likewise |
| **R** unpaid reachability | the checked eligible routes are unusable for this test | three current target buyers reachable through one eligible channel, its access and rules checked | plus a repeatable way to find the next batch, with the effort observed | likewise |

A zero needs a completed, dated search of the named buyer and job; an outage, a throttle or the
wrong venue is `U`. Adjacent evidence stays in the brief but never qualifies as C. Advertising and
search volume never score on their own. There is no total: the signals overlap.

- **PASS** when R ≥ 1 and (P = 2, or C = 2, or P ≥ 1 and C ≥ 1 from independent sources). PASS
  authorizes the challenge, not a launch.
- **STOP** when PASS is unmet after the minimum coverage (two independent venues where this buyer
  appears inspected; one search for offers, spending and free substitutes; a second eligible
  channel checked when the first is unusable) and the decisive missing evidence is assessed
  absent, not unknown. STOP means no basis for this test this week, not "no market".
- **INCONCLUSIVE** otherwise: decisive evidence unknown or coverage incomplete; a provider failure
  is never evidence of absence. INCONCLUSIVE never advances on its own: the challenge decides
  whether to spend on the gap (a `re-triage` workstream) or to stop.

## Write `ideas/<slug>/brief.md`

From `.claude/skills/idea-triage/brief-template.md`: a section with nothing in it says `unknown`
or `pending` and why; the "Decisions for the challenge" section is the one that must be complete.
Each of its four blocks has the strongest supporting observation, the strongest contrary
observation, the unresolved fact and the consequence of that uncertainty. Economics come from
`value_basis` as scenarios with their assumptions (allowed CAC is a third of each); founder time
is costed at the idea's rate; a conversion rate is never manufactured: `unknown — measure by
<method>`. Every open question for the challenge names the evidence on each side, the
alternatives and the finding that would change the decision.

## Close the step

1. `uv run factory costs total --idea <slug> --json` again: the research cash actually spent and
   the wall-clock go in the brief's last section (a STOP still reports what was spent; what it
   saves is the launch).
2. PASS or INCONCLUSIVE: `uv run factory idea set <slug> status=TRIAGED`. STOP:
   `uv run factory idea set <slug> status=DROP` and `uv run factory plan mark <slug> 3 skipped`,
   likewise for steps 4 to 7. The gate and its reason are in the brief and in learnings; `notes`
   stays the intake's.
3. `uv run factory plan mark <slug> 2 done`; append
   `- <YYYY-MM-DD> /idea-triage: <gate>; <what the tools lacked, what took longest, the real cost>`
   to `ideas/<slug>/learnings.md`; `uv run factory board`.
4. **Summary, one screen**: the three signals with their evidence, the gate and the rule that
   fired, the four decision blocks in one line each, the route found, the promise limits, what is
   `pending` or `U`, cost and time, and the next step: `/idea-challenge` (one session with Vlad)
   or, on STOP, why the week ends here.

## Rules

- Timebox 60 minutes and 3 EUR: when the clock or the money runs out, write the brief with what
  exists, mark the rest `pending` or `U`, and say so in learnings. A cut step is noted, not
  finished. The tool cap protects the idea's 300 EUR, not the triage's 3: check the running total
  yourself before each paid call.
- Evidence or nothing: every number in the brief comes from a research file or a cited page, with
  its provenance; a cited number can still answer the wrong question, so every record says what it
  proves. A guess is `unknown — measure by <method>`.
- Reuse before research: the intake's evidence is classified, not recounted; an unchanged search
  is not rerun; a throttled provider gets one short attempt, not ten minutes.
- The brief is public-safe: no private context, no company names from the pitch's origin story, no
  AdsInsights raw rows, no secret values.
- This skill owns the session until its summary is printed: do not invoke other skills; the
  challenge step calls them.
