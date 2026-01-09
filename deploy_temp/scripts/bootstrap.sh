#!/usr/bin/env bash
set -euo pipefail

# Creates .env from example if missing
if [ ! -f .env ]; then
  cp .env.template .env
  echo "Created .env from .env.template"
fi

echo "Bootstrap complete."
