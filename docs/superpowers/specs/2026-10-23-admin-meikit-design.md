# admin.meikit.ai — design

Status: draft of 2026-10-23, awaiting Vlad's approval. Brainstormed 2026-10-22/23; a fresh
reviewer (the builder check) read the first version and its findings are folded in: two questions
remain for Vlad (section 10). Plan: `docs/superpowers/plans/` (written after approval, with
superpowers:writing-plans).

## 1. Intent

A private web page where the two founders see the state of the ideas factory without a terminal
and without a git checkout: every idea, its status, the step it is at, what comes next and what it
has cost. Today that view exists only as `make board` in one laptop's shell. The cofounder joins
the repo but will not run the CLI daily; Vlad wants to glance at the factory from anywhere.

The page is read-only for now. It is built so that "act" (marking a step, setting a status,
answering a lead) can be added later without redoing it, and so that git stays the single source
of truth: the ledger `ideas/<slug>/` is what the page shows, and acting later means writing a
commit, never a second database of ideas.

## 2. What Vlad said

- "help me also build an admin.meikit.ai administrative interface"
- "- list of ideas, status of each idea / - later on: leads that we've captured, where we need to
  do stuff"
- "for now only look at - in the future, you can use its admin to act on"
- "ok" to: a Next.js app on Vercel at admin.meikit.ai, reading the ledger straight from the GitHub
  repo so git stays the single source of truth and a later "act" is a commit back.

The *why* above is my reading of those lines, not his words.

## 3. Goals, non-goals, anti-goals

Goals (v1):

- The board on the web: every idea with title, status, current step, next command, spend against
  the cap, current experiment, last change; sorted by last change.
- One page per idea: the plan's steps with their marks and dates, the costs by kind and by phase,
  the brief rendered, and links to the other files (`intake.md`, `learnings.md`, `research/`) on
  GitHub.
- Fresh at every push to `main` within a few minutes, with no one doing anything.
- Behind a login the two founders share; invisible to search engines; nothing from the ledger
  reachable without it.
