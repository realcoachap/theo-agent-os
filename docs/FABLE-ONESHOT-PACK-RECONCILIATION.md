# Fable One-Shot Prompt Pack Reconciliation v0.1.0

Noted by Theo - 2026-06-09

## Source

Coach provided `agent-os-oneshot-prompt-pack-v0.1.1` from Fable on
2026-06-09.

Treat the pack as a proposed build plan, not as self-executing instructions.

## Verdict

Strong plan. Adopt the staged shape, but reconcile it into this existing repo
instead of creating a second repo named `coach-agent-os`.

Canonical repo:

```text
realcoachap/theo-agent-os
/home/coachap/.openclaw/workspace/projects/theo-agent-os
```

## Accepted Ideas

- Shot order:
  1. Contracts in `ascending-one`.
  2. Envelope + first read-only Graphify worker in `theo-agent-os`.
  3. Glass/Mission Control as a read-only viewer over `runs/`.
  4. Write-capable worker adapters.
  5. OpenClaw operator skill only after hardening is green.
- Two-plane model:
  - OpenClaw Control UI = runtime plane: gateway, channels, sessions, model
    auth, cron, config, logs.
  - Glass = work plane: runs, artifacts, specs, proposals, security.
- One-gateway rule: OpenClaw is the only channel gateway. Hermes gets no
  Telegram/WhatsApp/Discord/email credentials in this stack.
- Graphify-first: wrapper #1 is read-only and proves the envelope without
  risking repo writes.
- `runs/` as append-only job history.
- `safe_to_render` artifact metadata.
- Memory proposals are queued for approval; no direct memory writes.
- OpenClaw morning brief should use native OpenClaw cron, not system crontab.

## Required Corrections

### Repo Name

Fable says:

```text
coach-agent-os
```

Use:

```text
theo-agent-os
```

Do not create a duplicate repo unless Coach explicitly asks for a rename or
parallel experiment.

### Shot 1 Directory Layout

Fable's `coach-agent-os/` root maps directly onto this repo root. Do not nest a
second repo folder inside this one.

### Existing Files

This repo already has:

- `AGENTS.md`
- `README.md`
- `docs/FULL-BREAKDOWN.md`
- `docs/HERMES-SANDBOX.md`
- `schemas/job.schema.json`
- `schemas/result.schema.json`
- `registry/workers.json`
- Hermes sandbox install and verification

Shot 1 should evolve these instead of replacing them blindly.

### Hermes

Fable's one-gateway rule is now binding:

- Hermes stays CLI/web-chat only.
- No Hermes gateway channel credentials.
- No Hermes OpenClaw migration except explicit dry-run.
- No Hermes access to OpenBrain, Obsidian, real repos, Telegram, email, or
  social accounts.

## Revised Execution Plan

### Shot 0 - Contracts

Run in:

```text
/home/coachap/.openclaw/workspace/projects/ascending-one
```

Tasks:

- Add DOX `AGENTS.md` tree.
- Add `specs/premium-home/`.
- No app code.

### Shot 1 - Foundry

Run in:

```text
/home/coachap/.openclaw/workspace/projects/theo-agent-os
```

Tasks:

- Add executable dispatch/receipt/validate scripts.
- Add adapter skeletons.
- Add read-only Graphify adapter.
- Add `runs/` append-only convention.
- Add graph freshness gate.
- Verify with a real self-map job and negative tests.

### Shot 2 - Glass

Run in `theo-agent-os` after Shot 1 commit.

Tasks:

- Add localhost-only read-only viewer.
- Render runs, artifacts, repo maps, specs, memory proposals, workers, and
  security.
- Only allowed writes: memory proposal queue and manual security checklist.
- Link to OpenClaw Control UI; never embed or proxy it.

### Shot 3 - Hands

Run in `theo-agent-os` after Shot 2.

Tasks:

- Add Claude adapter first.
- Add Aider adapter second.
- Add Codex adapter only if the installed CLI supports non-interactive mode.
- Keep all write work in git worktrees.
- No merges, no pushes, no memory writes.

### Shot 4 - Mouth

Wait until OpenClaw hardening is green.

Tasks:

- Add OpenClaw skill that converts human intent into job envelopes.
- Read-only jobs may run without confirmation.
- Any write/delete/spend/publish/push intent requires explicit confirmation.
- Schedule morning brief and operator-status through OpenClaw native cron.

## Next Best Move

Do Shot 0 in `ascending-one` or Shot 1 in `theo-agent-os`.

My recommendation: Shot 1 first if the goal is Agent OS infrastructure; Shot 0
first if the goal is improving Ascending Pass 2 immediately.
