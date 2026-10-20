# Secrets

Every key the factory spends, researches or creates with lives in one encrypted file,
`secrets/config.yml.enc`, committed to git. `bin/secrets` (OpenSSL AES-256-CBC, PBKDF2 100k
iterations, YAML validated before every encryption) is the only way in or out. The key that opens
it, `secrets/master.key`, stays on this machine: gitignored, mode 600.

## Layout

| Path | In git | What |
|---|---|---|
| `bin/secrets` | yes | the scheme: `init`, `encrypt`, `decrypt`, `edit`, `cat`, `get`, `apply-diff`, `generate-key` (see "This copy of bin/secrets") |
| `secrets/config.yml.enc` | yes | the factory config, encrypted |
| `secrets/config.yml.example` | yes | its schema, every secret empty |
| `secrets/master.key` | no | the key; lose it and the `.enc` cannot be opened |
| `secrets/config.yml` | no | plaintext, only while you write a config by hand |
| `secrets/.gitignore` | yes | an allowlist: only itself, the example and the `.enc` can ever be committed |
| `.gitattributes` | yes | `diff=encrypted`: git diffs of the `.enc` show one hash per value (see Rules) |

## This copy of bin/secrets

It started as a copy of `~/wrk/pers/personal_skills_and_tools/bin/secrets` and differs from it in
two points:

- openssl reads the key from the key file (`-pass file:secrets/master.key`), so the key never
  appears on a command line or in the process list; upstream passes `-pass pass:<key>`. Both read
  the same passphrase, so a file encrypted by either script opens with the other;
- `decrypt-for-textconv`, the git diff filter, prints hashes instead of the plaintext unless
  `SECRETS_TEXTCONV=full` is set (see Rules).

## Two layers (spec section 11)

- **Factory secrets**, this repo: `operator` (legal pages), `nb` (NeuralBox), `providers.*`
  (research), `accounts.*` (GitHub owner, Vercel scope, Meta, Google Ads, Stripe, Porkbun, Resend,
  sending domain, Turnstile) and `ideas.<slug>` (`master_key`, `stats_token`: the only way into
  that idea's secrets).
- **Idea secrets**, each idea repo's own `secrets/config.yml.enc`: only what that site needs to
  run, decrypted in memory by the site from its `MASTER_KEY` Vercel env var. No factory key is
  ever copied into an idea repo.

## Commands

| Command | Does |
|---|---|
| `make secrets-init` | creates `secrets/master.key` once and configures the git textconv |
| `make secrets-edit` | decrypt, open `$EDITOR`, validate, re-encrypt: how a key is added, changed or rotated |
| `make secrets-get K=a.b.c` | prints one value: for non-secret values only (`providers.seranking.source`) |
| `make secrets-cat` | prints the whole decrypted config: never in a shared terminal or an agent session |
| `make secrets-apply-diff` | applies a unified diff from stdin, then re-encrypts |

First setup: `make secrets-init`, `cp secrets/config.yml.example secrets/config.yml`, fill it in,
`bin/secrets encrypt`, `rm secrets/config.yml`. On another machine, copy `secrets/master.key` over
from this one: `make secrets-init` would create a different key that cannot open the committed file.

## In code

```python
from factory import secrets

key = secrets.get("providers.searchapi.api_key")      # SecretMissing if absent or empty
url = secrets.get("nb.url", "http://127.0.0.1:3076")  # a default instead of raising
safe = secrets.redact(text)                           # every config string of 8+ chars becomes ***
```

`secrets.load()` decrypts once per process and factory root (`refresh=True` reads the file again).
Without a key or a `.enc` it raises `SecretsUnavailable` with one line naming `make secrets-init`
or `bin/secrets encrypt`, before running anything; a tool prints that line and exits 1, never a
traceback. `secrets.save(config)` re-encrypts a whole config: its plaintext exists only in a
private temp file (mode 600, outside the repo) while `bin/secrets` runs, and the new `.enc` is
written next to the old one and renamed over it once encryption succeeded, so a failure or Ctrl-C
leaves the old file intact.

## NeuralBox keys

`uv run factory secrets-import-nb [--nb-root ~/wrk/dolead/neural_box] [--dry-run]` copies the
provider keys NeuralBox already holds:

| NeuralBox | Factory |
|---|---|
| `tools.SearchAPI.api_key` | `providers.searchapi.api_key` |
| `tools.SEranking.api_token` | `providers.seranking.api_token` |
| `tools.Apify.api_key` | `providers.apify.api_key` |
| `tools.Firecrawl.api_key` | `providers.firecrawl.api_key` |
| `tools.Tavily.api_key` | `providers.tavily.api_key` |
| `tools.ScreenshotAPI.token` | `providers.screenshotapi.token` |
| `tools.OpenAI.api_key` | `providers.openai.api_key` |
| `tools.Legnext.api_key` | `providers.legnext.api_key` |
| `tools.FalAI.api_key` | `providers.fal.api_key` |
| `tools.ElevenLabs.api_key` | `providers.elevenlabs.api_key` |
| `tools.Submagic.api_key` | `providers.submagic.api_key` |
| `tools.Gemini.vertex_ai` (the whole mapping) | `providers.gemini.vertex_ai` |
| `NB_API_KEY` in `.env` | `nb.api_key` |

It runs `make -C <nb-root> secrets-cat` and parses the output in memory, reads `<nb-root>/.env`,
and writes nothing inside NeuralBox. Each value lands next to `source: neural_box` and
`imported_at: <date>`; the factory config is re-encrypted and only the dotpaths written are
printed. A value NeuralBox lacks is skipped and named on stderr. `--dry-run` reads both sides and
prints the dotpaths it would write, changing nothing. `make` runs without `NEURAL_BOX_ENV` and
`ENV`, so NeuralBox's Makefile reads its local config, and a `--nb-root` without a `Makefile` is
refused before anything runs.

Run it again to pick up a key NeuralBox rotated: entries marked `source: neural_box` are
refreshed. An entry whose value is set and whose `source` is anything else, or absent, is an own
key: the import keeps it and names its dotpath on stderr (in `--dry-run` too). To move a provider
to an own key: `make secrets-edit`, replace the value, and delete its `source` and `imported_at`
(or set `source` to where the key comes from).

The import rewrites the YAML from data, so comments in the decrypted config are not kept (the
example keeps them).

## Rules

- A secret value never appears in stdout, logs, exceptions, research files, commits or chat.
  Check presence, not values: `secrets.get(path, None) is not None`, or a walk that prints key
  paths only.
- Once `make secrets-init` has run, `git diff`, `git show` and `git log -p` render
  `secrets/config.yml.enc` through `bin/secrets decrypt-for-textconv`: one line per value, sorted
  by dotpath, `dotpath: <first 8 hex digits of the value's sha256>` or `dotpath: (empty)`. A diff
  shows which keys changed, never a value.
- `SECRETS_TEXTCONV=full git diff …` (or `git show`, `git log -p`) renders the plaintext instead:
  for your own screen only, never in a shared terminal, an agent session or a review file. Without
  the key, or with `--no-textconv`, git shows the `.enc` as a binary file.
- Rotate a key: issue a new one at the provider, `make secrets-edit`, replace the value, commit the
  `.enc`. A key that leaked is rotated at the provider, not just removed from the file: the old
  value stays in git history.
- Rotate the master key: `bin/secrets decrypt secrets/config.yml.enc secrets/master.key
  secrets/config.yml`, `rm secrets/master.key`, `make secrets-init`, `bin/secrets encrypt`,
  `rm secrets/config.yml`, commit the `.enc`. Older commits open only with the old key.
