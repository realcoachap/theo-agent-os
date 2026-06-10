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
