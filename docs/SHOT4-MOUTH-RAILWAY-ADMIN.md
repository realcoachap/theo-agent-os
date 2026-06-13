# Shot 4 Railway Admin Door v0.1.1

Noted by Theo - 2026-06-10

## Purpose

Railway can host Coach's away-from-home Mission Control door, but it must not
turn public Glass into an unauthenticated write surface. `bin/glass` therefore
has two explicit remote modes:

- `--remote-review`: public, read-only, current default.
- `--remote-admin`: single-operator login, enabled only by Railway secrets.

The admin door is for operator UI and limited reviewed actions. It is not a raw
shell, not an arbitrary tunnel, and not a way to bypass Mouth/dispatch. Current
Railway admin mode also exposes `/control/spartacus/` as the guarded Spartacus
OpenClaw Control route, with `/control/` as its compatibility alias; that route
keeps Spartacus gateway token and device pairing as the authority.

## Required Railway Variables

```text
THEO_GLASS_REMOTE_ADMIN=1
THEO_GLASS_ADMIN_USER=coach
THEO_GLASS_ADMIN_PASSWORD_HASH=<pbkdf2 hash>
THEO_GLASS_ADMIN_SESSION_SECRET=<long random secret>
THEO_GLASS_ADMIN_LOGIN_MAX_FAILURES=5
THEO_GLASS_ADMIN_LOGIN_WINDOW_SECONDS=300
```

Generate the password hash locally:

```bash
printf '%s\n' '<admin-password>' | bin/glass --hash-admin-password
```

Do not commit the password or session secret. Set them only in Railway's
environment-variable UI or CLI.

## Guarantees

- Without `THEO_GLASS_REMOTE_ADMIN=1`, Railway starts in public read-only review
  mode exactly as before.
- Admin mode refuses startup unless both a password/password-hash and session
  secret are configured.
- Unauthenticated admin requests see the login page only; `/api/state` returns
  `401`.
- Login uses a signed `HttpOnly`, `Secure`, `SameSite=Lax` session cookie.
- Repeated failed login attempts are throttled per client with `429` and
  `Retry-After`. This is in-process by design for the single-operator Railway
  stage.
- Admin writes still require the existing `X-Theo-Glass: 1` header and same-host
  origin checks.
- `/control/spartacus/` is available only behind the Glass admin login as the
  guarded Spartacus VPS proof-of-concept route. `/control/` remains a
  compatibility alias. Glass probes the configured Spartacus gateway from the
  web tier and verifies an app-layer response so the admin UI can show whether
  the remote VPS path is actually answering, not only whether the port is open.
  The proxy stores no gateway token, strips Glass admin cookies/auth headers
  upstream, strips upstream cookies on the way back, and relies on Spartacus
  gateway token/device-pairing checks.
- Glass still does not execute shell commands, dispatch jobs, push code, or
  proxy arbitrary OpenClaw upstreams.
- Glass now uses a strict allowlisted node registry. Spartacus is the reference
  remote/VPS POC and the Jarvis / Agent OS cockpit proof surface; Caesar and
  Theokoles are present as disabled/planned entries until Railway can reach
  their gateways through Tailscale or another guarded relay.

## First Proof

1. Public default Railway mode remains `railway-review`, `writes_enabled=false`,
   and POST returns `403`.
2. Local admin-mode smoke test without cookie returns `/api/state -> 401`.
3. Bad login returns `401`.
4. Good login sets a session cookie and `/api/state` reports
   `mode=railway-admin`, `writes_enabled=true`.
5. Repeated bad logins return `429` after the configured failure threshold.
6. Logout clears the session cookie.

This document originally described the Shot 4 admin foundation before the
Spartacus Control proxy landed. The current next layer is Caesar/Theokoles
reachability plus live-state sync/action design without broadening Glass into
raw shell or arbitrary tunnel access.
