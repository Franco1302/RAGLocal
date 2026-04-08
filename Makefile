.PHONY: setup lint test ingest query ui run-help

setup:
	python -m pip install --upgrade pip
	python -m pip install -e .[dev]

lint:
	ruff check src tests
	mypy src

test:
	pytest

ingest:
	rag ingest --source-dir data/raw

query:
	rag query --question "Explica la arquitectura del sistema"

ui:
	python -m streamlit run src/rag_local/ui/app.py

run-help:
	rag --help
