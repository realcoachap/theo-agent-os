# Fable Shot 3 Hands QA Risk v0.1.0 - Noted by Theo - 2026-06-10

## Preservation Note

Coach forwarded this Markdown QA artifact from Fable on 2026-06-10 after
reviewing commit `88503e62006877fcaf827b01c828edfb69563f61`.

Verdict at that commit: `RISK`.

The one real defect Fable identified was that write-run `diff.patch` artifacts
missed untracked/new files and symlinks because the adapter library relied on
plain `git diff`. Theo fixed that after this review in commit
`e2c28e89bf1e80a681af94fabaf0a251ed078e56`, tagged
`shot3-hands-v0.3.1`, with follow-up evidence run
`runs/2026-06-10/d43c7251-2b35-4bdb-8132-9a4f96a31bd7`.

The review below is preserved as received in substance, with punctuation
normalized to this repo's Markdown style.

---

# QA Pass - Shot 3 "Hands"

Reviewer: Fable
Date: 2026-06-10
Mode: strict local software-engineering QA
Target commit: `88503e62006877fcaf827b01c828edfb69563f61`

Method: fetched the allowlist at the pinned commit via raw endpoint, then
reproduced behavioral evidence by executing the repo's own dispatch and
adapters in a sandbox lane. The named selftest run and the evidence ZIP were
not present in my inputs; see the Evidence Availability note.

## 1. Verdict: RISK

Shot 3 is functionally complete and the safety rails work under live test:
timeout, lane lock, stale-lock recovery, `.git*`/realpath/symlink denial,
`blocked.log` evidence, env stripping, crash forensics, schema validity, and no
memory writes all pass when I ran their code.

One real defect keeps this at `RISK` rather than `PASS`: the worktree diff
artifact is not captured, which defeats one of Shot 3's own
definition-of-done items: Glass rendering the write-run diff. It is a one-line
fix. No merge blockers; fix the diff capture, then it is a `PASS`.

## 2. Merge Blockers

None.

The diff-capture defect is a `RISK`, not a blocker. The run still produces a
valid reviewable envelope with `blocked.log` and test output; it just lacks the
diff patch the contract promises.

## 3. Evidence Table

| Requirement | File / artifact checked | Result | Note |
|---|---|---|---|
| `budget.max_minutes` timeout | live: 1-minute budget, 75-second sleeper | PASS | SIGTERM-grace-SIGKILL via `run_adapter`; produced `failed` envelope citing the budget; `blocked.log` row `budget.max_minutes timeout after 1 minute(s)`; exit 4 |
| One-writer lane lock | live: sleeper plus second writer | PASS | `O_EXCL` lock held for full adapter duration; second writer got `blocked`, exit 3, message names the holding `job_id` |
| Stale-lock recovery | live: planted dead-PID lock | PASS | Dead PID detected, lock reclaimed, recovery logged to `blocked.log` with `stale_lane_lock_recovered: lock owner pid ... not alive` |
| `.git*` denial, relative | live selftest `blocked.log` | PASS | `.git/config` write produced `git_path_denied` |
| `.git*` denial, absolute | live selftest `blocked.log` | PASS | Absolute `.../.git/config` produced `git_path_denied` |
| `.git*` denial, symlink-resolved | live selftest `blocked.log` | PASS | Symlink to git-common-dir produced `realpath_git_state_denied`; guard runs `git rev-parse --git-dir/--git-common-dir`, resolves realpath, denies |
| deny-list write | live selftest `blocked.log` | PASS | `.env` produced `deny_pattern:.env*` |
| git push blocked | live selftest `blocked.log` | PASS | `theo_git` intercepts `push` and produces `git_push_false` |
| Legitimate work continues while blocked actions are recorded | live selftest result and worktree | PASS | Target fixture written and `verify.tests` passed (`passed: 1`) while five denied actions were logged; status `success` |
| `blocked.log` JSONL contract | live `blocked.log` | PASS | One JSON object per line, keys exactly `{ts,tool,path_or_cmd,rule}`, ISO-Z `ts`; dispatch also auto-attaches it as a `safe_to_render: true` artifact |
| Env A, mapped present | code plus live | PASS by design | Only workers with an `env_profile` receive mapped vars; `claude-glm` carries `$THEO_GLM_*` indirection and is `adapter_pending`, so dispatch correctly blocks it before adapter exec. Indirection plumbing unchanged from the verified 1.2 pass |
| Env B, missing vars block | live | PASS | Unset `$THEO_GLM_*` produced `blocked` envelope naming the missing variable; adapter never launched; exit 3 |
| Env C, stray vars stripped | live | PASS | `ANTHROPIC_*` exported in caller shell did not reach the plain `claude` adapter; assertion `THEO_ASSERT_NO_ANTHROPIC` would have flagged it; `STRIPPED_CHILD_ENV` applied |
| Adapter crash handling and forensic worktree | live: crash probe, exit 42 | PASS | Wrapped as `failed` (`did not write result.json`), stderr preserved, worktree left in place for forensics, lock released |
| Aider status honesty | `adapters/aider.sh`, registry | PASS | `adapter_pending`; real run gated behind `THEO_ENABLE_REAL_AIDER=1` plus env-profile creds; selftest path proves boundary shape without a binary |
| Codex status honesty | `adapters/codex.sh`, registry | PASS | Same pattern, `THEO_ENABLE_REAL_CODEX=1` gate |
| Receipt undo uses actual worktree | live receipt output | PASS | Prints `git worktree remove <lane>/.worktrees/<job_id> && git branch -D agent/<job_id>`, matching dispatch's real worktree path; v0.3.0 receipt reads `job.json` for the lane |
| Result schema validity | live: `bin/validate` on run | PASS | Selftest result validates against `result.schema.json` |
| No silent memory writes | `_lib` result builder | PASS | `memory_proposals` hardcoded `[]`; no vault or queue write path in any adapter |
| Worktree diff artifact | live: selftest result | FAIL -> RISK | `diff: None` and no `Worktree diff` artifact even though a file was created. Cause: `_lib` runs `git diff --`, which is unstaged and tracked-only, in a fresh worktree where the new file is untracked, so the diff is empty. `git add -A` then `git diff --cached` shows the change |
| Glass renders write-run diff, public read-only | `bin/glass` unchanged v0.2.3 | PARTIAL | Glass read-only plus Railway write killswitch verified previously and unchanged. Cannot render a diff that is not produced; unblocks once the diff-capture fix lands. The `blocked.log` artifact renders today |
| Adapter path escape guard | `bin/dispatch` | PASS bonus | New: dispatch resolves the registry `adapter` path and refuses any that escapes repo root |
| Schemas parse | `schemas/*.json` | PASS | Both parse |

