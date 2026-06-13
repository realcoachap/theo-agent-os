#!/usr/bin/env python3
"""Theo OS chat backup importer regression v0.1.0 - Noted by Theo - 2026-06-11.

Uses tiny synthetic Telegram and WhatsApp exports to prove the importer writes
Obsidian Markdown and OpenBrain-ready JSONL without touching private real chat
history.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
IMPORTER = REPO_ROOT / "scripts" / "import-chat-backups-to-obsidian.py"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="theo-chat-import-") as tmp:
        root = Path(tmp)
        telegram = root / "telegram.json"
        whatsapp = root / "whatsapp.txt"
        vault = root / "vault"
        telegram.write_text(
            json.dumps(
                {
                    "name": "Coach and Spartacus",
                    "messages": [
                        {
                            "id": 1,
                            "type": "message",
                            "date": "2026-06-11T09:00:00",
                            "from": "A P",
                            "text": "Morning. Check OpenBrain.",
                        },
                        {
                            "id": 2,
                            "type": "message",
                            "date": "2026-06-11T09:01:00",
                            "from": "Spartacus",
                            "text": [{"type": "plain", "text": "OpenBrain is healthy."}],
                            "file": "status.txt",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        whatsapp.write_text(
            "[6/11/26, 9:02:00 AM] A P: Import this too\n"
            "[6/11/26, 9:03:00 AM] Caesar: Logged with directionality\n"
            "continued line\n",
            encoding="utf-8",
        )

        proc = run([sys.executable, str(IMPORTER), "--vault", str(vault), str(telegram), str(whatsapp)])
        assert_true(proc.returncode == 0, proc.stderr or proc.stdout)
        tg_note = vault / "60 Chat Imports" / "Telegram" / "Coach and Spartacus.md"
        wa_note = vault / "60 Chat Imports" / "WhatsApp" / "whatsapp.md"
        jsonl = vault / ".theo-index" / "chat-messages.jsonl"
        assert_true(tg_note.exists(), "telegram note missing")
        assert_true(wa_note.exists(), "whatsapp note missing")
        assert_true(jsonl.exists(), "jsonl index missing")
        tg_text = tg_note.read_text(encoding="utf-8")
        wa_text = wa_note.read_text(encoding="utf-8")
        rows = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines()]
        assert_true("direction: `incoming`" in tg_text, "incoming direction missing")
        assert_true("direction: `outgoing`" in tg_text, "outgoing direction missing")
        assert_true("continued line" in wa_text, "multiline WhatsApp message missing")
        assert_true(len(rows) == 4, f"expected 4 rows, got {len(rows)}")
        assert_true(rows[0]["channel"] == "telegram", "telegram row channel missing")
        assert_true(rows[-1]["direction"] == "outgoing", "whatsapp outgoing direction missing")

        openclaw_export = root / "telegram-openclaw-shape.json"
        openclaw_export.write_text(
            json.dumps(
                {
                    "id": 8264702446,
                    "messages": [
                        {
                            "id": 10,
                            "type": "message",
                            "date": 1773958601,
                            "text": "Unix timestamp shape works",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        proc = run([sys.executable, str(IMPORTER), "--vault", str(vault), str(openclaw_export)])
        assert_true(proc.returncode == 0, proc.stderr or proc.stdout)
        openclaw_note = vault / "60 Chat Imports" / "Telegram" / "8264702446.md"
        assert_true(openclaw_note.exists(), "OpenClaw Telegram shape note missing")
        assert_true("2026-" in openclaw_note.read_text(encoding="utf-8"), "Unix timestamp did not normalize")

        html_one = root / "messages.html"
        html_two = root / "messages2.html"
        html_template = """<!DOCTYPE html>
<html>
 <body>
  <div class="page_header"><div class="text bold">Theokoles</div></div>
  <div class="message default clearfix" id="message{message_id}">
   <div class="body">
    <div class="pull_right date details" title="{timestamp}">time</div>
    <div class="from_name">{sender}</div>
    <div class="text">{text}</div>
   </div>
  </div>
 </body>
</html>
"""
        html_one.write_text(
            html_template.format(
                message_id=101,
                timestamp="16.03.2026 19:48:40 UTC-05:00",
                sender="A P",
                text="First export page",
            ),
            encoding="utf-8",
        )
        html_two.write_text(
            html_template.format(
                message_id=102,
                timestamp="17.03.2026 23:33:52 UTC-05:00",
                sender="Theokoles",
                text="Second export page",
            ),
            encoding="utf-8",
        )
        html_vault = root / "html-vault"
        proc = run([sys.executable, str(IMPORTER), "--vault", str(html_vault), str(html_one), str(html_two)])
        assert_true(proc.returncode == 0, proc.stderr or proc.stdout)
        html_note = html_vault / "60 Chat Imports" / "Telegram" / "Theokoles.md"
        html_jsonl = html_vault / ".theo-index" / "chat-messages.jsonl"
        html_note_text = html_note.read_text(encoding="utf-8")
        html_rows = [json.loads(line) for line in html_jsonl.read_text(encoding="utf-8").splitlines()]
        assert_true("First export page" in html_note_text, "first HTML page was overwritten")
        assert_true("Second export page" in html_note_text, "second HTML page missing")
        assert_true(len(html_rows) == 2, f"expected 2 grouped HTML rows, got {len(html_rows)}")
    print("chat backup importer regression passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
