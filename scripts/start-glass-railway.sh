#!/usr/bin/env bash
# Theo Agent OS Glass Railway start v0.2.2 - Noted by Theo - 2026-06-10.
# Runs the public review surface read-only on Railway's assigned port.

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -s runs/index.jsonl ]]; then
  python3 bin/seed-demo
fi

python3 bin/operator-status || true
python3 bin/glass --host 0.0.0.0 --port "${PORT:-4040}" --remote-review
