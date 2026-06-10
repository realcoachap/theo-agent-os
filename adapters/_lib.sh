#!/usr/bin/env bash
# Theo Agent OS shared adapter library v0.3.0 - Noted by Theo - 2026-06-10
# Shell adapters source this file so write workers share one result builder,
# path guard, blocked-action log, git wrapper, and test-output contract.
set -euo pipefail

: "${JOB_PATH:?JOB_PATH is required}"
: "${RUN_DIR:?RUN_DIR is required}"
: "${RUN_DIR_REL:?RUN_DIR_REL is required}"
: "${LANE_PATH:?LANE_PATH is required}"
: "${REPO_ROOT:?REPO_ROOT is required}"

THEO_WRITE_ROOT="${WORKTREE:-}"
if [[ -z "$THEO_WRITE_ROOT" ]]; then
  THEO_WRITE_ROOT="$LANE_PATH"
fi

theo_job_field() {
  local field="$1"
  python3 - "$field" <<'PY'
import json
import os
import sys
from pathlib import Path

field = sys.argv[1]
data = json.loads(Path(os.environ["JOB_PATH"]).read_text(encoding="utf-8"))
value = data
for part in field.split("."):
    if not isinstance(value, dict):
        value = ""
        break
    value = value.get(part, "")
if value is None:
    value = ""
print(value if isinstance(value, str) else json.dumps(value))
PY
}

theo_blocked_log() {
  local tool="$1"
  local path_or_cmd="$2"
  local rule="$3"
  python3 - "$tool" "$path_or_cmd" "$rule" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

tool, path_or_cmd, rule = sys.argv[1:4]
path = Path(os.environ.get("THEO_BLOCKED_LOG") or Path(os.environ["RUN_DIR"]) / "blocked.log")
path.parent.mkdir(parents=True, exist_ok=True)
row = {
    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    "tool": tool,
    "path_or_cmd": path_or_cmd,
    "rule": rule,
}
with path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(row, sort_keys=True) + "\n")
PY
}

theo_guard_path() {
  local raw_path="$1"
  local tool="${2:-path_guard}"
  python3 - "$raw_path" "$tool" <<'PY'
import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

raw_path, tool = sys.argv[1:3]
job = json.loads(Path(os.environ["JOB_PATH"]).read_text(encoding="utf-8"))
root = Path(os.environ.get("WORKTREE") or os.environ["LANE_PATH"]).resolve()
blocked_log = Path(os.environ.get("THEO_BLOCKED_LOG") or Path(os.environ["RUN_DIR"]) / "blocked.log")

def log(rule: str) -> int:
    blocked_log.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "tool": tool,
        "path_or_cmd": raw_path,
        "rule": rule,
    }
    with blocked_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(rule, file=sys.stderr)
    return 1