- Zero running cost (Vercel Hobby, GitHub's free Actions minutes).

Non-goals (v1, kept for later phases, section 7):

- No writes of any kind: no buttons that change the ledger.
- No leads, no "where we need to do stuff" list: the stands that produce leads do not exist yet.
- No per-person accounts, no audit of who looked.
- No charts, no history views, no research files rendered (they are linked).
- No realtime: the page is as fresh as the last push, and an idea being worked on a laptop is not
  visible until pushed (which the repo's rules already require).
- No CI for the Python suite beyond what the deploy job needs (a pull-request CI is a separate,
  welcome, small change).
- The scout's candidate ideas (`scout/`): in v1 or as the first follow-up, Vlad's call (section
  10, question 2).

Anti-goals (what would make it a failure even if it worked):

- A second place where the state of an idea lives (a database the page writes, a cache that
  disagrees with git).
- A page that shows a private-context paragraph, a founder profile, a secret value, or anything
  from `founders/` or `secrets/`.
- A credential of the factory that can reach Dolead's Vercel team (the company boundary rule of
  `~/.claude/CLAUDE.md`); see section 4 and question 1.
- A deploy that breaks because one idea's files are malformed: the CLI board tolerates a broken
  idea and shows it as broken (`docs/ledger.md`); the page must do the same.
- Logic duplicated in TypeScript that already exists in Python (the board, the plan parser, the
  costs totals): the page renders what the factory computes.

## 4. Constraints and facts checked on 2026-10-23

- `meikit.ai` is registered at Porkbun (nameservers `*.ns.porkbun.com`); the root and
  `admin.meikit.ai` currently resolve to Porkbun's parking (`pixie.porkbun.com`). The factory
  design (D3) wants a wildcard pointed to Vercel one day; that is `/factory-setup`'s job, not this
  one's. This design needs one CNAME.
- **Vercel scope, unresolved since 2026-10-21** (`docs/doctor.md`, "The Vercel scope"): the login
  on this machine, `vladzloteanu-4035`, is a team-based account with no personal scope; its only
  team, and its default, is Dolead's. Design D9 ("Vlad's personal account, the login already on
  this machine, never a team scope") cannot be followed as written. The doctor's `vercel.scope`
  check fails on purpose until Vlad chooses a scope. This design needs that choice (question 1).
- A Vercel account token reaches every team the account belongs to; there is no project-scoped
  token. A token of the current login, stored in GitHub Actions, would therefore reach Dolead's
  Vercel team. That rules out "a new Hobby team under the current login" for anything that puts a
  token in CI.
- Vercel Hobby, private repo: a commit whose Git author is not a member of the Vercel team does
  not deploy through the Git integration ("Git author must have access to the project on Vercel to
  create deployments", Vercel KB), and a Hobby team has one member. The cofounder's merges would
  never deploy. Consequence: the deploy does not use the Git integration (section 5.5).
- Vercel Hobby: Vercel Authentication (Deployment Protection) leaves the production custom domain
  open; protecting it needs Pro. Consequence: the login is inside the app (section 5.4).
- The factory CLI already computes everything the board shows: `uv run factory board --all --json`
  prints rows `{slug, status, step, exp, spend_eur, cap_eur, updated, next}`; `factory.ledger`
  parses `idea.yml` and `plan.md` (marks `todo|doing|done|skipped|void`); `factory.costs` sums
  `costs.jsonl` by kind and phase. They work without the master key.
- Which ledger files are public-safe: `brief.md` is, by the triage skill's rule ("no private
  context, no company names from the pitch's origin story, no AdsInsights raw rows, no secret
  values"). `intake.md` is not: besides `## Private context`, the intake keeps the pitch verbatim
  and the firsthand answer, which may name an employer, a person or an incident ("keep
  identifying details local: they stay in this folder"). `learnings.md` has no such rule. The
  research files are raw provider data. `founders/` is git-ignored and never in a checkout the
  deploy sees.
- `scout/` (untracked today, being built by the idea-sourcing pilot): `ideas.yml`, the store of
  candidate ideas (42 entries from the round of 2026-10-23; statuses `proposed`, `kept`,
  `refused`, `parked`, `carded`, `in-factory`; the founders decide), `board.md` rebuilt from it,
  `prompts/`, `runs/<date>/`, `costs.jsonl`. Its README forbids private context in the store. Its
  format is a draft of this morning and nothing of it is committed yet.
- Tooling present: Node 25, npm 11, Vercel CLI 63, `gh` 2.86, `uv`. No pnpm.
- Repo: `https://github.com/vladzloteanu/meikit_ai.git`, branch `main`, private, two
  contributors.

## 5. The parts, as decided

### 5.1 What it shows

Two pages. Styling, typography and components are the builder's (section 8); the content is fixed
here.

The board, `/`:

```
meikit admin                                              generated 2026-10-23 14:02 from a1b2c3d

 idea                     status    step            next             spend / cap   exp   updated
 ─────────────────────────────────────────────────────────────────────────────────────────────────
 Ad Account Watchdog      TRIAGED   3. challenge    /idea-challenge   0.05 / 300    —     2026-10-22
 (ad-account-watchdog)

 [ ] show the fixture idea
```

- One row per idea folder, `_fixture` hidden behind the toggle (as `make board` hides it without
  `--all`). The title comes from `idea.yml`, the slug under it; the row links to the idea page.
- Status is a coloured chip; the eleven statuses are exactly those of `docs/ledger.md`. A broken
  idea (unreadable `idea.yml`, invalid `plan.md`, unreadable `costs.jsonl`) shows the board's own
  words (`invalid`, `?`) in the cell, never an empty row and never a failed build.
- Spend is cash against the cap, as the board prints it; `exp` is `current_experiment`.
- The header says when the snapshot was generated and from which commit (short SHA, linked to
  GitHub). This is how a founder knows whether what they see includes the push they just made.

The idea page, `/ideas/<slug>`:

```
← board                                  Ad Account Watchdog   TRIAGED   next: /idea-challenge

 Plan                                   Costs
  ✓ 1. intake      /idea-new   2026-10-22  cash 0.05 EUR of 300 (api 0.05)
  ✓ 2. triage      /idea-triage 2026-10-22  founder time 0.00 EUR
  · 3. challenge   /idea-challenge         by phase: triage 0.05
  · 4. launch      /idea-launch
  · 5. run         /idea-status
  · 6. conversations
  · 7. verdict     /idea-verdict

 Idea: buyer, signer, geo, language, value per customer and its basis, cap, rate, notes
 Brief ▸ (brief.md rendered; gate PASS)
 On GitHub: intake.md · learnings.md · idea.yml · plan.md · costs.jsonl · research/
```

- Steps show the five marks with their dates; the step the board calls next is highlighted.
- Costs: the totals by kind and by phase, and the lines of `costs.jsonl` in a collapsible table.
- The brief is rendered from Markdown with GitHub-flavoured tables (it is full of them). Relative
  links in it (`research/<file>`) point to the file on GitHub at the snapshot's commit. Before the
  triage, the brief's place says "not written yet".
- Only files whose producing skill guarantees them public-safe are rendered: today that is
  `brief.md` (section 4). `intake.md`, `learnings.md` and the research files are links to GitHub,
  where the cofounder's own login protects them. A skill that later wants another file on the
  admin says so in its SKILL.md, and the snapshot's allow-list grows by one line.
- Every page carries `X-Robots-Tag: noindex` and a `<meta name="robots" content="noindex">`.

### 5.2 Where the data comes from: a snapshot made by the factory CLI

A new factory tool, `uv run factory snapshot --out <dir> [--all]`, writes the ledger as the admin
needs it. It is the only bridge between the ledger and the page; the page never parses `idea.yml`,
`plan.md` or `costs.jsonl` itself.

```
<out>/
  meta.json                 {"generated_at": ISO-8601 UTC, "commit": "<sha or null>", "ideas": n}
  board.json                the rows of `board --json` (`--all` includes _fixture), each with
                            "title" (idea.yml) and "gate" (PASS|STOP|INCONCLUSIVE|null, read from
                            the `## Gate` section of brief.md when there is one)
  ideas/<slug>/idea.json    every field of idea.yml, including `totals`
  ideas/<slug>/plan.json    [{"n": 1, "name": "intake", "skill": "/idea-new", "budget": "15 min",
                            "status": "done", "date": "2026-10-22"}, ...] from factory.ledger's
                            plan parser, never a second one
  ideas/<slug>/costs.json   {"totals": <costs total --json>, "by_phase": {...}, "lines": [...]}
  ideas/<slug>/brief.md     verbatim, when it exists
```

Rules of the tool:

- It reads `ideas/` only. It never opens `founders/`, `secrets/`, a research file, `intake.md` or
  `learnings.md`: the files it copies are an allow-list (`brief.md` today), not a deny-list. There
  is no "strip the private section" logic: a file that needs stripping is a file that is not
  copied.
- A broken idea does not stop it: its `board.json` row carries the board's `invalid`/`?` values,
  its `idea.json`/`plan.json`/`costs.json` carry `{"error": "<the board's reason>"}` in place of the
  part that failed, and the exit code is still 0. It exits non-zero only when `<out>` cannot be
  written.
- `commit` is `git rev-parse HEAD` of the repo root when available, else null.
- It needs no master key and makes no network call; it respects `FACTORY_ROOT` like every tool.
  It costs nothing and writes outside the ledger: nothing is appended to any `costs.jsonl`, and
  there is no `--dry-run`.
- Tests in `tools/tests/test_snapshot.py`: the layout above on a throwaway root with `_fixture`;
  the gate values (PASS, STOP, INCONCLUSIVE, no brief, a brief without a gate section); a broken
  idea alongside a good one; `--all` versus default; and the allow-list: an `intake.md`, a
  `learnings.md`, a research file and a planted `founders/` file in the throwaway root are not in
  the output.

### 5.3 The app

- A Next.js App Router app in `admin/` at the repo root (TypeScript, `npm`, the current stable
  Next.js at build time; a `.nvmrc` pins the Node major that Vercel builds with). It is part of
  this repo, not a second one: the cofounder clones once, and the deploy reads the ledger from the
  same checkout.
- The app reads `admin/data/` (the snapshot, git-ignored) at build time: `generateStaticParams`
  for the idea pages, static rendering for everything. No database, no runtime data access, no
  runtime secret but the login.
- `admin/lib/snapshot.ts` is the only module that touches `admin/data/`; the TypeScript types of
  the snapshot files in section 5.2 live there, and a snapshot that does not match them fails the
  build with the file name (a build that silently renders nothing is the failure to avoid).
- `make admin-dev` runs the snapshot with `--all` into `admin/data/` and then `next dev`;
  `make admin-build` runs the snapshot without `--all` and `next build` (what the deploy does).
- Tests: `admin/` has its own runner (builder's pick); at least a render test of the board from a
  committed fixture snapshot (`admin/test/fixtures/`, generated once from `ideas/_fixture`), a
  render test of an idea page with a missing brief, and a test of the login check (section 5.4).
  `make admin-check` runs typecheck, lint and these tests; `make check` runs `admin-check` too when
  `admin/node_modules` exists and says in one line that it skipped it otherwise.

### 5.4 Login

- HTTP Basic auth, implemented in the app's request proxy (`middleware.ts`/`proxy.ts` as the
  Next.js version names it), on every route except Next's static chunks and the favicon. The
  credentials come from the env vars `ADMIN_USER` and `ADMIN_PASSWORD`; comparison is
  constant-time; a miss answers 401 with `WWW-Authenticate: Basic realm="meikit admin"` and an
  empty body. When either env var is missing, every request answers 503 "admin login not
  configured" — never an open page.
- One pair shared by the two founders. Per-person login comes with "act" (section 7), when
  actions must be attributed.
- The source of truth of the pair is the factory's encrypted config, new section
  `admin: {user, password}` in `secrets/config.yml.example`; `make admin-env` pushes both to the
  Vercel project's production environment through `vercel env add` reading from `bin/secrets get`
  without printing them; `make admin-dev` exports them into the dev server's environment the same
  way.

### 5.5 Deploy

- The Vercel project `meikit-admin` lives in the factory's own Vercel team (question 1 decides
  which; `accounts.vercel.scope` names it), is created once with the CLI, and is **not connected
  to the Git repository** (section 4: Hobby ignores the cofounder's commits).
- Every Vercel command of this design, local or in CI, runs with `--scope <the factory team>` and
  with the factory's token (`--token`, read from the encrypted config, never shown), **never with
  the global CLI login of this machine**, which belongs to Dolead's team. The Makefile passes the
  token from a shell variable; the builder keeps it out of `ps` where the CLI allows.
- A GitHub Actions workflow `.github/workflows/admin-deploy.yml` deploys on every push to `main`
  that touches `ideas/**`, `admin/**`, `tools/**`, `pyproject.toml`, `uv.lock` or the workflow
  itself, and on manual dispatch. Jobs, in order: checkout; `astral-sh/setup-uv` and
  `uv sync`; `make test` (the Python suite, not `make check`: the offline doctor needs the master
  key, which CI never has); `uv run factory snapshot --out admin/data`; `npm ci` in `admin/`;
  `make admin-check`; then `vercel pull --yes --environment=production`, `vercel build --prod`
  and `vercel deploy --prebuilt --prod`, with `VERCEL_TOKEN`, `VERCEL_ORG_ID` and
  `VERCEL_PROJECT_ID` from the repository's Actions secrets.
- Those three values live in the encrypted config under `admin:` too (`vercel_token`,
  `vercel_org_id`, `vercel_project_id`); `make admin-gh-secrets` sets them with `gh secret set`
  from `bin/secrets get`, nothing printed. The token is an account token created once in the
  factory's Vercel account. Because a token reaches the whole team, that team must hold nothing
  but the factory's projects (question 1).
- Concurrency: one deploy at a time (`concurrency: admin-deploy`), the newest push wins. A failed
  `make test` or `make admin-check` stops the deploy and leaves the previous version up.
- Expected time from push to live: two to four minutes. Cost: GitHub's free minutes for private
  repos (2,000 a month) at roughly three minutes a run.

Alternatives considered and not taken: Vercel's Git integration (Hobby, see section 4); a
build-time read through the GitHub API with a token (needs a secret at build time and a second
reader of the ledger); committing a generated `board.json` (a generated file in git goes stale).

### 5.6 Domain

- `admin.meikit.ai` is a CNAME to `cname.vercel-dns.com` created by hand in Porkbun's DNS panel
  (one record; the Porkbun API keys of the config are for `/factory-setup`'s wildcard later), then
  attached with `vercel domains add admin.meikit.ai meikit-admin`. Until the record exists, the
  project's `*.vercel.app` URL serves the same page behind the same login.
- `uv run factory doctor` gains one online check, `admin.url`: `https://admin.meikit.ai/` answers
  401 (the login is up) — `warn` on anything else, `skip` offline. `docs/doctor.md` lists it.
- The doctor's `vercel.login` and `vercel.scope` checks are taught the outcome of question 1 (the
  factory's token and team instead of the machine's login) in this plan, since the admin is the
  first thing that deploys; `docs/doctor.md` and design D9 are amended in the same commit.

### 5.7 What else changes in the repo (the end-of-task sweep, named now)

- `Makefile`: `admin-dev`, `admin-build`, `admin-check`, `admin-env`, `admin-gh-secrets`, each
  with its `##` line; `check` extended as in 5.3.
- `README.md`: Node in the install list, the admin in "what is in the repo", the `make admin-*`
  commands, and a troubleshooting line for "the board is stale" (look at the Actions run).
- `CLAUDE.md`: a row in the table (admin: `admin/`, its design, the deploy workflow) and one line
  in "Start here" (the board is also at admin.meikit.ai).
- `docs/secrets.md`: the `admin` section of the config and what `make admin-env` /
  `make admin-gh-secrets` do.
- `docs/doctor.md`: the `admin.url` check and the amended Vercel checks. `docs/ledger.md`: the
  `snapshot` tool in the CLI table.
- `docs/factory-design.md`: an amendment line in section 13 pointing at this design (a
  factory-wide admin beside the per-idea `/admin` of section 9) and the amendment of D9.
- `.claude/skills/idea-triage/SKILL.md`: one line saying the brief is rendered on the admin, which
  is why it is public-safe.
- `secrets/config.yml.example`: the `admin` section. `.gitignore`: `admin/data/`, `admin/.vercel/`,
  `admin/node_modules/`, `admin/.next/`, `admin/.env*.local`.

## 6. What the founders do by hand, once

1. Vlad settles question 1 (the Vercel account or team), creates its account token and adds it,
   with the user/password pair, to the config with `make secrets-edit`; commits the `.enc`.
2. Vlad creates the project and attaches the domain (two CLI commands, written in the plan), adds
   the CNAME at Porkbun, runs `make admin-env` and `make admin-gh-secrets`.
3. Both founders keep the pair in their password manager. The cofounder needs nothing else.

## 7. Later phases, doors kept open

Not designed here; named so v1 does not close them.

- **The scout board** (if not in v1, question 2): a `/scout` page listing `scout/ideas.yml` with
  id, title, buyer, job, price, pattern, origin, round, first read (C/P/R/H/F), the challenge
  verdicts and the status with its decision; the snapshot gains `scout.json` when the file
  exists. The store's own rule (nothing from `founders/`) makes it public-safe.
- **Leads and the attention list** (Vlad: "leads that we've captured, where we need to do stuff").
  Each running idea's stand exposes `/api/stats` under its `stats_token` (design section 9; the
  factory holds `ideas.<slug>.stats_token`). The admin fetches it server-side at request time with
  a short revalidation, so these pages are dynamic while the ledger pages stay static. The
  attention list is derived: leads without a reply, intents without a call, a test past its
  window, an idea waiting on a decision at a gate. `admin/lib/snapshot.ts` stays the ledger
  reader; a sibling module reads the stands.
- **Act** (Vlad: "in the future, you can use its admin to act on"). Per-person login first (the
  two GitHub accounts, so an action has an author), then actions that are commits: `plan mark`,
  `idea set status=`, a note in learnings, a scout decision, written by the factory CLI in a
  workflow or through a GitHub App; the page shows "pending until the deploy lands". The ledger
  stays the truth.
- **Pull-request CI** running `make test` and `make admin-check` on every PR; the deploy workflow
  already contains the steps.

## 8. Left to the builder

- The look: typography, colours of the status chips, light and dark, layout at phone width (a
  founder will open it from a phone). The frontend-design skill applies; the brand is "a lab
  notebook", not a SaaS dashboard.
- The exact Next.js version and file names (`middleware.ts` or `proxy.ts`), the Markdown renderer
  (GitHub-flavoured tables are required), the test runner and the linter for `admin/`.
- How `make check` detects a usable `admin/node_modules`, and the `.nvmrc` value.
- The workflow's path filter details and whether `npm ci` is cached.
- The shape of the Python module for the snapshot (one file under `tools/factory/tools/`, reusing
  `factory.ledger`, `factory.costs` and `tools/factory/tools/board.py`'s `row_of`).
- How the Makefile hands the token to the Vercel CLI without printing it.

## 9. My calls, for Vlad to check while reading

- One shared login pair for v1; per-person accounts only when "act" arrives.
- The app lives in this repo (`admin/`), not in a repo of its own.
- The page is a static build from a snapshot made at every push, not a live reader of git: fresh
  within minutes, zero runtime cost, nothing to break at 3 a.m.
- The snapshot is a factory tool in Python so that the ledger parsing stays in one tested place.
- Only `brief.md` is rendered; `intake.md`, `learnings.md` and the research files are links to
  GitHub. The reviewer found that the intake keeps the pitch and the firsthand answer verbatim,
  which may name people or incidents; stripping one section would not be enough, and the brief is
  the document the cofounder needs. Say so if you want the intake on the page too.
- Deploy from GitHub Actions with a Vercel token instead of Vercel's Git integration, because a
  Hobby team would ignore the cofounder's commits.
- Every Vercel command uses the factory's token and team, never this machine's global login.
- `_fixture` is deployed only when `--all` is used, so production shows real ideas only; dev shows
  the fixture.
- A broken idea shows as broken and never fails a deploy.

## 10. Open questions for Vlad

1. **Which Vercel account hosts the factory?** The login on this machine has no personal scope and
   only Dolead's team (section 4), and any token of it would reach that team. My recommendation:
   a separate Vercel account for the factory, on a personal address, with its own free Hobby
   team; the factory uses it only through its token (`accounts.vercel.scope` names the team),
   this machine's `vercel` login stays Dolead's and is never used by the factory. This amends D9.
   The alternative, a new Hobby team under the current login, keeps one login but puts a token
   that can reach Dolead's Vercel into GitHub Actions; I advise against it.
2. **The scout board: in v1 or as the first follow-up?** `scout/ideas.yml` holds 42 candidates
   the two of you are meant to review, and it is where the cofounder's review work of the next
   weeks happens; the factory board has one real idea. My recommendation: in v1, as the last task
   of the plan, reading the store only once it is committed in the format of its README; if the
   store is not committed when the plan reaches that task, the task is skipped and becomes the
   first follow-up. The risk is the format moving under the page; the snapshot is its only
   reader, so a change costs one function and its test.
