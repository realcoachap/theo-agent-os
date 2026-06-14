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

## Phase 2 - Foundry - complete in Shot 1

- Build dispatch, receipt, and validate scripts.
- Build `adapters/graphify.sh`.
- Require graph freshness against `HEAD`.
- Emit and validate result envelopes under `runs/`.

## Phase 3 - Glass

- Build localhost-only Mission Control viewer.
- Render runs, artifacts, specs, memory proposals, workers, and security.
- Keep it read-only except proposal queue and manual security checklist.
- Current Railway admin mode includes the Spartacus VPS proof-of-concept: a
  strict allowlisted OpenClaw Control node registry where
  `/control/spartacus/` reaches Spartacus' Control UI, `/control/` remains the
  Spartacus compatibility alias, and Glass verifies both network reachability
  and app-layer gateway response from the web tier.
- Glass v0.5.6 adds the first Jarvis / Agent OS cockpit shell above that proof:
  left workspace/channel/agent rail, live mission timeline, right Mission
  Details rail, and an inert command composer stub. Mutating node actions still
  wait for confirm + receipt gates.
- Glass v0.5.7 adds the first safe node action inside that cockpit: Refresh
  Spartacus forces the existing proof probe, writes a local read-only receipt,
  and renders it in the timeline/details rail without mutating the remote node.
- Caesar and Theokoles are registry entries, but their routes stay disabled
  until Railway can reach their gateways through Tailscale or another guarded
  relay.

## Phase 4 - Hands

- Claude lane uses Claude Agent SDK hooks if practical.
- Codex lane handles implementation/tests.
- Aider handles narrow patches.
- Grok handles alternate/research lanes.
- Every write lane works in a git worktree.
- Dispatch enforces `budget.max_minutes` for adapter execution.
- Write lanes take a lane lockfile so two writers never touch one repo at once.
- Worktree hooks hard-block `.git*` paths, including the gitfile trapdoor.
- No merges, no pushes, no direct memory writes.

## Phase 5 - Mouth

- Add OpenClaw operator skill after hardening is green.
- Convert structured human intent into job envelopes.
- Require explicit confirmation for write/delete/spend/publish/push.
- Schedule read-only morning brief via OpenClaw native cron.

Shot 4 starts this phase with `schemas/command.schema.json` and `bin/mouth`:
phone/OpenClaw commands compile into `jobs/inbox/<command_id>/job.json`, then
optionally run through dispatch and return the existing receipt text.

Glass v0.6.0 adds the first live ingress bridge for this phase:
`POST /api/mouth/ingest` lets OpenClaw's Telegram runtime post a sanitized event
into Railway Glass with `THEO_GLASS_MOUTH_INGEST_SECRET`. The endpoint routes
through `bin/mouth-openclaw --direct-chat --json`, writes a draft-only Mouth
record, and never dispatches. The next slices are outbound reply receipts back
to Telegram, then Glass approve / hold / reject gates.

## Phase 6 - Sandboxed Experiments

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- LiteLLM
- Odysseus UI ideas
