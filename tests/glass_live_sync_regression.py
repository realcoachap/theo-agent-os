#!/usr/bin/env python3
"""Theo Agent OS Glass live-sync regression v0.2.1 - Noted by Theo - 2026-06-14.

Proves the v0.5.0 admin-door live-state sync stays honest:
- the embedded app JS parses (a syntax error there bricks the whole panel),
- the served shell exposes the sync indicator, Refresh, and Live/Pause controls,
- the Mission Control cockpit shell markers are present,
- the mobile cockpit keeps a bottom nav and More sheet available without the
  desktop rail,
- /api/state still serves a well-formed snapshot,
- the first cockpit-native Spartacus refresh action writes a visible receipt,
- the live Telegram-to-Mouth bridge compiles a trusted event into a draft only,
- the Glass Mouth lifecycle gate writes approve/hold/reject receipts without dispatch,
- approved Mouth commands can receive a schema-valid, sender-guard-compatible
  outbound reply draft,
- the guarded reply payload / sent-marker handoff records delivery without
  Glass sending Telegram directly,
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
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
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


def request_json(url: str, payload: dict[str, object], headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        response = urllib.request.urlopen(request, timeout=8)
        return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


class TeamWebhookHandler(BaseHTTPRequestHandler):
    posts: list[dict[str, object]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        payload = json.loads(body)
        self.__class__.posts.append({
            "path": self.path,
            "payload": payload,
        })
        raw = b"ok"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, _format: str, *_args: object) -> None:
        return


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
    receipt_path = REPO_ROOT / "runs" / ".test-control-receipts.jsonl"
    mouth_verdicts_path = REPO_ROOT / "runs" / ".test-mouth-verdicts.jsonl"
    team_receipts_path = REPO_ROOT / "runs" / ".test-team-room-receipts.jsonl"
    mouth_index = REPO_ROOT / "runs" / "mouth-index.jsonl"
    original_mouth_index = mouth_index.read_text(encoding="utf-8") if mouth_index.exists() else None
    ingested_command_id = ""
    receipt_path.unlink(missing_ok=True)
    mouth_verdicts_path.unlink(missing_ok=True)
    team_receipts_path.unlink(missing_ok=True)
    TeamWebhookHandler.posts = []
    webhook_server = HTTPServer(("127.0.0.1", 0), TeamWebhookHandler)
    webhook_thread = threading.Thread(target=webhook_server.serve_forever, daemon=True)
    webhook_thread.start()
    proc = subprocess.Popen(
        [PYTHON, str(GLASS), "--host", "127.0.0.1", "--port", str(port)],
        cwd=REPO_ROOT,
        env={
            **os.environ,
            "THEO_GLASS_CONTROL_RECEIPTS_PATH": str(receipt_path),
            "THEO_GLASS_MOUTH_VERDICTS_PATH": str(mouth_verdicts_path),
            "THEO_GLASS_TEAM_ROOM_RECEIPTS_PATH": str(team_receipts_path),
            "THEO_GLASS_TEAM_ROOM_WEBHOOK_URL": f"http://127.0.0.1:{webhook_server.server_port}/hooks/glass-test",
            "THEO_GLASS_TEAM_ROOM_RECEIPT_SECRET": "team-receipt-secret",
            "THEO_GLASS_MOUTH_INGEST_SECRET": "shot4-ingest-secret",
            "THEO_GLASS_MOUTH_TRUSTED_TELEGRAM_IDS": "7148548566",
            "THEO_TRUSTED_TELEGRAM_IDS": "7148548566",
        },
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        wait_for_glass(base_url, proc)
        html = urllib.request.urlopen(base_url + "/", timeout=2).read().decode("utf-8")
        for marker in (
            'id="sync-status"',
            'id="refresh-btn"',
            'id="live-btn"',
            'id="mobile-bottom-nav"',
            'id="mobile-more-panel"',
            'id="mobile-more-grid"',
            '"Control"',
            'Theo OS',
            'Mission Control',
            'mission-control',
            'Mission Details',
            'Mouth gates write receipts only',
            'Open Agent Room',
            'Open Team Room',
            'Team Rooms',
            'Team Receipts',
            'team-room-link',
            'team_room_receipts',
            'Mattermost delivery',
            'Mouth pipeline',
            'function renderMouthFlow',
            'function mouthNextAction',
            'send_approval',
            'team_rooms',
            'data-agent-tab',
            'function renderMission',
            'function renderControl',
            'Jarvis / Agent OS Control Panel',
            'Spartacus VPS Proof',
            'Proof Chain',
            'Spartacus gateway response',
            'function refreshSpartacusAction',
            'function mouthVerdict',
            'function mouthReplyDraft',
            'function mouthReplyPayload',
            'function mouthReplyQueue',
            'function mouthReplySent',
            '/api/mouth/verdict',
            '/api/mouth/reply-draft',
            '/api/mouth/reply-payload',
            '/api/mouth/reply-send-approval',
            '/api/mouth/reply-sent',
            'const mobilePrimaryTabs',
            'function renderMobileNav',
            'function selectTab',
            '/api/control/spartacus/refresh',
        ):
            assert_true(marker in html, f"served shell is missing live-sync control {marker}")
        body = urllib.request.urlopen(base_url + "/api/state", timeout=8).read().decode("utf-8")
        snapshot = json.loads(body)
        for key in ("generated_at", "runs", "mouth", "security", "writes_enabled", "admin", "control_nodes", "control_receipts", "team_rooms", "team_room_receipts"):
            assert_true(key in snapshot, f"/api/state snapshot missing key: {key}")
        team_room_ids = {room.get("id") for room in snapshot["team_rooms"]}
        assert_true({"mission-control", "agent-chatter", "theo-receipts"}.issubset(team_room_ids), "/api/state missing team room links")
        mission_room = next(room for room in snapshot["team_rooms"] if room.get("id") == "mission-control")
        assert_true(mission_room.get("configured") is True and str(mission_room.get("url", "")).startswith("http"), "mission team room URL is not configured")
        node_ids = {node.get("id") for node in snapshot["control_nodes"]}
        assert_true({"spartacus", "caesar", "theokoles"}.issubset(node_ids), "/api/state missing Control node registry")
        spartacus = next(node for node in snapshot["control_nodes"] if node.get("id") == "spartacus")
        assert_true(spartacus.get("reference") is True, "Spartacus is no longer marked as the reference POC")
        assert_true(spartacus.get("proof"), "Spartacus reference POC proof text is missing")
        assert_true("responding" in spartacus, "Spartacus node health is missing app-layer response state")
        status, refreshed = request_json(
            base_url + "/api/control/spartacus/refresh",
            {"node_id": "spartacus"},
            {"X-Theo-Glass": "1"},
        )
        assert_true(status == 200, f"Spartacus refresh action returned {status}: {refreshed}")
        receipt = refreshed.get("receipt")
        assert_true(isinstance(receipt, dict), "refresh action did not return a receipt")
        assert_true(receipt.get("kind") == "control_refresh", "refresh receipt has the wrong kind")
        assert_true(receipt.get("node_id") == "spartacus", "refresh receipt is not tied to Spartacus")
        assert_true(receipt.get("state") == "read_only", "refresh receipt is not marked read-only")
        refreshed_state = refreshed.get("state")
        assert_true(isinstance(refreshed_state, dict), "refresh action did not return updated state")
        receipts = refreshed_state.get("control_receipts")
        assert_true(isinstance(receipts, list) and receipts, "updated state does not expose control receipts")
        assert_true(receipts[0].get("id") == receipt.get("id"), "latest control receipt is not first in state")
        team_receipts = refreshed_state.get("team_room_receipts")
        assert_true(isinstance(team_receipts, list) and team_receipts, "updated state does not expose team-room receipts")
        control_team_receipt = team_receipts[0]
        assert_true(control_team_receipt.get("kind") == "control_refresh", "control refresh did not create a team-room receipt")
        assert_true(((control_team_receipt.get("mattermost") or {}).get("status") == "sent"), "control team-room receipt was not sent to webhook")
        status, deploy_rejected = request_json(
            base_url + "/api/team-room/deploy-receipt",
            {"title": "Regression deploy", "summary": "Should require auth", "status": "success"},
        )
        assert_true(status == 403 and deploy_rejected.get("ok") is False, f"unauthorized deploy receipt did not fail closed: {status} {deploy_rejected}")
        status, deploy_receipt = request_json(
            base_url + "/api/team-room/deploy-receipt",
            {
                "title": "Regression deploy",
                "summary": "Head deploy smoke stayed green.",
                "status": "success",
                "room_id": "deploys",
                "deployment_id": "deploy-regression-1",
                "fields": {"deployment": "deploy-regression-1", "secret_token": "must-not-ship"},
            },
            {"Authorization": "Bearer team-receipt-secret"},
        )
        assert_true(status == 200, f"deploy receipt returned {status}: {deploy_receipt}")
        deploy_record = deploy_receipt.get("receipt")
        assert_true(isinstance(deploy_record, dict) and deploy_record.get("kind") == "deploy_receipt", "deploy receipt has wrong shape")
        assert_true(deploy_record.get("room_id") == "deploys", "deploy receipt did not target deploys room")
        assert_true("secret_token" not in (deploy_record.get("fields") or {}), "deploy receipt did not scrub secret-shaped fields")
        event = {
            "version": "0.6.0-test",
            "channel": "telegram",
            "chat_id": "telegram:7148548566",
            "message_id": "10398",
            "sender_id": "7148548566",
            "sender": {"label": "A P"},
            "timestamp": "2026-06-14T03:40:23Z",
            "text": "OK let's get it done",
        }
        status, rejected = request_json(base_url + "/api/mouth/ingest", {"event": event})
        assert_true(status == 403 and rejected.get("ok") is False, f"unauthorized Mouth ingest did not fail closed: {status} {rejected}")
        status, ingested = request_json(
            base_url + "/api/mouth/ingest",
            {"event": event, "ingest_secret": "shot4-ingest-secret"},
        )
        assert_true(status == 200, f"Mouth ingest returned {status}: {ingested}")
        record = ingested.get("record")
        assert_true(isinstance(record, dict), "Mouth ingest did not return a record")
        ingested_command_id = str(record.get("command_id") or "")
        assert_true(record.get("state") == "compiled", "Mouth ingest should compile a draft, not dispatch it")
        assert_true(record.get("mode") == "draft", "Mouth ingest should force draft mode")
        assert_true(record.get("result_path") == "", "Mouth ingest unexpectedly dispatched a result")
        assert_true(((record.get("source") or {}).get("trusted") is True), "trusted Telegram sender was not trusted")
        webhook_text = "\n".join(str(post.get("payload", {}).get("text", "")) for post in TeamWebhookHandler.posts)
        assert_true("OK let's get it done" not in webhook_text, "team-room receipt leaked Telegram message text")
        ingested_state = ingested.get("state")
        assert_true(isinstance(ingested_state, dict), "Mouth ingest did not return refreshed state")
        mouth_records = ingested_state.get("mouth")
        assert_true(isinstance(mouth_records, list), "refreshed state is missing Mouth records")
        assert_true(any(item.get("command_id") == ingested_command_id for item in mouth_records if isinstance(item, dict)), "new Mouth command is missing from state")
        status, verdict = request_json(
            base_url + "/api/mouth/verdict",
            {"command_id": ingested_command_id, "verdict": "approve"},
            {"X-Theo-Glass": "1"},
        )
        assert_true(status == 200, f"Mouth verdict returned {status}: {verdict}")
        lifecycle = verdict.get("lifecycle")
        assert_true(isinstance(lifecycle, dict), "Mouth verdict did not return lifecycle receipt")
        assert_true(lifecycle.get("status") == "approved", "Mouth verdict lifecycle did not approve the command")
        verdict_state = verdict.get("state")
        assert_true(isinstance(verdict_state, dict), "Mouth verdict did not return refreshed state")
        verdict_records = verdict_state.get("mouth")
        assert_true(isinstance(verdict_records, list), "Mouth verdict state is missing Mouth records")
        updated = next((item for item in verdict_records if isinstance(item, dict) and item.get("command_id") == ingested_command_id), {})
        assert_true(((updated.get("lifecycle") or {}).get("status") == "approved"), "Mouth verdict lifecycle is missing from state")
        assert_true(mouth_verdicts_path.exists(), "Mouth verdict audit file was not written")
        status, drafted = request_json(
            base_url + "/api/mouth/reply-draft",
            {"command_id": ingested_command_id, "text": "Regression reply draft."},
            {"X-Theo-Glass": "1"},
        )
        assert_true(status == 200, f"Mouth reply draft returned {status}: {drafted}")
        reply = drafted.get("reply")
        assert_true(isinstance(reply, dict), "Mouth reply draft did not return reply")
        assert_true(reply.get("command_id") == ingested_command_id, "Mouth reply draft has wrong command id")
        drafted_state = drafted.get("state")
        assert_true(isinstance(drafted_state, dict), "Mouth reply draft did not return refreshed state")
        replies = drafted_state.get("mouth_replies")
        assert_true(isinstance(replies, list), "Mouth reply draft state is missing replies")
        assert_true(any(item.get("command_id") == ingested_command_id for item in replies if isinstance(item, dict)), "drafted reply is missing from state")
        reply_path = REPO_ROOT / "jobs" / "outbox" / ingested_command_id / "reply.json"
        status, pending_rejected = request_json(base_url + "/api/mouth/pending-replies", {"limit": 5})
        assert_true(status == 403 and pending_rejected.get("ok") is False, f"unauthorized pending replies did not fail closed: {status} {pending_rejected}")
        status, empty_pending = request_json(
            base_url + "/api/mouth/pending-replies",
            {"limit": 5},
            {"Authorization": "Bearer shot4-ingest-secret"},
        )
        assert_true(status == 200, f"Mouth pending replies returned {status}: {empty_pending}")
        assert_true(empty_pending.get("pending") == [], "unqueued reply appeared in runtime pending replies")
        status, queued = request_json(
            base_url + "/api/mouth/reply-send-approval",
            {"command_id": ingested_command_id},
            {"X-Theo-Glass": "1"},
        )
        assert_true(status == 200, f"Mouth send approval returned {status}: {queued}")
        send_approval = queued.get("send_approval")
        assert_true(isinstance(send_approval, dict) and send_approval.get("status") == "queued", "Mouth send approval did not queue the reply")
        queued_state = queued.get("state")
        assert_true(isinstance(queued_state, dict), "Mouth send approval did not return refreshed state")
        queued_replies = queued_state.get("mouth_replies")
        assert_true(isinstance(queued_replies, list), "Mouth send approval state is missing replies")
        queued_reply = next((item for item in queued_replies if isinstance(item, dict) and item.get("command_id") == ingested_command_id), {})
        assert_true(((queued_reply.get("send_approval") or {}).get("status") == "queued"), "queued send approval is missing from state")
        status, pending = request_json(
            base_url + "/api/mouth/pending-replies",
            {"limit": 5},
            {"Authorization": "Bearer shot4-ingest-secret"},
        )
        assert_true(status == 200, f"runtime pending replies returned {status}: {pending}")
        pending_items = pending.get("pending")
        assert_true(isinstance(pending_items, list), "runtime pending replies did not return a list")
        pending_item = next((item for item in pending_items if isinstance(item, dict) and item.get("command_id") == ingested_command_id), {})
        pending_payload = pending_item.get("payload") if isinstance(pending_item, dict) else None
        assert_true(isinstance(pending_payload, dict), "queued reply is missing runtime payload")
        assert_true(pending_payload.get("action") == "send" and pending_payload.get("target") == "telegram:7148548566", "runtime pending payload has wrong target")
        sender_guard = subprocess.run(
            [PYTHON, "bin/mouth-send-reply", str(reply_path), "--emit-message-json"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert_true(sender_guard.returncode == 0, f"sender guard rejected reply draft: {sender_guard.stderr or sender_guard.stdout}")
        payload = json.loads(sender_guard.stdout)
        assert_true(payload.get("action") == "send" and payload.get("target") == "telegram:7148548566", "sender guard emitted the wrong message payload")
        status, emitted = request_json(
            base_url + "/api/mouth/reply-payload",
            {"command_id": ingested_command_id},
            {"X-Theo-Glass": "1"},
        )
        assert_true(status == 200, f"Mouth reply payload returned {status}: {emitted}")
        emitted_payload = emitted.get("payload")
        assert_true(isinstance(emitted_payload, dict), "Mouth reply payload did not return payload")
        assert_true(emitted_payload.get("action") == "send" and emitted_payload.get("target") == "telegram:7148548566", "Mouth reply payload emitted the wrong message payload")
        status, sent = request_json(
            base_url + "/api/mouth/reply-sent",
            {"command_id": ingested_command_id, "message_id": "regression-message-id"},
            {"Authorization": "Bearer shot4-ingest-secret"},
        )
        assert_true(status == 200, f"Mouth sent marker returned {status}: {sent}")
        marker = sent.get("sent")
        assert_true(isinstance(marker, dict) and marker.get("status") == "sent", "Mouth sent marker did not return a sent marker")
        sent_state = sent.get("state")
        assert_true(isinstance(sent_state, dict), "Mouth sent marker did not return refreshed state")
        sent_replies = sent_state.get("mouth_replies")
        assert_true(isinstance(sent_replies, list), "Mouth sent marker state is missing replies")
        delivered = next((item for item in sent_replies if isinstance(item, dict) and item.get("command_id") == ingested_command_id), {})
        assert_true(((delivered.get("delivery") or {}).get("message_id") == "regression-message-id"), "delivery marker is missing from refreshed state")
        status, drained = request_json(
            base_url + "/api/mouth/pending-replies",
            {"limit": 5},
            {"Authorization": "Bearer shot4-ingest-secret"},
        )
        assert_true(status == 200 and drained.get("pending") == [], "sent reply still appeared in runtime pending replies")
        team_log = team_receipts_path.read_text(encoding="utf-8")
        for marker in ("control_refresh", "deploy_receipt", "mouth_received", "mouth_verdict", "mouth_reply_draft", "mouth_reply_send_approval", "mouth_reply_sent"):
            assert_true(marker in team_log, f"team-room receipt log is missing {marker}")
        assert_true(len(TeamWebhookHandler.posts) >= 7, "fake Mattermost webhook did not receive each receipt class")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
        webhook_server.shutdown()
        webhook_server.server_close()
        receipt_path.unlink(missing_ok=True)
        mouth_verdicts_path.unlink(missing_ok=True)
        team_receipts_path.unlink(missing_ok=True)
        if ingested_command_id:
            shutil.rmtree(REPO_ROOT / "jobs" / "inbox" / ingested_command_id, ignore_errors=True)
            shutil.rmtree(REPO_ROOT / "jobs" / "outbox" / ingested_command_id, ignore_errors=True)
        if original_mouth_index is None:
            mouth_index.unlink(missing_ok=True)
        else:
            mouth_index.write_text(original_mouth_index, encoding="utf-8")
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
