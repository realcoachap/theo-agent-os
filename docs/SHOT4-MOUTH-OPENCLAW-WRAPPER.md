# Shot 4 Mouth OpenClaw Wrapper v0.1.0

Noted by Theo - 2026-06-10

## Purpose

`bin/mouth-openclaw` is the reviewed wrapper between a Telegram/OpenClaw event
and `bin/mouth`. It exists so the runtime can turn a phone message into a
structured command envelope without creating a raw chat-to-shell path.

## Trust Rule

The wrapper does not trust event metadata by itself. A non-test event becomes
`source.trusted=true` only when the sender or chat id is present in either:

```bash
THEO_TRUSTED_TELEGRAM_IDS=123,456
THEO_TRUSTED_TELEGRAM_CHATS=123,456
```

or the matching CLI flags:

```bash
--trusted-sender 123
--trusted-chat 123
```

The event can claim whatever it wants; the wrapper recomputes trust locally.

## Safe Selftest

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

That path compiles a `command.schema.json` envelope, calls `bin/mouth`, sets
`THEO_ADAPTER_SELFTEST=1`, dispatches through the existing Claude selftest
adapter, and prints the normal `bin/receipt` output. It spends no model tokens.

With `--write-reply`, it also writes a schema-valid delivery payload:

```text
jobs/outbox/<command_id>/reply.json
```

The OpenClaw runtime should send that payload to Telegram. The repo does not
store Telegram secrets and does not deliver messages by itself.

Before sending, the runtime should validate the payload with:

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json --emit-message-json
```

After the Telegram connector returns a message id, record the delivery marker:

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json \
  --mark-sent <telegram-message-id> \
  --sent-path
```

## Direct Chat Mode

Direct Telegram chats can skip the `/theo` prefix if the caller explicitly uses
`--direct-chat`. The text is still only copied into `task`; it is never executed
as shell.

## Real Execution

Real model execution remains deliberately noisy. The wrapper must be called
with `--mode dispatch_real --dispatch`, the command must be trusted, write/spend
approvals must be present, and `bin/mouth` still requires the worker's
`THEO_ENABLE_REAL_*` environment switch.
