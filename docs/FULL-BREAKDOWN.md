# Agent OS Full Breakdown v0.1.0

Noted by Theo - 2026-06-09

## Plain English Definition

An Agent OS is not a single web app. The web app is only the visible control
surface.

The real Agent OS is the operating pattern behind it:

1. A human enters intent through a front door.
2. One operator turns intent into a concrete job.
3. The operator plays back the plan.
4. The human confirms when needed.
5. A specialized worker does the work.
6. Tests, permissions, previews, and receipts gate the result.
7. Artifacts and memory proposals are saved in a durable run folder.

For Coach's system:

- Front doors: Telegram, terminal, OpenChat, later Mission Control and voice.
- Operator: OpenClaw / Theo.
- Workers: Graphify, Claude, Codex, Aider, Grok.
- Contracts: DOX / AGENTS.md / specs.
- Memory: OpenBrain, Obsidian, repo decisions, daily memory.
- Gates: tests, previews, receipts, approval, undo where possible.
- Artifacts: `runs/<date>/<job_id>/result.json` plus declared files.

## Operator Model

The operator is the lazy path, not the only path.

Manual UI and operator UI must both hit the same validation, preview, save,
receipt, and undo paths.

Operator loop:

```text
intent -> plan -> playback -> confirm -> execute -> receipt -> undo/followup
```

Confirmation tiers:

- Cheap and undoable: execute, then receipt.
- Expensive, destructive, publishing, secrets, money, push/deploy: confirm
  before execution.

## Worker Model

Workers are hired for a job. They are not peers voting in a council.

This avoids authority confusion and runaway multi-agent loops.

Worker lanes:

- Graphify: map the repo, find modules, identify load-bearing files, explain
  blast radius.
- Claude: architecture, product synthesis, specs, long-context review, deeper
  implementation when guarded.
- Codex: local repo implementation, verification, tests, commits.
- Aider: narrow known-file patches.
- Grok: alternate reasoning, external research, creative divergence.

## Why Graphify First

Graphify is the safest first wrapper because it is read-only.

It gives every later write job:

- repo summary
- key modules
- load-bearing files
- dependency context
- blast-radius estimate
- graph artifact paths

No write worker should start broad edits without graph/spec/context.

## Required Write Context

Every write job must include:

- `graph`: Graphify graph path.
- `spec`: feature/spec path.
- `agents_md`: true.
- `blast_radius`: Graphify precheck result for broad changes.

If these are missing, the operator should block or downgrade to planning mode.

## Job Envelope

Jobs enter the system as structured input:

```json
{
  "job_id": "uuid",
  "lane": "ascending-one",
  "intent": "build|patch|research|review|map|content|propose",
  "worker": "graphify|claude|codex|aider|grok|auto",
  "task": "plain-language goal",
  "context": {
    "graph": "graphify-out/graph.json",
    "spec": "specs/feature/spec.md",
    "agents_md": true,
    "blast_radius": "runs/date/job/graphify-pre.json"
  },
  "permissions": {
    "tier": "read_only|write_sandboxed|write_trusted",
    "write": ["src/**"],
    "deny": ["secrets/**", ".env*"],
    "network": false,
    "git_push": false
  },
  "verify": {
    "tests": "npm test",
    "lint": true
  },
  "budget": {
    "max_minutes": 20,
    "max_tokens": 200000
  }
}
```

## Result Envelope

Every worker returns structured output:

```json
{
  "job_id": "uuid",
  "status": "success|partial|failed|blocked",
  "state": "review",
  "summary": "Three sentences max.",
  "diff": "runs/date/job/changes.patch",
  "files_touched": [],
  "tests": {"ran": true, "passed": 0, "failed": 0},
  "git": {"branch": "job/uuid", "dirty": false, "commits": []},
  "transcript": "runs/date/job/transcript.md",
  "artifacts": [],
  "memory_proposals": [],
  "followups": [],
  "cost": {"tokens": 0, "minutes": 0}
}
```

## Artifact Library

Mission Control should not scrape random files. Workers declare artifacts.

Artifact metadata:

```json
{
  "artifact_type": "report|html|doc|image|video|code|data",
  "title": "Home QA screenshot",
  "summary": "390px mobile screenshot after Pass 2 polish.",
  "path": "runs/date/job/home-mobile.png",
  "preview_kind": "text|html|image|none",
  "worker": "codex",
  "source_job": "uuid",
  "safe_to_render": false
}
```

`safe_to_render` defaults to false, especially for HTML created by a job with
network access.

## Memory Policy

Workers never write durable memory directly.

They emit:

```json
"memory_proposals": [
  "Candidate fact or decision for Theo/Coach approval."
]
```

Theo or Coach approves before anything lands in OpenBrain, Obsidian, or long
term repo memory.

## Dreaming Policy

"Dreaming" is allowed only as a read-only scheduled review:

- read `runs/*/result.json`
- read approved decisions/specs
- emit a morning brief
- emit memory proposals

It must not:

- change memory
- install skills
- edit repos
- send public messages
- publish content

## Mission Control

Mission Control is not the brain. It is a viewer and approval surface.

First tabs:

- Runs
- Artifacts
- Repo Maps
- Specs
- Memory Proposals
- Workers
- Hardening / Security

Not first:

- voice build mode
- SEO room
- agent swarm
- auto-publish
- self-evolving skill lab

## Security Boundaries

Hard rules:

- No direct repo writes by OpenClaw outside wrapper gates.
- No `.env` reads by workers.
- No unreviewed MCP/skill installs.
- No Hermes/OpenHands/Goose beside real vaults.
- No voice command direct execution.
- No generated HTML render unless marked safe.
- No social/email publishing without explicit approval.

Sandbox/watch only:

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- Odysseus
- LiteLLM

## Build Order

1. DOX/spec pilot in `ascending-one`.
2. Graphify wrapper.
3. Unified runner for proven workers.
4. Claude Agent SDK wrapper.
5. Codex/Aider/Grok wrappers.
6. Artifact Library contract.
7. Mission Control viewer.
8. Read-only morning review.
9. Hermes sandbox evaluation.
10. Voice/content/social lanes only after gates exist.

