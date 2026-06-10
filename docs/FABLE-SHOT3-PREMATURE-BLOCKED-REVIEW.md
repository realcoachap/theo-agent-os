# Fable Shot 3 Premature Blocked Review v0.1.0 - Noted by Theo - 2026-06-10

## Source

Coach forwarded Fable's strict Shot 3 review after the prompt placeholder was
left unfilled. Fable pinned `HEAD` as `ddc0dc7c`, which was the pre-Shot-3
contract-hardening commit, and no selftest run directory was named.

## Verdict

Fable verdict: `BLOCKED`.

The finding was correct for the reviewed commit. Shot 3 "Hands" implementation
was not present yet; only the contract/TODO/preflight docs existed.

## Merge Blockers Fable Identified

1. `adapters/_lib.sh` was missing.
2. `adapters/claude.sh` was missing while the registry called Claude
   `installed`, creating an honesty defect.
3. `bin/dispatch` still lacked `budget.max_minutes` timeout enforcement, a
   write-lane lockfile, `.git*` realpath/symlink denial, and implemented
   `blocked.log` evidence.
4. No Shot 3 selftest run directory was named.
5. Env acceptance tests A/B/C could not be verified against a write adapter.

## Follow-up

Treat this as a premature-review checkpoint, not a broken implementation. The
next Fable handoff must name the actual Shot 3 commit and the specific
`runs/<date>/<job_id>` evidence directory for review.
