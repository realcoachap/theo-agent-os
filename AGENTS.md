# AGENTS.md - Theo Agent OS

Noted by Theo - 2026-06-09

## Mission

Build Coach's Agent OS as a trustworthy local routing system:

- one operator
- explicit job envelopes
- proven workers
- read-only memory proposals
- artifacts with receipts
- no silent writes
- no self-evolving agent on the main machine

## Local Rules

1. Read this file before editing.
2. Read `docs/FULL-BREAKDOWN.md` before changing architecture.
3. For write jobs, require:
   - repo graph path
   - spec path
   - AGENTS.md chain
   - blast-radius note
4. Write outputs under `runs/<date>/<job_id>/`.
5. Never auto-write memory. Emit `memory_proposals`.
6. Never render generated HTML unless `safe_to_render` is true.
7. Never install MCP servers, skills, Hermes, Goose, OpenHands, or other agents
   outside sandbox paths from this repo.

## Current Worker Policy

Proven first-class workers:

- Graphify: read-only repo map and blast radius.
- Claude: architecture, specs, review, deeper builds.
- Codex: implementation, tests, code review.
- Aider: surgical patch lane.
- Grok: alternate reasoning and research lane.

Sandbox/watch only:

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- Odysseus
- LiteLLM

## Approval State Machine

All jobs, ideas, and memory proposals use:

```text
proposed -> approved -> running -> review -> shipped | killed
```

Irreversible actions require approval before execution.

## Foundry Contract

- `schemas/job.schema.json` and `schemas/result.schema.json` are the active
  Shot 1 contracts.
- `registry/workers.json` is the only worker manifest.
- `runs/` is append-only generated history; never edit past result envelopes.
- Adapters stay thin. They may emit `memory_proposals`, but never write memory.
- Read-only adapters must not mutate target repos. Use run-local or temporary
  scratch space for generated analysis artifacts.
- Before commits that touch adapters, worker registry, env plumbing, or model
  configuration, run a key-string guard such as:
  `git grep -nE '(sk-|api[_-]?key\s*[:=]|Bearer )'`.
