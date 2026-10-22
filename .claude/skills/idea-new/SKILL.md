---
name: idea-new
description: Intake of a new idea, office-hours style — the pitch verbatim, one firsthand question, a ten-minute evidence card, one editable hypothesis screen (buyer with a route to reach them, status quo, geo, offer and test price, value or unknown), one prepared 48-hour test, an evidence audit by an outside model; writes the ledger folder. Step 1 of the weekly plan.
---

# /idea-new — intake (step 1, about 30 minutes of Vlad's time)

The intake turns a pitch into a ledger entry the triage can work on, by helping Vlad find the
answers: he brings an idea, not the buyer, the price or the geo. This skill is an oriented wrapper
around `/gstack-office-hours`: its posture, its forcing questions and its brief format, aimed at
the factory's output. You do the homework, you recommend, Vlad decides; nothing is written as a
fact without evidence, and a field nobody can support is written `unknown`, not filled to look
complete. The gate at the end: slug, geo, language, buyer, value per customer (or unknown) and cap
are written down, each with its evidence status and its decision mark, and one 48-hour test is
prepared.

Vlad's time, in order: one question before the homework (2 minutes), nothing during it (at most
10 minutes, unattended), one screen to edit (about 15 minutes), one test to approve (5 minutes).

## Prerequisites (check them first, propose installs, never install silently)

This skill leans on things outside the repo. Check each in one shell call before anything else;
for every missing one, show the install line and ask Vlad whether to run it (one question for all
of them). Without gstack the skill cannot run; without Codex and Gemini the evidence audit falls
back to a fresh Claude subagent, which is weaker but allowed.

| Needed | Check | Install if missing |
|---|---|---|
| gstack office-hours skill | `test -f ~/.claude/skills/gstack-office-hours/SKILL.md \|\| test -f ~/.claude/skills/gstack/office-hours/SKILL.md` | `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup` (then re-open the session) |
| Codex CLI, logged in | `codex login status` | `npm install -g @openai/codex`, then `codex login` (or pipe an API key: `… \| codex login --with-api-key`) |
| Gemini CLI, logged in (optional) | `gemini --version` and a one-word `gemini -p pong -o text` | `npm install -g @google/gemini-cli`, then `gemini` once interactively to log in |
| factory CLI | `uv run factory --version` | `make sync` in the repo |

## The method (read it before the first message)

Read these sections of `~/.claude/skills/gstack-office-hours/SKILL.md` and nothing else of it
(find them with `grep -n '^#' <file>`, read only those line ranges): the startup-mode operating
principles ("Interest is not demand"), the response posture, the anti-sycophancy rules, the
pushback patterns, the six forcing questions with their smart routing by stage and the smart-skip
rule (this skill uses Q1 to Q4, and Q5 when the pitch already has users), and the decision-brief
format a question must use (search the same file for "ELI10": D-numbering, ELI10, stakes,
recommendation, pros and cons, net). If that file is missing, `docs/challenge-techniques.md`
sections 0.1 and 1.1 hold the same text verbatim.

Posture, in short: take a position on every answer and say what evidence would change it; push
once with the Q3 forcing push when a buyer is a category instead of a person, then accept; never
push on "I don't know", which is a correct answer to most questions about a raw pitch
(smart-skip: ask only what the pitch and the evidence leave open); name the failure pattern when
you see one; never the banned phrases. Do not invoke `/gstack-office-hours` itself (its own flow
would take the session to a software design doc): follow its text here.

Two vocabularies run through the whole intake and the ledger:

- **Evidence status** of a value: `observed` (a behavior trace: someone paid, hired, built or
  scrambled), `reported` (someone, Vlad included, said so), `inferred` (your reading of the
  evidence), `unknown`.
- **Decision mark** of a value: `Vlad's call`, `accepted recommendation`, `delegated` (he said
  "just decide"). A mark never upgrades an evidence status: his acceptance is a decision, not
  evidence.

## Checklist

1. **Pitch, verbatim.** The pitch is the text after `/idea-new`, or the next message when there is
   none; if there is none at all, ask for it. Keep it byte for byte, typos included. Propose a
   working title and a slug (lowercase, hyphens, 2–4 words) in one line; Vlad can override either
   at any point. Create the folder at once so the tools can write into it:
   `uv run factory idea new <slug> --title "<title>" --provisional` (the values come at step 8).
   Note the stage from the pitch (pre-product, has users, has paying customers): it routes the
   forcing questions.
2. **Private context.** If the pitch names an employer, a client, a person or an incident that
   must not reach the public, say so in one line now, keep it for `## Private context`, and keep it
   out of every prompt that leaves this machine (the evidence audit of step 7 included) and out of
   every web search. The origin story is motivation, never content.
