#!/usr/bin/env bash
# Theo Agent OS Graphify adapter v0.1.0 - Noted by Theo - 2026-06-09
# Read-only map worker. It copies the lane into temporary scratch before
# Graphify writes graph artifacts, then copies durable outputs into the run.
set -euo pipefail

if ! command -v graphify >/dev/null 2>&1; then
  python3 - <<'PY'
import json, os
from pathlib import Path

run_dir = Path(os.environ["RUN_DIR"])
job = json.loads(Path(os.environ["JOB_PATH"]).read_text())
result = {
  "job_id": job["job_id"],
  "status": "blocked",
  "state": "review",
  "summary": "Graphify CLI is missing. Install graphify before running map jobs.",
  "diff": None,
  "files_touched": [],
  "tests": {"ran": False, "passed": 0, "failed": 0},
  "git": {"branch": "", "dirty": False, "commits": []},
  "transcript": os.environ["RUN_DIR_REL"] + "/transcript.md",
  "artifacts": [],
  "memory_proposals": [],
  "followups": ["Install graphify and rerun the job."],
  "cost": {"tokens": 0, "minutes": 0}
}
(run_dir / "transcript.md").write_text("graphify command not found\n", encoding="utf-8")
(run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
  exit 3
fi

python3 - <<'PY'
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

job = json.loads(Path(os.environ["JOB_PATH"]).read_text())
run_dir = Path(os.environ["RUN_DIR"])
run_rel = os.environ["RUN_DIR_REL"]
lane = Path(os.environ["LANE_PATH"]).resolve()
scratch = Path(tempfile.mkdtemp(prefix=f"theo-agent-os-{job['job_id']}-"))
graph_dir_tmp = scratch / "graphify-out"
graph_dir = run_dir / "graphify-out"
answer_path = run_dir / "graph-answer.md"
transcript_path = run_dir / "transcript.md"
started = float(os.environ.get("STARTED_EPOCH", time.time()))

def ignore(_dir, names):
    return {name for name in names if name in {".git", ".sandbox", "runs", "graphify-out", ".worktrees", "node_modules", "__pycache__"}}

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

shutil.rmtree(scratch)
shutil.copytree(lane, scratch, ignore=ignore)
mirror_dir = scratch / "src_mirror"
mirror_dir.mkdir(exist_ok=True)
for name in ("dispatch", "receipt", "validate"):
    source = scratch / "bin" / name
    if source.exists():
        shutil.copy2(source, mirror_dir / f"{name}.py")

branch_proc = run(["git", "branch", "--show-current"], cwd=lane)
branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else ""
head_proc = run(["git", "rev-parse", "HEAD"], cwd=lane)
head = head_proc.stdout.strip() if head_proc.returncode == 0 else ""

update_proc = run(["graphify", "update", str(scratch)])
transcript = [
    "# Graphify Adapter Transcript",
    "",
    f"lane: {lane}",
    f"scratch: {scratch}",
    "## graphify update stdout",
    update_proc.stdout,
    "## graphify update stderr",
    update_proc.stderr,
]

if update_proc.returncode != 0 or not (graph_dir_tmp / "graph.json").exists():
    transcript_path.write_text("\n".join(transcript), encoding="utf-8")
    result = {
        "job_id": job["job_id"],
        "status": "blocked",
        "state": "review",
        "summary": "Graphify could not build an AST-only graph for this lane; see transcript.",
        "diff": None,
        "files_touched": [],
        "tests": {"ran": False, "passed": 0, "failed": 0},
        "git": {"branch": branch, "dirty": False, "commits": [head] if head else []},
        "transcript": f"{run_rel}/transcript.md",
        "artifacts": [],
        "memory_proposals": [],
        "followups": ["Inspect adapter.stderr.log and graphify installation."],
        "cost": {"tokens": 0, "minutes": round((time.time() - started) / 60, 3)}
    }
    (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(3)

if graph_dir.exists():
    shutil.rmtree(graph_dir)
shutil.copytree(graph_dir_tmp, graph_dir)
(graph_dir / ".head").write_text(head + "\n", encoding="utf-8")
task = job["task"]
question = "Summarize this repo and its load-bearing files." if task == "summary" else task
query_proc = run(["graphify", "query", question, "--graph", str(graph_dir / "graph.json")])
transcript.extend([
    "## graphify query stdout",
    query_proc.stdout,
    "## graphify query stderr",
    query_proc.stderr,
])
answer = query_proc.stdout.strip() or query_proc.stderr.strip() or "Graphify returned no answer."
answer_path.write_text(
    "# Graphify Answer\n\n"
    f"Question: {question}\n\n"
    "## Answer\n\n"
    f"{answer}\n\n"
    "## Generated Graph\n\n"
    f"- graph: {graph_dir / 'graph.json'}\n"
    f"- head: {head or '(unknown)'}\n",
    encoding="utf-8",
)
transcript_path.write_text("\n".join(transcript), encoding="utf-8")
status = "success" if query_proc.returncode == 0 else "partial"
summary = "Graphify built a run-local repo graph and answered the map request. Target repo files were not changed."
if query_proc.returncode != 0:
    summary = "Graphify built a run-local graph, but the query returned warnings or errors; see graph-answer.md."
result = {
    "job_id": job["job_id"],
    "status": status,
    "state": "review",
    "summary": summary,
    "diff": None,
    "files_touched": [],
    "tests": {"ran": False, "passed": 0, "failed": 0},
    "git": {"branch": branch, "dirty": False, "commits": [head] if head else []},
    "transcript": f"{run_rel}/transcript.md",
    "artifacts": [
        {
            "artifact_type": "report",
            "title": "Graphify map answer",
            "summary": "Full Graphify answer plus generated graph location.",
            "path": f"{run_rel}/graph-answer.md",
            "preview_kind": "text",
            "worker": "graphify",
            "source_job": job["job_id"],
            "safe_to_render": True
        },
        {
            "artifact_type": "data",
            "title": "Run-local graph.json",
            "summary": "Graph generated in temporary scratch and copied into this run.",
            "path": f"{run_rel}/graphify-out/graph.json",
            "preview_kind": "none",
            "worker": "graphify",
            "source_job": job["job_id"],
            "safe_to_render": False
        }
    ],
    "memory_proposals": [],
    "followups": [],
    "cost": {"tokens": 0, "minutes": round((time.time() - started) / 60, 3)}
}
(run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
shutil.rmtree(scratch, ignore_errors=True)
PY
