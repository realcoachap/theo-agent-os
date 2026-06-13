#!/usr/bin/env python3
"""Theo Agent OS Glass Control proxy regression v0.1.0 - Noted by Theo ☠️ - 2026-06-13.

Proves the v0.5.1 `/control/` proxy keeps the Spartacus OpenClaw Control UI
reachable through Glass without creating a new Railway resource:
- `/control/` proxies the gateway HTML,
- `/control/assets/*` strips the `/control` prefix and forwards assets,
- the `/control` WebSocket upgrade tunnels cleanly,
- and Glass admin cookies are not forwarded to the upstream gateway.
"""

from __future__ import annotations

import base64
import hashlib
import os
import socket
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
GLASS = REPO_ROOT / "bin" / "glass"
REQUESTS: list[tuple[str, dict[str, str]]] = []


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class FakeGatewayHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        request_line = self.rfile.readline().decode("utf-8", errors="replace").strip()
        headers: dict[str, str] = {}
        while True:
            line = self.rfile.readline().decode("utf-8", errors="replace")
            if line in {"\r\n", "\n", ""}:
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()

        path = request_line.split(" ")[1]
        REQUESTS.append((path, headers))

        if headers.get("upgrade", "").lower() == "websocket":
            accept = base64.b64encode(
                hashlib.sha1((headers["sec-websocket-key"] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()
            ).decode("ascii")
            self.wfile.write(
                (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                ).encode("ascii")
            )
            return

        if path == "/assets/app.js":
            body = b"console.log('control asset');\n"
            content_type = "application/javascript"
        else:
            body = b"<!doctype html><title>OpenClaw Control</title>\n"
            content_type = "text/html; charset=utf-8"

        self.wfile.write(
            (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Cache-Control: no-store\r\n\r\n"
            ).encode("ascii")
            + body
        )


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


def read_url(url: str, *, cookie: str | None = None) -> str:
    request = urllib.request.Request(url, headers={"Cookie": cookie} if cookie else {})
    return urllib.request.urlopen(request, timeout=2).read().decode("utf-8")


def websocket_probe(host: str, port: int) -> str:
    key = base64.b64encode(b"glass-control-proxy").decode("ascii")
    request = (
        "GET /control HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Connection: Upgrade\r\n"
        "Upgrade: websocket\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Origin: http://127.0.0.1\r\n"
        "Cookie: theo_glass_admin=do-not-forward\r\n\r\n"
    )
    with socket.create_connection((host, port), timeout=2) as sock:
        sock.sendall(request.encode("ascii"))
        return sock.recv(4096).decode("utf-8", errors="replace")


def main() -> int:
    REQUESTS.clear()
    fake_port = free_port()
    fake_gateway = socketserver.ThreadingTCPServer(("127.0.0.1", fake_port), FakeGatewayHandler)
    fake_gateway.daemon_threads = True
    fake_thread = threading.Thread(target=fake_gateway.serve_forever, daemon=True)
    fake_thread.start()

    glass_port = free_port()
    proc = subprocess.Popen(
        [PYTHON, str(GLASS), "--host", "127.0.0.1", "--port", str(glass_port)],
        cwd=REPO_ROOT,
        env={
            **os.environ,
            "THEO_GLASS_CONTROL_PROXY_HOST": "127.0.0.1",
            "THEO_GLASS_CONTROL_PROXY_PORT": str(fake_port),
        },
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    base_url = f"http://127.0.0.1:{glass_port}"
    try:
        wait_for_glass(base_url, proc)
        html = read_url(base_url + "/control/", cookie="theo_glass_admin=do-not-forward")
        assert_true("OpenClaw Control" in html, "/control/ did not return gateway HTML")
        asset = read_url(base_url + "/control/assets/app.js", cookie="theo_glass_admin=do-not-forward")
        assert_true("control asset" in asset, "/control/assets/* did not proxy the asset")
        upgrade = websocket_probe("127.0.0.1", glass_port)
        assert_true("101 Switching Protocols" in upgrade, "/control WebSocket did not upgrade")
        assert_true(REQUESTS[0][0] == "/", "control root was not stripped to upstream root")
        assert_true(REQUESTS[1][0] == "/assets/app.js", "control asset path was not stripped correctly")
        assert_true(REQUESTS[2][0] == "/", "control websocket path was not stripped to upstream root")
        for _path, headers in REQUESTS:
            assert_true("cookie" not in headers, "Glass admin cookie leaked to the Control proxy target")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
        fake_gateway.shutdown()
        fake_gateway.server_close()
    print("glass control proxy regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
