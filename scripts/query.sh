#!/usr/bin/env bash
set -euo pipefail

QUESTION="${1:-Describe la documentacion principal del sistema.}"

rag query --question "$QUESTION"
