# Fable Shot 3 Preflight v0.1.1 - Noted by Theo - 2026-06-10

## Source

Coach forwarded Fable's early Shot 3 review/prediction after Shot 2 passed,
then a scoped RISK review after the repo went public. Treat these as advisory
QA pressure, not as self-executing instructions.

The detailed scoped review is preserved in
`docs/FABLE-SHOT3-RISK-REVIEW.md`.

## Forecast

Fable expects Shot 3 to be the first bumpy shot because it introduces external
write-capable runtimes, git worktrees, real spend-capable verification, and
hook semantics outside our direct bash/Python control.

The useful prediction is not "Shot 3 will fail"; it is where the first fix
rounds will probably live.

## Hard Gates To Bake In

- PreToolUse/path hooks must be tested with both relative and absolute path
  forms before they are trusted.
- Worktree confinement must hard-block `.git*` paths inside the worktree. A git
  worktree's `.git` file points back to shared repo state, so `.git` adjacent
  writes are not safe just because the job is in a worktree.
- Deny logic must resolve real paths before glob matching. A symlink inside a
  worktree that points at `.git` or other shared repo state must be blocked.
- Dispatch must enforce `budget.max_minutes` around adapter execution. Hung
  SDK/CLI sessions should be killed cleanly and written as failed envelopes
  that cite the budget timeout.
- "Never two writers on one repo" must become code, not prose. Add a lane
  lockfile taken at dispatch, released after result writing, with stale-lock
  detection by PID/age.
- `blocked.log` must have a contract before adapters write to it. Use
  `RUN_DIR/blocked.log` as JSONL with `{ts, tool, path_or_cmd, rule}` rows.
- Aider may stay `adapter_pending` if credentials are not available. If it runs,
  it must use the existing `$VAR` env indirection rather than assuming Claude
  subscription OAuth works for Aider.

## Expected Build Shape

- Prove `claude.sh` plus shared adapter library shape first.
- Clone the proven wrapper shape into Aider/Codex only after the Claude lane
  passes selftests.
- Landing as multiple commits is acceptable if the first commit proves the
  shared adapter/hook contract and the second adds sibling adapters.

## Fable QA Will Hammer

- Env acceptance tests A/B/C from Fable v0.1.2.
- `blocked.log` proving a job can complete legitimate work while stopping
  `.env`/push/denied actions.
- `.git*` trapdoor protection inside worktrees, including symlink variants.
- Budget-timeout behavior and failed envelope quality.
- Lane lock behavior for concurrent write jobs.
- Receipt undo commands that actually work.
- Receipt undo commands that name the actual worktree path once worktrees are
  real.
- Glass rendering the first write-run with a real diff artifact.
- Glass remote-review mode remaining read-only and demo-only unless an explicit
  operator acknowledgement allows public exposure of real runs.
- Real adapter `tests.passed` / `tests.failed` counts using best-effort truth
  with raw test output preserved as an artifact.

## Shot 3 Definition Of Done Addition

Shot 3 is not done merely when adapters run. It is done when a write-capable job
can be blocked, timed out, locked, and rendered in Glass with enough evidence
for review without merging, pushing, or writing memory.
