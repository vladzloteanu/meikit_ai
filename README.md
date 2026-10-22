# Ideas Factory

One bootstrapped business idea tested per week until one is worth pursuing. A Claude Code agent
challenges the idea, researches it, launches a small market test from a recipe, measures it and
gives a verdict; the founders decide at every gate. The design is `docs/factory-design.md`, the
rules an agent session follows are in `CLAUDE.md`.

## What is in the repo

| Path | What |
|---|---|
| `.claude/skills/` | the steps of the weekly plan as Claude Code skills: `/idea-new`, `/idea-triage`, later `/idea-challenge`… |
| `tools/factory/` | the `factory` command line: research tools, the ledger, costs, secrets (Python 3.14) |
| `tools/tests/` | the test suite (pytest) |
| `tools/factory/fixtures/` | canned provider answers for dry runs, with their provenance in its README |
| `ideas/<slug>/` | one folder per idea, the ledger (`docs/ledger.md`); `_fixture` is the dry-run idea |
| `docs/` | design, ledger, secrets, doctor, NeuralBox, challenge techniques, build plans |
| `secrets/` | the encrypted config `config.yml.enc` (committed) and its schema `config.yml.example` |
| `bin/secrets` | the encryption scheme (openssl; `docs/secrets.md`) |

## Install

You need git, `make`, `openssl` and [uv](https://docs.astral.sh/uv/) (it installs Python 3.14 on
its own). For the agent side: [Claude Code](https://claude.com/claude-code), the gstack skills,
the Codex CLI (the outside voice) and, optionally, the Gemini CLI; `/idea-new` checks those three
and prints the install lines.

```bash
git clone https://github.com/vladzloteanu/meikit_ai.git astrafable
cd astrafable
make sync            # the virtualenv and the dependencies
```

Then the master key. The config is committed encrypted; the key that opens it is not. Ask Vlad for
`secrets/master.key`, copy it to that path over a private channel and make it yours only:

```bash
chmod 600 secrets/master.key
bin/secrets init     # configures the git textconv for the encrypted file; keeps an existing key
make check           # the tests, then the offline doctor: secrets.master_key must say ok
```

Never commit the key (it is git-ignored) and never paste it anywhere. Without it the tools that
need a provider key refuse to run; the ledger commands, the free tools and every `--dry-run` work.
NeuralBox (the AdsInsights service) runs on Vlad's machine only: `uv run factory doctor` tells
what your machine can do and which channels it unlocks.

## Use it

```bash
make                       # the commands
make board                 # every idea: status, next step, spend against the cap
uv run factory --help      # the tools; each has --dry-run (no key, no network, the fixture idea)
uv run factory doctor      # what is configured
```

In Claude Code, from the repo: `/idea-new <pitch>` starts an idea, `/idea-triage <slug>` runs the
next step; the board names the next command. The plan is one step at a time: each step is
validated on a real idea before the next one is built.

## Contribute

- **Branch and pull request.** Branch from `main`, open a pull request; `make check` is green
  before you ask for a review. Commit and push often: small commits, pushed the same day.
- **Leave nothing stale.** A change to a tool, a field, a status or a command updates, in the
  same pull request, the skills that name it, the docs, this README, `CLAUDE.md` and the
  `Makefile`.
- **Tests first.** A change comes with its test in `tools/tests/`; one file runs with
  `uv run pytest -q tools/tests/test_<name>.py`. Tests never reach a provider: they use the
  fixtures and the `_fixture` idea in a throwaway root.
- **Commits.** A conventional prefix (`feat:`, `fix:`, `docs:`, `chore:`), a body that says why,
  one change per commit.
- **Docs move with the code.** A new tool, field or status updates `docs/ledger.md` or the tool's
  doc, and the skill that uses it.
- **Skills are checklists.** Short, exact commands, evidence or nothing, no value invented to fill
  a field. Change one, then rehearse it on a real idea (or on `_fixture`) before relying on it.
- **Secrets.** Never print, log or paste a value. `make secrets-edit` adds or rotates a key and
  re-encrypts; commit the `.enc`. A leaked key is rotated at the provider, not just removed. The
  default `git diff` of the encrypted file shows one hash per value; keep it so.
- **Private context.** What a pitch says about an employer, a client, a person or an incident stays
  in `intake.md` under `## Private context` and never reaches a page, an ad, a message, a web search
  or a prompt sent to an outside model.
- **Spending.** Every paid tool checks the idea's cash cap (300 EUR) and appends its cost to
  `ideas/<slug>/costs.jsonl`; the outside voices and NeuralBox spend on configured keys: say the
  cost, log it with `uv run factory costs add`.

## Troubleshooting

- `make check` fails at `secrets.master_key`: the key is missing, misplaced or not the one that
  encrypted the committed config. Copy it again from Vlad.
- A tool answers `429` from SearchAPI: the monthly quota is used up; the triage marks those sections
  `pending` with the date it resets.
- Reddit (Arctic Shift) answers `422 Timeout`: the archive throttles; the tool waits within
  `--max-wait-s` and returns lower bounds marked `complete: false`.
- `make fixture` makes real calls with real keys to refresh the fixtures: run it only when a
  provider's answer shape changed.
