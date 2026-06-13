#!/usr/bin/env python3
"""Theo OS chat backup to Obsidian importer v0.1.2 - Noted by Theo - 2026-06-11.

Turns Telegram/OpenClaw JSON exports, Telegram HTML exports, and WhatsApp text
exports into a local Obsidian-readable vault plus a machine-readable JSONL index
for later OpenBrain ingest.
The importer is intentionally stdlib-only and local-first because these exports
can contain private conversations, attachments, phone numbers, and credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


VERSION = "0.1.2"
DEFAULT_VAULT = Path.home() / "Documents" / "Ascending Research Vault"
DEFAULT_SELF_ALIASES = ("A P", "Coach", "coach", "7148548566")
CONTROL_CHARS = re.compile(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]")
WHATSAPP_PATTERNS = (
    re.compile(r"^\[(?P<date>[^\]]+)\]\s(?P<sender>[^:]+):\s(?P<text>.*)$"),
    re.compile(r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s-\s(?P<sender>[^:]+):\s(?P<text>.*)$"),
)


@dataclass
class Message:
    source_kind: str
    source_path: str
    chat_title: str
    channel: str
    sender: str
    timestamp: str
    text: str
    message_id: str = ""
    direction: str = "unknown"
    attachments: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return CONTROL_CHARS.sub(" ", text).strip()


def slugify(value: str, fallback: str = "untitled") -> str:
    cleaned = clean_text(value)
    cleaned = re.sub(r"[\/\\:*?\"<>|]", "-", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return (cleaned or fallback)[:120]


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return '""'
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(str(item), ensure_ascii=False) for item in value) + "]"
    return json.dumps(str(value), ensure_ascii=False)


def frontmatter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def resolve_inside(root: Path, relative: str) -> Path:
    root_resolved = root.resolve()
    target = (root_resolved / relative).resolve()
    if target != root_resolved and not str(target).startswith(f"{root_resolved}{os.sep}"):
        raise ValueError(f"Refusing to write outside vault: {relative}")
    return target


def markdown_escape(text: str) -> str:
    return text.replace("|", "\\|")


def flatten_telegram_text(value: Any) -> str:
    if isinstance(value, str):
        return clean_text(value)
    if isinstance(value, list):
        chunks: list[str] = []
        for item in value:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict):
                chunks.append(str(item.get("text", "")))
        return clean_text("".join(chunks))
    return clean_text(value)


def infer_direction(sender: str, self_aliases: set[str]) -> str:
    normalized = sender.strip().casefold()
    if not normalized or normalized in {"unknown", "deleted account"}:
        return "unknown"
    if normalized in self_aliases:
        return "incoming"
    return "outgoing"


def normalize_timestamp(value: Any) -> str:
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        try:
            return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        except (OSError, OverflowError, ValueError):
            pass
    text = clean_text(value)
    if not text:
        return ""
    if text.endswith("Z"):
        return text
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.isoformat(timespec="seconds")
        return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except ValueError:
        return text


def parse_telegram_html_timestamp(value: str) -> str:
    text = clean_text(value).replace("\u00a0", " ")
    candidates = [
        "%d.%m.%Y %H:%M:%S UTC%z",
        "%d.%m.%Y %H:%M UTC%z",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    ]
    for fmt in candidates:
        try:
            parsed = datetime.strptime(text, fmt)
            if parsed.tzinfo:
                return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
            return parsed.isoformat(timespec="seconds")
        except ValueError:
            continue
    return normalize_timestamp(text)


def parse_telegram_json(path: Path, self_aliases: set[str]) -> list[Message]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    messages = payload.get("messages")
    if not isinstance(messages, list):
        raise ValueError(f"{path} does not look like a Telegram/OpenClaw JSON export")
    chat_title = clean_text(payload.get("name") or payload.get("title") or payload.get("chat_name") or payload.get("id") or path.stem)
    parsed: list[Message] = []
    for item in messages:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        sender = clean_text(item.get("from") or item.get("from_id") or item.get("sender") or item.get("author") or "unknown")
        text = flatten_telegram_text(item.get("text"))
        attachments = [
            clean_text(item.get(key))
            for key in ("file", "photo", "thumbnail", "media_type")
            if clean_text(item.get(key))
        ]
        timestamp = normalize_timestamp(item.get("date") or item.get("date_unixtime"))
        message_id = clean_text(item.get("id"))
        parsed.append(
            Message(
                source_kind="telegram_json",
                source_path=str(path),
                chat_title=chat_title,
                channel="telegram",
                sender=sender,
                timestamp=timestamp,
                text=text,
                message_id=message_id,
                direction=infer_direction(sender, self_aliases),
                attachments=attachments,
                metadata={
                    "telegram_id": message_id,
                    "actor": clean_text(item.get("actor")),
                    "reply_to_message_id": clean_text(item.get("reply_to_message_id")),
                },
            )
        )
    return parsed


class TelegramHtmlExportParser(HTMLParser):
    """WHY: Telegram desktop exports are HTML, not JSON. This parser extracts the
    fields we need while keeping the raw export private/local and preserving the
    Telegram message IDs for later OpenBrain ingestion.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.messages: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.message_div_depth = 0
        self.capture: str | None = None
        self.capture_depth = 0
        self.last_sender = ""
        self.header_text: list[str] = []
        self.capture_header = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        classes = set(attrs.get("class", "").split())

        if tag == "div" and "message" in classes:
            self.current = {
                "id": attrs.get("id", "").replace("message", ""),
                "sender": "",
                "timestamp": "",
                "text": [],
                "attachments": [],
                "service": "service" in classes,
            }
            self.message_div_depth = 1
            return

        if self.current is not None and tag == "div":
            self.message_div_depth += 1
            if "from_name" in classes:
                self.capture = "from_name"
                self.capture_depth = self.message_div_depth
            elif "text" in classes:
                self.capture = "text"
                self.capture_depth = self.message_div_depth
            elif "date" in classes and "details" in classes:
                self.current["timestamp"] = attrs.get("title", "")
            return

        if self.current is None and tag == "div" and "text" in classes and "bold" in classes:
            self.capture_header = True
            return

        if self.current is not None and tag == "br" and self.capture == "text":
            self.current["text"].append("\n")

        if self.current is not None and tag == "a":
            href = clean_text(attrs.get("href", ""))
            if href and not href.startswith("#") and not href.startswith("tel:") and not href.startswith("javascript:"):
                self.current["attachments"].append(href)

    def handle_endtag(self, tag: str) -> None:
        if self.capture_header and tag == "div":
            self.capture_header = False
            return

        if self.current is None or tag != "div":
            return

        if self.capture and self.message_div_depth == self.capture_depth:
            self.capture = None
            self.capture_depth = 0

        if self.message_div_depth == 1:
            self._finish_message()
            self.current = None
            self.message_div_depth = 0
            return

        self.message_div_depth = max(0, self.message_div_depth - 1)

    def handle_data(self, data: str) -> None:
        text = html.unescape(data)
        if self.capture_header:
            self.header_text.append(text)
            return
        if self.current is None:
            return
        if self.capture == "from_name":
            self.current["sender"] += text
        elif self.capture == "text":
            self.current["text"].append(text)

    def handle_entityref(self, name: str) -> None:
        self.handle_data(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.handle_data(f"&#{name};")

    def _finish_message(self) -> None:
        if self.current is None or self.current.get("service"):
            return
        sender = clean_text(self.current.get("sender", ""))
        if sender:
            self.last_sender = sender
        else:
            sender = self.last_sender or "unknown"
        text = clean_text("".join(self.current.get("text", [])))
        attachments = sorted(set(clean_text(item) for item in self.current.get("attachments", []) if clean_text(item)))
        self.messages.append(
            {
                "id": clean_text(self.current.get("id", "")),
                "sender": sender,
                "timestamp": clean_text(self.current.get("timestamp", "")),
                "text": text,
                "attachments": attachments,
            }
        )

    @property
    def chat_title(self) -> str:
        return clean_text(" ".join(self.header_text)) or "Telegram HTML Export"


def parse_telegram_html(path: Path, self_aliases: set[str]) -> list[Message]:
    parser = TelegramHtmlExportParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    chat_title = slugify(parser.chat_title, fallback=path.stem)
    parsed: list[Message] = []
    for index, item in enumerate(parser.messages, start=1):
        sender = clean_text(item.get("sender") or "unknown")
        text = clean_text(item.get("text"))
        timestamp = parse_telegram_html_timestamp(clean_text(item.get("timestamp")))
        message_id = clean_text(item.get("id")) or stable_message_id(
            Message(
                source_kind="telegram_html",
                source_path=str(path),
                chat_title=chat_title,
                channel="telegram",
                sender=sender,
                timestamp=timestamp,
                text=text,
            ),
            index,
        )
        parsed.append(
            Message(
                source_kind="telegram_html",
                source_path=str(path),
                chat_title=chat_title,
                channel="telegram",
                sender=sender,
                timestamp=timestamp,
                text=text,
                message_id=message_id,
                direction=infer_direction(sender, self_aliases),
                attachments=item.get("attachments", []),
                metadata={"telegram_html_id": message_id},
            )
        )
    return parsed


def parse_whatsapp_timestamp(value: str) -> str:
    text = clean_text(value).replace("\u202f", " ")
    candidates = [
        "%m/%d/%y, %I:%M:%S %p",
        "%m/%d/%y, %I:%M %p",
        "%m/%d/%Y, %I:%M:%S %p",
        "%m/%d/%Y, %I:%M %p",
        "%m/%d/%y %I:%M:%S %p",
        "%m/%d/%y %I:%M %p",
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        "%d/%m/%y, %H:%M",
        "%d/%m/%Y, %H:%M",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(text, fmt).isoformat(timespec="seconds")
        except ValueError:
            continue
    return text


def parse_whatsapp_text(path: Path, self_aliases: set[str]) -> list[Message]:
    chat_title = path.stem
    parsed: list[Message] = []
    current: Message | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = clean_text(raw_line)
        match = None
        for pattern in WHATSAPP_PATTERNS:
            match = pattern.match(line)
            if match:
                break
        if match:
            sender = clean_text(match.group("sender"))
            current = Message(
                source_kind="whatsapp_txt",
                source_path=str(path),
                chat_title=chat_title,
                channel="whatsapp",
                sender=sender,
                timestamp=parse_whatsapp_timestamp(match.group("date")),
                text=clean_text(match.group("text")),
                direction=infer_direction(sender, self_aliases),
            )
            parsed.append(current)
            continue
        if current and line:
            current.text = f"{current.text}\n{line}".strip()
    for index, message in enumerate(parsed, start=1):
        message.message_id = stable_message_id(message, index)
        if "<attached:" in message.text.lower() or "omitted" in message.text.lower():
            message.attachments.append(message.text)
    return parsed


def stable_message_id(message: Message, index: int) -> str:
    seed = "\n".join(
        [
            message.channel,
            message.source_path,
            message.chat_title,
            message.timestamp,
            message.sender,
            message.text,
            str(index),
        ]
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]


def message_sort_key(message: Message) -> tuple[str, int, str]:
    try:
        numeric_id = int(re.sub(r"\D+", "", message.message_id) or "0")
    except ValueError:
        numeric_id = 0
    return (message.timestamp or "", numeric_id, message.message_id)


def message_dedupe_key(message: Message) -> tuple[str, str, str, str]:
    if message.message_id:
        return (message.channel, message.chat_title, message.source_kind, message.message_id)
    fallback = hashlib.sha256(
        "\n".join([message.source_path, message.timestamp, message.sender, message.text]).encode("utf-8")
    ).hexdigest()[:16]
    return (message.channel, message.chat_title, message.source_kind, fallback)


def thread_key(message: Message) -> tuple[str, str]:
    return (message.channel, message.chat_title)


def parse_input(path: Path, self_aliases: set[str]) -> list[Message]:
    if path.suffix.lower() == ".json":
        return parse_telegram_json(path, self_aliases)
    if path.suffix.lower() in {".html", ".htm"}:
        return parse_telegram_html(path, self_aliases)
    if path.suffix.lower() == ".txt":
        return parse_whatsapp_text(path, self_aliases)
    raise ValueError(f"Unsupported backup type for {path}; expected .json, .html, or .txt")


def note_for_chat(messages: list[Message], imported_at: str) -> str:
    first = messages[0]
    dates = [message.timestamp[:10] for message in messages if len(message.timestamp) >= 10]
    source_paths = sorted({message.source_path for message in messages})
    fields = {
        "version": VERSION,
        "generated_by": "import-chat-backups-to-obsidian.py",
        "entity_type": "chat_backup_thread",
        "chat_title": first.chat_title,
        "channel": first.channel,
        "source_kind": first.source_kind,
        "source_path": first.source_path,
        "source_paths": source_paths,
        "message_count": len(messages),
        "date_start": min(dates) if dates else "",
        "date_end": max(dates) if dates else "",
        "privacy": "local_private",
        "imported_at": imported_at,
        "openbrain_ready": True,
    }
    lines = [
        frontmatter(fields),
        "",
        f"# {first.chat_title}",
        "",
        "## Import Notes",
        "",
        "- Local private chat backup converted for Obsidian lookup and OpenBrain indexing.",
        "- Multi-page exports with the same chat title are grouped into one chronological thread note.",
        "- Direction is from Theo/OpenBrain's perspective: `incoming` means Coach/self alias sent it to the agent lane.",
        "- Raw export stays outside this generated note unless the operator chooses to preserve it elsewhere.",
        "",
        "## Messages",
        "",
    ]
    for message in messages:
        timestamp = message.timestamp or "unknown-time"
        text = message.text or "[no text]"
        lines.append(f"### {timestamp} - {message.sender}")
        lines.append("")
        lines.append(f"- direction: `{message.direction}`")
        lines.append(f"- message_id: `{message.message_id}`")
        if message.attachments:
            lines.append(f"- attachments: {', '.join(f'`{markdown_escape(item)}`' for item in message.attachments)}")
        lines.append("")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def index_row(message: Message, note_relative_path: str, imported_at: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "entity_type": "chat_backup_message",
        "channel": message.channel,
        "direction": message.direction,
        "sender": message.sender,
        "receiver": "theo-agent-os",
        "timestamp": message.timestamp,
        "thread_id": f"{message.channel}:{message.chat_title}",
        "message_id": message.message_id,
        "source_path": message.source_path,
        "note_path": note_relative_path,
        "chat_title": message.chat_title,
        "text": message.text,
        "attachments": message.attachments,
        "metadata": message.metadata,
        "imported_at": imported_at,
    }


def write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"dry-run write: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]], dry_run: bool) -> None:
    if dry_run:
        print(f"dry-run write {len(rows)} rows: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_vault_index(vault_root: Path, imported_at: str, dry_run: bool) -> None:
    index_path = resolve_inside(vault_root, "00 Index.md")
    content = "\n".join(
        [
            frontmatter(
                {
                    "version": VERSION,
                    "generated_by": "import-chat-backups-to-obsidian.py",
                    "entity_type": "theo_os_memory_vault_index",
                    "privacy": "local_private",
                    "updated_at": imported_at,
                }
            ),
            "",
            "# Theo OS / Ascending Memory Vault",
            "",
            "This vault is the human-readable memory layer for imported chat backups.",
            "OpenBrain should index `.theo-index/chat-messages.jsonl` for structured search.",
            "",
            "## Folders",
            "",
            "- `60 Chat Imports/Telegram/` - Telegram/OpenClaw JSON and HTML exports converted to Markdown.",
            "- `60 Chat Imports/WhatsApp/` - WhatsApp text exports converted to Markdown.",
            "- `.theo-index/` - JSONL message rows for OpenBrain/OpenClaw ingest.",
            "",
            "## Privacy",
            "",
            "Keep this vault local unless Coach explicitly approves a specific export or sync target.",
        ]
    )
    # WHY: The vault home can contain separately generated sections, such as the
    # OpenClaw Command Wing. Preserve those blocks while refreshing chat-import
    # metadata so one importer does not erase another local memory lane.
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8", errors="replace")
        marker = "## OpenClaw Command Wing"
        if marker in existing:
            content = content.rstrip() + "\n\n" + existing[existing.index(marker):].strip()
    write_text(index_path, content + "\n", dry_run)


def import_backups(inputs: list[Path], vault_root: Path, self_aliases: set[str], index_relative: str, dry_run: bool) -> int:
    imported_at = utc_now()
    all_rows: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[Message]] = {}
    write_vault_index(vault_root, imported_at, dry_run)

    for input_path in inputs:
        messages = parse_input(input_path, self_aliases)
        if not messages:
            print(f"warning: no messages parsed from {input_path}", file=sys.stderr)
            continue
        grouped.setdefault(thread_key(messages[0]), []).extend(messages)
        first = messages[0]
        folder = "Telegram" if first.channel == "telegram" else "WhatsApp"
        note_relative = f"60 Chat Imports/{folder}/{slugify(first.chat_title)}.md"
        print(f"parsed {len(messages)} messages from {input_path} -> {note_relative}")

    for messages in grouped.values():
        deduped: list[Message] = []
        seen: set[tuple[str, str, str, str]] = set()
        for message in sorted(messages, key=message_sort_key):
            key = message_dedupe_key(message)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(message)
        first = deduped[0]
        folder = "Telegram" if first.channel == "telegram" else "WhatsApp"
        note_relative = f"60 Chat Imports/{folder}/{slugify(first.chat_title)}.md"
        note_path = resolve_inside(vault_root, note_relative)
        write_text(note_path, note_for_chat(deduped, imported_at), dry_run)
        all_rows.extend(index_row(message, note_relative, imported_at) for message in deduped)
        print(f"wrote {len(deduped)} grouped messages -> {note_relative}")

    write_jsonl(resolve_inside(vault_root, index_relative), all_rows, dry_run)
    print(f"ready: {len(all_rows)} indexed messages for later OpenBrain ingest at {index_relative}")
    return 0 if all_rows else 2


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import Telegram JSON/HTML and WhatsApp text backups into a local Obsidian vault.",
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Backup exports: Telegram .json/.html or WhatsApp .txt")
    parser.add_argument("--vault", type=Path, default=Path(__import__("os").environ.get("THEO_OBSIDIAN_VAULT", DEFAULT_VAULT)))
    parser.add_argument(
        "--self-alias",
        action="append",
        default=[],
        help="Alias treated as Coach/self. May be repeated. Defaults include A P, Coach, coach, 7148548566.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned writes without changing files")
    parser.add_argument(
        "--index-relative",
        default=".theo-index/chat-messages.jsonl",
        help="Vault-relative JSONL output path. Use a pending/staged path to avoid replacing the main OpenBrain-ready index.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    self_aliases = {alias.casefold() for alias in DEFAULT_SELF_ALIASES}
    self_aliases.update(clean_text(alias).casefold() for alias in args.self_alias if clean_text(alias))
    try:
        return import_backups(args.inputs, args.vault, self_aliases, args.index_relative, args.dry_run)
    except Exception as exc:
        print(f"import failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
