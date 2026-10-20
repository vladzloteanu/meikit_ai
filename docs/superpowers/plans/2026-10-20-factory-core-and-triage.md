# Factory core and triage — implementation plan (plan 1 of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the factory's control plane (repo, secrets, ledger, board, research tools, doctor, entry skills) and prove it by taking the first real idea, the ad-account watchdog, from pitch to a triage brief.

**Architecture:** A Python package `factory` (under `tools/`) exposes one CLI, `factory <tool>`, with deterministic tools that read keys from the encrypted `secrets/config.yml.enc`, write JSON under `ideas/<slug>/research/`, and append every cost to `ideas/<slug>/costs.jsonl`. Markdown skills in `.claude/skills/` orchestrate those tools; the ledger (`idea.yml`, `plan.md`) is the only state. NeuralBox is reached through one client with a tool whitelist and structured output, used only where it holds unique data.

**Tech Stack:** Python 3.14, `uv`, `httpx`, `pyyaml`, `pytest`; bash `bin/secrets` (OpenSSL AES-256-CBC, PBKDF2 100k); `gh` and `vercel` CLIs already logged in; Claude Code project skills.

**Spec:** `docs/factory-design.md` (approved 2026-10-20). Sections 6, 10, 11, 13, 14, 18 are implemented here; sections 7, 8, 9 (recipes, channels, the stand, launch) are plan 2; section 12 (measurement, verdicts, retro) is plan 3.

**Plan sequence:** plan 1 (this file) ends with `ideas/ad-account-watchdog/brief.md` written by the real tools. Plan 2 (`2026-10-xx-challenge-and-launch.md`) adds `/idea-challenge`, recipes, channel kits, the stand template repo and `/idea-launch`. Plan 3 (`2026-10-xx-measure-and-verdict.md`) adds `/idea-status`, the verdict engine, calibration and `/factory-retro`. Plans 2 and 3 are written after plan 1 lands, against the package layout it fixes.

## Global Constraints

- Python `>=3.14`, managed by `uv`; runtime dependencies are exactly `httpx` and `pyyaml`; dev dependencies `pytest`. No LLM call inside any tool except the `nb` tool, which calls NeuralBox.
- Every tool takes `--idea <slug>`, supports `--dry-run` (fixtures, zero cost, no network) and `--selftest` (one minimal real call), writes to `ideas/<slug>/research/<tool>_<YYYYMMDD-HHMMSS>.json`, and appends its cost to `ideas/<slug>/costs.jsonl` (spec section 10).
- Secret values never appear in stdout, logs, exceptions, research files or git. Keys are read through `factory.secrets`; `bin/secrets` is the only decryption path (spec section 11).
- Company boundary: nothing is written into `~/wrk/dolead/*` or `~/wrk/cmt/*`; nothing from Dolead (names, client rows, screenshots, the incident) is written into any idea file (spec sections 4 and 18). NeuralBox keys are copied once and annotated `source: neural_box`.
- AdsInsights output persisted only as aggregated conclusions: counts, shares of named public advertisers, typical hooks. No client-level rows, no raw exports, no Dolead identifiers (spec section 4).
- Defaults: cap 300 EUR cash per experiment, founder rate 100 EUR/h, USD→EUR 0.92 (spec sections 4, 6).
- SE Ranking: pace 2.5 s between calls, country `uk` not `gb`, retry on 429; SearchAPI pace 0.35 s; Arctic Shift honours `X-RateLimit-Reset` (v1 `tools.md`, v1 scripts).
- Idea statuses are exactly `NEW, TRIAGED, GO, NO-GO, LAUNCHED, RUNNING, REWORK, BUILD, PIVOT, PARK, DROP`; plan step statuses are exactly `todo, doing, done, skipped, void` (spec sections 5, 6).
- Commits end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Review Focus

1. **A tool run without `secrets/master.key`** must stop with one line naming `make secrets-init`, not a traceback; `--dry-run` must still work without any key. Pinned in Task 2 (`test_load_without_key_names_setup`) and Task 6 (`test_dry_run_needs_no_secrets`).
2. **A provider that answers 429 or 5xx** must be retried with backoff and then reported as a `ProviderError` with the status and no key material; a half-written research file must never be left behind. Pinned in Task 5 (`test_retry_then_error_redacts_key`) and Task 6 (`test_output_written_atomically`).
3. **A tool asked to spend past the idea's cap** must refuse before the call unless `--force` is given. Pinned in Task 3 (`test_check_cap_raises`) and Task 8 (`test_nb_refuses_over_cap`).
4. **A malformed `plan.md` line** must fail with its line number while the board still renders the other ideas. Pinned in Task 3 (`test_plan_parse_error_has_line`) and Task 4 (`test_board_survives_bad_plan`).
5. **A `--idea` slug that does not exist** (typo) must be refused by every tool before any network call, naming the `ideas/` folder. Pinned in Task 6 (`test_unknown_idea_refused`).

---

### Task 1: Repo skeleton and the `factory` CLI

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `Makefile`, `README.md`
- Create: `tools/factory/__init__.py`, `tools/factory/cli.py`, `tools/factory/paths.py`
- Test: `tools/tests/conftest.py`, `tools/tests/test_cli.py`

**Interfaces:**
- Produces: `factory.cli.main(argv: list[str] | None = None) -> int`; `factory.cli.TOOL_MODULES: list[str]` (module names under `factory.tools`, each exposing `add_parser(sub: argparse._SubParsersAction) -> None` and `run(args: argparse.Namespace) -> int`); `factory.paths.ROOT: Path` (the `FACTORY_ROOT` env var, else `Path(__file__).resolve().parents[2]`), `paths.IDEAS = ROOT / "ideas"`, `paths.DOCS = ROOT / "docs"`, `paths.SECRETS = ROOT / "secrets"`, `paths.idea_dir(slug: str) -> Path`, `paths.research_dir(slug) -> Path`.
- `conftest.py` provides fixture `root(tmp_path, monkeypatch) -> Path` that sets `FACTORY_ROOT`, creates `ideas/` and copies `ideas/_fixture` from the repo once it exists (Task 3).

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_cli.py
from factory.cli import main

def test_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "factory 0.1.0"

def test_unknown_command_exits_2():
    assert main(["no-such-tool"]) == 2

def test_help_lists_tools(capsys):
    main(["--help"])
    assert "board" in capsys.readouterr().out
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tools/tests/test_cli.py -v` — Expected: import error, `factory` not installed.

- [ ] **Step 3: Create `pyproject.toml`**

`[project] name = "astrafable-factory"`, `version = "0.1.0"`, `requires-python = ">=3.14"`, `dependencies = ["httpx>=0.28", "pyyaml>=6"]`; `[project.scripts] factory = "factory.cli:main"`; `[dependency-groups] dev = ["pytest>=8"]`; build backend `hatchling` with `[tool.hatch.build.targets.wheel] packages = ["tools/factory"]`; `[tool.pytest.ini_options] testpaths = ["tools/tests"]`. Run `uv sync` (creates `.venv` and `uv.lock`).

- [ ] **Step 4: Implement `paths.py` and `cli.py`**

`cli.main` builds an argparse parser with `--version`, registers every module in `TOOL_MODULES` (start with `[]`; a stub `board` is added in Task 4, so for now register a `version` no-op so the help test has a name to find: use `"board"` only after Task 4 and make `test_help_lists_tools` assert on `"version"` until then). Unknown commands return 2 via `parser.exit`-free handling (catch `SystemExit` from argparse and return its code). `main` returns the tool's `run(args)` result.

- [ ] **Step 5: `.gitignore`, `Makefile`, `README.md`**

`.gitignore`: `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `secrets/master.key`, `secrets/config.yml`, `ideas/*/research/*.tmp`. `Makefile` targets: `sync` (`uv sync`), `test` (`uv run pytest -q`), `check` (`test` + `uv run factory doctor --offline`, the doctor arrives in Task 9, so leave `check` as `test` until then), `fixture` (runs `scripts/fixture.sh`, Task 10). `README.md`: three lines, points at `CLAUDE.md` and `docs/factory-design.md`.

- [ ] **Step 6: Run tests, commit**

