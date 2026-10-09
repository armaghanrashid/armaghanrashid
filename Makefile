PY := .venv/bin/python

.PHONY: all generate test lint preview clean-venv

all: generate

generate:
	$(PY) -m profile_gen

test: lint
	$(PY) -m pytest -q

lint:
	.venv/bin/ruff check .

preview: generate
	$(PY) -m profile_gen.preview
