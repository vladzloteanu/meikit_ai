# The ledger

`ideas/<slug>/` is the factory's folder for one idea, the single source of truth for everything but
the site code (spec section 6). A run that leaves no files did not happen. `factory.ledger` reads
and writes the folder, `idea.yml`, `plan.md` and `learnings.md`; `factory.costs` reads and writes
`costs.jsonl`.

## The folder

| Path | Written by | What |
|---|---|---|
| `idea.yml` | `factory.ledger` | status, dates, buyer, cap, computed totals (below) |
| `plan.md` | `factory.ledger`, you | the steps and workstreams with their status (below) |
| `intake.md` | `/idea-new` | `# Intake — <title>`, the verbatim pitch and the intake answers; not edited after step 1 |
| `brief.md` | `/idea-triage` | the triage brief |
| `costs.jsonl` | `factory.costs` | one line per spend (below) |
| `learnings.md` | every command | `# Learnings — <slug>`, then one `- YYYY-MM-DD <command>: <text>` line per entry, append-only |
| `research/` | the tools | `<tool>_<YYYYMMDD-HHMMSS>.json`; `.gitkeep` keeps the folder in git |

Later plans add `challenge.md`, `experiments/`, `results/`, `channels/`, `creatives/`,
`verdict.md` and `conversations/` (spec section 6).

A slug is lowercase letters, digits, `-` and `_`, and does not start with `-`. Anything else is
not an idea: every function refuses it with `IdeaNotFound` before touching a file, so a typo never
creates a folder and a slug never reaches outside `ideas/`. `_fixture` is the dry-run idea, a dummy
with canned data; the board and `list_ideas` leave it out unless asked, and tests get a fresh copy
of it in a throwaway factory root.

## idea.yml

| Key | Type | Meaning |
|---|---|---|
| `slug` | text | the folder's name; a file that says otherwise is refused |
| `title` | text | working title (the slug when absent) |
| `status` | one of the statuses below | where the idea stands (default `NEW`) |
| `created`, `updated` | `YYYY-MM-DD` | `updated` is set to today by every `save_idea` |
| `geo` | list of country codes | quote `"NO"`: YAML reads a bare `NO` as false |
| `language` | text | the language of the pages and ads (default `en`) |
| `buyer` | text | who pays |
| `signer` | text | who signs the purchase |
| `value_per_customer_eur` | number | first-year gross margin per customer; allowed CAC is a third of it |
| `cap_eur` | number | cash cap, compared with the cash spent by `costs.check_cap` (default 300) |
| `founder_hour_rate_eur` | number | prices founder time (default 100) |
| `repo`, `local_path`, `domain` | text or null | the idea's GitHub repo, its local checkout, its domain |
| `current_experiment` | whole number or null | the experiment being run |
| `provisional` | true or false | the intake values are placeholders still to confirm |
| `notes` | text | free text |
| `totals` | mapping | computed, never edited (below) |

`totals` is `{cash_eur, founder_time_eur, by_kind: {ads, api, llm, domain, founder_time, other}}`,
recomputed from `costs.jsonl` by every `save_idea`. It is a snapshot: ask `factory.costs` for the
live figures. `cash_eur` is every kind but `founder_time`.

Keys the file has that are not in this table are kept: they load into `Idea.extra` and are written
back after the known ones (a migrated v1 idea keeps its `v1_status`; `create_idea(..., extra={...})`
sets them on a new idea). Saving rewrites the file from data, so comments in it are not kept, and
replaces it in one step, so a crash leaves the old file or the new one. A file that cannot be read
(broken YAML, an unknown status, a number that is not a number) raises `IdeaFileError` naming the
file.

## Statuses

`NEW`, `TRIAGED`, `GO`, `NO-GO`, `LAUNCHED`, `RUNNING`, `REWORK`, `BUILD`, `PIVOT`, `PARK`, `DROP`
(`ledger.STATUSES`, in this order). They follow the weekly cycle: `NEW` once the intake is written,
`TRIAGED` once the brief is, `GO` or `NO-GO` after the challenge, `LAUNCHED` when the site is live,
`RUNNING` while traffic or outreach is on, `REWORK` while a workstream changes part of the plan.
`BUILD`, `PIVOT`, `PARK` and `DROP` are the verdict labels (spec section 12); `PARK` is the only
one a human can set over the computed label. Nothing else is accepted: `save_idea` raises
`ValueError`, `load_idea` raises `IdeaFileError`.

## plan.md

One step per line, under a `## Steps` or `## Workstream: <name>` heading:

```
- [<m>] <id>. <name> — `<command>` — <timebox>[ — <YYYY-MM-DD>]
```

The separator is a space, an em dash (U+2014) and a space; the command is in backticks.

| `<m>` | Status | Meaning |
|---|---|---|
| ` ` | `todo` | not started |
| `~` | `doing` | in progress |
| `x` | `done` | finished |
| `-` | `skipped` | decided not to do |
| `!` | `void` | ran but proves nothing (a VOID verdict, broken tracking) |

