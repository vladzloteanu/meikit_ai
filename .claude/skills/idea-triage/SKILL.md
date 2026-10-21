---
name: idea-triage
description: Automatic triage of an intaken idea — keyword buckets, demand, who pays today, complaints, landscape, AdsInsights conclusions, a triage score and a PASS/STOP gate written to brief.md. Step 2 of the weekly plan, 60 minutes and 3 EUR at most.
---

# /idea-triage — triage (step 2, agent-run, 60 min, 3 EUR)

The triage answers one question with evidence: is there any sign that money or pain already
exists around this idea? Three signals: someone pays to reach this buyer today, a trigger
keyword exists, recurring complaints exist. All three absent ends the run at cost zero.
Nothing here argues the idea; the challenge (step 3) does that with this brief in hand.

## Before you start

1. The idea: `uv run factory board` shows it at `2. triage`; read `ideas/<slug>/idea.yml` and
   `ideas/<slug>/intake.md` (pitch, buyer, geo, language, claims checked, private context).
   `intake.md` is private: nothing from `## Private context` reaches `brief.md`.
2. The budget: `uv run factory costs total --idea <slug> --json` and note `cash_eur`; the triage
   may add 3 EUR at most; every tool checks the cap itself. Note the start time: 60 minutes.
3. The providers: `uv run factory doctor --offline` once; a provider that the doctor marks
   `fail` (e.g. SearchAPI quota used up) is not retried during the run. Its sections of the brief
   say `pending: <reason> — rerun: <command>` and the gate is scored on the rest.

## Checklist

1. **Keyword buckets** → `ideas/<slug>/research/buckets.json`, a JSON object with four lists of
   5–10 keywords each, in the idea's language plus English when they differ:
   `solution_aware` (people searching for this kind of product), `problem_aware` (people
   describing the pain), `trigger` (the event that makes them search today), `adjacent_budget`
   (what this buyer already pays for nearby: tools, services, competitor brands).
2. **Demand**: `uv run factory keyword_volume --idea <slug> --cc <cc> --buckets-file ideas/<slug>/research/buckets.json --language <xx>`
   once per geo (`cc` = the country code in lower case). Read the per-bucket sums, the top
   keywords and the CPC range. A keyword with `found: false` has no data, it is not zero.
3. **Who pays today**: `uv run factory serp_ads --idea <slug> --gl <cc> --hl <xx> --keywords <the 8 highest-volume keywords>`;
   then, for the top 5 advertiser domains it returns,
   `uv run factory ad_library --idea <slug> --engine google_transparency --domain <domain>` and
   `uv run factory ad_library --idea <slug> --engine meta --q "<advertiser name or domain>" --country <CC>`
   (`linkedin` likewise with `--q`; `--domain` exists only for google_transparency). When SearchAPI is
   unavailable, find the advertisers with the session's own web search instead, say so in the
   brief ("found by web search, not by SERP"), and leave the SERP and ad-library rows `pending`.
4. **Prices and offer shapes**: `uv run factory pricing_scan --idea <slug> --urls <the top 5 competitor landing pages>`
   (0.01 EUR a page). Every row of "Who pays today" needs a price or `quote`/`unknown`.
5. **Complaints**: 3–5 pain phrases in the buyer's words, over the last 12 months:
   `uv run factory reddit_mentions --idea <slug> --terms "<phrase>" ... --subreddits <3–5 where the buyer posts> --since <12 months ago> --max-wait-s 600`
   and `uv run factory hn_mentions --idea <slug> --terms "<phrase>" ...`. The Reddit provider
   throttles: a run may take ten minutes and still mark counts `complete: false` (lower bounds);
   read the hits, keep the five most telling quotes with links, and say which counts are lower
   bounds. Never fill a count from memory.
6. **AdsInsights** (one call, both geos): `uv run factory nb adsinsights --idea <slug> --category "<the market in words>" --countries <CC,CC> --networks facebook,search`.
   If it answers `not_found` (no matching category) the brief says "no matching category" and
   nothing else is asked of NeuralBox. Only the conclusions the tool keeps go in the brief
   (reach, number of advertisers, top shares, hooks, caveats): never raw rows, never a second
   call to get more.
7. **Landscape**: from the research above and the session's web search: incumbents (who sells
   this today), free alternatives (what the buyer does for free instead), institutional
   alternatives (platform features, regulators, associations). One line each with a source.
8. **Write `ideas/<slug>/brief.md`** from `.claude/skills/idea-triage/brief-template.md`: keep
   every heading in order, fill each from the research files (cite them by name), and score:
   - `pays_today` 0–2: 0 nobody advertises to this buyer for this job; 1 one or two advertisers or
     only adjacent ones; 2 three or more advertisers buy ads for this buyer and job.
   - `trigger` 0–2: 0 no trigger keyword has volume; 1 trigger volume exists under 500 a month
     across geos; 2 500 or more, or a CPC above 1 EUR on a trigger keyword.
   - `complaints` 0–2: 0 none found; 1 a few threads a year; 2 recurring (several a month) with
     money or time named.
   Gate: PASS when any score is 1 or more, else STOP at cost zero (the idea's status becomes
   `STOPPED` and the summary says why). One line of evidence per score, no adjectives.
9. **Close the step**: `uv run factory costs total --idea <slug> --json` again and write the
   triage's cost and wall-clock time into the brief's last section;
   `uv run factory idea set <slug> status=TRIAGED` (or `status=STOPPED`);
   `uv run factory plan mark <slug> 2 done`; append `- <YYYY-MM-DD> /idea-triage: <what the tools lacked, what took longest, the real cost>`
   to `ideas/<slug>/learnings.md`; `uv run factory board`.
10. **Summary, one screen**: the three scores with their evidence, the gate, the advertisers and
    prices found, the strongest complaint quote, what is `pending`, cost and time, and the next
    step: `/idea-challenge` (one session with Vlad).

## Rules

- Timebox 60 minutes and 3 EUR: when the clock or the money runs out, write the brief with what
  exists, mark the rest `pending`, and say so in learnings. A cut step is noted, not finished.
- Evidence or nothing: every number in the brief comes from a research file or a cited page;
  a guess is written as `unknown — measure by <method>`.
- The brief is public-safe: no private context from the intake, no company names from the
  pitch's origin story, no AdsInsights raw data, no secret values.
- This skill owns the session until its summary is printed: do not invoke other skills; the
  challenge step calls them.
