# Scout: the store of candidate ideas

Every idea the scouting proposes lands here, whoever proposed it: Claude, Codex, Gemini, a
harvest source, or a founder. The founders decide what is kept; a refused idea stays in the store
with its reason, so no later round proposes it again. The method is `docs/idea-sourcing.md`.

## Files

| Path | What |
|---|---|
| `ideas.yml` | the store: one entry per idea, the single source of truth |
| `board.md` | a readable table rebuilt from `ideas.yml` after every change; `ideas.yml` wins when they differ |
| `prompts/brief.md` | the founder brief sent to outside models: skills and constraints only, no private context |
| `prompts/generate.md`, `prompts/challenge.md` | the generation and challenge prompts, sent with the brief |
| `runs/<date>/` | each round's raw outputs: `<model>_generate.json`, the merged list sent for challenge, `<model>_challenge.json` |
| `costs.jsonl` | the cost of every scouting call, in the ideas' `costs.jsonl` line format |

## An entry in `ideas.yml`

```yaml
- id: sc-001                   # never reused
  title: "..."
  pitch: "..."                 # 2-3 sentences
  buyer: "..."                 # role, company type, size
  job: "..."                   # the job they already pay to get done
  geo: FR | EU | US | RO | global
  price_eur_month: 250
  customers_for_14k: 56
  pattern: marketplace gap     # one of the ten in docs/idea-sourcing.md section 8
  origin: claude | codex | gemini | <harvest source> | vlad
  round: 2026-10-23
  related: [sc-014]            # same buyer or job, another framing
  evidence: []                 # signals: {date, source, url, kind: C|P|R, strength, what}
  first_read: {C: U, P: U, R: U, H: 1, F: 2, conflict: none}   # section 7 of the method
  challenge: {codex: "keep: ...", gemini: "kill: ..."}
  status: proposed
  decision: null               # {date, by, reason: "the founder's words, verbatim"}
```

- **C, P and R** stay `U` until a harvest attaches evidence. A model's opinion is not evidence.
- **H, F and conflict** are Claude's first read, from the idea and the founders' constraints.

## Statuses

`proposed` → `kept` or `refused` (or `parked`). A kept idea gets its evidence harvested, then
becomes `carded` (an intake-ready card with a 48-hour test) and finally `in-factory`, once
`/idea-new` has created `ideas/<slug>/`.

## Refusing, and never repeating

- **To refuse,** a founder says which ideas and why ("refuse sc-007 and sc-012: restaurants have
  no budget"). The agent sets `status: refused` and records the reason verbatim in `decision`.
  Editing `ideas.yml` by hand works too.
- **Every new round reads the whole store before generating.** Each prompt carries every existing
  title with its buyer and job, plus every refusal reason written as a rule. A model may not
  propose anything already in the store, nor anything a refusal reason excludes ("no restaurants"
  excludes every restaurant idea, not one).
- **New ideas are checked against the store before they are added.** Same buyer and same job is a
  duplicate and is dropped. Same buyer or same job is linked through `related`.

## Rules

- Nothing from `founders/` enters `ideas.yml` or a prompt: no employer, client, person or incident.
  An idea born from private context is written in generic terms.
- Outside models never see this repository. The Codex and Gemini command-line tools run from an
  empty folder with no tools. Through NeuralBox (`make prompt` with its `Gemini Generate`), only
  the brief and the list are sent.
- Every call is logged in `costs.jsonl`.
