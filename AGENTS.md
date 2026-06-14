# AGENTS.md - Theo Agent OS

Noted by Theo - 2026-06-09

## Mission

Build Coach's Agent OS as a trustworthy local routing system:

- one operator
- explicit job envelopes
- proven workers
- read-only memory proposals
- artifacts with receipts
- no silent writes
- no self-evolving agent on the main machine

## Local Rules

1. Read this file before editing.
2. Read `docs/FULL-BREAKDOWN.md` before changing architecture.
3. For write jobs, require:
   - repo graph path
   - spec path
   - AGENTS.md chain
   - blast-radius note
4. Write outputs under `runs/<date>/<job_id>/`.
5. Never auto-write memory. Emit `memory_proposals`.
6. Never render generated HTML unless `safe_to_render` is true.
7. Never install MCP servers, skills, Hermes, Goose, OpenHands, or other agents
   outside sandbox paths from this repo.

## Current Worker Policy

Proven first-class workers:

- Graphify: read-only repo map and blast radius.
- Claude: architecture, specs, review, deeper builds.
- Codex: implementation, tests, code review.
- Aider: surgical patch lane.
- Grok: alternate reasoning and research lane.

Sandbox/watch only:

- Hermes
- Goose
- OpenHands
- Antigravity CLI
- Odysseus
- LiteLLM

## Approval State Machine

All jobs, ideas, and memory proposals use:

```text
proposed -> approved -> running -> review -> shipped | killed
```

Irreversible actions require approval before execution.

## Foundry Contract

- `schemas/job.schema.json` and `schemas/result.schema.json` are the active
  Shot 1 contracts.
- `schemas/command.schema.json` is the active Shot 4 phone/OpenClaw intake
  contract. Mouth commands compile into jobs; they do not replace jobs.
- `schemas/reply.schema.json` is the active Shot 4 outbound receipt contract.
  Runtime delivery should read `jobs/outbox/*/reply.json` instead of scraping
  terminal output.
- `schemas/delivery.schema.json` is the active Shot 4 post-send marker
  contract for `jobs/outbox/*/sent.json`.
- `registry/workers.json` is the only worker manifest.
- `env_profile` maps adapter env var -> `$CALLER_ENV_VAR`. Dispatch must block
  when a referenced caller variable is missing.
- Dispatch strips caller `ANTHROPIC_BASE_URL` and `ANTHROPIC_API_KEY` from
  every child env unless the worker profile explicitly re-adds them.
- Dispatch exit codes are canonical: `0` success, `2` validation/semantic
  rejection, `3` blocked, `4` failed, `5` partial.
- `runs/` is append-only generated history; never edit past result envelopes.
- `job_id` values are single-use identities. A duplicate dispatch must fail
  before creating or modifying run state.
- Adapters stay thin. They may emit `memory_proposals`, but never write memory.
- Read-only adapters must not mutate target repos. Use run-local or temporary
  scratch space for generated analysis artifacts.
- Write-capable adapters must run under `budget.max_minutes` enforcement, a
  write-lane lock, and a denied-action log before Shot 3 can merge.
- Denied adapter actions write JSONL rows to `RUN_DIR/blocked.log` shaped as
  `{ts, tool, path_or_cmd, rule}`.
- Worktree deny checks must resolve real paths before matching. `.git*` and
  symlink paths into shared `.git` state are always blocked, even if a job has
  write permission for ordinary source files.
- Real write-capable Claude/Codex/Aider CLI execution must be explicitly
  enabled by the matching `THEO_ENABLE_REAL_*` environment switch. Selftest
  mode may prove dispatch, worktree, denial, diff, and receipt behavior without
  spending model tokens.
- `bin/mouth` is the only reviewed command-intake bridge in this repo. It must
  reject raw chat-to-shell behavior, keep `git_push=false`, keep `network=false`
  until a later reviewed lane exists, require trusted source plus explicit
  write approval for write dispatch, and reuse `bin/receipt` for operator
  replies.
- `bin/mouth-openclaw` is the reviewed OpenClaw/Telegram wrapper. It must
  recompute trust from local allowlists such as `THEO_TRUSTED_TELEGRAM_IDS` and
  must never trust event-provided metadata alone.
