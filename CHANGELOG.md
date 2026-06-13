# Changelog v0.1.0

Noted by Theo - 2026-06-09

## Unreleased

### Added

- Glass v0.5.6 Theo OS Mission Control cockpit: left workspace/channel/agent
  rail, center live mission timeline, right Mission Details rail, and an inert
  command composer stub. The new shell renders from existing `/api/state` data,
  keeps Spartacus as the VPS proof target, and limits actions to safe refresh
  or deep-link routes until confirm + receipt gates exist.
- Glass v0.5.1 admin-gated `/control/` proxy for the Spartacus OpenClaw
  gateway Control UI, including HTTP asset forwarding, WebSocket upgrade
  tunneling, stripped admin cookies, and `tests/glass_control_proxy_regression.py`.
- Glass v0.5.0 admin-door **live-state sync**: visibility-aware, signature-gated
  polling that re-renders only on real change and never clobbers an open run
  detail, artifact preview, or action feedback. Adds a sync indicator, manual
  Refresh, and a Live/Pause toggle, plus `tests/glass_live_sync_regression.py`
  and the `docs/SHOT5-ADMIN-LIVE-SYNC.md` design (deeper dispatch-from-panel
  actions scoped for a follow-up preflight).
- Explicit `partial`-status demo fixture in `bin/seed-demo` so Glass and
  operator-status exercise the partial badge/branch (diff applied, tests red,
  held in review), not just success/failed/blocked.
- OpenBrain `chat_exports` ingest lane (`~/.opensuites/openbrain/openbrain.py`
  v0.2.0): indexes the importer's vault JSONL into batched, directional,
  searchable chunks. First run: Coach's Telegram backup -> 9,859 messages ->
  5,044 chunks, idempotent re-ingest verified.
- Obsidian chat backup import foundation:
  `scripts/import-chat-backups-to-obsidian.py`,
  `docs/OBSIDIAN-CHAT-BACKUP-IMPORT.md`,
  `docs/OBSIDIAN-CHAT-IMPORT-ARCHITECTURE.md`,
  `jobs/examples/import-chat-backups-to-vault.json`, and
  `tests/chat_backup_importer_regression.py` convert Telegram/OpenClaw JSON and
  WhatsApp text exports into the local Ascending Research Obsidian vault with
  OpenBrain-ready JSONL indexes.
- Shot 4 hardening regression script:
  `tests/shot4_hardening_regression.py` proves explicit test-channel trust,
  sender-guard forgery/untrusted blocking, and admin login throttling.
- Fable's Shot 4.2/4.3 QA PASS + Mission Control chat UI scout artifact,
  preserving the Mattermost primary / Zulip runner-up recommendation and the
  follow-up closure commit for non-blocking hardening items.
- Shot 4 Mouth intake: `schemas/command.schema.json`, `bin/mouth`, and
  `jobs/examples/mouth-shot4-selftest.json` compile trusted phone/OpenClaw
  commands into canonical `job.json` envelopes, optionally dispatch them
  through Foundry, and return existing receipt text without creating a raw
  chat-to-shell lane.
- `bin/mouth-openclaw` wraps Telegram/OpenClaw event JSON, recomputes trust
  from local allowlists, emits Mouth command envelopes, and calls `bin/mouth`.
- `schemas/reply.schema.json` and `jobs/outbox/<command_id>/reply.json` provide
  a durable outbound receipt payload for the OpenClaw runtime to send.
- `schemas/delivery.schema.json` and `bin/mouth-send-reply` validate outbound
  replies against their original trusted command before OpenClaw sends them,
  then record `jobs/outbox/<command_id>/sent.json` after delivery.
- Railway admin door: `bin/glass --remote-admin` adds a single-operator login
  with signed session cookie, while `scripts/start-glass-railway.sh` keeps
  public read-only review mode as the default unless
  `THEO_GLASS_REMOTE_ADMIN=1` is set.
- Glass now renders read-only Mouth queue/operator state from
  `jobs/inbox/*/mouth.json` plus outbound reply records from
  `jobs/outbox/*/reply.json` and delivery markers from
  `jobs/outbox/*/sent.json`.
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

- Glass admin login now preserves deep links such as `/control/#token=...` after
  successful authentication, instead of always redirecting to `/`.
- `bin/mouth-openclaw` no longer auto-trusts `channel=test` events; fixtures
  must opt in with `--allow-test-trust` or `THEO_ALLOW_TEST_TRUST=1`.
- `bin/glass --remote-admin` now throttles repeated bad login attempts per
  client and returns `429` with `Retry-After`.
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
