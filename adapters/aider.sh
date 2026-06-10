#!/usr/bin/env bash
# Theo Agent OS Aider adapter v0.3.0 - Noted by Theo - 2026-06-10
# Aider wrapper clone of the Shot 3 adapter shape. It stays adapter-pending
# unless credentials/runtime support are intentionally enabled by environment.
set -euo pipefail

source "$(dirname "$0")/_lib.sh"

worker_name="${WORKER_NAME:-aider}"

if [[ "${THEO_ADAPTER_SELFTEST:-0}" == "1" ]]; then
  theo_materialize_selftest "$worker_name"
  if theo_run_verify; then
    theo_finish_result "success" "Aider adapter selftest completed legitimate work while denied write, realpath, and git-push actions were recorded."
  else
    theo_finish_result "partial" "Aider adapter selftest completed, but verify.tests failed; raw output is attached."
  fi
  exit 0
fi

if [[ "${THEO_ENABLE_REAL_AIDER:-0}" != "1" ]]; then
  theo_blocked_log "$worker_name" "aider" "adapter_pending_requires_THEO_ENABLE_REAL_AIDER"
  theo_finish_result "blocked" "Aider adapter shape is present, but the worker remains adapter_pending until THEO_ENABLE_REAL_AIDER=1 and env-profile credentials are configured."
  exit 3
fi

if ! command -v aider >/dev/null 2>&1; then
  theo_blocked_log "$worker_name" "aider" "binary_missing"
  theo_finish_result "blocked" "Aider CLI is not on PATH for this adapter run."
  exit 3
fi

task="$(theo_job_field "task")"
set +e
(cd "$THEO_WRITE_ROOT" && aider --yes-always --message "$task") >"$RUN_DIR/transcript.md" 2>&1
adapter_rc=$?
set -e

verify_rc=0
theo_run_verify || verify_rc=$?

if [[ "$adapter_rc" -ne 0 ]]; then
  theo_finish_result "failed" "Aider CLI exited nonzero; see transcript and raw logs."
  exit 4
fi
if [[ "$verify_rc" -ne 0 ]]; then
  theo_finish_result "partial" "Aider CLI completed, but verify.tests failed; raw output is attached."
  exit 5
fi

theo_finish_result "success" "Aider CLI completed inside the dispatch-created worktree; review diff artifacts before merge."
