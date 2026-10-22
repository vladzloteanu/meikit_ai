.DEFAULT_GOAL := help
.PHONY: help sync test check board ideas fixture secrets-init secrets-edit secrets-cat secrets-get secrets-apply-diff

# `make` alone lists the targets: every target carries a `## one-line description` on its line.
help: ## list the targets (the default)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-18s %s\n", $$1, $$2}'

sync: ## install the Python dependencies (uv sync)
	uv sync

test: ## run the test suite
	uv run pytest -q

# The tests, then the doctor without the network (docs/doctor.md): it reads the secrets and
# exits 1 when a check fails.
check: test ## tests, then the offline doctor (fails when a check fails)
	uv run factory doctor --offline

fixture: ## capture the providers' dry-run fixtures with one real call each (real keys, real cost)
	uv run python scripts/capture-fixtures.py

# The board: one row per idea (slug, status, step, experiment, spend/cap, updated, next command).
board: ## list the ideas: status, next step, spend against cap
	@uv run factory board

ideas: board ## alias of board

# Secrets (docs/secrets.md): every target delegates to bin/secrets. secrets-cat prints every
# value; secrets-get K=a.b.c prints one, so use it for non-secret values only.
secrets-init: ## create secrets/master.key and an empty encrypted config
	bin/secrets init

secrets-edit: ## open the encrypted secrets in your editor
	bin/secrets edit

secrets-cat: ## print every secret value (never in a review or a shared terminal)
	@bin/secrets cat

secrets-get: ## print one value: make secrets-get K=a.b.c (non-secret values only)
	@bin/secrets get "$(K)"

secrets-apply-diff: ## apply a decrypted diff to the encrypted config
	bin/secrets apply-diff
