# Hermes Sandbox Plan v0.1.0

Noted by Theo - 2026-06-09

## Verdict

Hermes Agent is worth testing, but not on Coach's main machine state.

Official source:

- https://github.com/NousResearch/hermes-agent
- https://hermes-agent.nousresearch.com/docs/getting-started/installation

## Why Sandbox

Hermes is designed to remember, create skills, schedule work, and connect to
messaging/tools. That is powerful, but it is also exactly the sensitive attack
surface we want to contain.

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

