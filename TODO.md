# TODO v0.1.0

Noted by Theo - 2026-06-09

## 2026-06-09 Task: Shot 1 Foundry

- [x] Tighten schemas and registry contract.
- [x] Build `bin/dispatch`, `bin/receipt`, and `bin/validate`.
- [x] Build read-only Graphify adapter.
- [x] Add examples, run layout, and graph hook.
- [x] Verify positive and negative paths.
- [x] Commit and push.

## 2026-06-09 Task: Fable Shot 1 Review Patches

- [x] Fix worker-specific `$VAR` env indirection for `claude-glm`.
- [x] Block missing env-profile variables before adapter launch.
- [x] Strip stray caller `ANTHROPIC_*` from child env by default.
- [x] Document canonical dispatch exit codes.
- [x] Add labeled Graphify stub mode.
- [x] Remove duplicate schema aliases and example directory.
- [x] Verify and push.

## 2026-06-10 Task: Shot 1.x Duplicate Guard

- [x] Reject duplicate `job_id` before run creation.
- [x] Suppress `bin/receipt` BrokenPipe noise when piped.
- [x] Verify and push.

## 2026-06-10 Task: Shot 2 Glass

- [x] Build localhost-only `bin/glass` Mission Control viewer.
- [x] Add schema-valid `bin/seed-demo` fixtures.
- [x] Add credential-stripped `bin/operator-status`.
- [x] Add `security/checklist.json` manual attestation surface.
- [x] Verify UI, write lanes, bind refusal, and artifact blocking.
- [x] Commit and push.

## 2026-06-10 Task: Shot 3 Hands Preflight

- [x] Preserve Fable's Shot 3 forecast/advice in `docs/FABLE-SHOT3-PREFLIGHT.md`.
- [x] Preserve Fable's scoped Shot 3 RISK review in
  `docs/FABLE-SHOT3-RISK-REVIEW.md`.
- [x] Enforce adapter execution timeout from `budget.max_minutes`.
- [x] Add lane lockfile for write jobs with stale-lock detection.
- [x] Define `blocked.log` as `RUN_DIR/blocked.log` JSONL rows with
  `{ts, tool, path_or_cmd, rule}`.
- [x] Hard-block `.git*` writes inside worktrees after resolving real paths.
- [x] Prove hook/path denial with relative, absolute, and symlinked path forms.
- [x] Decide real-adapter `tests.passed` / `tests.failed` counting and preserve
  raw test output as an artifact.
- [x] Ensure receipt undo commands use the actual worktree path.
- [x] Keep Aider `adapter_pending` unless credentials are available through
  `$VAR` env indirection.
- [x] Verify env acceptance tests A/B/C before claiming Shot 3 complete.
- [x] Delta-QA Railway review mode after Glass v0.2.4 demo-only public guard.
- [x] Render first write-run diff artifact in Glass.

## 2026-06-10 Task: Shot 3 Hands Implementation

- [x] Build `adapters/_lib.sh` shared write-run guard/result library.
- [x] Add `adapters/claude.sh`, `adapters/codex.sh`, and `adapters/aider.sh`.
- [x] Keep real CLI execution opt-in with `THEO_ENABLE_REAL_*` environment
  switches while selftests prove the dispatch/adapter boundary without spend.
- [x] Run timeout, lane-lock, stale-lock, path-denial, env, receipt, and Glass
  write-run evidence checks.
- [x] Commit, push, deploy Glass if needed, and hand Fable a pinned commit plus
  a named selftest run directory.

## 2026-06-10 Task: Shot 3 Hands QA Closeout

- [x] Fix Fable's diff-capture RISK by including tracked, staged, and
  untracked/symlink changes in `diff.patch`.
- [x] Tag `shot3-hands-v0.3.1`.
- [x] Preserve Fable's final PASS artifact in
  `docs/FABLE-SHOT3-HANDS-QA-PASS.md`.
- [x] Add one explicit partial-status fixture.
- [x] Run first live `THEO_ENABLE_REAL_CLAUDE=1` session in a throwaway lane
  when token spend is approved. (2026-06-13: job
  `3e4436b4-5644-4206-a50b-dc0c00bea0b6`, status success, 0.173 min, wrote
  `LIVE-CLAUDE-PROOF.txt`, diff captured, no blocked actions.)

## 2026-06-10 Task: Shot 4 Mouth

- [x] Define the Shot 4 preflight and merge gates in
  `docs/SHOT4-MOUTH-PREFLIGHT.md`.
- [x] Add `schemas/command.schema.json` for structured phone/OpenClaw command
  intake.
- [x] Add `bin/mouth` to compile commands into canonical `job.json` envelopes.
- [x] Keep dispatch behind a second local `--dispatch` gate and block draft
  commands from execution.
- [x] Reuse `bin/receipt` for operator reply text.
- [x] Add Glass read-only Mouth queue/operator state.
- [x] Wire the external OpenClaw/Telegram wrapper to call `bin/mouth`.
- [x] Add schema-valid `jobs/outbox/<command_id>/reply.json` payloads for
  OpenClaw Telegram delivery.