Run: `uv run pytest -q` — Expected: 3 passed.
```bash
git add -A && git commit -m "feat: factory package skeleton, CLI entry point, uv project"
```

---

### Task 2: Secrets layer

**Files:**
- Create: `bin/secrets` (verbatim copy of `~/wrk/pers/personal_skills_and_tools/bin/secrets`, mode 755), `secrets/.gitignore`, `secrets/config.yml.example`, `.gitattributes`
- Create: `tools/factory/secrets.py`, `tools/factory/tools/secrets_import_nb.py`, `docs/secrets.md`
- Modify: `Makefile` (targets `secrets-init`, `secrets-edit`, `secrets-cat`, `secrets-get K=…`, `secrets-apply-diff`, each delegating to `bin/secrets`)
- Test: `tools/tests/test_secrets.py`

**Interfaces:**
- Produces: `factory.secrets.load(root: Path | None = None, *, refresh: bool = False) -> dict` (runs `bin/secrets decrypt <root>/secrets/config.yml.enc <root>/secrets/master.key`, parses YAML, caches per root); `secrets.get(dotpath: str, default: Any = MISSING) -> Any` raising `SecretMissing(dotpath)`; exceptions `SecretsUnavailable(msg)` whose message contains `make secrets-init` when the key file is absent and `bin/secrets encrypt` when the `.enc` is absent; `secrets.redact(text: str) -> str` replacing every string value of length ≥ 8 found anywhere in the loaded config with `***` (no-op when secrets are unavailable).
- `secrets_import_nb` CLI: `factory secrets-import-nb [--nb-root ~/wrk/dolead/neural_box] [--dry-run]`: reads `make -C <nb-root> secrets-cat` and `<nb-root>/.env` (`NB_API_KEY`), decrypts the factory config, writes the mapped values with sibling `source: neural_box` and `imported_at: <date>`, re-encrypts via `bin/secrets encrypt`, prints only the list of dotpaths written. Mapping: `tools.SearchAPI.api_key→providers.searchapi.api_key`, `tools.SEranking.api_token→providers.seranking.api_token`, `tools.Apify.api_key→providers.apify.api_key`, `tools.Firecrawl.api_key→providers.firecrawl.api_key`, `tools.Tavily.api_key→providers.tavily.api_key`, `tools.ScreenshotAPI.token→providers.screenshotapi.token`, `tools.OpenAI.api_key→providers.openai.api_key`, `tools.Legnext.api_key→providers.legnext.api_key`, `tools.FalAI.api_key→providers.fal.api_key`, `tools.ElevenLabs.api_key→providers.elevenlabs.api_key`, `tools.Submagic.api_key→providers.submagic.api_key`, `tools.Gemini.vertex_ai→providers.gemini.vertex_ai` (whole mapping), `.env NB_API_KEY→nb.api_key`.

- [ ] **Step 1: Write the failing tests**

```python
# tools/tests/test_secrets.py
import subprocess, yaml
from factory import secrets
from factory.secrets import SecretsUnavailable, SecretMissing

def make_root(tmp_path):
    (tmp_path / "secrets").mkdir()
    (tmp_path / "bin").mkdir()
    # copy repo bin/secrets into tmp root
    ...
    subprocess.run([tmp_path/"bin/secrets", "generate-key", tmp_path/"secrets/master.key"], check=True)
    (tmp_path/"secrets/config.yml").write_text(yaml.safe_dump({"providers": {"searchapi": {"api_key": "abcdefgh12345"}}, "nb": {"url": "http://127.0.0.1:3076"}}))
    subprocess.run([tmp_path/"bin/secrets", "encrypt", tmp_path/"secrets/config.yml", tmp_path/"secrets/config.yml.enc", tmp_path/"secrets/master.key"], check=True)
    (tmp_path/"secrets/config.yml").unlink()
    return tmp_path

def test_load_and_get(tmp_path):
    root = make_root(tmp_path)
    assert secrets.load(root)["nb"]["url"] == "http://127.0.0.1:3076"
    assert secrets.get("providers.searchapi.api_key", root=root) == "abcdefgh12345"

def test_get_missing_raises(tmp_path):
    root = make_root(tmp_path)
    try: secrets.get("providers.nope.key", root=root); assert False
    except SecretMissing as e: assert "providers.nope.key" in str(e)

def test_load_without_key_names_setup(tmp_path):
    (tmp_path / "secrets").mkdir()
    try: secrets.load(tmp_path, refresh=True); assert False
    except SecretsUnavailable as e: assert "make secrets-init" in str(e)

def test_redact_hides_values(tmp_path):
    root = make_root(tmp_path); secrets.load(root, refresh=True)
    assert "abcdefgh12345" not in secrets.redact("key=abcdefgh12345 ok", root=root)
```

- [ ] **Step 2: Run to see them fail** — Run: `uv run pytest tools/tests/test_secrets.py -v` — Expected: `ModuleNotFoundError: factory.secrets`.

- [ ] **Step 3: Copy `bin/secrets`, write `secrets/.gitignore` (`master.key`, `config.yml`), `.gitattributes` (`secrets/config.yml.enc diff=encrypted`), `secrets/config.yml.example`**

The example holds the spec section 11 factory schema with empty strings: `operator: {name, address, email, siren}`, `nb: {url: "http://127.0.0.1:3076", api_key, user_email}`, `providers: {searchapi: {api_key}, seranking: {api_token}, apify: {api_key}, firecrawl: {api_key}, tavily: {api_key}, screenshotapi: {token}, gemini: {vertex_ai: {}}, openai: {api_key}, legnext: {api_key}, fal: {api_key}, elevenlabs: {api_key}, submagic: {api_key}}`, `accounts: {github: {owner: vladzloteanu}, vercel: {scope: vladzloteanu-4035}, meta: {business_id, ad_account_id, system_user_token, app_id, app_secret}, google_ads: {customer_id, developer_token, oauth: {}}, stripe: {secret_key}, porkbun: {api_key, secret}, resend: {account_key}, sending_domain: {domain, tool, api_key}, turnstile: {site_key, secret_key}}`, `ideas: {}`.

- [ ] **Step 4: Implement `tools/factory/secrets.py` with the signatures above**

Decryption is a `subprocess.run([ROOT/"bin/secrets", "decrypt", enc, key], capture_output=True)`; on non-zero exit raise `SecretsUnavailable` with the script's stderr (which holds no values). `redact` collects leaf strings of the cached dict.

- [ ] **Step 5: Run tests** — Expected: 4 passed.

- [ ] **Step 6: Implement `secrets_import_nb.py` and register it in `TOOL_MODULES`**

Also add `docs/secrets.md`: layout, the two layers (section 11), the import tool, the "never print values" rule, how to rotate (`make secrets-edit`).

- [ ] **Step 7: Create the real factory config (one-time, values never shown)**

