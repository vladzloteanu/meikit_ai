---
name: idea-new
description: Intake of a new idea, office-hours style — the pitch verbatim, an evidence sweep, then decision briefs with a recommendation that settle buyer, status quo, price shape, value, geo and language with Vlad, a premise check and an outside voice; writes the ledger folder. Step 1 of the weekly plan.
---

# /idea-new — intake (step 1, about 30 minutes of Vlad's time)

The intake turns a pitch into a ledger entry the triage can work on, by helping Vlad find the
answers: he brings an idea, not the buyer, the price or the geo. This skill is an oriented wrapper
around `/gstack-office-hours`: its posture, its forcing questions and its decision briefs, aimed
at the factory's output. You do the homework, you recommend, Vlad decides. The gate at the end:
slug, geo, language, buyer, value per customer and cap are written down, each marked as Vlad's
call or as a recommendation he accepted.

## Prerequisites (check them first, propose installs, never install silently)

This skill leans on things outside the repo. Check each in one shell call before anything else;
for every missing one, show the install line and ask Vlad whether to run it (one question for all
of them). Without gstack the skill cannot run; without Codex and Gemini the outside voice falls
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
principles, the response posture, the anti-sycophancy rules, the pushback patterns, the six
forcing questions (this skill uses Q1 to Q4), "Phase 3" premise challenge and "Phase 3.5" second
opinion. Then the decision-brief format every question must use (search the same file for
"ELI10": D-numbering, ELI10, stakes, recommendation, pros and cons, net). If that file is
missing, `docs/challenge-techniques.md` sections 0.1 and 1.1 hold the same text verbatim.

Posture, in short: take a position on every answer and say what evidence would change it; push
once, then again, when an answer is a category instead of a person or a feeling instead of a
number; name the failure pattern when you see one; never the banned phrases. Do not invoke
`/gstack-office-hours` itself (its own flow would take the session to a software design doc):
follow its text here.

## Checklist

1. **Pitch, verbatim.** The pitch is the text after `/idea-new`, or the next message when there is
   none; if there is none at all, ask for it. Keep it byte for byte, typos included. Propose a
   working title and a slug (lowercase, hyphens, 2–4 words) in one line; Vlad can override either
   at any point. Create the folder at once so the tools can write into it:
   `uv run factory idea new <slug> --title "<title>" --provisional` (the values come at step 6).
2. **Private context.** If the pitch names an employer, a client, a person or an incident that
   must not reach the public, say so in one line now, keep it for `## Private context`, and keep it
   out of every prompt that leaves this machine (the outside voice of step 5 included). The origin
   story is motivation, never content.
3. **Homework, before any question (at most 10 minutes, nothing spent).**
   - Answer Q1 to Q4 yourself on the pitch, one line each: the demand evidence you expect to find,
     the status quo and its cost, the actual human who needs this most, the narrowest wedge
     someone would pay for this week. These are your bets; the evidence corrects them.
   - Evidence sweep with the free tools: `uv run factory reddit_mentions --idea <slug> --terms "<pain phrase>" [--terms …] --subreddits <2–3 where that human posts> --since <90 days ago> --max-wait-s 240 --phase intake`
     (at most three terms; the provider throttles, counts marked `complete: false` are lower
     bounds), `uv run factory hn_mentions --idea <slug> --terms "<phrase>" --phase intake`, and
     the session's own web search for the landscape: "[problem space] startup approach <year>",
     "[problem space] common mistakes", "why [incumbent] fails". Read the hits, not the counts:
     who complains (role, situation), what they lose (money, time), what they do today instead,
     any price mentioned, any product already sold for this.
   - Rewrite your four bets with the evidence under them. A bet the evidence contradicts is
     dropped, not defended.
4. **The decisions, as decision briefs, one at a time.** Ask through AskUserQuestion when it is
   available (in plain text with the same brief otherwise), numbered D1, D2…; each brief carries
   your recommendation with the evidence behind it, two to four options, pros and cons, and the
   stakes; Vlad can always type his own answer. Wait for the answer before the next brief. When
   his pick contradicts the evidence, push once with the evidence, then accept and mark the value
   `Vlad's call`.
   - **D1 Buyer** (Q3, desperate specificity): the two to four concrete people the evidence shows,
     role and situation, not categories; the recommended one and why; who signs is part of each
     option ("the owner signs for the agency"). A category answer gets the Q3 forcing push.
   - **D2 Status quo and its cost** (Q2): what that buyer does today instead and what it costs
     them in money or hours, from the hits; the options are the workarounds seen; this feeds the
     value and the triage's "who pays today".
   - **D3 Narrowest wedge and price shape** (Q4): the smallest thing this buyer would pay for this
     week and how it is priced (per account per month, per workspace per month, a one-shot audit,
     a share of spend, a yearly fee…); each option shows its arithmetic for the value per
     customer = price × purchases in the first year × gross margin (software 0.9, services lower;
     six paying months for a new monthly subscription unless Vlad gives retention). The
     recommendation names the number.
   - **D4 Geo and language**: where the evidence and the buyer are, and the language of the pages
     and ads; one brief, with your recommendation.
   - Cash cap (300 EUR) and founder rate (100 EUR/h) are defaults: state them in the summary, change
     them only when Vlad says so. Q1 (demand reality) is not asked: the sweep answers it, and your
     position on it goes in the summary with what would change your mind.
   - Escape hatch, as office hours has it: when Vlad says "just decide", give every open brief
     your recommendation as its value, mark each `accepted recommendation (unasked)` and move on;
     do not argue a second time.