- [x] Add guarded runtime sender payload emission plus post-send
  `jobs/outbox/<command_id>/sent.json` delivery markers.
- [x] Add Railway single-operator admin login mode, disabled by default behind
  explicit secrets.
- [x] Close Clawd Shot 4 hardening carry-overs: explicit test-channel trust
  fixture gate, admin login throttling, and sender-guard regression tests.
- [x] Preserve Fable's Shot 4.2/4.3 PASS + chat UI scout artifact in
  `docs/FABLE-SHOT4-QA-PASS-CHATUI.md`.
- [x] Design live-state sync/actions for the authenticated Railway admin door.
  (2026-06-13, Glass v0.5.0: visibility-aware, signature-gated polling that
  never clobbers an open detail; sync indicator + Refresh + Live/Pause;
  `tests/glass_live_sync_regression.py`; deeper dispatch-from-panel actions
  scoped in `docs/SHOT5-ADMIN-LIVE-SYNC.md` for a follow-up preflight.)
- [x] Ask Fable for a narrow Shot 4 QA pass after the wrapper exists.

## 2026-06-11 Task: Obsidian Chat Backup Import

- [x] Add a local-first Telegram/WhatsApp backup importer for the Obsidian
  vault lane.
- [x] Preserve directionality, source paths, message ids, timestamps, and
  attachment metadata in Markdown plus JSONL.
- [x] Add synthetic importer regression coverage.
- [x] Add Theo OS docs and an example job envelope for future imports.
- [x] Import Coach's uploaded Telegram/WhatsApp backup bundle after upload.
  (2026-06-13: 11 Telegram HTML pages -> 9,859 grouped messages in
  `60 Chat Imports/Telegram/Theokoles.md` plus staged index
  `98 Indexes/chat-import-staged.jsonl`.)
- [ ] Add direct OpenBrain `chat_exports` ingest lane after the generated vault
  output is reviewed.

## 2026-06-13 Task: Theo OS Mission Control UI

- [x] Pull Claude CLI second opinion framed as Jarvis / Agent OS and preserve
  the key safety boundary: Glass observes/routes; it does not execute commands.
- [x] Build the first three-pane Mission Control cockpit in `bin/glass`.
- [x] Render the left workspace/channel/agent rail, center live mission
  timeline, right Mission Details rail, and read-only composer stub from
  existing `/api/state` data.
- [x] Keep Spartacus as the VPS proof target and limit action controls to
  refresh/deep-link routes.
- [x] Add regression markers for the new cockpit shell.
- [x] Add the first cockpit-native Spartacus refresh action with a read-only
  receipt rendered in the timeline and Mission Details rail.
- [x] Deploy to Railway and verify live admin gates; authenticated refresh action
  verified locally with regression and Playwright smoke because the admin
  plaintext password is intentionally not stored in the workspace.

## 2026-06-14 Task: Live Telegram To Mouth Bridge

- [x] Add a guarded Glass `/api/mouth/ingest` endpoint for OpenClaw runtime
  Telegram events.
- [x] Keep ingress draft-only by routing through `bin/mouth-openclaw` without
  `--dispatch`.
- [x] Require bearer auth through `THEO_GLASS_MOUTH_INGEST_SECRET` for
  non-browser runtime posts.
- [x] Preserve local allowlist trust semantics with
  `THEO_TRUSTED_TELEGRAM_IDS` / `THEO_GLASS_MOUTH_TRUSTED_TELEGRAM_IDS`.
- [x] Add regression coverage proving unauthorized ingest fails and trusted
  ingest appears in `/api/state` without dispatching.
- [x] Deploy to Railway, set the new secret/allowlist env, ingest the current
  Telegram turn, and verify it appears in live Glass.
- [x] Add Glass approve / hold / reject Mouth lifecycle gates with auditable
  receipts and no dispatch.
- [x] Deploy and live-verify the Mouth lifecycle gate. (2026-06-14:
  deployment `7701aede-4981-4425-9543-57441eb79d93` SUCCESS; live smoke draft
  `bccedabd-8005-4989-a634-fc328a985dc0` approved through
  `/api/mouth/verdict`; unauth `/api/state` and unauth verdict stayed 401.)
- [x] Add approved Mouth reply drafts that write schema-valid outbox payloads
  without sending Telegram messages.
- [x] Deploy and live-verify the approved reply-draft path. (2026-06-14:
  deployment `f664c722-f970-4c7c-8f93-bc5cb1adda68` SUCCESS; live smoke draft
  `3baa9262-c5d5-4260-ab2f-6117df72ebe9` was ingested, approved, and given a
  pending `jobs/outbox/.../reply.json`; unauth reply draft stayed 401.)
- [x] Add guarded runtime send handoff endpoints for reply payload emission and
  post-delivery `sent.json` markers.
- [ ] Deploy and live-verify the runtime send handoff with one harmless
  Telegram message.