Run `make secrets-init`; `cp secrets/config.yml.example secrets/config.yml`; set `operator.name: Vlad Zloteanu`, `operator.email` left for Vlad, `nb.user_email: astrafable@local` (replace if NeuralBox rejects it in Task 8's selftest); `bin/secrets encrypt`; `rm secrets/config.yml`; then `uv run factory secrets-import-nb` and check its output lists 13 dotpaths. Verify with `make secrets-get K=providers.seranking.source` → `neural_box`.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "feat: encrypted factory secrets (bin/secrets scheme), loader, NeuralBox key import"
```
Verify `git show --stat HEAD` lists `secrets/config.yml.enc` and not `master.key` or `config.yml`.

---

### Task 3: Ledger: `idea.yml`, `plan.md`, `costs.jsonl`, fixture idea

**Files:**
- Create: `tools/factory/ledger.py`, `tools/factory/costs.py`, `docs/ledger.md`
- Create: `ideas/_fixture/idea.yml`, `ideas/_fixture/plan.md`, `ideas/_fixture/intake.md`, `ideas/_fixture/brief.md`, `ideas/_fixture/costs.jsonl`, `ideas/_fixture/learnings.md`, `ideas/_fixture/research/.gitkeep`
- Test: `tools/tests/test_ledger.py`, `tools/tests/test_costs.py`

**Interfaces:**
- Produces: `ledger.STATUSES: list[str]` (the eleven, in spec order); `@dataclass Idea(slug, title, status, created: str, updated: str, geo: list[str], language: str, buyer: str, signer: str, value_per_customer_eur: float, cap_eur: float, founder_hour_rate_eur: float, repo: str | None, local_path: str | None, domain: str | None, current_experiment: int | None, provisional: bool, notes: str, totals: dict)`; `ledger.load_idea(slug) -> Idea` (raises `IdeaNotFound(slug)` whose message names `ideas/`), `ledger.save_idea(idea) -> None` (rewrites `idea.yml`, bumps `updated`), `ledger.list_ideas(include_fixture=False) -> list[Idea]`, `ledger.create_idea(slug, title, **fields) -> Idea` (creates the folder, `idea.yml`, default `plan.md`, `intake.md` with a `# Intake — <title>` header, `learnings.md`, empty `costs.jsonl`, `research/`), `ledger.append_learning(slug, command: str, text: str) -> None` (line `- YYYY-MM-DD <command>: text`).
- Plan: `@dataclass Step(id: str, name: str, command: str, timebox: str, status: str, done_at: str | None, section: str)`; `ledger.load_plan(slug) -> list[Step]`; `ledger.next_step(slug) -> Step | None` (first `todo` or `doing`); `ledger.mark_step(slug, step_id, status, when: str | None = None) -> Step`; `ledger.DEFAULT_PLAN: str` (the seven steps of spec section 5 with their commands and timeboxes: `1. intake — /idea-new — 15 min`, `2. triage — /idea-triage — 60 min`, `3. challenge — /idea-challenge — 1 session`, `4. launch — /idea-launch — 1 day`, `5. run — /idea-status — 5 min/day`, `6. conversations — manual — 5 × 20 min`, `7. verdict — /idea-verdict — 30 min`); `PlanParseError(line_no: int, text: str)`.
- `plan.md` grammar (one step per line, under a `## Steps` or `## Workstream: <name>` heading): `- [<m>] <id>. <name> — `<command>` — <timebox>[ — <YYYY-MM-DD>]` where `<m>` is ` ` todo, `~` doing, `x` done, `-` skipped, `!` void; ids are `1`…`7` for the default plan and `<ws>.<n>` (for example `lp-improve.1`) inside a workstream section.
- Costs: `costs.KINDS = ["ads","api","llm","domain","founder_time","other"]`; `costs.PRICE_TABLE_EUR = {"searchapi": 0.01, "seranking": 0.02, "firecrawl": 0.01, "arcticshift": 0.0, "algolia": 0.0, "rdap": 0.0}` (estimates, corrected by the retro); `costs.USD_EUR = 0.92`; `costs.append(slug, kind, provider, amount_eur, ref="", phase="", note="", channel=None) -> dict` (line `{ts, kind, provider, amount_eur, ref, phase, note, channel}`); `costs.total(slug, kind=None, phase=None) -> float`; `costs.check_cap(slug, planned_eur=0.0, force=False) -> None` raising `CapExceeded(slug, total, cap)` when `total + planned > idea.cap_eur` and not `force`; cash kinds exclude `founder_time`.

- [ ] **Step 1: Write the failing tests**

```python
# tools/tests/test_ledger.py (uses the `root` fixture with the copied _fixture idea)
def test_load_fixture_idea(root):
    i = ledger.load_idea("_fixture"); assert i.status == "RUNNING" and i.cap_eur == 300

def test_list_ideas_skips_fixture(root):
    assert all(i.slug != "_fixture" for i in ledger.list_ideas())

def test_plan_next_and_mark(root):
    assert ledger.next_step("_fixture").id == "5"
    s = ledger.mark_step("_fixture", "5", "done", when="2026-10-21")
    assert s.status == "done" and s.done_at == "2026-10-21"
    assert "- [x] 5. run" in (root/"ideas/_fixture/plan.md").read_text()

def test_plan_parse_error_has_line(root):
    p = root/"ideas/_fixture/plan.md"; p.write_text(p.read_text() + "\n- [x] broken line\n")
    with pytest.raises(ledger.PlanParseError) as e: ledger.load_plan("_fixture")
    assert e.value.line_no > 1

def test_create_idea_writes_files(root):
    i = ledger.create_idea("demo", "Demo", geo=["FR"], language="fr", cap_eur=300)
    d = root/"ideas/demo"
    assert (d/"idea.yml").exists() and (d/"plan.md").exists() and (d/"costs.jsonl").exists()
    assert ledger.next_step("demo").id == "1"

def test_unknown_idea_message(root):
    with pytest.raises(ledger.IdeaNotFound) as e: ledger.load_idea("nope")
    assert "ideas/" in str(e.value)

# tools/tests/test_costs.py
def test_append_and_total(root):
    costs.append("_fixture", "api", "searchapi", 0.05, phase="triage")
    assert costs.total("_fixture", kind="api") >= 0.05

def test_check_cap_raises(root):
    costs.append("_fixture", "ads", "meta", 299.0)
    with pytest.raises(costs.CapExceeded): costs.check_cap("_fixture", planned_eur=5.0)
    costs.check_cap("_fixture", planned_eur=5.0, force=True)

def test_founder_time_not_cash(root):
    costs.append("_fixture", "founder_time", "vlad", 1000.0)
    costs.check_cap("_fixture")  # no raise
```

- [ ] **Step 2: Run to see them fail** — Expected: import errors.

- [ ] **Step 3: Write the fixture idea**

`ideas/_fixture/idea.yml`: slug `_fixture`, title `Fixture idea (dry runs only)`, status `RUNNING`, geo `[FR]`, language `fr`, buyer `independent dog groomers`, value 228, cap 300, rate 100, current_experiment 1, provisional false. `plan.md`: the default plan with steps 1–4 `[x]` dated, 5 `[ ]`. `intake.md`: a two-paragraph fake pitch. `brief.md`: a short brief in the Task 10 template. `costs.jsonl`: three lines (api 0.12, llm 0.28, founder_time 25). `learnings.md`: one line.

- [ ] **Step 4: Implement `ledger.py` and `costs.py`** with the signatures above; `plan.md` parsing is a regex per line, non-step lines are ignored, a line starting with `- [` that does not match raises `PlanParseError`.

- [ ] **Step 5: Run tests** — Expected: all pass. Write `docs/ledger.md` (the folder, `idea.yml` keys, the `plan.md` grammar, `costs.jsonl` line, statuses).

- [ ] **Step 6: Commit** — `git commit -m "feat: idea ledger (idea.yml, plan.md grammar, costs.jsonl) and fixture idea"`

---

### Task 4: Board and ledger CLI

**Files:**
- Create: `tools/factory/tools/board.py`, `tools/factory/tools/idea.py`, `tools/factory/tools/plan.py`, `tools/factory/tools/costs_cmd.py`
- Modify: `tools/factory/cli.py` (`TOOL_MODULES += ["board", "idea", "plan", "costs_cmd"]`, `costs_cmd` registers the name `costs`)
- Test: `tools/tests/test_board_cli.py`

**Interfaces:**
- `factory board [--json] [--all]`: one row per idea, columns `slug | status | step | exp | spend/cap | updated | next`; `step` is the next step id and name, `spend` is `costs.total(slug)` excluding founder time; `--all` includes `_fixture`; `--json` prints a list of dicts with the same keys. A `PlanParseError` in one idea renders that row with `step = "plan.md:<line> invalid"` and does not abort.
- `factory idea new <slug> --title T [--geo FR,US] [--language en] [--buyer ..] [--signer ..] [--value-eur N] [--cap-eur 300] [--rate-eur 100] [--provisional] [--notes ..]` → `ledger.create_idea`; refuses an existing slug (exit 1).
- `factory idea set <slug> key=value [key=value ...]` → typed update of `Idea` fields; `status` validated against `STATUSES`.
- `factory plan show <slug>` (table), `factory plan next <slug>` (one line `id. name — command — timebox`), `factory plan mark <slug> <id> <status>`.
- `factory costs add --idea S --kind K --amount-eur N [--provider P] [--phase ..] [--note ..] [--channel ..]`, `factory costs total --idea S [--json]` (prints totals by kind and the cap).

- [ ] **Step 1: Write the failing tests** (`main([...])` with `capsys`; the `root` fixture)

```python
def test_board_lists_fixture_only_with_all(root, capsys):
    main(["board"]); assert "_fixture" not in capsys.readouterr().out
    main(["board", "--all"]); assert "_fixture" in capsys.readouterr().out

def test_idea_new_then_board(root, capsys):
    assert main(["idea", "new", "demo", "--title", "Demo", "--geo", "FR"]) == 0
    main(["board", "--json"]); rows = json.loads(capsys.readouterr().out)
    assert rows[0]["slug"] == "demo" and rows[0]["next"].startswith("1.")

def test_board_survives_bad_plan(root, capsys):
    main(["idea", "new", "demo", "--title", "Demo"])
    (root/"ideas/demo/plan.md").write_text("## Steps\n- [x] garbage\n")
    assert main(["board", "--all"]) == 0
    out = capsys.readouterr().out; assert "invalid" in out and "_fixture" in out

def test_plan_mark_and_costs(root, capsys):
    main(["plan", "mark", "_fixture", "5", "done"])
    main(["plan", "next", "_fixture"]); assert capsys.readouterr().out.startswith("6.")
    main(["costs", "add", "--idea", "_fixture", "--kind", "api", "--amount-eur", "0.5", "--provider", "searchapi"])
    main(["costs", "total", "--idea", "_fixture", "--json"]); assert json.loads(capsys.readouterr().out)["api"] >= 0.5
```

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement the four modules.** Table rendering is a small helper `factory.tables.render(rows: list[dict], columns: list[str]) -> str` in `tools/factory/tables.py` (used by every tool's summary). - [ ] **Step 4: Run tests, expected pass.** - [ ] **Step 5: Commit** — `git commit -m "feat: board, idea, plan and costs commands"`

---

### Task 5: HTTP client and the SearchAPI / SE Ranking providers

**Files:**
- Create: `tools/factory/http.py`, `tools/factory/providers/__init__.py`, `tools/factory/providers/searchapi.py`, `tools/factory/providers/seranking.py`
- Create fixtures: `tools/factory/fixtures/searchapi/google.json`, `meta_ad_library.json`, `tiktok_ads_library.json`, `google_ads_transparency_center.json`, `linkedin_ad_library.json`; `tools/factory/fixtures/seranking/analyze_keywords.json`, `domain_keywords.json`, `domain_advertising.json`, `domain_overview.json`
- Test: `tools/tests/test_http.py`, `tools/tests/test_providers.py`

**Interfaces:**
- `http.Client(provider: str, base_url: str, headers: dict | None = None, pace_s: float = 0.0, retries: int = 3, timeout_s: float = 90.0, dry_run: bool = False, transport: httpx.BaseTransport | None = None)`; `.get_json(path: str, params: dict | None = None, *, fixture: str | None = None) -> Any`; `.post_json(path: str, json: Any = None, *, fixture: str | None = None) -> Any`; `.calls: int`; `ProviderError(provider: str, status: int | None, detail: str)` (detail is `secrets.redact`-ed and cut to 300 chars); retry on 429 and ≥500 with sleep `max(2 * attempt, Retry-After or X-RateLimit-Reset seconds, capped 300)`; pacing sleeps `pace_s` between consecutive calls of one client; `dry_run` returns `json.load` of `tools/factory/fixtures/<fixture>.json` and makes no request (and `calls` still increments so cost estimates can be previewed, but tools log nothing in dry-run).
- `searchapi.client(dry_run=False) -> Client` (base `https://www.searchapi.io/api/v1`, pace 0.35, key `providers.searchapi.api_key` sent as the `api_key` query param); `searchapi.search(client, engine: str, **params) -> dict` (fixture name = engine).
- `seranking.client(dry_run=False) -> Client` (base `https://api4.seranking.com`, header `Authorization: Token <key>`, pace 2.5); `seranking.cc(geo: str) -> str` (`GB`/`UK`→`uk`, else lowercase); `seranking.analyze_keywords(client, cc, keywords: list[str]) -> list[dict]` (POST `/research/{cc}/analyze-keywords/` with JSON `{"keywords": [...]}`, batches of 20, accepts status 200 or 201; each row has `keyword, volume, cpc, difficulty, competition, intents, history_trend, is_data_found`); `seranking.domain_keywords(client, cc, domain, limit=60) -> list[dict]` (GET `/research/{cc}/keywords/?domain=&limit=`); `seranking.domain_advertising(client, cc, domain) -> list[dict]` (GET `/research/{cc}/advertising/?domain=`); `seranking.domain_overview(client, cc, domain) -> dict` (GET `/research/{cc}/overview/?domain=`).

- [ ] **Step 1: Write the failing tests**

```python
# tools/tests/test_http.py
def test_retry_then_ok(monkeypatch):
    seen = []
    def handler(req):
        seen.append(req.url.path)
        return httpx.Response(429, headers={"Retry-After": "0"}) if len(seen) == 1 else httpx.Response(200, json={"ok": 1})
    monkeypatch.setattr(time, "sleep", lambda s: None)
    c = Client("t", "https://x.test", transport=httpx.MockTransport(handler))
    assert c.get_json("/a") == {"ok": 1} and len(seen) == 2

def test_retry_then_error_redacts_key(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    c = Client("t", "https://x.test", retries=2, transport=httpx.MockTransport(lambda r: httpx.Response(500, text="boom api_key=SECRETVALUE123")))
    with pytest.raises(ProviderError) as e: c.get_json("/a", params={"api_key": "SECRETVALUE123"})
    assert "SECRETVALUE123" not in str(e.value) and e.value.status == 500

def test_dry_run_reads_fixture():
    c = Client("searchapi", "https://x.test", dry_run=True)
    assert "organic_results" in c.get_json("/search", fixture="searchapi/google")

def test_pacing_sleeps(monkeypatch):
    slept = []; monkeypatch.setattr(time, "sleep", slept.append)
    c = Client("t", "https://x.test", pace_s=2.5, transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
    c.get_json("/a"); c.get_json("/b"); assert 2.5 in slept

# tools/tests/test_providers.py
def test_analyze_keywords_posts_json_batches():
    bodies = []
    def handler(req): bodies.append(json.loads(req.content)); return httpx.Response(201, json=[{"keyword": k, "volume": 10, "cpc": 0, "is_data_found": True} for k in bodies[-1]["keywords"]])
    c = Client("seranking", "https://x.test", transport=httpx.MockTransport(handler))
    rows = seranking.analyze_keywords(c, "us", [f"kw{i}" for i in range(25)])
    assert len(rows) == 25 and len(bodies) == 2 and bodies[0]["keywords"][0] == "kw0"

def test_cc_mapping():
    assert seranking.cc("GB") == "uk" and seranking.cc("FR") == "fr"
```

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement `http.py`, `searchapi.py`, `seranking.py`.** Redaction in `ProviderError`: apply `secrets.redact` when secrets load, and additionally strip any query value of a param named `api_key`/`token`.

- [ ] **Step 4: Capture the fixtures with one real call each** (a throwaway script in the scratchpad that uses the real clients, writes each response into `tools/factory/fixtures/...`, and asserts no secret value appears in the written files: `grep -c` of the key must be 0). Queries to use: google `facebook ad account hacked` (gl us), meta_ad_library `ad account security` (country ALL), tiktok `ad account hacked`, transparency `domain=hootsuite.com region=US num=5`, linkedin `ad account security`; analyze_keywords `["facebook ad account hacked","business manager hacked"]` (us); domain_* on `hootsuite.com` (us). Trim each fixture to ≤ 10 result items.

- [ ] **Step 5: Run tests** — Expected: all pass. - [ ] **Step 6: Commit** — `git commit -m "feat: http client with retry, pacing, dry-run fixtures; SearchAPI and SE Ranking providers"`

---

### Task 6: Demand tools: `serp_ads`, `keyword_volume`, `ad_library`

**Files:**
- Create: `tools/factory/toolbase.py`, `tools/factory/tools/serp_ads.py`, `tools/factory/tools/keyword_volume.py`, `tools/factory/tools/ad_library.py`
- Modify: `tools/factory/cli.py` (register the three)
- Test: `tools/tests/test_toolbase.py`, `tools/tests/test_demand_tools.py`

**Interfaces:**
- `toolbase.add_common(parser) -> None` adds `--idea` (required unless `--selftest`), `--dry-run`, `--json`, `--out`, `--selftest`, `--phase` (default `triage`), `--force`; `toolbase.Run` context: `with toolbase.run(args, tool="serp_ads") as r:` validates the idea (`IdeaNotFound` → message naming `ideas/`, exit 1), checks the cap with the tool's planned cost (`costs.check_cap`; `CapExceeded` → exit 1 unless `--force`), exposes `r.dry_run`, `r.slug`; `r.write(data: dict) -> Path` writes `research/<tool>_<ts>.json` via a `.tmp` file renamed at the end (atomic), or `--out`; `r.log_cost(provider: str, calls: int) -> None` appends `api` cost `calls × PRICE_TABLE_EUR[provider]` (skipped in dry-run); `r.summary(text: str)` prints unless `--json`, in which case `r.write` also prints the JSON.
- `factory serp_ads --idea S (--keywords K ... | --keywords-file F) [--gl us] [--hl en] [--num 10]` → `{"gl","hl","queries": {kw: {"n_ads": int, "ads": [{"position","title","domain","link","snippet","sitelinks"}], "organic": [{"p","domain","title","url"}]}}, "advertisers": {domain: n_keywords}}`; summary table `keyword | n_ads | advertisers`.
- `factory keyword_volume --idea S --cc us (--keywords K ... | --buckets-file F.json) [--language en]` where the buckets file is `{"solution_aware": [...], "problem_aware": [...], "trigger": [...], "adjacent_budget": [...]}` → `{"cc", "keywords": {kw: {"volume","cpc","competition","difficulty","intents","trend_12m": [..], "found": bool, "bucket"}}, "buckets": {bucket: {"volume_sum","n","cpc_median"}}}`; summary table per bucket then top 15 keywords by volume.
- `factory ad_library --idea S --engine (meta|tiktok|linkedin|google_transparency) (--q TERM | --domain D) [--country ALL|FR|..] [--region US] [--num 20]` → `{"engine","query","total_results": int, "items": [{"advertiser","page_or_domain","text","format","first_seen","last_seen","active","link"}]}` using the field paths from the v1 scripts (`meta_ads.py`, `tiktok_ads.py`, `linkedin_ads.py`, `google_transparency.py`); engine name mapping `meta→meta_ad_library`, `tiktok→tiktok_ads_library`, `linkedin→linkedin_ad_library`, `google_transparency→google_ads_transparency_center`.

- [ ] **Step 1: Write the failing tests**

```python
def test_dry_run_needs_no_secrets(root, capsys, monkeypatch):
    monkeypatch.setattr(secrets, "load", lambda *a, **k: (_ for _ in ()).throw(SecretsUnavailable("no key")))
    assert main(["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--keywords", "x"]) == 0
    assert list((root/"ideas/_fixture/research").glob("keyword_volume_*.json"))

def test_unknown_idea_refused(root, capsys):
    assert main(["serp_ads", "--idea", "nope", "--dry-run", "--keywords", "x"]) == 1
    assert "ideas/" in capsys.readouterr().err

def test_output_written_atomically(root, monkeypatch):
    # make the provider raise after the client call: no *.json must remain, only no .tmp either
    monkeypatch.setattr(searchapi, "search", lambda *a, **k: (_ for _ in ()).throw(ProviderError("searchapi", 500, "x")))
    assert main(["serp_ads", "--idea", "_fixture", "--keywords", "x", "--dry-run"]) == 1
    assert not list((root/"ideas/_fixture/research").glob("serp_ads_*"))

def test_keyword_volume_buckets(root, tmp_path, capsys):
    f = tmp_path/"b.json"; f.write_text(json.dumps({"trigger": ["facebook ad account hacked"], "solution_aware": ["business manager hacked"]}))
    main(["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--buckets-file", str(f), "--json"])
    out = json.loads(capsys.readouterr().out); assert set(out["buckets"]) == {"trigger", "solution_aware"}

def test_cost_logged_outside_dry_run(root, monkeypatch):
    monkeypatch.setattr(searchapi, "client", lambda dry_run=False: Client("searchapi", "https://x.test", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=json.load(open(FIXTURES/"searchapi/google.json"))))))
    main(["serp_ads", "--idea", "_fixture", "--keywords", "a", "--keywords", "b"])
    assert costs.total("_fixture", kind="api") >= 0.02
```

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement `toolbase.py` and the three tools.** - [ ] **Step 4: Run tests, expected pass.**

- [ ] **Step 5: Selftests** — Run `uv run factory keyword_volume --selftest` and `uv run factory serp_ads --selftest` and `uv run factory ad_library --selftest`; each prints `OK <provider> <n> items` after one real call (ad_library selftest uses `--engine meta --q "ad account"`). Expected: three `OK` lines.

- [ ] **Step 6: Commit** — `git commit -m "feat: demand tools serp_ads, keyword_volume, ad_library with cost logging"`

---

### Task 7: Voice-of-customer and landscape tools

**Files:**
- Create: `tools/factory/providers/arcticshift.py`, `algolia_hn.py`, `firecrawl.py`, `rdap.py`
- Create: `tools/factory/tools/reddit_mentions.py`, `hn_mentions.py`, `pricing_scan.py`, `domain_check.py`
- Create fixtures: `fixtures/arcticshift/posts_search.json`, `comments_search.json`; `fixtures/algolia/search_by_date.json`; `fixtures/firecrawl/scrape.json`; `fixtures/rdap/available.json` (an empty 404 marker), `rdap/taken.json`
- Modify: `tools/factory/cli.py`
- Test: `tools/tests/test_voc_tools.py`

**Interfaces:**
- `arcticshift.client(dry_run) -> Client` (base `https://arctic-shift.photon-reddit.com`, pace 1.0, no key); `posts_search(client, query, subreddit=None, after=None, before=None, limit=100) -> list[dict]` (GET `/api/posts/search`, params `query, subreddit, after, before, limit, sort=desc`; `after`/`before` are ISO dates); `comments_search(client, body, subreddit=None, after=None, before=None, limit=100) -> list[dict]` (GET `/api/comments/search`, param `body`). A 422 whose body contains `slow down` is a rate limit: sleep `X-RateLimit-Reset` seconds (cap 300) and retry (handled by `Client` because 422+that body is added to its retry predicate via `retry_on: Callable[[httpx.Response], bool]`, a new optional `Client` argument).
- `algolia_hn.client(dry_run)` (base `https://hn.algolia.com/api/v1`, pace 0.2); `search_by_date(client, query, tag: str, since_ts: int, until_ts: int, hits_per_page=100) -> dict` (GET `/search_by_date`, params `query, tags, numericFilters=created_at_i>{since},created_at_i<{until}, hitsPerPage, typoTolerance=false`).
- `firecrawl.client(dry_run)` (base `https://api.firecrawl.dev/v1`, header `Authorization: Bearer <providers.firecrawl.api_key>`); `scrape(client, url) -> dict` (POST `/scrape`, JSON `{"url": url, "formats": ["markdown"], "onlyMainContent": true}`; returns `data` with `markdown` and `metadata.title`; if the selftest shows the v1 route is gone, switch base to `/v2` and note it in `docs/tools.md`).
- `rdap.status(client, domain) -> str` (`"available"` on 404, `"taken"` on 200, `"unknown"` otherwise; base `https://rdap.org`, path `/domain/<domain>`; `Client` must not retry 404).
- `factory reddit_mentions --idea S --terms T ... [--subreddits a,b] [--since 2025-10-01] [--until 2026-10-20] [--limit 100]` → `{"terms": {term: {"posts": n, "comments": n, "by_month": {YYYY-MM: n}, "hits": [{"kind","subreddit","title","url","score","created","snippet"}]}}}`; `url` is `https://www.reddit.com` + permalink; summary table `term | posts | comments | top subreddits`.
- `factory hn_mentions --idea S --terms T ... [--since] [--until]` → same shape with `stories`/`comments`.
- `factory pricing_scan --idea S --urls U ...` → `{"pages": [{"url","title","headline","prices": [str], "cta","offer_shape"}]}`; pure helpers `pricing_scan.extract_prices(md: str) -> list[str]` (matches `$29`, `$29/mo`, `29 €`, `29€/mois`, `€29 per month`, `29 EUR`, `From $19`), `pricing_scan.guess_offer_shape(prices, md) -> str` in `{"subscription","one_shot","quote","unknown"}` (`/mo`, `month`, `mois`, `/yr` → subscription; `quote`, `devis`, `contact sales` and no price → quote).
- `factory domain_check --idea S --name N [--tlds com,io,ai,dev,fr]` → `{"name", "domains": {domain: status}, "lab": "<name>.meikit.ai"}`; summary table; no cost.

- [ ] **Step 1: Write the failing tests** (MockTransport for each provider; fixtures for dry-run; `extract_prices` cases: `"Pro $29/mo"→["$29/mo"]`, `"à partir de 19 € par mois"→["19 € par mois"]`, `"no digits"→[]`; `guess_offer_shape(["$29/mo"], "")=="subscription"`; `guess_offer_shape([], "Contact sales for a quote")=="quote"`; `rdap.status` 404→available; Arctic Shift 422 `slow down` then 200 → one result and a sleep of the header's seconds.)

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement providers and tools** (port the query/field logic from v1 `reddit_mentions.py` and `hn_mentions.py`; counts only, no term-rule engine). - [ ] **Step 4: Run tests, expected pass.**

- [ ] **Step 5: Selftests** — `uv run factory reddit_mentions --selftest`, `hn_mentions --selftest`, `pricing_scan --selftest` (scrapes `https://example.com`), `domain_check --selftest` (checks `example.com` → taken). Expected: four `OK` lines. Capture fixtures from these calls.

- [ ] **Step 6: Commit** — `git commit -m "feat: reddit/hn mentions, pricing scan, RDAP domain check"`

---

### Task 8: The NeuralBox tool

**Files:**
- Create: `tools/factory/providers/neuralbox.py`, `tools/factory/tools/nb.py`, `tools/factory/fixtures/neuralbox/respond.json`, `fixtures/neuralbox/adsinsights.json`, `docs/neuralbox.md`
- Modify: `tools/factory/cli.py`
- Test: `tools/tests/test_nb.py`

**Interfaces:**
- `neuralbox.client(dry_run) -> Client` (base `nb.url`, header `X-API-Key: <nb.api_key>`, timeout 600, retries 1); `neuralbox.heartbeat(client) -> dict` (GET `/heartbeat`); `neuralbox.respond(client, prompt: str, *, allowed_tools: list[str] | None = None, schema: dict | None = None, max_turns: int = 8, session_id: str | None = None) -> NBResult` where `NBResult(answer: str, structured: dict | None, cost_usd: float, tools_called: list[str], session_id: str | None, request_id: str | None)`; the request body is `{"prompt": prompt + DISCIPLINE, "allowed_tools": [...], "permission_mode": "bypassPermissions", "max_turns": n, "output_format": {"type": "json_schema", "schema": schema}, "properties": {"user_email": <nb.user_email>}, "session_id": ...}` with `None` fields omitted; `DISCIPLINE = "\n\nIf a tool call fails or a key is missing, say exactly which tool failed. Never invent numbers. Never print secret values."`
- `factory nb ask --idea S (--prompt P | --prompt-file F) [--tools A,B] [--schema F.json] [--max-turns 8] [--session ID]` → writes `{"prompt","answer","structured","cost_usd","tools_called","session_id","request_id"}`; logs `llm`/`neuralbox` cost `cost_usd × USD_EUR` with `ref=request_id`; planned cost for the cap check is 0.5 EUR.
- `factory nb adsinsights --idea S --category C --countries FR,US [--networks facebook,search] [--top 10]` → prompt: resolve `C` with `LookupAdsInsights` (and `ListCategories` when needed), then for each network call `QueryAdsInsights` with `section=aggregations`, `tile=company`, `sort=all`, `countries`, `categories=[resolved]`, `top`; `allowed_tools=["LookupAdsInsights","ListCategories","QueryAdsInsights"]`; `schema = ADSINSIGHTS_SCHEMA` = `{category_resolved: str, countries: [str], networks: [{network: str, total_reach: number, advertisers_count: int, top_companies: [{name: str, share_pct: number}], caveats: [str]}], typical_hooks: [str], not_found: bool}`; the research file holds `structured` only (never `answer`), which is the persistence rule.
- `tools_called` entries are tool names only (strip arguments and outputs from NeuralBox's `ToolCall` objects).

- [ ] **Step 1: Write the failing tests**

```python
def test_respond_body_and_headers(root):
    seen = {}
    def handler(req):
        seen["headers"] = dict(req.headers); seen["body"] = json.loads(req.content)
        return httpx.Response(200, json={"request_id": "r1", "answer": "pong", "structured_output": {"a": 1}, "cost_usd": 0.01, "tools_called": [{"name": "X", "input": {"k": "v"}}], "session_id": "s1"})
    c = Client("neuralbox", "https://nb.test", headers={"X-API-Key": "KEY12345678"}, transport=httpx.MockTransport(handler))
    r = neuralbox.respond(c, "ping", allowed_tools=["X"], schema={"type": "object"}, max_turns=2)
    assert seen["headers"]["x-api-key"] == "KEY12345678"
    b = seen["body"]; assert b["permission_mode"] == "bypassPermissions" and b["allowed_tools"] == ["X"] and b["output_format"]["type"] == "json_schema" and b["prompt"].endswith("Never print secret values.")
    assert r.structured == {"a": 1} and r.tools_called == ["X"] and r.cost_usd == 0.01

def test_nb_ask_logs_cost_and_hides_key(root, monkeypatch, capsys):
    monkeypatch.setattr(neuralbox, "client", lambda dry_run=False: Client("neuralbox", "https://nb.test", headers={"X-API-Key": "KEY12345678"}, transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"request_id": "r1", "answer": "ok", "cost_usd": 1.0, "tools_called": []}))))
    assert main(["nb", "ask", "--idea", "_fixture", "--prompt", "hi"]) == 0
    f = next((root/"ideas/_fixture/research").glob("nb_*.json")); assert "KEY12345678" not in f.read_text()
    assert abs(costs.total("_fixture", kind="llm") - 0.92) < 1e-6 or costs.total("_fixture", kind="llm") >= 0.92

def test_nb_refuses_over_cap(root, capsys):
    costs.append("_fixture", "ads", "meta", 300.0)
    assert main(["nb", "ask", "--idea", "_fixture", "--prompt", "hi", "--dry-run"]) == 1
    assert "cap" in capsys.readouterr().err

def test_adsinsights_persists_structured_only(root, monkeypatch):
    monkeypatch.setattr(neuralbox, "client", lambda dry_run=False: Client("neuralbox", "https://nb.test", transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"request_id": "r", "answer": "RAW ROWS HERE", "structured_output": {"category_resolved": "Home Security", "countries": ["FR"], "networks": [], "typical_hooks": [], "not_found": False}, "cost_usd": 0.3, "tools_called": []}))))
    main(["nb", "adsinsights", "--idea", "_fixture", "--category", "home security", "--countries", "FR"])
    f = next((root/"ideas/_fixture/research").glob("nb_adsinsights_*.json")); assert "RAW ROWS HERE" not in f.read_text()
```

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement provider and tool; write `docs/neuralbox.md`** (what NeuralBox is for the factory, the two subcommands, the cost, the persistence rule, `user_email`, the whitelist, what never to ask it: spending, Dolead client data).

- [ ] **Step 4: Run tests, expected pass.**

- [ ] **Step 5: Selftest** — `uv run factory nb ask --selftest` = heartbeat then a no-tool `respond("Reply with the single word pong", max_turns=1)`; expected `OK neuralbox heartbeat 357 tools; respond cost_usd=0.0x`. If NeuralBox rejects `user_email: astrafable@local`, set `nb.user_email` to Vlad's Dolead work address found in `~/wrk/dolead/neural_box/.env` or its docs (name only, via `make secrets-edit`), and record the fact in `docs/neuralbox.md`.

- [ ] **Step 6: Commit** — `git commit -m "feat: NeuralBox client with whitelist, structured output, AdsInsights summary mode"`

---

### Task 9: Doctor

**Files:**
- Create: `tools/factory/vercel.py`, `tools/factory/tools/doctor.py`, `docs/doctor.md`
- Modify: `tools/factory/cli.py`, `Makefile` (`check` = `test` + `uv run factory doctor --offline`)
- Test: `tools/tests/test_doctor.py`

**Interfaces:**
- `vercel.cli_auth() -> dict | None` reads `~/Library/Application Support/com.vercel.cli/auth.json` (`token`) and `config.json` (`currentTeam`), never prints the token; `vercel.current_scope() -> tuple[str, str | None]` → `("personal", None)` when `currentTeam` is absent or null, else `("team", slug)` from `cachedTeamSlugs`; `vercel.user_plan() -> dict` (GET `https://api.vercel.com/v2/user` with the token → `{"username", "plan"}`).
- `doctor.CHECKS: list[Check]` with `Check(name: str, fn: Callable[[Ctx], Result], needs_network: bool, blocks: str)` and `Result(ok: bool, level: "ok"|"warn"|"fail", detail: str)`; checks, in order: `secrets.master_key` (fail), `secrets.providers` (searchapi, seranking, firecrawl keys present; fail), `nb.heartbeat` (warn), `vercel.login` (`vercel whoami` exit 0; fail, blocks launch), `vercel.scope` (personal; fail, detail names `vercel switch <username>`), `vercel.plan` (`hobby` → warn "Hobby forbids commercial use; upgrade to Pro before the first paid traffic"), `gh.auth` (`gh auth status`; fail, blocks launch), `domain.meikit` (`rdap.status("meikit.ai")`: available → warn "lab domain not bought: /factory-setup step 1"; taken → `dig +short meikit.ai` contains `76.76.21.21` or a `vercel-dns` CNAME else warn), `assets.meta` (`accounts.meta.ad_account_id` set), `assets.google_ads` (`accounts.google_ads.customer_id`), `assets.stripe` (`accounts.stripe.secret_key`), `assets.sending_domain` (`accounts.sending_domain.domain`), `assets.resend` (`accounts.resend.account_key`), `assets.turnstile` (`accounts.turnstile.site_key`); asset checks are `warn` when empty and carry the channel or recipe they unlock.
- `doctor.eligible_channels(results) -> list[str]`: always `["reddit_reply", "reddit_post", "linkedin_outreach", "community_post"]`; plus `google_search` when `assets.google_ads` ok, `meta_feed` when `assets.meta` ok, `cold_email_b2b` when `assets.sending_domain` ok; `doctor.eligible_recipes(results)`: all except `pre-order` unless `assets.stripe` ok.
- CLI `factory doctor [--json] [--offline] [--live]`: `--offline` skips network checks (for `make check`), `--live` additionally runs each provider's selftest; prints a table `check | level | detail` then `eligible channels: …` and `eligible recipes: …`; exit 1 when any `fail`.

- [ ] **Step 1: Write the failing tests** (monkeypatch every `fn` through a fake `Ctx`; assert `eligible_channels` with and without meta/google; assert exit code 1 on a fail; assert `--json` shape `{"checks": [...], "eligible_channels": [...], "eligible_recipes": [...]}`; assert `vercel.current_scope` on a temp config dir with `currentTeam: null` and with a team id).

- [ ] **Step 2: Run to see them fail.** - [ ] **Step 3: Implement.** - [ ] **Step 4: Run tests, expected pass.**

- [ ] **Step 5: Run it for real** — `uv run factory doctor`; expected today: `vercel.scope` fail (team `dolead-product`), `vercel.plan` warn (hobby), `domain.meikit` warn (available), all `assets.*` warn, everything else ok; eligible channels = the four human ones. Do **not** run `vercel switch` here; that is the user's setup step. Write `docs/doctor.md` with the table of checks and what unlocks each channel.

- [ ] **Step 6: Commit** — `git commit -m "feat: factory doctor with channel eligibility"`

---

### Task 10: Skills, fixture script, CLAUDE.md and docs

**Files:**
- Create: `.claude/skills/factory/SKILL.md`, `.claude/skills/idea-new/SKILL.md`, `.claude/skills/idea-triage/SKILL.md`, `.claude/skills/idea-triage/brief-template.md`, `.claude/skills/factory-doctor/SKILL.md`, `.claude/skills/factory-setup/SKILL.md`
- Create: `CLAUDE.md`, `docs/tools.md`, `docs/triage.md`, `docs/setup.md`, `docs/skills.md`, `docs/learnings.md`, `docs/calibration.csv`, `scripts/fixture.sh`
- Modify: `Makefile` (`fixture` target), `README.md`
- Test: `tools/tests/test_docs.py`

**Interfaces (what each skill must contain; all are checklists Vlad runs alone):**
- `/factory` (frontmatter `name: factory`, `description: Entry point: board of ideas, pick or create one, follow the plan or rework a part`): 1) `uv run factory doctor --offline` and show fails; 2) `uv run factory board` and show it; 3) ask with AskUserQuestion: pick a slug or "new idea"; 4) new → invoke `/idea-new`; existing → show `uv run factory plan show <slug>` and ask **follow** (run the command of `plan next`) or **rework** (list workstreams `lp-improve, ab-test, new-creatives, new-channel, re-triage, re-challenge, pivot`; the ones that exist in `workstreams/` are runnable, the others answer "lands in plan 2"); 5) also list ideas with status `RUNNING` that need `/idea-status` today; 6) end with a one-screen summary.
- `/idea-new`: capture the pitch verbatim into `intake.md` under `## Pitch (verbatim)`; ask one at a time: geo, language, buyer, who signs, value per customer (with the first-year gross-margin rule), cap (default 300), founder rate (default 100); when the user is absent or says "later", record provisional values with `provisional: true` and a `## To confirm` list; run `uv run factory idea new <slug> ...`; check any factual claim in the pitch with `serp_ads` or `reddit_mentions` and write the result under `## Claims checked`; mark plan step 1 done; append a learning; summary.
- `/idea-triage`: timebox 60 min and 3 EUR (check `uv run factory costs total --idea S --json` before and after); build the four keyword buckets (5–10 each, idea language + English) into `research/buckets.json`; run `keyword_volume` per geo `cc`; `serp_ads` on the 8 highest-volume keywords; `ad_library` (meta, google_transparency, linkedin) on the top 5 advertiser domains found; `reddit_mentions` and `hn_mentions` on 3–5 pain phrases over the last 12 months; `pricing_scan` on the top 5 competitor landing pages; `nb adsinsights` only when `LookupAdsInsights` knows a matching category (one call, FR plus US); write `brief.md` from `brief-template.md` (sections: Summary; Who pays today (table: advertiser, where seen, promise, price, offer shape); Demand (bucket table + top keywords + CPC range); Complaints (counts + 5 quotes with links); Landscape (incumbents, free alternatives, institutional alternatives); AdsInsights conclusions (aggregated only, or "no matching category"); Triage score (`pays_today 0–2`, `trigger 0–2`, `complaints 0–2` with one line of evidence each); Gate (PASS when any score ≥ 1, else STOP at cost zero); Open questions for the challenge; Cost and time of this triage); `uv run factory idea set S status=TRIAGED`; mark step 2 done; learnings; summary.
- `/factory-doctor`: run `uv run factory doctor` (`--live` on request), explain each fail with its fix, print eligible channels and recipes.
- `/factory-setup`: the resumable checklist from spec section 14, one asset per section with: why, the exact UI steps, the dotpath to paste the key into (`make secrets-edit`), the doctor check that proves it. Order: 1 buy `meikit.ai` (Porkbun or `vercel domains buy`) and point `*` and `@` at Vercel; 2 Vercel: `vercel switch <username>` to the personal scope, Pro upgrade decision; 3 Meta Business Manager, ad account, pixel dataset, system user token; 4 Google Ads account, developer token (basic access), conversion access; 5 Stripe (individual); 6 Resend; 7 Turnstile; 8 Porkbun API; 9 cold-email sending domain and warm-up; 10 `npm i -g vercel@latest`. Each step ends with `uv run factory doctor`.
- `CLAUDE.md` (≤ 60 lines): what the factory is; "start every session with `/factory`"; the rules (company boundary verbatim from spec section 4 first bullet; never spend from company accounts; no Dolead content in ideas; secrets never printed; costs always logged); the tool runner (`uv run factory <tool> --help`); the docs index with one line each: `docs/factory-design.md`, `docs/ledger.md`, `docs/tools.md`, `docs/secrets.md`, `docs/neuralbox.md`, `docs/doctor.md`, `docs/triage.md`, `docs/setup.md`, `docs/skills.md`, `docs/learnings.md`, `docs/superpowers/plans/`; the plan sequence (plans 2 and 3 pending).
- `docs/calibration.csv` header: `date,slug,experiment,recipe,channel,buyer_type,geo,variant,pred_cpc,act_cpc,pred_ctr,act_ctr,pred_cvr,act_cvr,pred_cost_per_primary,act_cost_per_primary,status,verdict`.
- `scripts/fixture.sh`: runs, against `_fixture` with `--dry-run`, `board --all`, `plan next`, `keyword_volume`, `serp_ads`, `ad_library`, `reddit_mentions`, `hn_mentions`, `pricing_scan`, `domain_check`, `nb ask`, `nb adsinsights`, then `doctor --offline`; exits non-zero on the first failure; cleans the research files it produced (`git checkout -- ideas/_fixture` and `git clean -fdq ideas/_fixture`).
- `tools/tests/test_docs.py`: every relative path written in backticks in `CLAUDE.md` exists; every `.claude/skills/*/SKILL.md` has `name:` and `description:` frontmatter and its `name` equals its folder; every `uv run factory <tool>` mentioned in a SKILL.md is a registered tool.

