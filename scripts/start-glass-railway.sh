#!/usr/bin/env bash
# Theo Agent OS Glass Railway start v0.4.4 - Noted by Theo - 2026-06-10.
# Runs the public review surface read-only by default; admin mode is env-gated.

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -s runs/index.jsonl ]]; then
  python3 bin/seed-demo
fi

python3 bin/operator-status || true
if [[ "${THEO_GLASS_REMOTE_ADMIN:-0}" == "1" ]]; then
  python3 bin/glass --host 0.0.0.0 --port "${PORT:-4040}" --remote-admin
else
  python3 bin/glass --host 0.0.0.0 --port "${PORT:-4040}" --remote-review
fi
