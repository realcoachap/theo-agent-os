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
  glass
  mouth
  mouth-openclaw
  operator-status
  receipt
  seed-demo
  validate
adapters/
  _lib.sh
  aider.sh
  claude.sh
  codex.sh
  graphify.sh
  _template.sh
fixtures/
  shot3-write-target.txt
hooks/
  post-commit
schemas/
  command.schema.json
  job.schema.json
  reply.schema.json
  result.schema.json
registry/
  pinned-version.txt
  workers.json
jobs/
  examples/
  inbox/
  outbox/
runs/
  .gitkeep
security/
  checklist.json
scripts/
  import-chat-backups-to-obsidian.py
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
are the adapter environment variable names; values are `$VAR` references to the
calling environment. Example: `claude-glm` maps adapter
`ANTHROPIC_BASE_URL` from `$THEO_GLM_BASE_URL`, so multiple
Anthropic-compatible lanes can coexist without clobbering each other's
credentials.

Dispatch fails loud when a referenced `$VAR` is unset, writes a `blocked`
result, and never launches the adapter half-credentialed. Dispatch also strips
caller `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` from child environments by
default; a worker only receives those names if its own `env_profile` explicitly
sets them.

`job_id` values are single-use. Redispatching an existing id exits `2` before
creating or changing run state; mint a new UUID for every job attempt.

Graphify has a labeled demo mode for machines without the CLI:

```bash
GRAPHIFY_STUB=1 bin/dispatch jobs/examples/map-self.json
```

Stub results prove envelope plumbing only. Real map jobs must use the Graphify
CLI before any write worker consumes graph context.

## Obsidian Chat Imports

Chat backups are archive material, not live instructions. The local importer
turns reviewed Telegram/OpenClaw JSON exports and WhatsApp text exports into
Obsidian Markdown under the existing Ascending Research vault:

```bash
python3 scripts/import-chat-backups-to-obsidian.py \
  --vault "$HOME/Documents/Ascending Research Vault" \
  /path/to/telegram-export.json \
  /path/to/whatsapp-export.txt
```

The importer writes human-readable notes under `60 Chat Imports/` plus
`.theo-index/chat-messages.jsonl` for later OpenBrain ingest review. Imported
messages stay `archive_only`; Theo OS jobs can orchestrate the import through
`jobs/examples/import-chat-backups-to-vault.json`, but raw chat history must not
be treated as command input or durable memory without explicit review.

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

## Shot 2 Glass

Glass is the localhost Mission Control viewer over Foundry run envelopes:

```bash
bin/seed-demo
bin/operator-status
bin/glass
```

Then open:

```text
http://127.0.0.1:4040
```

Glass is deliberately read-mostly. It can append memory proposal verdicts to
`memory/queue.jsonl` and update manual security checklist timestamps in
`security/checklist.json`; it cannot dispatch jobs.

In Railway admin mode, Glass also exposes the Spartacus VPS proof-of-concept:
a strict, admin-gated OpenClaw Control node registry where
`/control/spartacus/` is the canonical Spartacus route and `/control/` remains
its compatibility alias. Glass probes the configured Spartacus gateway from the
web tier, verifies an app-layer gateway response, and marks it as the reference
remote node, proving the path without a physical machine. The Control tab is the
first Jarvis / Agent OS cockpit surface for this proof: it shows the Spartacus
proof chain, operator entry routes, and future nodes without exposing write
actions yet. Caesar and Theokoles remain registry entries, but stay disabled
until Railway can reach them through Tailscale or another guarded relay. The
proxy stores no gateway token, strips Glass cookies and auth headers
before forwarding upstream, strips upstream cookies before returning responses,
and keeps each OpenClaw gateway's own token/device-pairing checks as the real
authority. Arbitrary upstream dashboard URLs stay out of scope.

Unsafe HTML artifacts show a blocked badge unless the result envelope declares
`safe_to_render=true`, and artifact preview paths must stay inside their own
run directory.

## Railway Review Surface

Railway runs Glass in explicit read-only review mode:

```bash
bash scripts/start-glass-railway.sh
```

This mode binds to `0.0.0.0` for Railway, allows Railway Host headers, seeds
demo Shot 2 runs when no run index exists, and disables Glass POST writes.

Public review mode refuses to serve non-demo run history unless the operator
sets:

```bash
THEO_GLASS_REMOTE_REVIEW_ACK=public-runs-ok
```

