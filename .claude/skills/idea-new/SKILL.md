---
name: idea-new
description: Intake of a new idea — the pitch verbatim, the seven intake questions one at a time, the ledger folder, cheap checks on the pitch's factual claims. Step 1 of the weekly plan.
---

# /idea-new — intake (step 1, 15 minutes of Vlad's time)

The intake turns a pitch into a ledger entry the triage can work on. It is not the challenge:
do not argue the idea, sharpen its inputs. The gate at the end: slug, geo, language, buyer,
value per customer and cap are written down.

## Checklist

1. **Pitch, verbatim.** The pitch is the text after `/idea-new`, or the next message when there
   is none; if there is none at all, ask for it. Keep it byte for byte, typos included. Propose a
   working title and a slug (lowercase, hyphens, 2–4 words, e.g. `ad-account-watchdog`); Vlad can
   override either at any point.
2. **Private context.** If the pitch names an employer, a client, a person or an incident that
   must not reach the public (pages, ads, outreach), say so in one line now and keep it for the
   `## Private context` section. The origin story is motivation, never content.
3. **The intake questions, one per message, in this order.** Ask, wait for the answer, then ask
   the next. No list of questions, no message with two questions in it.
   1. Geo: which countries (ISO codes, e.g. US, FR)?
   2. Language of the pages and ads?
   3. Buyer: who pays? Push once when the answer is a category rather than a person with a job
      ("a performance marketer running several Meta accounts for clients" beats "marketers").
   4. Who signs the purchase: the buyer, their boss, a client?
   5. Value per customer = first-year gross margin in EUR: price × purchases in the first year ×
      gross margin (software 0.9, services lower). For a monthly subscription assume six paying
      months unless Vlad gives a retention figure. Given only a price shape, compute it and show
      the arithmetic with its assumptions; given no price, propose the obvious shape, compute,
      and mark the value provisional.
   6. Cash cap in EUR (default 300).
   7. Founder hour rate in EUR (default 100).
   "Later", "don't know" or an absent Vlad: record a provisional value (the default, or your best
   estimate said as such) and move on. The idea is then `provisional: true` and every such value
   goes under `## To confirm`.
4. **Create the ledger folder:**
   `uv run factory idea new <slug> --title "<title>" --geo <CC,CC> --language <xx> --buyer "<…>" --signer "<…>" --value-eur <n> --cap-eur <n> --rate-eur <n> [--provisional] [--notes "<one line>"]`.
   It writes `idea.yml`, `plan.md`, `intake.md` (header only), `learnings.md`, `costs.jsonl` and
   `research/`. It refuses an existing slug: pick another one, never delete. Field values in
   `idea.yml` are short labels (buyer and signer at most 12 words each); Vlad's exact words go in
   `intake.md`, not in `idea.yml`.
5. **Write `ideas/<slug>/intake.md`** below its header, in this order:
   - `## Pitch (verbatim)` — the pitch as a blockquote, unchanged.
   - `## Intake answers` — one line per question (geo, language, buyer, signer, value with its
     arithmetic, cap, rate); provisional ones end with `(provisional)`.
   - `## Private context` — only when step 2 found something: what stays out of public content.
   - `## Claims checked` — step 6.
   - `## To confirm` — only when provisional: one line per value and what would settle it (usually
     the challenge session).
6. **Check the pitch's factual claims, with the free tools only.** List each claim about the world
   the pitch relies on: that a problem happens, that people complain about it, that a competitor
   exists, that a price is paid. The intake checks the first two kinds; "someone advertises on it"
   and "someone pays" are the triage's questions (its tools cost money) and are written down as
   `deferred to triage`. At most three terms and three subreddits at intake (the Reddit provider
   throttles; the triage goes wider):
   - complaints on Reddit:
     `uv run factory reddit_mentions --idea <slug> --terms "<phrase>" [--terms "<phrase>"] --subreddits <a,b,c> --since <90 days ago, YYYY-MM-DD>`
     (`--subreddits` is required: name the subreddits where the buyer actually posts, e.g.
     `FacebookAds,PPC,marketing` for people who run ads; a run waits out throttles for up to five
     minutes and then reports what it got, with `complete: false` where it is a lower bound);
   - complaints on Hacker News: `uv run factory hn_mentions --idea <slug> --terms "<phrase>" --since <12 months ago>`
     (fast; expect little for consumer or marketing pains).
   Read the hits, not just the counts. Write one entry per claim: the evidence (counts with their
   window, whether they are lower bounds, one or two quotes with links) and a verdict: `supported`,
   `weak`, `unchecked (<reason>)` or `deferred to triage`. A claim you could not check stays
   `unchecked` with the reason (tool missing, provider down, throttled): never fill it from memory
   and never write a new tool for it.
7. **Close the step:** `uv run factory plan mark <slug> 1 done`; append one line to
   `ideas/<slug>/learnings.md` in its format, `- <YYYY-MM-DD> /idea-new: <what the intake lacked, what took longest>`;
   then `uv run factory board`.
8. **Summary, one screen:** title and slug; the seven values, provisional ones flagged; each claim
   with its verdict; the private-context rule if any; the next step, `/idea-triage` (60 min, 3 EUR).

## Rules

- Timebox: 15 minutes of Vlad's time. Short messages; a question is one sentence.
- Vlad's words are never cleaned up: the pitch is verbatim, the answers are quoted.
- Secrets: never print a key value. Costs: the intake spends nothing.
- This skill owns the session until its summary is printed: do not invoke `/gstack-office-hours`
  or any other skill during the intake, even when a pitch looks like their trigger; the challenge
  step calls them.
