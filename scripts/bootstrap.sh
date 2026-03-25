#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -e .[dev]

cp -n .env.example .env || true

echo "Proyecto inicializado. Ajusta .env antes de ejecutar ingest o query."
