# Fable Shot 1 ZIP Review v0.1.1

Noted by Theo - 2026-06-09

## Source

Coach forwarded two files on 2026-06-09:

- `SPRINT-BRIEF-FOR-THEO---6effae02-ef91-4912-b4bc-8ce27a90008c.md`
- `coach-agent-os-shot1---b000fd20-efbe-49ee-84a8-02a123e91c44.zip`

SHA-256:

```text
9507fd583f482e225c1c419ac4d0bde2ce5f78c25e1a8b022486c883f73edfc7  SPRINT-BRIEF-FOR-THEO
5dab80ab13b1df890f57f3129c4ddf4826c73082ef4db074efe672fb1211332e  coach-agent-os-shot1.zip
```

The ZIP was extracted only to `/tmp/fable-coach-agent-os-shot1` for review.
Do not execute or merge it blindly.

## Verdict

Useful reference, not a replacement.

The canonical implementation remains:

```text
realcoachap/theo-agent-os
commit 25bd02e plus review/fix follow-ups
```

Our Shot 1 is stricter and safer because it:

- Uses strict schemas with `additionalProperties: false`.
- Requires `context.graph`, `context.spec`, `context.agents_md`, and
  `context.blast_radius` for write jobs.
- Runs a real Graphify map job locally, not only a stub demo.
- Prevents Graphify target repo mutation by building from a temp copy and
  copying artifacts into `runs/`.
- Keeps generated run artifacts ignored while tracking only fixtures and
  `.gitkeep`.

## What Fable Did Well

- `lib/envelope.py` cleanly separates envelope enforcement from `bin/dispatch`.
- `AGENTS.md` has a strong rule that schemas and enforcement must change in
  the same commit.
- `bin/validate` UX is simple: `bin/validate schemas`, `bin/validate job`,
  `bin/validate result`.
- The sprint brief is clear about the Day-1 order and standing rules.
- The included demo runs are useful examples for Shot 2 fixture seeding.

## Why It Should Not Replace Ours

- It uses repo name `coach-agent-os`, but our canonical repo is
  `theo-agent-os`.
- The ZIP includes `.git/`, `__pycache__`, and demo `runs/` artifacts.
- The verified success path relies on `GRAPHIFY_STUB=1`, which proves plumbing
  but not the real Graphify worker.
- The real Graphify adapter path runs `graphify build/update` inside the target
  lane and writes `graphify-out/` there. That violates our read-only worker
  interpretation for Shot 1.
- Its schema files are documentation-oriented and less strict than ours.
- Its result artifacts contain absolute sandbox paths like `/home/claude/...`.

## Ideas To Steal Later

### Shot 1.1 Or Shot 3

Refactor shared enforcement into:

```text
lib/envelope.py
```

Only do this after preserving current behavior with tests. The current
`bin/dispatch` works; do not churn it merely for aesthetics.

### Shot 2

Use Fable's demo result shapes as seed ideas for Glass fixture generation:

- success map result
- stale graph blocked result
- fresh graph result

But regenerate fixtures in our repo with relative paths.

### AGENTS.md

Adopt Fable's guard:

```bash
git grep -nE '(sk-|api[_-]?key\s*[:=]|Bearer )'
```

before commits that touch worker registry, adapters, env plumbing, or model
configuration.

## Final Decision

No code merge from the ZIP tonight.

Keep `theo-agent-os` Shot 1 as canonical, and revisit `lib/envelope.py` as a
small refactor only if Shot 2/3 makes dispatch too large to reason about.

## Fable Review Of Theo ZIP

After reviewing Theo's canonical ZIP, Fable agreed this repo should remain
canonical and flagged four useful fixes before Shot 3:

- `env_profile` needed worker-specific caller variable indirection for
  `claude-glm`.
- Dispatch exit codes should be documented as the standard for Shot 4.
- A labeled stub path is useful on machines without Graphify.
- Duplicate schema aliases and duplicate example-job paths should be removed.

Those fixes were applied as Shot 1.1 follow-up work.

Fable then cut prompt-pack v0.1.2 with the binding env version: registry values
must be `$VAR` strings, dispatch must fail loud when a referenced variable is
missing, and child environments must strip caller `ANTHROPIC_BASE_URL` /
`ANTHROPIC_API_KEY` unless the worker explicitly re-adds them. That stricter
version is now the repo contract.