def inside(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents

def git_path(name: str) -> Path | None:
    proc = subprocess.run(
        ["git", "rev-parse", name],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve(strict=False)

raw = Path(raw_path).expanduser()
candidate = raw if raw.is_absolute() else root / raw
resolved = candidate.resolve(strict=False)
git_roots = [path for path in (git_path("--git-dir"), git_path("--git-common-dir")) if path]
for git_root in git_roots:
    if inside(resolved, git_root):
        raise SystemExit(log("realpath_git_state_denied"))
try:
    rel = resolved.relative_to(root)
except ValueError:
    raise SystemExit(log("path_outside_write_root"))

rel_text = rel.as_posix()
raw_parts = [part for part in raw.parts if part not in {"", "."}]
rel_parts = list(rel.parts)
if any(part.startswith(".git") for part in raw_parts + rel_parts):
    raise SystemExit(log("git_path_denied"))

deny_patterns = list(job.get("permissions", {}).get("deny", []))
deny_patterns.extend([".git", ".git/**", ".git*", "**/.git", "**/.git/**", "**/.git*"])
for pattern in deny_patterns:
    if fnmatch.fnmatch(rel_text, pattern) or fnmatch.fnmatch("/" + rel_text, pattern):
        raise SystemExit(log(f"deny_pattern:{pattern}"))

write_patterns = list(job.get("permissions", {}).get("write", []))
if write_patterns and not any(fnmatch.fnmatch(rel_text, pattern) or rel_text == pattern.rstrip("/") for pattern in write_patterns):
    raise SystemExit(log("path_not_in_permissions.write"))

print(str(resolved))
PY
}

theo_write_text() {
  local target="$1"
  local content="${2:-}"
  local resolved
  if ! resolved="$(theo_guard_path "$target" "write_file")"; then
    return 1
  fi
  mkdir -p "$(dirname "$resolved")"
  printf "%s" "$content" > "$resolved"
}

theo_git() {
  local subcmd="${1:-}"
  if [[ "$subcmd" == "push" ]]; then
    theo_blocked_log "git" "git $*" "git_push_false"
    return 1
  fi
  git -C "$THEO_WRITE_ROOT" "$@"
}

theo_run_verify() {
  local tests_cmd
  tests_cmd="$(theo_job_field "verify.tests")"
  export THEO_TESTS_RAN="false"
  export THEO_TESTS_PASSED="0"
  export THEO_TESTS_FAILED="0"
  if [[ -z "$tests_cmd" || "$tests_cmd" == "null" ]]; then
    return 0
  fi
  export THEO_TESTS_RAN="true"
  set +e
  (cd "$THEO_WRITE_ROOT" && bash -lc "$tests_cmd") >"$RUN_DIR/test-output.log" 2>&1
  local rc=$?
  set -e
  if [[ "$rc" -eq 0 ]]; then
    export THEO_TESTS_PASSED="1"
    export THEO_TESTS_FAILED="0"
  else
    export THEO_TESTS_PASSED="0"
    export THEO_TESTS_FAILED="1"
  fi
  return "$rc"
}

theo_materialize_selftest() {
  local worker_name="${1:-$WORKER_NAME}"
  local stamp
  local target="${THEO_SELFTEST_TARGET:-fixtures/shot3-write-target.txt}"
  stamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  theo_write_text "$target" \
    "Shot 3 selftest touched by ${worker_name} at ${stamp}.
This file is edited only inside the dispatch-created worktree during tests.
"

  theo_write_text ".env" "this denied write should not land
" || true
  theo_write_text ".git/config" "this relative git-state write should not land
" || true
  theo_write_text "$THEO_WRITE_ROOT/.git/config" "this absolute git-state write should not land
" || true

  local link_path
  if link_path="$(theo_guard_path "fixtures/git-common-link" "ln")"; then
    mkdir -p "$(dirname "$link_path")"
    rm -f "$link_path"
    ln -s "$(git -C "$THEO_WRITE_ROOT" rev-parse --path-format=absolute --git-common-dir)" "$link_path"
  fi
  theo_write_text "fixtures/git-common-link/config" "this realpath write should not land
" || true

  theo_git push origin HEAD || true
}

theo_finish_result() {
  local status="$1"
  local summary="$2"
  python3 - "$status" "$summary" <<'PY'
import json
import os
import subprocess
import sys
import time
from difflib import unified_diff
from pathlib import Path

status, summary = sys.argv[1:3]
job = json.loads(Path(os.environ["JOB_PATH"]).read_text(encoding="utf-8"))
repo_root = Path(os.environ["REPO_ROOT"]).resolve()
run_dir = Path(os.environ["RUN_DIR"]).resolve()
run_rel = os.environ["RUN_DIR_REL"]
root = Path(os.environ.get("WORKTREE") or os.environ["LANE_PATH"]).resolve()
started = float(os.environ.get("STARTED_EPOCH", time.time()))
worker = os.environ.get("WORKER_NAME", job.get("worker", "unknown"))

def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        try:
            return str(path.resolve().relative_to(run_dir))
        except ValueError:
            return str(path)

def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def git_quote(path_text: str) -> str:
    return path_text.replace("\\", "\\\\").replace('"', '\\"')

def untracked_patch() -> str:
    """Render untracked files without following symlinks into hidden git state."""
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0 or not proc.stdout:
        return ""
    chunks: list[str] = []
    for raw_name in proc.stdout.split(b"\0"):
        if not raw_name:
            continue
        rel_name = raw_name.decode("utf-8", errors="surrogateescape")
        path = root / rel_name
        quoted = git_quote(rel_name)
        if path.is_symlink():
            target = os.readlink(path)
            chunks.append(
                f"diff --git a/{quoted} b/{quoted}\n"
                "new file mode 120000\n"
                "--- /dev/null\n"
                f"+++ b/{quoted}\n"
                "@@ -0,0 +1 @@\n"
                f"+{target}\n"
                "\\ No newline at end of file\n"
            )
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data[:8192]:
            chunks.append(
                f"diff --git a/{quoted} b/{quoted}\n"
                "new file mode 100644\n"
                f"Binary files /dev/null and b/{quoted} differ\n"
            )
            continue
        text = data.decode("utf-8", errors="replace")
        lines = text.splitlines(keepends=True)
        chunks.append(
            f"diff --git a/{quoted} b/{quoted}\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            f"+++ b/{quoted}\n"
            + "".join(unified_diff([], lines, fromfile="/dev/null", tofile=f"b/{rel_name}", lineterm=""))
        )
    return "\n".join(chunks)

branch_proc = run(["git", "branch", "--show-current"])
branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else ""
head_proc = run(["git", "rev-parse", "HEAD"])
head = head_proc.stdout.strip() if head_proc.returncode == 0 else ""
status_proc = run(["git", "status", "--short"])
status_lines = status_proc.stdout.splitlines() if status_proc.returncode == 0 else []
files_touched = []
for line in status_lines:
    if len(line) < 4:
        continue
    path_text = line[3:]
    if " -> " in path_text:
        path_text = path_text.split(" -> ", 1)[1]
    files_touched.append(path_text)

diff_parts: list[str] = []
diff_proc = run(["git", "diff", "--no-ext-diff", "--binary", "--"])
if diff_proc.returncode == 0 and diff_proc.stdout.strip():
    diff_parts.append(diff_proc.stdout)
cached_diff_proc = run(["git", "diff", "--cached", "--no-ext-diff", "--binary", "--"])
if cached_diff_proc.returncode == 0 and cached_diff_proc.stdout.strip():
    diff_parts.append(cached_diff_proc.stdout)
untracked_diff = untracked_patch()
if untracked_diff.strip():
    diff_parts.append(untracked_diff)
diff_text = "\n".join(part.rstrip() for part in diff_parts)
diff_path = run_dir / "diff.patch"
if diff_text.strip():
    diff_path.write_text(diff_text, encoding="utf-8")

transcript_path = run_dir / "transcript.md"
if not transcript_path.exists():
    blocked_count = 0
    blocked_path = run_dir / "blocked.log"
    if blocked_path.exists():
        blocked_count = len([line for line in blocked_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    transcript_path.write_text(
        "# Adapter Transcript\n\n"
        f"worker: {worker}\n"
        f"write_root: {root}\n"
        f"status: {status}\n"
        f"blocked_actions: {blocked_count}\n",
        encoding="utf-8",
    )

artifacts = []
if diff_path.exists():
    artifacts.append({
        "artifact_type": "code",
        "title": "Worktree diff",
        "summary": "Git diff captured from the dispatch-created worktree.",
        "path": f"{run_rel}/diff.patch",
        "preview_kind": "text",
        "worker": worker,
        "source_job": job["job_id"],
        "safe_to_render": True,
    })
blocked_path = run_dir / "blocked.log"
if blocked_path.exists():
    artifacts.append({
        "artifact_type": "data",
        "title": "Denied action log",
        "summary": "JSONL rows for blocked writes or commands.",
        "path": f"{run_rel}/blocked.log",
        "preview_kind": "text",
        "worker": worker,
        "source_job": job["job_id"],
        "safe_to_render": True,
    })
test_output = run_dir / "test-output.log"
if test_output.exists():
    artifacts.append({
        "artifact_type": "report",
        "title": "Raw test output",
        "summary": "Unedited stdout/stderr from the requested verify.tests command.",
        "path": f"{run_rel}/test-output.log",
        "preview_kind": "text",
        "worker": worker,
        "source_job": job["job_id"],
        "safe_to_render": True,
    })

result = {
    "job_id": job["job_id"],
    "status": status,
    "state": "review",
    "summary": summary,
    "diff": f"{run_rel}/diff.patch" if diff_path.exists() else None,
    "files_touched": files_touched,
    "tests": {
        "ran": os.environ.get("THEO_TESTS_RAN", "false") == "true",
        "passed": int(os.environ.get("THEO_TESTS_PASSED", "0")),
        "failed": int(os.environ.get("THEO_TESTS_FAILED", "0")),
    },
    "git": {
        "branch": branch,
        "dirty": bool(status_lines),
        "commits": [head] if head else [],
    },
    "transcript": f"{run_rel}/transcript.md",
    "artifacts": artifacts,
    "memory_proposals": [],
    "followups": [],
    "cost": {
        "tokens": 0,
        "minutes": round((time.time() - started) / 60, 3),
    },
}
(run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}
