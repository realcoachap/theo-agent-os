# Changelog v0.1.0

Noted by Theo - 2026-06-09

## Unreleased

### Added

- Shot 4 Mouth intake: `schemas/command.schema.json`, `bin/mouth`, and
  `jobs/examples/mouth-shot4-selftest.json` compile trusted phone/OpenClaw
  commands into canonical `job.json` envelopes, optionally dispatch them
  through Foundry, and return existing receipt text without creating a raw
  chat-to-shell lane.
- `bin/mouth-openclaw` wraps Telegram/OpenClaw event JSON, recomputes trust
  from local allowlists, emits Mouth command envelopes, and calls `bin/mouth`.
- `schemas/reply.schema.json` and `jobs/outbox/<command_id>/reply.json` provide
  a durable outbound receipt payload for the OpenClaw runtime to send.
- Glass now renders read-only Mouth queue/operator state from
  `jobs/inbox/*/mouth.json` plus outbound reply records from
  `jobs/outbox/*/reply.json`.
- Shot 3 Hands dispatch rails: `budget.max_minutes` adapter timeout with
  SIGTERM/SIGKILL escalation, per-lane write lockfiles in `runs/locks/`, stale
  lock recovery, and `RUN_DIR/blocked.log` JSONL denied-action evidence.
- Shared write adapter library `adapters/_lib.sh` plus Claude/Codex/Aider
  adapter wrappers. Real CLI execution is explicit-env gated; selftest mode
  proves worktree writes, denied path logging, git-push blocking, diff
  artifacts, and raw test-output artifacts without model spend.
- Shot 2 Glass implementation: localhost-only `bin/glass` run/artifact/spec/
  worker/security viewer, `bin/seed-demo` schema-valid fixtures,
  `bin/operator-status`, `registry/pinned-version.txt`, and
  `security/checklist.json`.
- Fable's scoped Shot 3 RISK review, including the realpath/symlink trapdoor,
  `blocked.log` contract, lane-lock, timeout, and write-run QA gates.
- Fable's full Shot 3 Hands QA RISK artifact for commit `88503e6`, preserving
  the live-execution evidence and the diff-capture defect that `e2c28e8`
  superseded.
- Fable's final Shot 3 Hands QA PASS artifact for
  `shot3-hands-v0.3.1` / `e2c28e8`, confirming canonical evidence run
  `runs/2026-06-10/d43c7251-2b35-4bdb-8132-9a4f96a31bd7`.

### Fixed

- Refuse Railway remote-review mode when real non-demo run history is present
  unless the operator explicitly acknowledges public exposure.
- Include untracked files and symlinks in write-run `diff.patch` artifacts
  instead of relying on `git diff` alone.
- Render receipt undo commands with the actual dispatch-created worktree path
  instead of a placeholder.
- Let `bin/operator-status` write a degraded status snapshot when the
  OpenClaw CLI is absent instead of crashing before Glass can render.
- Refuse duplicate `job_id` values cleanly before run creation instead of
  leaking a raw `FileExistsError` traceback.
- Restore default SIGPIPE handling in `bin/receipt` so piping to tools such as
  `head` does not print BrokenPipe noise.
- Resolve worker `env_profile` through explicit `$VAR` caller references,
  fail loud on missing variables, and strip stray caller `ANTHROPIC_*` values
  from child environments unless a worker explicitly declares them.

### Changed

- Document Shot 1 dispatch exit codes as the canonical operator contract.
- Remove duplicate schema aliases and duplicate example-job directory.
- Add labeled `GRAPHIFY_STUB=1` mode for envelope demos on machines without
  Graphify.
