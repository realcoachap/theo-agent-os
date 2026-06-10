# Fable Shot 3 Risk Review v0.1.0 - Noted by Theo - 2026-06-10

## Source

Coach forwarded Fable's scoped review after the repo was made public and Fable
read only the requested software/QA files on `main`.

Verdict: `RISK`, proceed. The Shot 3 contract is implementable, but four
engineering gates must land before Shot 3 merges.

## Blockers Before Merge

1. `budget.max_minutes` is still unenforced in `bin/dispatch`.
   Adapter execution must time out, terminate cleanly, escalate if needed, and
   write a schema-valid failed envelope that cites the budget.
2. The write-lane lockfile is absent. Fable recommends
   `runs/locks/<lane-hash>.lock` with `{pid, job_id, ts}` and stale detection
   by dead PID or age.
3. `.git*` denial inside worktrees must resolve real paths before matching deny
   rules. A symlink inside the worktree pointing at shared `.git` state must not
   bypass the trapdoor.
4. `blocked.log` needs a defined contract before QA asserts against it.
   Recommended location is `RUN_DIR/blocked.log`, JSONL rows shaped as
   `{ts, tool, path_or_cmd, rule}`.

## Risks To Manage

- Agent SDK hook semantics are the likely fix-round, especially path shape:
  relative paths, absolute paths, and symlink-resolved paths all need tests.
- Aider may remain `adapter_pending` unless credentials are available through
  the existing `$VAR` env indirection.
- Railway review mode was added after Fable's v0.2.1 Glass QA. Keep it
  read-only and refuse accidental public exposure of real run history unless an
  explicit operator acknowledgement is present.
- Real adapters need a clear `tests.passed` / `tests.failed` counting rule.
  Best effort counts are acceptable, but raw test output should be preserved as
  an artifact and precision should not be faked.
- Receipt undo commands must reference the actual worktree path once worktrees
  are real.

## Mandatory Tests Before Merge

- Env acceptance A/B/C.
- Hook denial with relative, absolute, and symlinked paths.
- `.git*` write probe inside a worktree.
- Legitimate-work-continues test: honest work completes while denied actions
  are recorded in `blocked.log`.
- Timeout job: killed, failed envelope written, lock released.
- Concurrent dispatch on one lane: second run blocked; stale-lock recovery
  after `kill -9`.
- Adapter mid-run crash: failed envelope written, worktree preserved for
  forensics.
- Receipt undo commands executed verbatim remove the actual worktree and
  branch.
- Glass renders the first real write-run with its diff artifact.
- `partial` status path exercised at least once.

## Implementation Order

1. Harden dispatch first with timeout, lane lock, `blocked.log` contract, and
   `.git*` realpath denial using fake/sleeping adapters.
2. Build `adapters/_lib.sh` for context assembly, test/git reporting, and
   result envelope writing.
3. Implement `claude.sh` against the Agent SDK and foundry selftests.
4. Clone the proven shape into `aider.sh` and `codex.sh`, or keep them honestly
   `adapter_pending`.
5. Run Glass delta QA for remote-review write killswitch and first write-run
   rendering.
6. Tag and hand the ZIP to Fable for full QA.
