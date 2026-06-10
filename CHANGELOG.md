# Changelog v0.1.0

Noted by Theo - 2026-06-09

## Unreleased

### Fixed

- Resolve worker `env_profile` through explicit `$VAR` caller references,
  fail loud on missing variables, and strip stray caller `ANTHROPIC_*` values
  from child environments unless a worker explicitly declares them.

### Changed

- Document Shot 1 dispatch exit codes as the canonical operator contract.
- Remove duplicate schema aliases and duplicate example-job directory.
- Add labeled `GRAPHIFY_STUB=1` mode for envelope demos on machines without
  Graphify.

### Added

- Shot 1 Foundry implementation: dispatch, receipt, validate, read-only
  Graphify adapter, examples, graph hook, and append-only run history.
