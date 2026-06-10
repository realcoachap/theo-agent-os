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

## Phase 2 - Graphify Wrapper

- Build `run-graphify-query.sh`.
- Require graph freshness against `HEAD`.
- Emit result envelope.

## Phase 3 - Unified Runner

- Build `run-agent-job.sh`.
- Dispatch only installed/proven workers.
- Write `runs/<date>/<job_id>/result.json`.

## Phase 4 - Claude/Codex/Aider/Grok

- Claude lane uses Claude Agent SDK hooks if practical.
- Codex lane handles implementation/tests.
- Aider handles narrow patches.
- Grok handles alternate/research lanes.

## Phase 5 - Mission Control Viewer

- Render run results.
- Render artifacts.
- Show memory proposals.
- Show worker manifests.
- Show security warnings.

## Phase 6 - Sandboxed Experiments

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- LiteLLM
- Odysseus UI ideas

