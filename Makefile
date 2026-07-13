.PHONY: install test lint demo api mcp clean

install:
	python -m pip install -e ".[all]"

test:
	pytest

lint:
	ruff check raven_biocomputer tests

demo:
	python app.py

api:
	raven-biocomputer serve --host 0.0.0.0 --port 8042

mcp:
	raven-biocomputer-mcp

clean:
	rm -rf .pytest_cache .ruff_cache runs build dist *.egg-info