3. **One question before the homework (Q1, firsthand).** Ask, in these words, skipping any part the
   pitch already answers: "What is the last real instance that made you think this should exist?
   Who was involved, what did they do instead, and can you reach them this week? 'Just a hunch' is
   enough. Keep identifying details local: they stay in this folder." Record the answer verbatim
   under `## Firsthand` with its evidence status (`observed` when he saw the behavior, `reported`
   when he heard of it). When the stage has users, this is also where Q5 is asked, once: what he
   watched someone do that surprised him. No other question before the homework.
4. **Homework: the evidence card (at most 10 minutes, unattended, nothing spent, hard stop).**
   Start from three competing explanations, not from a story: (a) the problem is costly enough to
   buy a fix; (b) it is annoying but tolerated; (c) the existing workaround is adequate. Spend the
   ten minutes finding what separates them. Before each search write one line in the card:
   "finding X would change decision Y"; skip a search with no decision behind it.
   - **Where to look**: the sources where this buyer actually appears. The free tools are the
     default sweep, because the buyers of most pitches complain in public:
     `uv run factory reddit_mentions --idea <slug> --terms "<pain phrase>" [--terms …] --subreddits <2–3 where that human posts> --since <90 days ago> --max-wait-s 240 --phase intake`
     (at most three terms; the provider throttles, counts marked `complete: false` are lower
     bounds) and `uv run factory hn_mentions --idea <slug> --terms "<phrase>" --phase intake`; the
     session's own web search for pricing pages, job postings, forum threads, "why [incumbent]
     works" as well as "why [incumbent] fails". Read the hits, not the counts.
   - **What to look for**, one of each at most: a trace of **behavior** (a paid alternative, a
     job posting, a manual workflow with a consequence, a request with an urgent consequence) and
     what it actually proves; the strongest **counter-trace** (a free workaround that works, a
     buyer without a budget, a rare trigger, an incumbent solving the job cheaply); a **reachable
     buying situation** (the trigger, a plausible budget owner, a route to three such people in
     seven days); a **switching obstacle** (data, integrations, trust, purchasing lead time).
   - **How to record** each retained observation: source and date, its class (`behavior`,
     `measured cost`, `complaint`, `opinion`), what it proves, which decision it affects.
     Deduplicate repeated stories. No quota: one documented purchase beats three complaints saying
     the same thing. A search that finds nothing is written `unobserved in <sources>`, never "no
     demand". Queries you did not get to are listed for the triage.
   - **The card**, one screen, kept verbatim for `intake.md`: the recommended first test in one
     line; the strongest supporting observation; the strongest counterexample; the unresolved fact
     that would reverse the recommendation; the route to three buyers, or "none found".
5. **One hypothesis screen, editable.** One message, not a sequence of briefs: every line below
   with your recommendation, its evidence status and the observation behind it; Vlad edits any
   line or accepts the screen. Then at most two questions, each naming the decision its answer
   would change, through AskUserQuestion in the decision-brief format when a choice is real (two
   to three options, the recommendation first, one line of stakes); accept `unknown` as an answer.
   - **Buyer**: the user, the budget owner and the approver (one person when they are the same),
     role and situation, not a category; the trigger that makes them buy; who signs. A category
     answer gets the Q3 forcing push, once.
   - **Reachability**: three kinds of people Vlad could contact in seven days, or a precise way to
     find them (a directory, a community, a job board, a conference list). The one question this
     line may carry: "Can you reach three people like this in seven days?" A buyer he cannot reach
     is not the first test's buyer.
   - **Status quo**: a fact with its evidence status, not a menu: what that buyer does today
     (tolerating, outsourcing, a workaround, nothing) and its cost when a source names one, else
     `unknown`. One complaint is one data point, never a representative cost.
   - **First test geo and language**: chosen by where the reachable buyers are and where the
     purchase can happen, not by where the English-language hits were; the eventual market, when
     different, is named as such.
   - **Offer and test price**: the smallest thing this buyer would pay for this week (Q4) and the
     charging unit that matches the benefit (per account, per workspace, a one-shot audit, a share
     of spend). A test price is an offer we choose; demonstrated willingness to pay is something
     else and is written separately when a source shows it.
   - **Value per customer**: price × purchases in the first year × gross margin, each input with
     its source (`observed`, `reported`, a competitor's price, Vlad's number) or `unknown`; a
     low/base/high when the inputs range. No default months, no default margin: when price or
     retention has no anchor, the value is `unknown` and stays so; a number is never produced to
     satisfy the field. The ledger's allowed CAC is a third of this value, so an invented input
     becomes a verdict later.
   - **Cap and rate**: 300 EUR cash and 100 EUR/h founder time are the defaults; stated here,
     changed only on Vlad's word, and then written (step 8).
   - **Unknowns**: the open fields, each with what would settle it and when (the conversations of
     the prepared test, the triage, the challenge).
   - Escape hatch: when Vlad says "just decide", take your recommendation for every open line, mark
     each `delegated`, and move on; do not argue a second time.
