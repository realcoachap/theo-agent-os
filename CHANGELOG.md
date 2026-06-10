# Changelog v0.1.0

Noted by Theo - 2026-06-09

## Unreleased

### Added

- Shot 2 Glass implementation: localhost-only `bin/glass` run/artifact/spec/
  worker/security viewer, `bin/seed-demo` schema-valid fixtures,
  `bin/operator-status`, `registry/pinned-version.txt`, and
  `security/checklist.json`.

### Fixed

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
