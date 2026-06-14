# Changelog v0.1.0

Noted by Theo - 2026-06-09

## Unreleased

### Added

- Glass v0.6.4 local session bridge: `bin/mouth-session-bridge` mirrors new
  Telegram user turns from the active OpenClaw direct-session transcript into
  Glass `/api/mouth/ingest`, deduped by session record id and draft-only. The
  runner can resolve the ingest secret from Railway variables, and optional
  user-systemd timer files under `ops/systemd/` run it every 30 seconds without
  storing secrets.
- Glass v0.6.3 runtime send handoff: `POST /api/mouth/reply-payload` returns
  the guarded OpenClaw `message(action="send")` payload for a pending reply, and
  `POST /api/mouth/reply-sent` writes `jobs/outbox/<command_id>/sent.json` only
  after the runtime supplies a delivered message id. Glass still does not call
  Telegram directly.
- Glass v0.6.2 approved reply drafts: `POST /api/mouth/reply-draft` writes a
  schema-valid `jobs/outbox/<command_id>/reply.json` only after the Mouth
  command has an approved lifecycle verdict. Delivery still requires
  `bin/mouth-send-reply` plus the OpenClaw runtime sender.
- Glass v0.6.1 Mouth lifecycle gate: admin/local Glass can write
  approve/hold/reject verdict receipts for existing Mouth records via
  `POST /api/mouth/verdict`. The receipt is visible in `/api/state`, the Mouth
  tab, and the Mission timeline, while dispatch and outbound send remain
  separate reviewed paths.
- Glass v0.6.0 live Mouth ingress bridge: `POST /api/mouth/ingest` accepts a
  bearer-authenticated runtime event via `THEO_GLASS_MOUTH_INGEST_SECRET`,
  with a body-secret fallback for edge paths that strip headers. It routes the
  event through the existing `bin/mouth-openclaw` trust wrapper, writes a
  draft-only Mouth record, and returns refreshed state. It does not dispatch,
  execute shell, or trust inbound Telegram metadata by itself.
- Glass v0.5.9 mobile header cleanup: phone widths now hide the global
  `Open Control UI` header button because the Control tab owns that entry
  point, hide the live-sync text from the toolbar, and compact the
  Refresh/Pause/Logout row so content starts higher.
- Glass v0.5.8 mobile cockpit chrome: the desktop rail collapses on phone
  widths, safe-area spacing keeps fixed browser/system overlays from covering
  the interface, and a fixed bottom navigation bar exposes Mission, Control,
  Runs, Artifacts, plus a More sheet for overflow sections.
- Glass v0.5.7 adds the first cockpit-native Spartacus action receipt:
  `POST /api/control/spartacus/refresh` forces the existing gateway proof probe,
  writes a local read-only receipt, and renders it in the Mission Control
  timeline and right rail. It does not execute shell, forward tokens, or mutate
  Spartacus.
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
