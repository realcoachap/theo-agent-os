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
schemas/
  job-envelope.schema.json
  result-envelope.schema.json
worker-registry/
  workers.json
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

The first real implementation target is the Graphify wrapper:

```text
scripts/agent-cli/run-graphify-query.sh
```

It should accept a job envelope, read a repo graph, emit a result envelope, and
refuse if the graph trails `HEAD`.

## Fable Prompt Pack

Fable's one-shot pack is reconciled in:

```text
docs/FABLE-ONESHOT-PACK-RECONCILIATION.md
```

Important correction: Fable said `coach-agent-os`, but this repo is the
canonical target. Do not create a duplicate repo unless Coach explicitly asks.
