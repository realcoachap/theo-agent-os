# Obsidian Chat Backup Import v0.1.1

Noted by Theo - 2026-06-11

## Purpose

Coach wants Telegram and WhatsApp backups from Theo, Spartacus, and Caesar
conversations turned into an Obsidian vault that humans and agents can search.
This is the local-first import contract for that lane.

## Utility

```bash
python3 scripts/import-chat-backups-to-obsidian.py \
  --vault "$HOME/Documents/Ascending Research Vault" \
  path/to/telegram-result.json \
  path/to/whatsapp-chat.txt
```

Supported input formats:

- Telegram Desktop JSON exports with a top-level `messages` array.
- Telegram Desktop HTML exports, including multi-page `messages.html`,
  `messages2.html`, etc. Pages with the same chat title are grouped into one
  chronological thread note.
- OpenClaw Telegram JSON exports such as `chat-log/telegram-*.json`.
- WhatsApp `.txt` exports in common bracketed or dash-separated timestamp
  formats.

Use `--dry-run` before importing unknown export batches.

## Vault Shape

```text
Ascending Research Vault/
  00 Index.md
  60 Chat Imports/
    Telegram/
      <chat title>.md
    WhatsApp/
      <chat title>.md
  .theo-index/
    chat-messages.jsonl
```

The Markdown files are for Obsidian. The JSONL file is for OpenBrain and future
Theo OS ingest jobs.

## Directionality

Direction is from Theo/OpenBrain's perspective:

- `incoming` means Coach/self alias sent the message into the agent lane.
- `outgoing` means Spartacus, Caesar, Theo, or another participant replied.
- `unknown` means the sender could not be resolved.

Default self aliases are `A P`, `Coach`, `coach`, and `7148548566`. Add more
with repeated `--self-alias` flags.

## Privacy Boundary

Chat backups stay local unless Coach explicitly approves a specific export,
sync target, or handoff. The importer does not call a network API and does not
upload attachments. Attachment names/metadata are preserved in notes and JSONL
when the export includes them.

## OpenBrain Path

OpenBrain should ingest `.theo-index/chat-messages.jsonl` rather than scraping
rendered Markdown. Each row preserves:

- channel
- direction
- sender / receiver
- timestamp
- thread ID
- message ID
- source export path
- Obsidian note path
- text
- attachment metadata

This satisfies the original OpenBrain Phase 1 directionality requirement while
also giving Coach a readable Obsidian vault.