That acknowledgement is intentionally noisy because real write runs may contain
repo history, specs, artifacts, and security checklist state.

## Shot 3 Hands

Write-capable workers now pass through dispatch rails before any adapter runs:

- `budget.max_minutes` is enforced around adapter execution.
- write jobs take a single-lane lock under `runs/locks/`.
- stale locks are recovered by dead PID or configured age.
- denied actions append JSONL rows to `RUN_DIR/blocked.log` as
  `{ts, tool, path_or_cmd, rule}`.
- adapter path checks resolve real paths before deny matching, so `.git*`
  writes and symlinks into git state are blocked.
- raw `verify.tests` output is preserved as a declared artifact when tests run.

Claude has an installed adapter with selftest support. Codex and Aider have the
same wrapper shape but remain `adapter_pending` for real execution until the
operator explicitly sets `THEO_ENABLE_REAL_CODEX=1` or
`THEO_ENABLE_REAL_AIDER=1`. Real Claude execution is likewise gated by
`THEO_ENABLE_REAL_CLAUDE=1`; selftest mode uses `THEO_ADAPTER_SELFTEST=1` and
does not spend model tokens.

## Shot 4 Mouth

Mouth is the first controlled phone-command intake:

```bash
bin/mouth jobs/examples/mouth-shot4-selftest.json
bin/mouth --dispatch --receipt jobs/examples/mouth-shot4-selftest.json
```

It validates `schemas/command.schema.json`, writes a canonical job envelope to
`jobs/inbox/<command_id>/job.json`, optionally calls `bin/dispatch`, and returns
the existing `bin/receipt` text. It does not execute raw chat text, accept
arbitrary shell verify commands, or bypass dispatch safety gates.

The OpenClaw/Telegram wrapper is:

```bash
THEO_TRUSTED_TELEGRAM_IDS=1000000000 \
  bin/mouth-openclaw \
  --event jobs/examples/openclaw-telegram-event.json \
  --selftest-fixture \
  --dispatch \
  --receipt \
  --write-reply \
  --reply-path
```

`bin/mouth-openclaw` recomputes trust from local allowlists; it does not trust
inbound event metadata by itself. `channel=test` fixture events are untrusted
unless the caller explicitly passes `--allow-test-trust` or sets
`THEO_ALLOW_TEST_TRUST=1`.

When `--write-reply` is set, the wrapper also writes
`jobs/outbox/<command_id>/reply.json`, validated by
`schemas/reply.schema.json`. The OpenClaw runtime can send that payload to
Telegram without scraping terminal text.

Before sending, route the payload through the sender guard:

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json --emit-message-json
```

After OpenClaw sends the emitted payload and returns a message id, record the
delivery marker:

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json \
  --mark-sent <telegram-message-id> \
  --sent-path
```

That writes `jobs/outbox/<command_id>/sent.json`, validated by
`schemas/delivery.schema.json`, and Glass shows the reply as sent.

`execution.mode=draft` compiles only. `dispatch_selftest` sets
`THEO_ADAPTER_SELFTEST=1` and spends no model tokens. `dispatch_real` requires
the command's spend approval and the worker's existing `THEO_ENABLE_REAL_*`
switch.

Glass renders Mouth records as queue/operator state, but Glass still does not
dispatch, retry, kill, or push. In Railway admin mode only, Glass also exposes
the guarded OpenClaw Control proxy described above; that proxy is a separate
admin surface and does not give Mouth new execution powers.

## Railway Admin Door

The deployed Railway URL defaults to public read-only review mode. A
single-operator admin login can be enabled only with explicit Railway secrets:

```text
THEO_GLASS_REMOTE_ADMIN=1
THEO_GLASS_ADMIN_USER=coach
THEO_GLASS_ADMIN_PASSWORD_HASH=<pbkdf2 hash>
THEO_GLASS_ADMIN_SESSION_SECRET=<long random secret>
```

Generate the password hash locally:

```bash
printf '%s\n' '<admin-password>' | bin/glass --hash-admin-password
```

Admin mode uses a signed `HttpOnly` session cookie. The Railway admin surface now
includes `/control/spartacus/` as a guarded Spartacus OpenClaw Control route,
with `/control/` as the compatibility alias. It still does not expose raw shell,
raw dispatch, git pushes, or arbitrary OpenClaw proxying.
