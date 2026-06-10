# Theo Agent OS Roadmap v0.1.0

Noted by Theo - 2026-06-09

## Phase 0 - Repo And Sandbox

- Create this repo.
- Install Hermes in `.sandbox/` only.
- Keep no secrets in repo.

## Phase 1 - Contracts

- Add DOX/AGENTS.md to `ascending-one`.
- Add first spec folder for Pass 2 product feel.
- Define decisions/tasks format.

## Phase 2 - Foundry

- Build dispatch, receipt, and validate scripts.
- Build `adapters/graphify.sh`.
- Require graph freshness against `HEAD`.
- Emit and validate result envelopes under `runs/`.

## Phase 3 - Glass

- Build localhost-only Mission Control viewer.
- Render runs, artifacts, specs, memory proposals, workers, and security.
- Keep it read-only except proposal queue and manual security checklist.

## Phase 4 - Hands

- Claude lane uses Claude Agent SDK hooks if practical.
- Codex lane handles implementation/tests.
- Aider handles narrow patches.
- Grok handles alternate/research lanes.
- Every write lane works in a git worktree.
- No merges, no pushes, no direct memory writes.

## Phase 5 - Mouth

- Add OpenClaw operator skill after hardening is green.
- Convert human intent into job envelopes.
- Require explicit confirmation for write/delete/spend/publish/push.
- Schedule read-only morning brief via OpenClaw native cron.

## Phase 6 - Sandboxed Experiments

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- LiteLLM
- Odysseus UI ideas
