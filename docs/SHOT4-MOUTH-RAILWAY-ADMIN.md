# Shot 4 Railway Admin Door v0.1.0

Noted by Theo - 2026-06-10

## Purpose

Railway can host Coach's away-from-home Mission Control door, but it must not
turn public Glass into an unauthenticated write surface. `bin/glass` therefore
has two explicit remote modes:

- `--remote-review`: public, read-only, current default.
- `--remote-admin`: single-operator login, enabled only by Railway secrets.

The admin door is for operator UI and limited reviewed actions. It is not a raw
shell, not a tunnel to localhost, and not a way to bypass Mouth/dispatch.

## Required Railway Variables

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
- Admin writes still require the existing `X-Theo-Glass: 1` header and same-host
  origin checks.
- The Control UI link remains hidden on Railway.
- Glass still does not execute shell commands, dispatch jobs, push code, or
  proxy OpenClaw.

## First Proof

1. Public default Railway mode remains `railway-review`, `writes_enabled=false`,
   and POST returns `403`.
2. Local admin-mode smoke test without cookie returns `/api/state -> 401`.
3. Bad login returns `401`.
4. Good login sets a session cookie and `/api/state` reports
   `mode=railway-admin`, `writes_enabled=true`.
5. Logout clears the session cookie.

The next layer after this is live-state sync/action design, not broadening the
admin door.
