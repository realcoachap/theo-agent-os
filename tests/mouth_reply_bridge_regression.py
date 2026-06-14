#!/usr/bin/env python3
"""Theo Agent OS Mouth reply bridge regression v0.1.0 - Noted by Theo - 2026-06-14.

Proves queued Glass reply payloads are sent through the OpenClaw CLI shape and
marked sent, while the bridge does nothing without explicit queued payloads.
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
BRIDGE = REPO_ROOT / "bin" / "mouth-reply-bridge"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class ReplyBridgeHandler(BaseHTTPRequestHandler):
    pending: list[dict[str, Any]] = []
    marks: list[dict[str, Any]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        if self.path == "/api/mouth/pending-replies":
            response = {"ok": True, "pending": self.__class__.pending, "errors": []}
        elif self.path == "/api/mouth/reply-sent":
            self.__class__.marks.append({
                "authorization": self.headers.get("Authorization", ""),
                "payload": payload,
            })
            response = {"ok": True, "sent": {"status": "sent", "message_id": payload.get("message_id")}}
        else:
            response = {"ok": False, "error": "unknown path"}
            self.send_response(404)
            raw = json.dumps(response).encode("utf-8")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        raw = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def run_bridge(args: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    merged_env = dict(os.environ)
    merged_env.update(env)
    return subprocess.run(
        [PYTHON, str(BRIDGE), *args],
        cwd=REPO_ROOT,
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_fake_openclaw(path: Path, args_path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"open({str(args_path)!r}, 'w', encoding='utf-8').write(json.dumps(sys.argv[1:]))\n"
        "print(json.dumps({'ok': True, 'messageId': 'telegram-message-123'}))\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def assert_reply_bridge_sends_and_marks() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        state = root / "reply-state.json"
        fake_openclaw = root / "fake-openclaw"
        args_path = root / "openclaw-args.json"
        write_fake_openclaw(fake_openclaw, args_path)
        ReplyBridgeHandler.pending = [{
            "command_id": "reply-command-1",
            "payload": {
                "action": "send",
                "target": "telegram:7148548566",
                "message": "queued reply smoke",
            },
        }]
        ReplyBridgeHandler.marks = []
        server = HTTPServer(("127.0.0.1", 0), ReplyBridgeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            glass_url = f"http://127.0.0.1:{server.server_port}"
            proc = run_bridge([
                "--glass-url", glass_url,
                "--state", str(state),
                "--message-command", str(fake_openclaw),
                "--json",
            ], env={"THEO_GLASS_MOUTH_INGEST_SECRET": "reply-secret"})
            assert_true(proc.returncode == 0, f"reply bridge failed: {proc.stderr or proc.stdout}")
            result = json.loads(proc.stdout)
            assert_true(result["sent"] == 1 and result["pending"] == 1, f"unexpected bridge result: {result}")
            cli_args = json.loads(args_path.read_text(encoding="utf-8"))
            assert_true(cli_args[:4] == ["message", "send", "--channel", "telegram"], f"wrong OpenClaw CLI prefix: {cli_args}")
            assert_true("--target" in cli_args and cli_args[cli_args.index("--target") + 1] == "7148548566", "reply bridge did not strip telegram target prefix")
            assert_true("--message" in cli_args and cli_args[cli_args.index("--message") + 1] == "queued reply smoke", "reply bridge sent wrong message text")
            assert_true(len(ReplyBridgeHandler.marks) == 1, "reply bridge did not mark Glass sent")
            mark = ReplyBridgeHandler.marks[0]
            assert_true(mark["authorization"] == "Bearer reply-secret", "reply bridge did not use runtime bearer auth")
            assert_true(mark["payload"]["command_id"] == "reply-command-1" and mark["payload"]["message_id"] == "telegram-message-123", "reply bridge marked wrong delivery")
        finally:
            server.shutdown()
            server.server_close()
    print("ok: Mouth reply bridge sends queued payload and marks sent")


def main() -> int:
    assert_reply_bridge_sends_and_marks()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
