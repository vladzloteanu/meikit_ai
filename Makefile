.PHONY: sync test check board ideas fixture secrets-init secrets-edit secrets-cat secrets-get secrets-apply-diff

sync:
	uv sync

test:
	uv run pytest -q

# The tests, then the doctor without the network (docs/doctor.md): it reads the secrets and
# exits 1 when a check fails.
check: test
	uv run factory doctor --offline

fixture:
	bash scripts/fixture.sh

# The board: one row per idea (slug, status, step, experiment, spend/cap, updated, next command).
board:
	@uv run factory board

ideas: board

# Secrets (docs/secrets.md): every target delegates to bin/secrets. secrets-cat prints every
# value; secrets-get K=a.b.c prints one, so use it for non-secret values only.
secrets-init:
	bin/secrets init

secrets-edit:
	bin/secrets edit

secrets-cat:
	@bin/secrets cat

secrets-get:
	@bin/secrets get "$(K)"

secrets-apply-diff:
	bin/secrets apply-diff