6. **One prepared test (replaces premises and homework).** Draft one offer for one reachable
   buyer situation: the trigger, the promised outcome, the delivery method, the proposed price, the
   contact route, the requested commitment and what each response would change. The commitment
   exposes the uncertainty: show a recent workflow, supply a real artifact, involve the budget
   owner, pay for a deliverable; "would you use this?" does not qualify. Write the message Vlad
   would send; do not send it. Then ask, in this shape: "I recommend testing [buyer] in [geo,
   language] with [offer]. In 48 hours, do [the contact or observation]. Continue if [predeclared
   behavior]; reconsider if [contrary behavior]. What part of that would you change?" His edits
   are his words; the approved test goes to `## Prepared test`.
7. **Evidence audit by an outside voice (two minutes, cents).** Build a context block: the pitch,
   the firsthand answer without identifying details, the evidence card, the hypothesis screen with
   its evidence statuses, the prepared test; nothing from `## Private context`. The prompt, in
   these words: "Which intake value is least justified by the supplied evidence? Identify the
   unsupported inference and the cheapest observation that would change the first test. Say 'none
   material' if appropriate. Do not propose a product build." Run it on another model family,
   first `codex exec -s read-only --skip-git-repo-check -c 'mcp_servers={}' -o <research/outside_voice_<stamp>.md> "<prompt>"`,
   then `gemini-vertex -p "<prompt>" -o text` if Codex fails, then a fresh subagent through the
   Agent tool if both fail. Save the full output in `ideas/<slug>/research/`; show Vlad only a
   material objection and its consequence for the test, or "none material"; reopen a line of the
   screen only when the objection changes the test. Log the spend:
   `uv run factory costs add --idea <slug> --kind llm --provider <openai|google|anthropic> --amount-eur <n> --phase intake --note "evidence audit, <model>, <tokens> tokens"`
   (estimate from the token count when the CLI prints no price). Vlad can say "skip" and it is
   skipped, noted as such.
8. **Write the ledger.**
   `uv run factory idea set <slug> geo=<CC,CC> language=<xx> buyer="<short label>" signer="<short label>" value_per_customer_eur=<n|unknown> value_basis="<each input with its source, the low/base/high when ranged>" provisional=<true|false> notes="<one line>"`
   (buyer and signer at most 12 words; `provisional=true` when any value is `delegated`, `inferred`
   or `unknown`), plus `cap_eur=<n>` and `founder_hour_rate_eur=<n>` when Vlad changed them. Then
   `ideas/<slug>/intake.md` below its header, in this order: `## Pitch (verbatim)` (blockquote);
   `## Firsthand` (his answer quoted, its evidence status); `## Evidence card` (the card, then
   every retained observation with source, date, class, what it proves, the decision it affects;
   the counts with their window and whether they are lower bounds; the queries not run);
   `## Hypothesis` (one entry per line of the screen: the value recorded, its evidence status, the
   observation behind it, the decision mark, Vlad's edit quoted when he made one); `## Prepared
   test` (the offer, the message as drafted, the 48-hour action, the continue and reconsider
   signals, his edits quoted); `## Outside voice` (model, the material objection or "none
   material", the full output's file, the cost, or "skipped"); `## Private context` (only when
   step 2 found something); `## Claims checked` (each factual claim of the pitch with its evidence
   and a verdict `supported`, `weak`, `unchecked (<reason>)` or `deferred to triage` for "someone
   advertises" and "someone pays"); `## Unknowns` (every `unknown`, `inferred` or `delegated` value
   and what settles it).
9. **Close the step**: `uv run factory plan mark <slug> 1 done`; append
   `- <YYYY-MM-DD> /idea-new: <what the evidence lacked, what took longest, what Vlad overrode, the cost>`
   to `ideas/<slug>/learnings.md`; `uv run factory board`.
10. **Summary, one screen**: title and slug; the values with their evidence status and decision
    mark; the prepared test in three lines (do, continue if, reconsider if); the unknowns; the
    outside voice's objection and its cost; the private-context rule if any; the queries carried to
    the triage; the next step `/idea-triage` (60 min, 3 EUR).

## Rules

- Timebox: about 30 minutes of Vlad's time; the homework stops at ten minutes with what it has.
  Short messages; one screen, at most two questions after it, one test.
- Vlad's words are never cleaned up: the pitch is verbatim, his answers are quoted.
- Evidence or nothing: a number in `intake.md` comes from a research file, a cited page or Vlad,
  with its evidence status; a guess is written as a bet or as `unknown`, never as a fact; absence of
  public discussion is `unobserved`, never "no demand". Never write a new tool to get a number.
- Never complete a field to satisfy the ceremony: `unknown` is a valid, recorded answer.
- Private context never leaves this machine: not in the outside-voice prompt, not in web searches.
- Secrets: never print a key value. Costs: the intake spends nothing beyond the evidence audit,
  which is logged.
- This skill owns the session until its summary is printed: do not invoke `/gstack-office-hours`
  or any other skill during the intake; the challenge step calls them.
