# Shot 4 Mouth Preflight v0.1.0

Noted by Theo - 2026-06-10

## Purpose

Shot 4 turns Coach's phone command into the same `job.json` contract that
Foundry already dispatches. It must not create a raw chat-to-shell path, a
hidden spend path, or a new source of truth for receipts.

## Merge Gates

- Phone/OpenClaw intake uses `schemas/command.schema.json`; raw chat text is
  never executed and cannot carry arbitrary shell fields.
- `bin/mouth` compiles a command envelope into a canonical `job.json` under
  `jobs/inbox/<command_id>/`.
- `bin/mouth --dispatch` is a second local/operator gate. A command asking for
  `draft` mode never dispatches.
- Write dispatch requires `source.trusted=true`, `approvals.operator=true`,
  `approvals.write=true`, `git_push=false`, and `network=false`.
- Real model execution requires `execution.mode=dispatch_real`,
  `approvals.spend=true`, and the worker's existing `THEO_ENABLE_REAL_*`
  environment switch.
- Selftest dispatch sets `THEO_ADAPTER_SELFTEST=1` and spends no model tokens.
- Mouth returns the existing `bin/receipt` output; it does not invent a second
  receipt format.
- Glass may show Mouth queue/operator state, but Glass still must not dispatch,
  retry, kill, push, proxy OpenClaw, or iframe Control UI.

## Expected First Proof

1. Validate a command envelope against `schemas/command.schema.json`.
2. Compile it into `jobs/inbox/<command_id>/job.json`.
3. Validate the generated job against `schemas/job.schema.json`.
4. Dispatch a selftest write command through the existing Claude adapter with
   `THEO_ADAPTER_SELFTEST=1`.
5. Render the receipt and expose the Mouth record in Glass state.

## Carry-Overs

- Telegram/OpenClaw wrapper can call `bin/mouth`; this repo only owns the safe
  intake contract and local runner.
- Human-friendly natural language classification can come later, but only as a
  producer of `command.schema.json`, not as an executor.
- The first live `THEO_ENABLE_REAL_CLAUDE=1` run remains a separate QA round.