5. **Premises and the outside voice.**
   - Premises (Phase 3): restate the intake as four or five premises ("1. The buyer is …; 2. Today
     they …, which costs them …; 3. They would pay … for …; 4. The test runs in … in …")
     with agree/disagree, in one question. A disagreement reopens its brief.
   - Outside voice (Phase 3.5, mandatory here, two to five minutes): build the context block the
     office-hours skill specifies (problem statement, the key answers with Vlad's verbatim quotes,
     the evidence findings, the agreed premises; nothing from `## Private context`), take the
     startup-mode second-opinion prompt verbatim from the skill, and run it on another model
     family, first `codex exec -s read-only --skip-git-repo-check "<prompt>"`, then
     `gemini-vertex -p "<prompt>" -o text` if Codex fails, then a fresh subagent through the Agent
     tool if both fail. Show the answer verbatim under `SECOND OPINION (<model>)`, add the three to
     five bullet synthesis (agree, disagree and why, does the challenged premise change the
     recommendation), and when a premise was challenged ask the revision check (A revise / B keep,
     with his reason). Both outside models spend cents on the configured keys: say the cost.
6. **Write the ledger.**
   `uv run factory idea set <slug> geo=<CC,CC> language=<xx> buyer="<short label>" signer="<short label>" value_per_customer_eur=<n> provisional=<true|false> notes="<one line>"`
   (buyer and signer at most 12 words; `provisional=true` when any value is an unasked
   recommendation or marked to confirm). Then `ideas/<slug>/intake.md` below its header, in this
   order: `## Pitch (verbatim)` (blockquote); `## Homework` (your four bets with the evidence,
   counts with their window and whether they are lower bounds, three quotes with links, the
   landscape in three lines); `## Decisions` (one entry per brief: the options shown, the
   recommendation, Vlad's answer quoted, the value recorded and its mark: `Vlad's call`,
   `accepted recommendation`, `accepted recommendation (unasked)`); `## Premises` (agreed or
   revised, with his words); `## Second opinion` (model, verbatim output, synthesis, the revision
   decision); `## Private context` (only when step 2 found something); `## Claims checked` (each
   factual claim of the pitch with its evidence from the sweep and a verdict `supported`, `weak`,
   `unchecked (<reason>)` or `deferred to triage` for "someone advertises" and "someone pays");
   `## To confirm` (every provisional value and what settles it, usually the challenge).
7. **Close the step**: `uv run factory plan mark <slug> 1 done`; append
   `- <YYYY-MM-DD> /idea-new: <what the evidence lacked, what took longest, what Vlad overrode>` to
   `ideas/<slug>/learnings.md`; `uv run factory board`.
8. **Summary and assignment, one screen**: title and slug; the values with their marks; your
   position on demand reality and what would change it; the outside voice's challenged premise
   and the decision on it; the private-context rule if any; the cost of the outside voice; the
   next step `/idea-triage` (60 min, 3 EUR); and, as office hours ends, one assignment Vlad can
   do in 48 hours without the factory (two conversations, one message, one observation).

## Rules

- Timebox: about 30 minutes of Vlad's time, ten of homework before he is asked anything. Short
  messages; one brief per message.
- Vlad's words are never cleaned up: the pitch is verbatim, his answers are quoted.
- Evidence or nothing: a number in `intake.md` comes from a research file, a cited page or
  Vlad; a guess is written as a bet, never as a fact. Never write a new tool to get a number.
- Private context never leaves this machine: not in the outside-voice prompt, not in web searches.
- Secrets: never print a key value. Costs: the intake spends nothing beyond the outside voice.
- This skill owns the session until its summary is printed: do not invoke `/gstack-office-hours`
  or any other skill during the intake; the challenge step calls them.
