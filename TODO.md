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
- [ ] Enforce adapter execution timeout from `budget.max_minutes`.
- [ ] Add lane lockfile for write jobs with stale-lock detection.
- [ ] Define `blocked.log` as `RUN_DIR/blocked.log` JSONL rows with
  `{ts, tool, path_or_cmd, rule}`.
- [ ] Hard-block `.git*` writes inside worktrees after resolving real paths.
- [ ] Prove hook/path denial with relative, absolute, and symlinked path forms.
- [ ] Decide real-adapter `tests.passed` / `tests.failed` counting and preserve
  raw test output as an artifact.
- [ ] Ensure receipt undo commands use the actual worktree path.
- [ ] Keep Aider `adapter_pending` unless credentials are available through
  `$VAR` env indirection.
- [ ] Verify env acceptance tests A/B/C before claiming Shot 3 complete.
- [ ] Delta-QA Railway review mode after Glass v0.2.4 demo-only public guard.
- [ ] Render first write-run diff artifact in Glass.
