#!/usr/bin/env bash
# Theo Agent OS Mouth reply bridge runner v0.1.0 - Noted by Theo - 2026-06-14.
#
# Resolve the Glass runtime secret from env or Railway variables, then send only
# explicitly queued Glass Mouth replies through OpenClaw.

set -euo pipefail

REPO_DIR="${THEO_AGENT_OS_REPO:-/home/coachap/.openclaw/workspace/projects/theo-agent-os}"
export PATH="/home/coachap/.npm-global/bin:/home/coachap/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

cd "$REPO_DIR"

secret="${THEO_GLASS_MOUTH_INGEST_SECRET:-}"
if [[ -z "$secret" ]] && command -v railway >/dev/null 2>&1; then
  secret="$(railway variable --kv 2>/dev/null | awk -F= '$1 == "THEO_GLASS_MOUTH_INGEST_SECRET" {print substr($0, index($0, "=") + 1); exit}')"
fi

if [[ -z "$secret" ]]; then
  printf '{"ok":false,"error":"THEO_GLASS_MOUTH_INGEST_SECRET missing and Railway variable lookup failed"}\n' >&2
  exit 2
fi

export THEO_GLASS_MOUTH_INGEST_SECRET="$secret"
exec "$REPO_DIR/bin/mouth-reply-bridge" "$@"
