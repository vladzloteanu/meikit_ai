# Ideas Factory

One bootstrapped business idea tested per week until one is worth pursuing: the agent challenges
the idea, researches, launches a small market test from a recipe, measures and gives a verdict.
The design is `docs/factory-design.md` (approved 2026-10-20). Vlad decides; the agent recommends.

## Start here

- `make` lists the commands; `make board` shows every idea with its status and next step.
- The weekly plan per idea: `/idea-new` → `/idea-triage` → `/idea-challenge` → `/idea-launch` →
  `/idea-status` → conversations → `/idea-verdict` (`ideas/<slug>/plan.md` holds each idea's steps).
  The skills live in `.claude/skills/`; only the first two exist. Each step is validated by Vlad on
  a real idea before the next one is built: never build a later step unasked, never undo what exists.
- The ledger `ideas/<slug>/` is the single source of truth (`docs/ledger.md`): a run that leaves no
  files did not happen. `ideas/_fixture` is the dry-run idea with canned data.
- The tools: `uv run factory <tool>` (`uv run factory --help` lists them). `--dry-run` reads the
  fixtures and writes `<tool>_<stamp>.dryrun.json`; every paid tool checks the idea's cash cap
  (300 EUR) and appends its cost to `costs.jsonl`.
- Tests: `make check` runs pytest, then the offline doctor. Test-first for every change.
- `/idea-new` checks the outside prerequisites (the gstack skills, the Codex CLI, the Gemini CLI)
  and proposes the install lines; nothing is installed silently.

## Rules

- Secrets (`docs/secrets.md`): the values live in `secrets/config.yml.enc` behind `bin/secrets`.
  Never print, echo or paste a value; read key names only. `make secrets-cat` and
  `make secrets-get` never run in a review or a shared terminal, and `SECRETS_TEXTCONV=full` is
  never set in one: the default `git diff` of the encrypted file shows redacted hashes, keep it so.
- Private context: what a pitch says about an employer, a client, a person or an incident stays in
  `intake.md` under `## Private context` and never reaches a page, an ad, an outreach message, a
  web search or a prompt sent to an outside model (Codex, Gemini, a subagent).
- Evidence or nothing: a number in the ledger comes from a research file, a cited page or Vlad.
  A guess is written as a bet or as `unknown — measure by <method>`, never as a fact.
- Vlad's words stay verbatim (the pitch, his answers). The skills do the homework and recommend
  through decision briefs; they never ask him for a value they could propose, and they push back
  once, with evidence, when his pick contradicts it.
- Spending: NeuralBox and the outside voices spend on configured keys. Say the cost, log it with
  `uv run factory costs add`.
- Commits: a conventional prefix (`feat:`, `fix:`, `chore:`, `docs:`), the body says why, and the
  last line is `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Commit and push often:
  every finished piece of work is committed at once and pushed to `origin` (Vlad, 2026-10-22);
  work in progress never sits unpushed at the end of a session.
- End of every task, before reporting: a sweep of what the change makes stale, and the fix in the
  same commit or the next one. Check, every time: the skills in `.claude/skills/` (a tool, flag,
  field or status they name), `docs/` (`ledger.md`, `secrets.md`, `doctor.md`, `neuralbox.md`,
  the design's amendments), `README.md` (install, commands, contribute rules), this `CLAUDE.md`
  (rules and the table below), the `Makefile` (a new command gets a target and its `##` line)
  and the tests. "Nothing to update" is a conclusion reached by looking, not a default.

## Where things are

| What | Where |
|---|---|
| Design, decisions, the first idea | `docs/factory-design.md` |
| Ledger format and the CLI | `docs/ledger.md` |
| Secrets scheme | `docs/secrets.md` |
| Doctor checks and channel eligibility | `docs/doctor.md` |
| NeuralBox (AdsInsights) | `docs/neuralbox.md` |
| Challenge techniques (digest of the gstack skills) | `docs/challenge-techniques.md` |
| Build plans | `docs/superpowers/plans/` |
| Build ledger, rehearsals, outside reviews | `.superpowers/sdd/` (git-ignored scratch) |
| Fixture provenance | `tools/factory/fixtures/README.md` |