- `bin/mouth-openclaw` must not auto-trust `source.channel="test"`. Test
  fixtures require `--allow-test-trust` or `THEO_ALLOW_TEST_TRUST=1`.
- `bin/mouth-openclaw --write-reply` may write `jobs/outbox/<command_id>/reply.json`.
  This is a delivery payload only; it must not trigger Telegram delivery from
  inside the repo.
- `bin/mouth-send-reply` is the reviewed runtime sender guard. It validates
  `reply.json`, checks it against the original trusted command record, emits a
  narrow OpenClaw message payload, and writes `sent.json` only after OpenClaw
  returns a message id.
- `bin/mouth-session-bridge` is the local runtime mirror from OpenClaw's
  Telegram direct-session transcript to Glass `/api/mouth/ingest`. It must
  filter to user turns, dedupe by OpenClaw record id, avoid backfilling whole
  chat history on first run, and never dispatch jobs or send replies.
- `bin/mouth-reply-bridge` is the local runtime sender for Glass replies. It
  may only send replies returned by Glass `/api/mouth/pending-replies`, which
  requires the command to be approved, drafted, and explicitly queued through a
  separate `send-approved.json` receipt. It must mark Glass sent only after
  OpenClaw returns a delivered message id.
- Before commits that touch adapters, worker registry, env plumbing, or model
  configuration, run a key-string guard such as:
  `git grep -nE '(sk-|api[_-]?key\s*[:=]|Bearer )'`.

## Glass Contract

- `bin/glass` is a localhost-only read surface over `runs/` and declared
  artifacts. It must refuse non-`127.0.0.1` binds.
- Glass never dispatches jobs, retries jobs, kills jobs, pushes code, accepts
  arbitrary upstream proxy targets, or iframes the Control UI. The only Control
  proxy path is the closed node registry in `bin/glass`.
- Glass may display Mouth records from `jobs/inbox/*/mouth.json`, but this is a
  read surface only. Mouth execution stays in `bin/mouth` and dispatch stays in
  `bin/dispatch`.
- The only Glass writes are reviewed append/update lanes:
  - append-only memory verdict entries in `memory/queue.jsonl`
  - manual checklist attestations in `security/checklist.json`
  - append-only control proof receipts in `runs/control-receipts.jsonl`
  - draft-only Mouth ingress records under `jobs/inbox/<command_id>/`
  - Mouth lifecycle verdict receipts under `jobs/inbox/<command_id>/glass-verdict.json`
    plus append-only audit rows in `runs/mouth-verdicts.jsonl`
  - approved Mouth reply drafts under `jobs/outbox/<command_id>/reply.json`
  - queued Mouth reply send approvals under
    `jobs/outbox/<command_id>/send-approved.json`
  - Mouth delivery markers under `jobs/outbox/<command_id>/sent.json` after
    OpenClaw reports a delivered message id
- Artifact previews must be declared by valid result envelopes and remain
  inside their run directory. Absolute paths and escaping paths are blocked.
- HTML artifact previews require `safe_to_render=true` and still render in a
  sandboxed iframe. Untrusted HTML shows metadata and a blocked badge.
- `bin/operator-status` reads `OPENCLAW_UI_TOKEN` only from the calling
  environment, strips credential-like data, and writes only
  `runs/operator-status.json`.
- Railway `--remote-review` mode is read-only and public-review oriented. It
  should serve demo-only run history by default; exposing real runs requires an
  explicit operator acknowledgement environment variable.
- Railway `--remote-admin` mode is single-operator only. It requires
  `THEO_GLASS_REMOTE_ADMIN=1`, admin credentials, and a session secret. It may
  expose reviewed Glass writes after login, but still must not expose shell,
  raw dispatch, pushes, OpenClaw proxying, or the Control UI link.
- Railway `--remote-admin` login must throttle repeated failures. The current
  in-process limiter is enough for the single-operator stage; use a durable
  shared limiter before multi-instance or broader team admin mode.
- `POST /api/mouth/ingest` is the only Glass live-chat ingress lane. It must
  require admin POST rules or `THEO_GLASS_MOUTH_INGEST_SECRET`, call
  `bin/mouth-openclaw` without `--dispatch`, and produce draft-only Mouth
  records. Trust must come from allowlist env such as
  `THEO_TRUSTED_TELEGRAM_IDS`, never from event metadata alone.