- [ ] **Step 1: Write `test_docs.py` and run it** — Expected: fails (no CLAUDE.md).
- [ ] **Step 2: Write the five skills, `CLAUDE.md`, the docs and `scripts/fixture.sh`.**
- [ ] **Step 3: Run `uv run pytest -q` and `make fixture`** — Expected: all pass; fixture script prints `FIXTURE OK`.
- [ ] **Step 4: Commit** — `git commit -m "feat: /factory, /idea-new, /idea-triage, /factory-doctor, /factory-setup skills; CLAUDE.md and docs"`

---

### Task 11: Migrate the v1 ideas and mark v1 superseded

**Files:**
- Create: `ideas/joomla-wp-migrations/{idea.yml,plan.md,intake.md,learnings.md,costs.jsonl,research/.gitkeep,v1/}`, same for `ideas/moneysaver-club/` and `ideas/post-purchase-affiliate-offers/`
- Modify (in `~/wrk/pers/personal_skills_and_tools`, committed there): `.claude/commands/idea-validate.md` (a first paragraph: superseded by `~/wrk/pers/astrafable` `/factory`, kept for history), `skills/generic/idea-validation/SKILL.md` (same note under the title), `CLAUDE.md` Business Ideas Convention (one line: new ideas go to astrafable `ideas/`)
- Test: `tools/tests/test_migrated_ideas.py`