Ids are `1` to `7` in `## Steps` (the default plan, `ledger.DEFAULT_PLAN`, a new idea's `plan.md`)
and `<workstream>.<n>`, for example `lp-improve.1`, in a workstream section; ids are unique across
the file. A name and a timebox are free text without the separator. The `section` of a step is
`steps` or the workstream's name.

```
## Steps

- [x] 1. intake — `/idea-new` — 15 min — 2026-10-14
- [~] 2. triage — `/idea-triage` — 60 min
- [ ] 3. challenge — `/idea-challenge` — 1 session

## Workstream: lp-improve

- [ ] lp-improve.1. design review — `/gstack-design-review` — 30 min
```

- Lines that do not start with `- [` are ignored: headings, prose, indented items, plain bullets.
- A line that starts with `- [` must be a step, and under a section: otherwise `load_plan`
  raises `PlanParseError`, whose message holds `ideas/<slug>/plan.md:<line>`. A board that meets one
  catches it, shows that idea as `plan.md:<line> invalid` and goes on with the others.
- `next_step` is the first `doing` step, else the first `todo`, in file order; none when the rest
  is done, skipped or void.
- `mark_step(slug, id, status, when=None)` rewrites that one line and nothing else (line endings
  too). The date is `when`; without it `done`, `skipped` and `void` get today's, or keep their own
  when the step already had that status, and `todo` and `doing` get none.

## costs.jsonl

One JSON object per line, appended and never rewritten, keys in this order:

```json
{"ts": "2026-10-14T10:12:03", "kind": "api", "provider": "searchapi", "amount_eur": 0.12, "ref": "serp_ads_20261014-101203.json", "phase": "triage", "note": "12 SERP queries at 0.01 EUR", "channel": null}
```

| Key | Meaning |
|---|---|
| `ts` | local time, ISO 8601 to the second, no offset |
| `kind` | one of `ads`, `api`, `llm`, `domain`, `founder_time`, `other` (`costs.KINDS`) |
| `provider` | who was paid: `meta`, `searchapi`, `neuralbox`, `vlad`... |
| `amount_eur` | number, rounded to 4 decimals |
| `ref` | what to find the spend by: a campaign id, a request id, the research file |
| `phase` | the plan step it belongs to: `triage`, `launch`, `run`... |
| `note` | free text |
| `channel` | the channel when the spend or the founder time was its execution, else null |

- **Cash** is every kind but `founder_time`. The cap counts cash only: founder time is priced at
  `founder_hour_rate_eur` so unpaid channels compare with paid ones, but never counts against it.
  `costs.total(slug, kind=None, phase=None)` sums any selection (founder time included unless
  filtered out); `costs.cash_total(slug)` is the figure for the cap; `costs.summary(slug)` is the
  `totals` block of `idea.yml`.
- `costs.check_cap(slug, planned_eur=0.0, force=False)` raises `CapExceeded` (its message names
  the idea, the cash spent, the amount planned and the cap) when spent plus planned is more than
  `cap_eur`; landing on the cap is allowed. `force` skips the refusal only.
- A wrong line is corrected by appending a negative one. Reading is strict: a line that is not a
  JSON object with a text `kind` and a finite numeric `amount_eur` raises `CostsParseError` naming
  its number, because skipping it would hide spend from the cap.
- `costs.PRICE_TABLE_EUR` holds the per-call price estimates of the API tools (the retro corrects
  them from invoices) and `costs.USD_EUR` converts NeuralBox's `cost_usd`.

## In code

```python
from factory import costs, ledger

idea = ledger.create_idea("dog-groomers", "Dog groomer booking", geo=["FR"], language="fr")
step = ledger.next_step("dog-groomers")                 # Step(id="1", name="intake", ...)
ledger.mark_step("dog-groomers", "1", "done")           # only line 1 of plan.md changes
costs.check_cap("dog-groomers", planned_eur=0.5)        # CapExceeded when over the cap
costs.append("dog-groomers", "api", "searchapi", 0.05, phase="triage")
ledger.append_learning("dog-groomers", "/idea-triage", "serp_ads returned no ads for the trigger")

idea = ledger.load_idea("dog-groomers")
idea.status = "TRIAGED"
ledger.save_idea(idea)                                  # bumps updated, recomputes totals
```

Every error raised on purpose is a `ledger.LedgerError` with a one-line message: `IdeaNotFound`
(names `ideas/` and the known slugs), `IdeaExists`, `IdeaFileError`, `PlanParseError`,
`StepNotFound`, `costs.CapExceeded`, `costs.CostsParseError`. A command catches `LedgerError`,
prints the message and exits 1. Bad arguments (a status that does not exist, a malformed date, an
unknown cost kind, a slug that is not a slug when creating) raise `ValueError`.

`ledger.idea_slugs()` lists the folders that hold an `idea.yml`. A board that must survive one
broken `idea.yml` calls `load_idea` on each slug and catches `LedgerError`; `ledger.list_ideas()`
stops at the first broken one.
