# Theo Agent OS

Noted by Theo - 2026-06-09

## What This Is

Theo Agent OS is Coach's local multi-agent operating pattern turned into a
repo: one operator, proven workers, explicit context, hard gates, durable run
artifacts, and a Mission Control viewer later.

This is not "another chatbot" and not a dashboard-first build.

The order is:

1. Contracts and specs.
2. Job/result envelope.
3. Graphify read-only map worker.
4. Unified runner for proven workers.
5. Artifact viewer / Mission Control.
6. Sandboxed experiments only after the core loop works.

## Current Verdict

- OpenClaw is the router/operator.
- Graphify is wrapper #1 because it is read-only and gives repo maps/blast
  radius before writes.
- Claude, Codex, Aider, and Grok are proven worker lanes.
- Hermes is sandbox-only until it proves value beyond OpenClaw + OpenBrain +
  Skills.
- Mission Control is a viewer/approval surface over `runs/*/result.json`, not
  the brain.

## Repo Layout

```text
AGENTS.md
docs/
  FABLE-ONESHOT-PACK-RECONCILIATION.md
  FULL-BREAKDOWN.md
  HERMES-SANDBOX.md
  ROADMAP.md
bin/
  dispatch
  receipt
  validate
adapters/
  graphify.sh
  _template.sh
hooks/
  post-commit
schemas/
  job.schema.json
  result.schema.json
registry/
  workers.json
jobs/
  examples/
runs/
  .gitkeep
scripts/
  install-hermes-sandbox.sh
```

## Hermes Sandbox

Hermes should not be installed beside real vaults, production repos, or
OpenBrain writes yet.

Use:

```bash
./scripts/install-hermes-sandbox.sh
```

The script creates:

- `.sandbox/hermes-venv`
- `.sandbox/hermes-home`

It does not write to `~/.hermes` and does not configure Telegram, Discord,
email, vault, social, or production tools.

## First Build Target

The first implementation target is now live: Shot 1 Foundry.

Use:

```bash
bin/dispatch jobs/examples/map-self.json
bin/receipt runs/<date>/<job_id>/result.json
```

`adapters/graphify.sh` builds a run-local Graphify graph from a temporary copy,
so target repos are not mutated by read-only map jobs.

## Shot 1 Canon

Status exit codes are part of the Foundry contract:

- `success` -> `0`
- validation or semantic rejection before a run exists -> `2`
- `blocked` -> `3`
- `failed` -> `4`
- `partial` -> `5`

`registry/workers.json` stores worker-specific environment indirection. Keys
are the adapter environment variable names; values are the caller environment
variable names. Example: `claude-glm` maps `ANTHROPIC_BASE_URL` from
`ANTHROPIC_BASE_URL_GLM` so multiple Anthropic-compatible lanes can coexist
without clobbering each other's credentials.

Graphify has a labeled demo mode for machines without the CLI:

```bash
GRAPHIFY_STUB=1 bin/dispatch jobs/examples/map-self.json
```

Stub results prove envelope plumbing only. Real map jobs must use the Graphify
CLI before any write worker consumes graph context.

## Fable Prompt Pack

Fable's one-shot pack is reconciled in:

```text
docs/FABLE-ONESHOT-PACK-RECONCILIATION.md
```

Important correction: Fable said `coach-agent-os`, but this repo is the
canonical target. Do not create a duplicate repo unless Coach explicitly asks.

Fable's delivered Shot 1 ZIP is reviewed in:

```text
docs/FABLE-SHOT1-ZIP-REVIEW.md
```

Verdict: useful reference, not a replacement for this repo's Shot 1.
