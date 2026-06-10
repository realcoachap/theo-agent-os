# Hermes Sandbox Plan v0.1.0

Noted by Theo - 2026-06-09

## Verdict

Hermes Agent is worth testing, but not on Coach's main machine state.

Official source:

- https://github.com/NousResearch/hermes-agent
- https://hermes-agent.nousresearch.com/docs/getting-started/installation
- https://hermes-agent.nousresearch.com/docs/getting-started/quickstart

## Why Sandbox

Hermes is designed to remember, create skills, schedule work, and connect to
messaging/tools. That is powerful, but it is also exactly the sensitive attack
surface we want to contain.

## What Hermes Actually Is

Hermes is a self-hosted personal agent runtime from Nous Research. It overlaps
with OpenClaw because it includes many of the same operating-system pieces:

- CLI chat and TUI.
- Web dashboard / desktop app.
- Gateway for messaging platforms.
- Cron jobs and scheduled automations.
- Persistent memory.
- Skill creation and skill maintenance.
- MCP and ACP surfaces.
- Tool permissions, hooks, checkpoints, and profiles.

For Coach's stack, Hermes is not the operator yet. OpenClaw remains the trusted
operator/router. Hermes is a sandboxed scout to test whether its memory, skill,
dashboard, and automation loop can do anything our current OpenClaw + Skills +
Claude/Codex/Graphify stack cannot already do.

## Local Sandbox Path

This repo installs Hermes into:

```text
.sandbox/hermes-venv
.sandbox/hermes-home
```

Run commands with:

```bash
export HERMES_HOME="$PWD/.sandbox/hermes-home"
.sandbox/hermes-venv/bin/hermes --help
```

## Installed State

Verified on 2026-06-09:

- Package: `hermes-agent`
- Version: `0.16.0`
- Hermes release string: `Hermes Agent v0.16.0 (2026.6.5)`
- Binary: `.sandbox/hermes-venv/bin/hermes`
- Home: `.sandbox/hermes-home`
- Gateway: stopped
- Messaging platforms: not configured
- Scheduled jobs: `0`
- Active sessions: `0`

## Safe Setup Path For This Repo

From this repo root:

```bash
cd /home/coachap/.openclaw/workspace/projects/theo-agent-os
./scripts/install-hermes-sandbox.sh
export HERMES_HOME="$PWD/.sandbox/hermes-home"
.sandbox/hermes-venv/bin/hermes --version
.sandbox/hermes-venv/bin/hermes status
.sandbox/hermes-venv/bin/hermes doctor
```

For first interactive configuration, use the sandbox home:

```bash
export HERMES_HOME="$PWD/.sandbox/hermes-home"
.sandbox/hermes-venv/bin/hermes setup --quick
```

Provider setup choices:

```bash
.sandbox/hermes-venv/bin/hermes model
.sandbox/hermes-venv/bin/hermes portal
```

First safe chat test:

```bash
export HERMES_HOME="$PWD/.sandbox/hermes-home"
.sandbox/hermes-venv/bin/hermes chat --ignore-rules --query "Reply exactly: HERMES_SANDBOX_OK"
```

Use `--ignore-rules` for the first tests so Hermes does not ingest our broader
workspace rules, memory, or repo context.

## Normal Global Setup Is Different

Official global install is:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup
```

Do not use that path for Coach's main machine until the sandbox scout earns it.
The global setup writes to normal Hermes state, can detect OpenClaw, and may
offer migration. Migration is useful later, but it is the wrong first move for
this stack.

If testing migration someday, run only a dry run first:

```bash
hermes claw migrate --dry-run
```

No real migration until Coach approves the exact preset and target.

## Allowed During Scout

- CLI help/version/doctor.
- Synthetic prompts.
- No private project data.
- No real vault.
- No real Telegram/Discord/email/social connectors.
- No OpenBrain writes.
- No ClawHub/skill auto-installs without scanner gate.

## Blocked During Scout

- `~/.hermes`
- Obsidian vault access
- OpenBrain write access
- production repo write access
- Telegram bot connection
- Discord connection
- email connection
- browser automation against logged-in accounts
- social posting

## Evaluation Question

Hermes earns more access only if it does something our current stack cannot do:

- OpenClaw + Skills
- Claude Code
- Codex
- Graphify
- Aider
- Grok
- OpenBrain

Until then, it stays sandboxed.
