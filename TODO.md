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
- [x] Deploy and live-verify the runtime send handoff with one harmless
  Telegram message.
  (2026-06-14: deployment `f5f2425e-e5d8-4e26-9bce-c810861b573a` SUCCESS;
  live command `cf2d772c-d5d7-4aac-a323-f87e491a020a` emitted a guarded
  payload, OpenClaw delivered Telegram message `10408`, and
  `/api/mouth/reply-sent` wrote a `sent.json` marker; unauth mark-sent stayed
  401.)
- [x] Add a local OpenClaw direct-session bridge that mirrors only new
  Telegram user turns into Glass Mouth, dedupes them, and avoids whole-history
  backfills on first run.
- [x] Live-verify and enable the local bridge timer. (2026-06-14: bridge smoke
  posted command `43780814-a4ac-4a71-b963-2823d45a47e7` to live Glass with
  36 older user turns bootstrapped as seen; immediate rerun and timer reruns
  posted zero duplicates; user timer `theo-mouth-session-bridge.timer` active
  every 30 seconds.)
- [x] Add a separate queued-send receipt plus a local reply sender bridge so
  approved reply drafts do not auto-send until Glass writes
  `send-approved.json`.
- [x] Deploy and live-verify the queued reply sender bridge. (2026-06-14:
  deployment `07de5fa8-22f1-4e81-bf07-8958233adf5f` SUCCESS; live
  `scripts/run-mouth-reply-bridge.sh --dry-run --json` returned
  `pending=0`, `sent=0`; `/login` returned 200 and logged-out `/api/state`
  stayed 401; user timer `theo-mouth-reply-bridge.timer` active every
  30 seconds and two journal ticks showed `pending=0`, `sent=0`, `marked=0`.)

## 2026-06-14 Task: Glass Team Room + Mouth UX Polish

- [x] Turn the left agent rail into deep links for the node/team surfaces.
- [x] Add Mission Control quick jumps into Agent Room and Mouth.
- [x] Add a compact Mouth receive -> gate -> draft -> queue -> sent pipeline
  summary.
- [x] Reframe reply actions around Queue Send and the local runtime bridge.
- [x] Run local Glass/control/hardening regressions.
- [x] Deploy and live-verify the polish slice. (2026-06-14: commit
  `1583957`, Railway deployment `3ee5b2b2-8411-4cb2-b725-fc27257d5c6e`
  SUCCESS; live `/login` returned 200, logged-out `/api/state` returned 401,
  unauth `/api/mouth/pending-replies` returned 401, Mattermost `/api/v4/system/ping`
  returned 200, local reply bridge dry-run stayed idle with `pending=0` /
  `sent=0`, both Mouth timers stayed active, and desktop/mobile Playwright
  screenshots showed the Agent Room / Team Room / Mouth jumps without overlap.)
- [x] Give Coach the full grounded roadmap after deployment verification.
  (2026-06-14: sent Telegram message `10444` with the shipped v0.6.6 checkpoint
  plus near/next/later roadmap for Glass / Theo OS, Mouth, Mattermost team
  room, Nango connectors, OpenBrain/Obsidian memory, and Ascending / Ask Theo.)

## 2026-06-14 Task: Outbound Mattermost Receipts

- [x] Add an append-only team-room receipt log surfaced through `/api/state`.
- [x] Add optional Mattermost webhook delivery with room-specific env support
  and secret-shaped field scrubbing.
- [x] Emit receipts for safe control refreshes and Mouth receive / gate /
  draft / queue / sent lifecycle events.
- [x] Add guarded deploy receipt intake at `/api/team-room/deploy-receipt` for
  deployment automation.
- [x] Extend the Glass live-sync regression with a fake Mattermost webhook,
  deploy receipt auth checks, and privacy proof that Telegram message text is
  not copied into team-room receipt posts.
- [x] Deploy and live-verify the Mattermost receipt slice. (2026-06-14: commit
  `f7cc8df`, Railway deployment `0139cc50-910a-4cc2-aa18-09a07a65c6e7`
  SUCCESS; live `/login` returned 200, logged-out `/api/state` returned 401,
  Mattermost `/api/v4/system/ping` returned 200, live
  `/api/team-room/deploy-receipt` wrote a `deploy_receipt` into the `deploys`
  room with Mattermost delivery `sent`, local reply bridge dry-run stayed idle
  with `pending=0` / `sent=0`, and both Mouth timers remained active.)

## 2026-06-14 Task: Nango Connector Map

- [x] Verify current Nango docs for auth/connections/Google/GitHub shape before
  turning the roadmap into a local connector plan.
- [x] Add `registry/connectors.json` with provider candidates, phases, risks,
  scope boundaries, receipt expectations, and blockers.
- [x] Keep the connector map policy-only: no OAuth install, no provider token
  storage, and no provider writes.
- [x] Surface the connector map through `/api/state` as `connectors` and add a
  read-only Glass Connectors tab.
- [x] Run local regressions, commit, deploy, and live-verify the connector map.
  (2026-06-14: commit `f7768dc`, Railway deployment
  `a4b198d5-9d78-464c-a6c1-561ecb2fd254` SUCCESS; local py_compile,
  Glass live-sync, Control proxy, Shot 4 hardening, Mouth reply/session bridge,
  diff check, and desktop/mobile Connectors visual smoke passed. Live checks
  passed: `/login` 200, logged-out `/api/state` 401, guarded deploy receipt
  Mattermost delivery `sent`, `connectors` exposed 6 candidates through the
  guarded state path, local reply bridge dry-run `pending=0` / `sent=0`, and
  both Mouth timers active.)

## 2026-06-14 Task: Mission Control Composer Envelopes

- [x] Add an inert composer-envelope write path at `/api/composer/envelope`.
- [x] Make the Mission Control Stage button write draft envelopes instead of
  staying as a pure stub.
- [x] Expose staged envelopes through `/api/state` as `composer_envelopes`.
- [x] Render composer envelopes in the Mission timeline and right rail.
- [x] Keep dispatch, connector calls, Telegram sends, and shell execution out
  of the composer path.
- [x] Run local regressions, commit, deploy, and live-verify the composer
  envelope slice. (2026-06-14: commit `f6d63eb`, Railway deployment
  `7126d440-ddc9-4924-ab41-53640243c18b` SUCCESS; local py_compile,
  Glass live-sync, Control proxy, Shot 4 hardening, Mouth reply/session bridge,
  diff check, and desktop/mobile composer staging smoke passed. Live checks
  passed: `/login` 200, logged-out `/api/state` 401, guarded deploy receipt
  Mattermost delivery `sent`, live guarded state exposed `composer_envelopes`,
  local reply bridge dry-run `pending=0` / `sent=0`, and both Mouth timers
  active. Live browser composer write was not run because the admin plaintext
  password is intentionally not stored.)
