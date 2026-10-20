.PHONY: sync test check fixture

sync:
	uv sync

test:
	uv run pytest -q

# The doctor (uv run factory doctor --offline) joins check once it exists.
check: test

fixture:
	bash scripts/fixture.sh
