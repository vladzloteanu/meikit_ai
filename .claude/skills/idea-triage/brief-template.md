# Brief — <title>

Triage of <YYYY-MM-DD>: <minutes> minutes, <EUR> cash. Research files: `research/<file>` …
Reused from the intake: `research/<file>` … Coverage: <the venues inspected, the queries, the
windows, what was not searched>.

## Summary

<Three sentences: the buyer and the action they were seen taking; what is sold for this job today
and at what price; the route to reach them. Then: P <0|1|2|U>, C <0|1|2|U>, R <0|1|2|U>, gate
<PASS|STOP|INCONCLUSIVE>.>

## Decisions for the challenge

Each block: the strongest supporting observation (record number), the strongest contrary
observation, the unresolved fact, the consequence of that uncertainty. `unknown` is allowed.

### Buyer and trigger

- Supports: <record #, one line>
- Contrary: <record #, one line>
- Unresolved: <the fact>
- Consequence: <what changes if it goes either way>

### Job and framing

- Supports: … / Contrary: … / Unresolved: … / Consequence: …

### Unpaid channel

- Supports: … / Contrary: … / Unresolved: … / Consequence: …

### Price and purchase unit

- Supports: … / Contrary: … / Unresolved: … / Consequence: …

## Evidence records

| # | Source (link or file), retrieved, event date | Buyer role, geo | Job | Action | Class | Fit | Independent of | Limitation |
|---|---|---|---|---|---|---|---|---|
| 1 | <link>, <YYYY-MM-DD>, <YYYY-MM-DD> | <role>, <CC> | <job> | <what they did> | <behavior|measured cost|complaint|opinion|offer|ad record> | <direct|adjacent> | <#, #> | <one line> |

## Offers, observed advertising and buyer spending

| Who | Kind | Promise | Price, unit, commitment | Job fit | Source, date |
|---|---|---|---|---|---|
| <name or domain> | <seller | verified advertiser (network, country, date) | buyer spending | free workaround> | "<headline>" | <59 EUR/month, per workspace, monthly | quote | unknown> | <direct|adjacent> | <link>, <YYYY-MM-DD> |

<`pending: <reason> — rerun: <command>` for the SERP and ad-library tools when they could not run;
ads inspected by hand are cited above as `verified advertiser` with the page.>

## Route to buyers

| Channel | Reachable buyers or live opportunities (count, source) | Rules | Founder work | Why this buyer would engage |
|---|---|---|---|---|
| <reddit_reply | reddit_post | linkedin_outreach | community_post> | <n people or threads, <link>> | <promotion allowed? verification? post history?> | <hours per batch> | <the trigger seen in the records> |

## Promise verification

| Platform | Claim | Documented capability | Permission needed | Latency | Status | Source |
|---|---|---|---|---|---|---|
| <Google Ads | Meta> | <"alert within minutes on a new admin"> | <what the API or UI exposes> | <scope, role> | <event lag or polling interval> | <supported|partial|unsupported|undocumented> | <link> |

## Complaints and incidents

<n> incidents after deduplication (<hits> hits in <threads> threads), window <since>–<until>,
sources <list>, completeness <complete | lower bound>, screened <n> → relevant <n>.

| Date | Role | Platform | Stage | Action taken | Loss (reported: gross / refund / net) | Link |
|---|---|---|---|---|---|---|

Quotes that carry a decision (with links):

- "<quote>" (<link>) — <the decision it bears on>

## Demand (search)

<`pending until <date> — rerun: <command>` | one row per keyword, country and language: volume,
CPC, `found`; overlaps flagged; never summed as a market.>

## Landscape

- Incumbents: <who sells this today; coverage of the job and its limits; source, date>.
- Free substitutes: <what the buyer does instead; coverage and limits; source, date>.
- Platform and institutional: <platform features, regulators, associations; coverage and limits; source, date; or "not found in this sweep: <queries>">.

## AdsInsights

<not run (no named question it would settle) | no matching category | category <name> (resolved
from "<query>"), <countries>, <network>, period <as reported or unknown>: <n> advertisers, the
three largest hold <x> % of reach (<a> %, <b> %, <c> %), hooks <…>, caveats <…>; provider-reported,
directional only.>

## Economics

| Scenario | Value per customer | Assumptions (from `value_basis`) | Allowed CAC (value / 3) |
|---|---|---|---|
| low | <EUR | unknown> | <each input with its source> | <EUR | unknown> |
| base | … | … | … |
| high | … | … | … |

Founder time at <rate> EUR/h counts in cost per primary event. Primary-event-to-customer
conversion: `unknown — measure by <method>`.

## Signals

| Signal | Score | Evidence (record numbers) |
|---|---|---|
| P buyer problem and action | <0|1|2|U> | <one line> |
| C commercial evidence | <0|1|2|U> | <one line> |
| R unpaid reachability | <0|1|2|U> | <one line> |

## Gate

<PASS | STOP | INCONCLUSIVE>: <the rule that fired>; minimum coverage <met | not met: what is
missing>.

## Open questions for the challenge

- **<question>** — for: <evidence>; against: <evidence>; alternatives: <…>; the finding that would
  change the decision: <…>.

## Carried forward

- Queries not run: <…>
- Pending tool rows: <command> (after <date>)
- For the conversations of the prepared test: <what they must settle>

## Cost and time

<cash before → after, by kind; wall-clock minutes; what was cut or left pending.>
