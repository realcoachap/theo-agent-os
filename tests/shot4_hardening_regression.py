#!/usr/bin/env python3
"""Theo Agent OS Shot 4 hardening regression v0.1.0 - Noted by Theo - 2026-06-10.

Proves the Clawd/Fable carry-overs that should stay true before live bot
wiring expands: test-channel Mouth events are not trusted by accident, the
runtime sender guard blocks forged/untrusted replies, and the Railway admin
login throttles repeated failures.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
MOUTH_INDEX = REPO_ROOT / "runs" / "mouth-index.jsonl"


def run(cmd: list[str], *, env: dict[str, str] | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env=merged_env,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def cleanup_command(command_id: str) -> None:
    shutil.rmtree(REPO_ROOT / "jobs" / "inbox" / command_id, ignore_errors=True)
    shutil.rmtree(REPO_ROOT / "jobs" / "outbox" / command_id, ignore_errors=True)


def restore_mouth_index(original: str | None) -> None:
    if original is None:
        try:
            MOUTH_INDEX.unlink()
        except FileNotFoundError:
            pass
    else:
        MOUTH_INDEX.parent.mkdir(parents=True, exist_ok=True)
        MOUTH_INDEX.write_text(original, encoding="utf-8")


def test_event(channel: str = "test") -> dict[str, object]:
    return {
        "version": "0.1.0",
        "channel": channel,
        "chat_id": "test-chat",
        "message_id": "test-message",
        "sender_id": "test-sender",
        "sender": {"label": "Shot 4 hardening test"},
        "timestamp": "2026-06-10T18:00:00Z",
        "text": "/theo compile this as a draft only",
    }


def mouth_openclaw_record(*extra_args: str) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(test_event(), handle)
        handle.write("\n")
        event_path = Path(handle.name)
    try:
        proc = run([PYTHON, "bin/mouth-openclaw", "--event", str(event_path), "--json", *extra_args])
    finally:
        event_path.unlink(missing_ok=True)
    assert_true(proc.returncode == 0, f"mouth-openclaw failed: {proc.stderr or proc.stdout}")
    record = json.loads(proc.stdout)
    cleanup_command(record["command_id"])
    return record


def assert_test_channel_trust_guard() -> None:
    original_index = MOUTH_INDEX.read_text(encoding="utf-8") if MOUTH_INDEX.exists() else None
    try:
        untrusted = mouth_openclaw_record()
        assert_true(untrusted["source"]["trusted"] is False, "channel=test was trusted without an explicit fixture flag")
        trusted = mouth_openclaw_record("--allow-test-trust")
        assert_true(trusted["source"]["trusted"] is True, "--allow-test-trust did not trust the fixture event")
    finally:
        restore_mouth_index(original_index)
    print("ok: test-channel Mouth trust requires explicit fixture flag")


def command_payload(command_id: str, *, channel: str = "telegram", trusted: bool = True, target: str = "111111") -> dict[str, object]:
    return {
        "command_id": command_id,
        "source": {
            "channel": channel,
            "chat_id": target,
            "message_id": "msg-1",
            "sender_id": "sender-1",
            "sender_label": "Shot 4 regression",
            "trusted": trusted,
            "received_at": "2026-06-10T18:00:00Z",
        },
        "execution": {"mode": "draft"},
        "lane": "self",
        "intent": "patch",
        "worker": "claude",
        "model_profile": "default",
        "task": "Regression fixture command.",
        "context": {"agents_md": True, "blast_radius": "Fixture only."},
        "permissions": {"tier": "read_only", "write": [], "deny": [".env*", "secrets/**"], "network": False, "git_push": False},
        "verify_profile": "none",
        "budget": {"max_minutes": 1, "max_tokens": 1000},
        "approvals": {"operator": trusted, "write": False, "spend": False},
        "delivery": {"reply": "receipt_text", "target": target},
    }


def reply_payload(command_id: str, *, channel: str = "telegram", target: str = "111111", result_path: str = "") -> dict[str, object]:
    return {
        "version": "0.4.1",
        "noted_by": "Theo",
        "created_at": "2026-06-10T18:00:00Z",
        "command_id": command_id,
        "job_id": command_id,
        "channel": channel,
        "target": target,
        "ok": True,
        "exit_code": 0,
        "result_path": result_path,
        "text": "Regression fixture reply.",
    }


def write_sender_fixture(command_id: str, *, channel: str = "telegram", trusted: bool = True, target: str = "111111") -> Path:
    inbox = REPO_ROOT / "jobs" / "inbox" / command_id
    outbox = REPO_ROOT / "jobs" / "outbox" / command_id
    cleanup_command(command_id)
    write_json(inbox / "command.json", command_payload(command_id, channel=channel, trusted=trusted, target=target))
    write_json(outbox / "reply.json", reply_payload(command_id, channel=channel, target=target, result_path=f"jobs/inbox/{command_id}/command.json"))
    return outbox / "reply.json"


def assert_sender_guard_regressions() -> None:
    valid_id = "55555555-5555-4555-8555-555555555555"
    forged_id = "66666666-6666-4666-8666-666666666666"
    untrusted_id = "77777777-7777-4777-8777-777777777777"
    test_id = "88888888-8888-4888-8888-888888888888"
    try:
        valid_reply = write_sender_fixture(valid_id)
        proc = run([PYTHON, "bin/mouth-send-reply", str(valid_reply)])
        assert_true(proc.returncode == 0 and "ready:" in proc.stdout, f"valid reply was not ready: {proc.stderr or proc.stdout}")

        forged_reply = write_sender_fixture(forged_id)
        forged_data = json.loads(forged_reply.read_text(encoding="utf-8"))
        forged_data["target"] = "999999"
        write_json(forged_reply, forged_data)
        proc = run([PYTHON, "bin/mouth-send-reply", str(forged_reply)])
        assert_true(proc.returncode == 3 and "reply target does not match" in proc.stderr, "forged target was not blocked")

        untrusted_reply = write_sender_fixture(untrusted_id, trusted=False)
        proc = run([PYTHON, "bin/mouth-send-reply", str(untrusted_reply)])
        assert_true(proc.returncode == 3 and "original command source was not trusted" in proc.stderr, "untrusted source was not blocked")

        test_reply = write_sender_fixture(test_id, channel="test", target="fixture-target")
        proc = run([PYTHON, "bin/mouth-send-reply", str(test_reply)])
        assert_true(proc.returncode == 3 and "test-channel delivery requires --allow-test" in proc.stderr, "test reply was allowed without --allow-test")
        proc = run([PYTHON, "bin/mouth-send-reply", str(test_reply), "--allow-test"])
        assert_true(proc.returncode == 0, f"explicit test reply was blocked: {proc.stderr or proc.stdout}")
    finally:
        for command_id in (valid_id, forged_id, untrusted_id, test_id):
            cleanup_command(command_id)
    print("ok: sender guard blocks forged, untrusted, and implicit test replies")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def post_json(url: str, payload: dict[str, object], *, forwarded_for: str) -> tuple[int, str, dict[str, str]]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "X-Forwarded-For": forwarded_for},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, response.read().decode("utf-8"), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8"), dict(exc.headers.items())


def wait_for_glass(base_url: str, proc: subprocess.Popen[str]) -> None:
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            raise AssertionError(f"Glass exited early:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        try:
            urllib.request.urlopen(base_url + "/login", timeout=1).read()
            return
        except Exception:
            time.sleep(0.1)
    raise AssertionError("Glass admin server did not become ready")


def assert_admin_login_throttle() -> None:
    password_hash = run([PYTHON, "bin/glass", "--hash-admin-password"], input_text="correct-password\n")
    assert_true(password_hash.returncode == 0, f"password hash failed: {password_hash.stderr}")
    port = free_port()
    env = {
        "THEO_GLASS_ADMIN_USER": "coach",
        "THEO_GLASS_ADMIN_PASSWORD_HASH": password_hash.stdout.strip(),
        "THEO_GLASS_ADMIN_SESSION_SECRET": "shot4-regression-session-secret",
        "THEO_GLASS_ADMIN_LOGIN_MAX_FAILURES": "2",
        "THEO_GLASS_ADMIN_LOGIN_WINDOW_SECONDS": "60",
    }
    proc = subprocess.Popen(
        [PYTHON, "bin/glass", "--host", "127.0.0.1", "--port", str(port), "--remote-admin"],
        cwd=REPO_ROOT,
        env={**os.environ, **env},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        wait_for_glass(base_url, proc)
        for _ in range(2):
            status, _body, _headers = post_json(base_url + "/api/login", {"user": "coach", "password": "bad"}, forwarded_for="203.0.113.10")
            assert_true(status == 401, f"bad login should return 401 before throttle, got {status}")
        status, body, headers = post_json(base_url + "/api/login", {"user": "coach", "password": "bad"}, forwarded_for="203.0.113.10")
        assert_true(status == 429 and "Retry-After" in headers and "too many failed" in body, f"throttled login did not return 429: {status} {body}")
        status, _body, headers = post_json(base_url + "/api/login", {"user": "coach", "password": "correct-password"}, forwarded_for="203.0.113.11")
        assert_true(status == 200 and "Set-Cookie" in headers, f"good login from a clean client failed: {status}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    print("ok: admin login throttles repeated failures")


def main() -> int:
    assert_test_channel_trust_guard()
    assert_sender_guard_regressions()
    assert_admin_login_throttle()
    print("shot4 hardening regressions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
