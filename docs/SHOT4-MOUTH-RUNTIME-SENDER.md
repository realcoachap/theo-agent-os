# Shot 4 Mouth Runtime Sender v0.1.0

Noted by Theo - 2026-06-10

## Purpose

`bin/mouth-send-reply` is the reviewed handoff between a Mouth reply payload
and the OpenClaw runtime message sender. It prevents a generated
`jobs/outbox/<command_id>/reply.json` from being edited into a forged outbound
message.

The repo still does not store Telegram secrets and does not call Telegram
directly. OpenClaw owns delivery. This binary only validates the payload, emits
a narrow message-tool request, and records a post-send marker once OpenClaw
returns a message id.

## Guard Rules

- `reply.json` must validate against `schemas/reply.schema.json`.
- The matching `jobs/inbox/<command_id>/command.json` must exist.
- `reply.command_id`, `reply.job_id`, `reply.channel`, and `reply.target` must
  match the original trusted command record.
- `reply.target` must equal the original `source.chat_id`; changing the target
  after dispatch is blocked.
- The original command source must be trusted.
- Telegram and explicit test-channel fixtures are the only supported delivery
  channels in this shot.
- `result_path`, when present, must stay inside the repo and exist.
- A `sent.json` marker is written only after OpenClaw reports a message id.

## Operator Flow

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json --emit-message-json
```

The OpenClaw runtime sends the emitted payload through its Telegram connector.
After delivery succeeds:

```bash
bin/mouth-send-reply jobs/outbox/<command_id>/reply.json \
  --mark-sent <telegram-message-id> \
  --sent-path
```

Glass reads both `reply.json` and `sent.json`, so the control center can show
whether an operator reply is pending or sent.