- [ ] **Step 1: Write the failing test** — `ledger.list_ideas()` contains the three slugs with statuses `PARK`, `PARK`, `NEW` and each `intake.md` contains `## Pitch (verbatim)`.
- [ ] **Step 2: Copy each `business_ideas/<slug>/` folder verbatim into `ideas/<slug>/v1/`; write `idea.yml` with `status` mapped (joomla-wp-migrations: `PARK`, notes "v1 PIVOT at P3 on 2026-08-10, never relaunched; surviving framing in v1/README.md"; moneysaver-club: `PARK`, notes "v1 VALIDATING: MonMagot rig built and live, no traffic bought, stalled 2026-06-04"; post-purchase-affiliate-offers: `NEW`, notes "v1 EXPLORATION 2026-10-17, deep research in v1/angles, no decisions"), `v1_status` kept, `created` from the v1 session dates; `intake.md` with the verbatim `pitch-original.md` under `## Pitch (verbatim)` and the v1 README's status line under `## v1 state`; `plan.md` default with step 1 done; empty `costs.jsonl`; `learnings.md` with one line per idea on why it stalled (from the spec's "Why v2 exists").**
- [ ] **Step 3: Edit the three v1 files and commit in `personal_skills_and_tools`** with message `docs: idea-validate superseded by astrafable /factory`.
- [ ] **Step 4: Run tests and `uv run factory board`** — Expected: four rows (three migrated plus any created since).
- [ ] **Step 5: Commit** — `git commit -m "chore: migrate v1 business ideas into the ledger"`

