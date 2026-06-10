#!/usr/bin/env bash
# Theo Agent OS Claude adapter v0.3.0 - Noted by Theo - 2026-06-10
# Write-capable Claude lane. Shot 3 proves the wrapper contract in selftest
# mode first; real CLI execution is opt-in until hook behavior is reviewed.
set -euo pipefail

source "$(dirname "$0")/_lib.sh"

worker_name="${WORKER_NAME:-claude}"

if [[ -n "${THEO_ADAPTER_SLEEP_SECONDS:-}" ]]; then
  sleep "$THEO_ADAPTER_SLEEP_SECONDS"
  theo_finish_result "success" "Claude adapter sleep probe completed without hitting the dispatch timeout."
  exit 0
fi

if [[ "${THEO_ADAPTER_CRASH:-0}" == "1" ]]; then
  echo "intentional adapter crash probe" >&2
  exit 42
fi

if [[ "${THEO_ASSERT_NO_ANTHROPIC:-0}" == "1" ]]; then
  if [[ -n "${ANTHROPIC_BASE_URL:-}" || -n "${ANTHROPIC_API_KEY:-}" ]]; then
    theo_blocked_log "$worker_name" "ANTHROPIC_*" "stray_anthropic_env_not_stripped"
    theo_finish_result "failed" "Plain Claude adapter received stray caller ANTHROPIC_* env; dispatch stripping failed."
    exit 4
  fi
fi

if [[ "${THEO_ASSERT_ANTHROPIC_PRESENT:-0}" == "1" ]]; then
  if [[ -z "${ANTHROPIC_BASE_URL:-}" || -z "${ANTHROPIC_API_KEY:-}" ]]; then
    theo_blocked_log "$worker_name" "ANTHROPIC_*" "mapped_anthropic_env_missing"
    theo_finish_result "failed" "Mapped Anthropic-compatible env was missing inside the adapter."
    exit 4
  fi
fi

if [[ "${THEO_ADAPTER_SELFTEST:-0}" == "1" ]]; then
  theo_materialize_selftest "$worker_name"
  if theo_run_verify; then
    theo_finish_result "success" "Claude adapter selftest completed legitimate work while denied write, realpath, and git-push actions were recorded."
  else
    theo_finish_result "partial" "Claude adapter selftest completed, but verify.tests failed; raw output is attached."
  fi
  exit 0
fi

if [[ "${THEO_ENABLE_REAL_CLAUDE:-0}" != "1" ]]; then
  theo_blocked_log "$worker_name" "claude" "real_cli_requires_THEO_ENABLE_REAL_CLAUDE"
  theo_finish_result "blocked" "Claude adapter is installed, but real CLI execution requires THEO_ENABLE_REAL_CLAUDE=1 after hook/path behavior review. Use THEO_ADAPTER_SELFTEST=1 for boundary proof."
  exit 3
fi

if ! command -v claude >/dev/null 2>&1; then
  theo_blocked_log "$worker_name" "claude" "binary_missing"
  theo_finish_result "blocked" "Claude CLI is not on PATH for this adapter run."
  exit 3
fi

task="$(theo_job_field "task")"
prompt_file="$RUN_DIR/adapter-prompt.md"
cat >"$prompt_file" <<EOF
You are running inside Theo Agent OS.

Task:
$task

Constraints:
- Work only in this dispatch-created worktree: $THEO_WRITE_ROOT
- Do not push git commits or branches.
- Do not write memory.
- Respect the job envelope write and deny lists.
- Leave changes for review; do not merge.
EOF

set +e
(cd "$THEO_WRITE_ROOT" && claude -p "$(cat "$prompt_file")") >"$RUN_DIR/transcript.md" 2>&1
adapter_rc=$?
set -e

verify_rc=0
theo_run_verify || verify_rc=$?

if [[ "$adapter_rc" -ne 0 ]]; then
  theo_finish_result "failed" "Claude CLI exited nonzero; see transcript and raw logs."
  exit 4
fi
if [[ "$verify_rc" -ne 0 ]]; then
  theo_finish_result "partial" "Claude CLI completed, but verify.tests failed; raw output is attached."
  exit 5
fi

theo_finish_result "success" "Claude CLI completed inside the dispatch-created worktree; review diff artifacts before merge."
