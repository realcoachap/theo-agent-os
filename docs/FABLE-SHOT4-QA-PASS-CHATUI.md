# Fable Shot 4 QA Pass + Chat UI Scout v0.1.0 - Noted by Theo - 2026-06-10

## Source

Coach forwarded Fable's Markdown report
`QA-shot4_2-4_3-and-chatUI-scout---b46f2ee7-3966-49bf-a7a9-4180b919e6e2.md`
on 2026-06-10. Fable reviewed commit `b2fc6a24` by code read plus sandbox
execution of the sender guard and Glass admin logic. No live service was
tested.

Verdict: `PASS`.

## Shot 4.2 / 4.3 Findings

Fable confirmed the load-bearing Shot 4 claims:

- `bin/mouth-send-reply` prevents forged reply targets by loading the original
  command record from `jobs/inbox/<command_id>/command.json` and checking both
  `command.delivery.target` and `command.source.chat_id`.
- `reply.json` and `sent.json` are strict, schema-valid contracts with
  `additionalProperties:false`; `sent.json` is written only after OpenClaw
  returns a message id.
- The sender guard holds no Telegram token and does not call Telegram itself.
  OpenClaw remains the privileged delivery runtime.
- `bin/glass --remote-admin` is a sound single-operator login foundation:
  PBKDF2-HMAC-SHA256 password verification, HMAC-signed bounded-TTL session
  cookie, `HttpOnly` / `SameSite=Lax` / remote `Secure` cookie flags, and
  fail-closed startup when secrets are absent.
- Railway review mode stays read-only unless explicitly elevated by
  `THEO_GLASS_REMOTE_ADMIN=1`.
- Remote admin mode exposes no raw shell, dispatch, retry, kill, git push,
  OpenClaw proxy, or Control UI route.

Fable's requested distinction is accepted:

> The Railway admin door is a good first authenticated foundation: remote =
> see and approve. It is not a remote action system; doing still flows through
> Mouth and dispatch.

## Non-Blocking Hardening

Fable called out these risk-level follow-ups:

- `mouth-openclaw` still auto-trusted `channel:"test"` events at commit
  `b2fc6a24`.
- `/api/login` had no attempt throttling.
- Session logout is client-side only; a leaked valid cookie remains valid until
  expiry.
- Add committed sender-guard, fail-closed, session, route-inventory, and
  partial-status tests.

## Follow-Up Closure

Commit `57048f5` (`Harden Shot 4 admin and mouth guards`) closed the two
immediate carry-overs:

- `bin/mouth-openclaw` v0.4.2 requires `--allow-test-trust` or
  `THEO_ALLOW_TEST_TRUST=1` before `channel:"test"` fixtures become trusted.
- `bin/glass` v0.4.4 throttles repeated failed admin logins per client with
  `429` and `Retry-After`.
- `tests/shot4_hardening_regression.py` proves explicit test-channel trust,
  sender-guard forged/untrusted/test blocking, and admin login throttling.

Local verification passed, and Railway deployment
`dfee19ac-2737-4271-80f0-4e3bff616f83` succeeded. Live checks after deploy:
`/login` 200, unauthenticated `/api/state` 401 in `railway-admin`, bad login
401. The production throttle was not intentionally tripped to avoid locking
Coach's active admin door.

## Mission Control Chat UI

Fable recommended:

- Primary: Mattermost.
- Runner-up: Zulip.

Reasoning accepted:

- Mattermost is the fastest useful ChatOps-style pilot: simple enough for a
  one-operator start, polished web/mobile UI, channels, webhooks, bot accounts,
  slash commands, and self-hosted data ownership.
- Zulip's topic model is better if automated chatter becomes the main pain, but
  its operational model is heavier than needed for the first operator room.
- Rocket.Chat, Matrix/Element, and Stoat/Revolt are useful references but not
  the first pilot path for Theo Agent OS.

Target shape:

- `#mission-control`
- `#theo-receipts`
- `#agent-chatter`
- `#deploys`
- `#fable-qa`
- `#alerts`

Pilot order:

1. Stand up Mattermost with Postgres on a VPS or similarly stable stateful host.
2. Create the six channels.
3. Wire outbound-only receipts first: Mouth/dispatch receipts, deploy notes,
   and QA summaries post into Mattermost with Glass deep links.
4. Wait before adding inbound `/theo`; when added, it must route through the
   same Mouth trust/approval gates as Telegram.

## Carry-Overs

- Do not let chat become the source of truth. Chat posts link back to Glass.
- Keep Mattermost credentials and webhook tokens out of the repo.
- Add the remaining route-inventory, fail-closed, expired-session, and partial
  fixtures before a broader remote action shot.
- Run the first paid `THEO_ENABLE_REAL_CLAUDE=1` QA round separately when Coach
  approves token spend.
