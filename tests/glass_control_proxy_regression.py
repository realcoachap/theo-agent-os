#!/usr/bin/env python3
"""Theo Agent OS Glass Control proxy regression v0.2.0 - Noted by Theo ☠️ - 2026-06-13.

Proves the v0.5.3 node-registry proxy keeps the Spartacus OpenClaw Control UI
reachable without becoming an arbitrary tunnel:
- legacy `/control/` and canonical `/control/spartacus/` proxy gateway HTML,
- asset paths strip either `/control` or `/control/spartacus` correctly,
- WebSocket upgrades tunnel on both compatibility and node routes,
- Glass admin cookies/Authorization are not forwarded to the gateway,
- upstream Set-Cookie headers are not forwarded back onto the Glass origin,
- and unknown node-looking routes fail closed.
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
import urllib.error
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
                "Set-Cookie: upstream=must-not-leak; Path=/\r\n"
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


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001 - stdlib hook signature
        return None


def read_url(
    url: str,
    *,
    cookie: str | None = None,
    authorization: str | None = None,
    follow_redirects: bool = True,
) -> tuple[int, str, dict[str, str]]:
    headers = {}
    if cookie:
        headers["Cookie"] = cookie
    if authorization:
        headers["Authorization"] = authorization
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener() if follow_redirects else urllib.request.build_opener(NoRedirect)
    try:
        response = opener.open(request, timeout=2)
        return response.status, response.read().decode("utf-8"), {key.lower(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8"), {key.lower(): value for key, value in exc.headers.items()}


def websocket_probe(host: str, port: int, path: str) -> str:
    key = base64.b64encode(b"glass-control-proxy").decode("ascii")
    request = (
        f"GET {path} HTTP/1.1\r\n"
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
        status, _body, headers = read_url(base_url + "/control", follow_redirects=False)
        assert_true(status == 302, "/control did not redirect to /control/")
        assert_true(headers.get("location") == "/control/", "/control redirect did not target /control/")
        status, _body, headers = read_url(base_url + "/control/spartacus?x=1", follow_redirects=False)
        assert_true(status == 302, "/control/spartacus did not redirect to /control/spartacus/")
        assert_true(headers.get("location") == "/control/spartacus/?x=1", "node redirect did not preserve query string")

        status, html, headers = read_url(
            base_url + "/control/",
            cookie="theo_glass_admin=do-not-forward",
            authorization="Bearer glass-only",
        )
        assert_true(status == 200, "/control/ did not return 200")
        assert_true("OpenClaw Control" in html, "/control/ did not return gateway HTML")
        assert_true("set-cookie" not in headers, "upstream Set-Cookie leaked through legacy route")

        status, asset, _headers = read_url(base_url + "/control/assets/app.js", cookie="theo_glass_admin=do-not-forward")
        assert_true(status == 200, "/control/assets/* did not return 200")
        assert_true("control asset" in asset, "/control/assets/* did not proxy the asset")

        status, html, headers = read_url(base_url + "/control/spartacus/?x=1", cookie="theo_glass_admin=do-not-forward")
        assert_true(status == 200, "/control/spartacus/ did not return 200")
        assert_true("OpenClaw Control" in html, "/control/spartacus/ did not return gateway HTML")
        assert_true("set-cookie" not in headers, "upstream Set-Cookie leaked through node route")

        status, asset, _headers = read_url(base_url + "/control/spartacus/assets/app.js", cookie="theo_glass_admin=do-not-forward")
        assert_true(status == 200, "/control/spartacus/assets/* did not return 200")
        assert_true("control asset" in asset, "/control/spartacus/assets/* did not proxy the asset")

        status, body, _headers = read_url(base_url + "/control/notreal/")
        assert_true(status == 404 and "unknown control node" in body, "unknown control node did not fail closed")
        status, body, _headers = read_url(base_url + "/control/spartacusish/")
        assert_true(status == 404 and "unknown control node" in body, "prefix collision did not fail closed")

        upgrade = websocket_probe("127.0.0.1", glass_port, "/control")
        assert_true("101 Switching Protocols" in upgrade, "/control WebSocket did not upgrade")
        upgrade = websocket_probe("127.0.0.1", glass_port, "/control/spartacus")
        assert_true("101 Switching Protocols" in upgrade, "/control/spartacus WebSocket did not upgrade")

        assert_true(REQUESTS[0][0] == "/", "control root was not stripped to upstream root")
        assert_true(REQUESTS[1][0] == "/assets/app.js", "control asset path was not stripped correctly")
        assert_true(REQUESTS[2][0] == "/?x=1", "node route query string was not preserved")
        assert_true(REQUESTS[3][0] == "/assets/app.js", "node asset path was not stripped correctly")
        assert_true(REQUESTS[4][0] == "/", "control websocket path was not stripped to upstream root")
        assert_true(REQUESTS[5][0] == "/", "node websocket path was not stripped to upstream root")
        for _path, headers in REQUESTS:
            assert_true("cookie" not in headers, "Glass admin cookie leaked to the Control proxy target")
            assert_true("authorization" not in headers, "Glass Authorization leaked to the Control proxy target")
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
