#!/usr/bin/env python3
"""Theo Agent OS Glass live-sync regression v0.1.0 - Noted by Theo - 2026-06-13.

Proves the v0.5.0 admin-door live-state sync stays honest:
- the embedded app JS parses (a syntax error there bricks the whole panel),
- the served shell exposes the sync indicator, Refresh, and Live/Pause controls,
- /api/state still serves a well-formed snapshot,
- and the old unconditional `setInterval(loadState, 3000)` clobber loop does not
  creep back in (it was the bug that wiped open run details every 3s).

WHY a regression test: live sync touches the one screen Coach watches Theo OS
through. The clobber loop is an easy thing to "helpfully" reintroduce; this nails
it shut.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
GLASS = REPO_ROOT / "bin" / "glass"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main_app_script() -> str:
    """Return the main front-end <script> block (the one with the app logic)."""
    src = GLASS.read_text(encoding="utf-8")
    blocks = re.findall(r"<script>(.*?)</script>", src, re.S)
    for block in blocks:
        if "function loadState" in block and "stateSignature" in block:
            return block
    raise AssertionError("could not locate the main Glass app script block")


def assert_app_js_parses() -> None:
    if not shutil.which("node"):
        print("ok: skipped JS parse check (node not on PATH)")
        return
    script = main_app_script()
    tmp = REPO_ROOT / "runs" / ".glass-live-sync-jscheck.js"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(script, encoding="utf-8")
    try:
        proc = subprocess.run(
            ["node", "--check", str(tmp)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        assert_true(proc.returncode == 0, f"Glass app JS failed to parse: {proc.stderr or proc.stdout}")
    finally:
        tmp.unlink(missing_ok=True)
    print("ok: Glass app JS parses cleanly")


def assert_no_clobber_loop() -> None:
    """The old `setInterval(loadState, 3000)` re-rendered unconditionally and
    wiped any open detail. v0.5.0 replaced it with visibility-aware, signature-
    gated polling via syncTick/startPolling. Guard against the clobber returning.
    """
    src = GLASS.read_text(encoding="utf-8")
    assert_true("setInterval(loadState," not in src,
                "unconditional setInterval(loadState, ...) clobber loop is back")
    for token in ("interactionLock", "stateSignature", "function startPolling", "function syncTick"):
        assert_true(token in src, f"expected live-sync token missing: {token}")
    print("ok: clobber loop stays gone; live-sync scaffolding present")


def assert_login_preserves_deep_links() -> None:
    """Control UI links carry token fragments, so login must not drop the URL."""
    src = GLASS.read_text(encoding="utf-8")
    assert_true('const next = window.location.pathname === "/login" ? "/" : window.location.href;' in src,
                "admin login no longer preserves deep links")
    assert_true("if (res.ok) window.location = next;" in src,
                "admin login success path does not use the preserved target")
    print("ok: admin login preserves deep links")


def wait_for_glass(base_url: str, proc: subprocess.Popen[str]) -> None:
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            raise AssertionError(f"Glass exited early:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        try:
            urllib.request.urlopen(base_url + "/", timeout=1).read()
            return
        except Exception:
            time.sleep(0.1)
    raise AssertionError("Glass server did not become ready")


def assert_shell_and_state() -> None:
    port = free_port()
    proc = subprocess.Popen(
        [PYTHON, str(GLASS), "--host", "127.0.0.1", "--port", str(port)],
        cwd=REPO_ROOT,
        env=dict(os.environ),
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        wait_for_glass(base_url, proc)
        html = urllib.request.urlopen(base_url + "/", timeout=2).read().decode("utf-8")
        for marker in ('id="sync-status"', 'id="refresh-btn"', 'id="live-btn"'):
            assert_true(marker in html, f"served shell is missing live-sync control {marker}")
        body = urllib.request.urlopen(base_url + "/api/state", timeout=2).read().decode("utf-8")
        snapshot = json.loads(body)
        for key in ("generated_at", "runs", "mouth", "security", "writes_enabled", "admin"):
            assert_true(key in snapshot, f"/api/state snapshot missing key: {key}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
    print("ok: served shell exposes sync controls and /api/state serves a snapshot")


def main() -> int:
    assert_app_js_parses()
    assert_no_clobber_loop()
    assert_login_preserves_deep_links()
    assert_shell_and_state()
    print("glass live-sync regressions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
