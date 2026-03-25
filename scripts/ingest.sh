#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-data/raw}"

rag ingest --source-dir "$SOURCE_DIR"
