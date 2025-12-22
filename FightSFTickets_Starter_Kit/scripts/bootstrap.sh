#!/usr/bin/env bash
set -euo pipefail

# Creates .env from example if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Bootstrap complete."
