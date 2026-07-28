#!/usr/bin/env bash
# Check provider-related env vars when feature flags are enabled.

set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"
ENV_FILE="${BACKEND_DIR}/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No backend/.env found. Run scripts/init-template.sh first."
  exit 1
fi

cd "$BACKEND_DIR"
uv run python -m app.tools.verify_providers