## 4. Missing Or Weak Tests

- Diff capture has no test. The gap above would have been caught by an
  assertion that the selftest run yields a non-empty `diff.patch`. Add it; make
  it a Shot 3 gate.
- `partial` path exists in adapters (`verify.tests` fail -> `partial`) but I
  did not see it exercised in committed evidence. It is worth one fixture where
  the test command fails.
- Real CLI path (`THEO_ENABLE_REAL_CLAUDE=1`) is unproven by design. The
  selftest harness covers boundaries, not an actual `claude -p` run. This is
  acceptable for this shot because it is explicitly opt-in, but hook behavior
  under a real agent session is still untested.
- Env A positive on `claude-glm` can only be truly proven once that worker
  leaves `adapter_pending`; today the mapped-env path is verified by reading
  and the dispatch indirection test, not an end-to-end adapter run.

## 5. Risks That Can Ride After Merge

- Diff capture. Fix it pre-merge ideally, but it does not endanger safety; the
  rails all hold, it only weakens reviewability.
- Real-CLI hook semantics remain the known unknown for whenever
  `THEO_ENABLE_REAL_CLAUDE` is first flipped. Keep the relative and absolute
  path hook tests ready to run against a live session.
- Glass v0.2.4 demo-only public guard still TODO, carried from Shot 2 review;
  unrelated to Hands but gates real-data exposure on Railway. Live URL not
  reviewed.
- `tests.passed` / `tests.failed` is binary (`1` / `0`) rather than parsed
  counts. It is honest and schema-valid, but coarse; fine until a real test
  runner is wired.

## 6. Suggested Fix Order

1. Diff capture: in `theo_finish_result`, stage before diffing, for example
   `git add -A` in the worktree and then `git diff --cached --binary`, or use
   `git diff HEAD`. Re-run selftest and assert `diff.patch` is non-empty and a
   `Worktree diff` artifact appears. This also lights up the Glass write-run
   render gate.
2. Add the non-empty-diff assertion to the selftest as a permanent gate.
3. Add one `partial` fixture with failing `verify.tests`.
4. Land Glass v0.2.4 demo-only public guard plus delta-QA, carried over.
5. Tag; full re-QA of the real-CLI path whenever `THEO_ENABLE_REAL_CLAUDE` is
   first enabled.

## 7. Skipped - Outside Allowlist

None analyzed. No cybersecurity-exploit or biological/domain material appeared
in any allowlisted file. All content was ordinary developer tooling, so nothing
was set aside on those grounds.

Files I did not open because they were outside the allowlist: `bin/seed-demo`,
`bin/operator-status`, `registry/pinned-version.txt`, `jobs/examples/*`,
`security/checklist.json`, `railway.json`, `requirements.txt`,
`scripts/install-hermes-sandbox.sh`.

`docs/FABLE-SHOT2-QA-PASS.md` was in scope and read.

## Evidence Availability Note

The named selftest run
`runs/2026-06-10/fcde0616-8c7d-44a4-9d56-3c90ae3a2d09` returned 404 at the
pinned commit and the evidence ZIP
`theo-agent-os-shot3-hands-evidence-2026-06-10.zip` was not present in my
inputs. Only the four earlier Shot 1/2 zips were present.

Rather than block on missing artifacts, I reproduced equivalent evidence by
executing the repo's own dispatch and adapters in selftest mode. This is
arguably stronger than reading Theo's committed run, since I generated fresh
runs and watched the gates fire.

For the formal record, please attach the ZIP or commit the named run directory
so the canonical evidence matches the commit. My live reproduction and that
evidence should agree.
