#!/usr/bin/env python3
"""Theo Agent OS Mouth session bridge regression v0.1.0 - Noted by Theo - 2026-06-14.

Proves the local OpenClaw session bridge mirrors only Telegram user turns,
bootstraps without backfilling whole history, sends the Glass ingest bearer
header, and records dedupe state after a successful post.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
BRIDGE = REPO_ROOT / "bin" / "mouth-session-bridge"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def session_record(record_id: str, role: str, content: str, *, source: str = "telegram", sender_id: str = "7148548566") -> dict[str, Any]:
    message: dict[str, Any] = {"role": role, "content": content}
    if role == "user":
        message.update({
            "timestamp": 1781410606000,
            "sourceChannel": source,
            "senderId": sender_id,
            "senderName": "A P",
            "senderLabel": "A P (7148548566)",
        })
    return {
        "type": "message",
        "id": record_id,
        "timestamp": "2026-06-14T04:16:48.147Z",
        "message": message,
    }


def write_session_fixture(root: Path) -> tuple[Path, Path, str]:
    session_key = "agent:main:telegram:direct:7148548566"
    session_file = root / "session.jsonl"
    rows = [
        session_record("old-user", "user", "older user turn"),
        session_record("assistant-row", "assistant", "assistant output"),
        session_record("other-channel", "user", "webchat user turn", source="webchat"),
        session_record("latest-user", "user", "latest user turn"),
    ]
    session_file.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    session_store = root / "sessions.json"
    write_json(session_store, {session_key: {"sessionFile": str(session_file)}})
    return session_store, session_file, session_key


class CaptureHandler(BaseHTTPRequestHandler):
    captures: list[dict[str, Any]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        self.__class__.captures.append({
            "path": self.path,
            "authorization": self.headers.get("Authorization", ""),
            "payload": payload,
        })
        response = {
            "ok": True,
            "record": {"command_id": "99999999-9999-4999-8999-999999999999"},
        }
        raw = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def run_bridge(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    return subprocess.run(
        [PYTHON, str(BRIDGE), *args],
        cwd=REPO_ROOT,
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def assert_bridge_posts_latest_and_dedupes() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        session_store, _session_file, session_key = write_session_fixture(root)
        state = root / "bridge-state.json"
        server = HTTPServer(("127.0.0.1", 0), CaptureHandler)
        CaptureHandler.captures = []
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            glass_url = f"http://127.0.0.1:{server.server_port}"
            proc = run_bridge([
                "--session-store", str(session_store),
                "--session-key", session_key,
                "--state", str(state),
                "--glass-url", glass_url,
                "--backfill-latest", "1",
                "--json",
            ], env={"THEO_GLASS_MOUTH_INGEST_SECRET": "bridge-secret"})
            assert_true(proc.returncode == 0, f"bridge failed: {proc.stderr or proc.stdout}")
            result = json.loads(proc.stdout)
            assert_true(result["posted"] == 1, f"expected one posted event: {result}")
            assert_true(len(CaptureHandler.captures) == 1, "bridge did not post exactly one event")
            capture = CaptureHandler.captures[0]
            assert_true(capture["path"] == "/api/mouth/ingest", f"wrong ingest path: {capture['path']}")
            assert_true(capture["authorization"] == "Bearer bridge-secret", "missing Glass ingest bearer token")
            event = capture["payload"]["event"]
            assert_true(event["message_id"] == "latest-user", "first run should post only the latest user turn")
            assert_true(event["chat_id"] == "telegram:7148548566", "bridge did not normalize Telegram chat target")

            state_data = json.loads(state.read_text(encoding="utf-8"))
            assert_true("old-user" in state_data["seen"] and "latest-user" in state_data["seen"], "bridge state did not mark baseline and posted rows seen")

            proc = run_bridge([
                "--session-store", str(session_store),
                "--session-key", session_key,
                "--state", str(state),
                "--glass-url", glass_url,
                "--backfill-latest", "1",
                "--json",
            ], env={"THEO_GLASS_MOUTH_INGEST_SECRET": "bridge-secret"})
            assert_true(proc.returncode == 0, f"second bridge run failed: {proc.stderr or proc.stdout}")
            second = json.loads(proc.stdout)
            assert_true(second["posted"] == 0 and len(CaptureHandler.captures) == 1, "bridge reposted a seen user turn")
        finally:
            server.shutdown()
            server.server_close()
    print("ok: Mouth session bridge posts latest user turn once and dedupes")


def main() -> int:
    assert_bridge_posts_latest_and_dedupes()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