---

### Task 12: First idea end to end: intake and triage of the ad-account watchdog

**Files:**
- Create: `ideas/ad-account-watchdog/` (via `/idea-new` and `/idea-triage`), `ideas/ad-account-watchdog/research/buckets.json`
- Modify: `docs/learnings.md`

- [ ] **Step 1: Intake.** Follow `/idea-new` exactly with the verbatim pitch from spec section 18. Provisional answers (all flagged `provisional: true`, listed under `## To confirm` for the challenge session): slug `ad-account-watchdog`, title `AI watchdog for ad accounts`; geo `US, FR`; language `en` (FR checked as a secondary market); buyer `performance marketer or agency owner administering several Meta and Google ad accounts`; signer `agency owner or head of paid`; value per customer `313 EUR` (29 EUR/month × 12 × 0.9 margin); cap `300`; rate `100`. Claim checked: "ad accounts get stolen through phished admins and the owner finds out late" via `reddit_mentions --terms "ad account hacked" --terms "business manager hacked" --since 2025-10-01`.
- [ ] **Step 2: Triage.** Follow `/idea-triage`: buckets (solution-aware: `ad account security monitoring`, `facebook ads monitoring tool`, `business manager security`, `ad account alerts`; problem-aware: `unauthorized ads on my account`, `someone is running ads on my facebook account`, `ad account spending without me`; trigger: `facebook ad account hacked`, `business manager hacked`, `meta ad account hacked what to do`, `google ads account hacked`, `facebook ads account compromised`; adjacent budget: `facebook ads management tool`, `ad account audit`, `meta ads automation rules`, `revealbot`, `madgicx`); the AdsInsights call only if `LookupAdsInsights` finds a category close to "marketing software" or "cybersecurity"; write `brief.md`; status `TRIAGED`.
- [ ] **Step 3: Verify** — `uv run factory board` shows `ad-account-watchdog | TRIAGED | 3. challenge`; `uv run factory costs total --idea ad-account-watchdog` ≤ 3 EUR; `brief.md` has all ten sections; no Dolead mention anywhere under `ideas/ad-account-watchdog/` (`grep -ri dolead ideas/ad-account-watchdog` returns nothing).
- [ ] **Step 4: Learnings** — append what the tools lacked, what took longest and the real cost to `ideas/ad-account-watchdog/learnings.md` and the durable ones to `docs/learnings.md`.
- [ ] **Step 5: Commit** — `git commit -m "feat(ideas): ad-account-watchdog intake and triage brief"`

---

## Self-review notes

- **Spec coverage:** section 6 → Tasks 3, 4; section 10 (demand, voice of customer, landscape, `nb`, board) → Tasks 5–8, 4; section 10 launch/ads/outreach/measure groups → plans 2 and 3; section 11 → Task 2; section 13 doctor and fixture → Tasks 9, 10; retro → plan 3; section 14 `/factory`, `/idea-new`, `/idea-triage`, `/factory-doctor`, `/factory-setup` → Task 10; `/idea-challenge`, `/idea-launch` → plan 2; `/idea-status`, `/idea-verdict`, `/factory-retro` → plan 3; v1 migration (section 10 last paragraph) → Task 11; section 18 → Task 12. Workstream insertion into `plan.md` (section 5) is parsed in Task 3 but only written by plan 2's `/factory` rework path.
- **Type consistency:** `Client`, `ProviderError`, `costs.append/total/check_cap`, `ledger.load_idea/next_step/mark_step`, `toolbase.run` are used with the same names in every task.
- **Review Focus:** each of the five lines names its tests above.
