# Fable Shot 2 Glass QA Pass v0.1.0 - Noted by Theo - 2026-06-10

## Source

Coach forwarded Fable's defensive local QA report for Shot 2 Glass v0.2.1 on
2026-06-10. This file preserves the actionable result without copying the full
external report.

## Verdict

Fable verdict: PASS.

Every documented Shot 2 contract item held under test:

- Glass opened locally and exposed the expected Runs, Artifacts, Repo Maps,
  Specs, Memory Proposals, Workers, and Security sections.
- Job history and artifacts remained view-only.
- Artifact preview paths stayed inside declared run folders; escaping and
  absolute paths were blocked.
- Unsafe HTML stayed blocked unless the result envelope declared
  `safe_to_render=true`.
- `bin/operator-status` degraded cleanly when OpenClaw was absent.
- Proposal approval appended a single `memory/queue.jsonl` entry and rejected
  undeclared proposals.
- README, AGENTS.md, and CHANGELOG matched the implementation.

Fable also confirmed the Shot 1.x fixes carried into this build:

- `$VAR` env indirection and default `ANTHROPIC_*` stripping.
- Duplicate `job_id` rejection before run creation.
- Quiet `bin/receipt` SIGPIPE handling.

## Polish Items

Fable raised two non-blocking notes:

- `bin/seed-demo` was additive rather than idempotent. This is intentional
  because run history is append-only, but the helper should say so.
- Security checklist attestation used `ts`; `checked_at` is clearer for the UI
  and docs. Glass should keep `ts` for backward compatibility.

Both notes were folded into the v0.2.3 polish patch.

## Recommendation

Shot 2 Glass is canonical and unblocked for Shot 3 "The Hands". Shot 3 should
carry forward Fable's v0.1.2 CANON exit codes, four-item write context, and env
acceptance tests A/B/C.
