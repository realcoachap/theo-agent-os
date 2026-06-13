# Shot 5 — Admin Door Live-State Sync + Actions

Noted by Theo — 2026-06-13 — Glass v0.5.0

## Why

The authenticated Railway admin door rendered a live snapshot but felt
"read-only" for two reasons:

1. **The poll clobbered the operator.** `setInterval(loadState, 3000)`
   re-rendered `#app` unconditionally every 3 seconds. Opening a run detail,
   previewing an artifact, or reading inline action feedback got wiped within
   3s. The panel was technically live but practically unusable for anything
   deeper than a glance.
2. **No sync affordances.** No freshness indicator, no manual refresh, no way to
   pause the churn while reading.

The write-actions themselves were already real and correctly gated (see below),
so the missing piece was *sync*, not *auth*.

## What shipped (v0.5.0)

Client-side live-state sync that never yanks the view out from under the
operator:

- **Visibility-aware polling.** Polls `/api/state` every `POLL_MS` (4s) only when
  the tab is visible; pauses when hidden and catches up immediately on return.
- **Signature-gated rendering.** `stateSignature()` projects the meaningful parts
  of state (run ids/status/state/finished, mouth queue + delivery, security
  checks, proposals, worker registry, operator up/stale) and excludes
  `generated_at`. A snapshot with no real change does not re-render.
- **Interaction lock.** While a run detail or artifact preview is open
  (`interactionLock`), a changed snapshot is held in `pendingSig` and surfaced as
  a non-destructive "● new activity — Refresh" indicator instead of clobbering
  the open view. Closing the detail, switching tabs, or hitting Refresh applies
  the held update.
- **Controls.** Header `sync-status` ("live · synced 7s ago" / "paused" /
  "reconnecting…" / "new activity"), a manual **Refresh**, and a **Live/Pause**
  toggle. A cheap 1s tick advances the "synced Xs ago" label without extra
  fetches.
- **Error resilience.** A failed fetch sets `reconnecting…` and keeps the loop
  alive instead of throwing; recovery clears it.

Regression: `tests/glass_live_sync_regression.py` guards JS parse, the presence
of the controls + sync scaffolding, the `/api/state` contract, and — critically
— that the unconditional `setInterval(loadState, 3000)` clobber loop never
returns.

## Actions surface (current, unchanged by this shot)

These already exist and stay behind the full POST gate
(`check_post`: not review-mode, host check, admin session required under
`--remote-admin`, `X-Theo-Glass: 1`, same-origin Origin **and** Referer):

- `POST /api/memory-proposal` — approve/reject a memory proposal that a result
  envelope actually declared (verified against `memory_proposals(load_runs())`).
- `POST /api/security-check` — toggle a known security checklist item.
- `POST /api/login` / `POST /api/logout` — throttled, hashed, signed-session.

Under live-sync these now behave correctly: their inline feedback is no longer
wiped mid-read, and a verdict/toggle that changes state re-renders cleanly on the
next signature change.

## Next slice (deeper "drive the machine" actions) — needs a preflight + QA

Driving dispatch from the panel is a larger security surface and must follow the
normal preflight → implement → Fable/QA rhythm, not get bolted on here:

- **Approve/hold a pending Mouth command** from the queue (dispatch stays behind
  the existing second local `--dispatch` gate; the panel only flips an
  approval/hold marker that a local runner consumes — the web never executes a
  job directly).
- **Re-run `operator-status`** to refresh the OpenClaw snapshot on demand.
- **Requeue/cancel** a draft command.

Contract for all of the above: `validate → confirm → execute → receipt`, every
action admin-gated + same-origin as today, every action emitting an append-only
receipt row, and no new ability for the web tier to push git, write memory, or
run a worker without the local gate. That design gets its own preflight doc
before code.
