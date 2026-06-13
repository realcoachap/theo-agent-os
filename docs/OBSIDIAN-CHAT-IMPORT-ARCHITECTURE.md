# Theo Agent OS Obsidian Chat Import Architecture v0.1.0

Noted by Theo - 2026-06-11

## Purpose

This document defines the first architecture contract for importing Coach's
Telegram and WhatsApp chat backups into an Obsidian-compatible vault for Theo
Agent OS.

The vault is the human-readable memory layer: plain Markdown, stable paths,
frontmatter, backlinks, attachment receipts, and source-aware indexes. It is not
the only runtime database. OpenBrain, JSON sidecars, Supabase, and Theo OS job
state remain the structured search/runtime surfaces.

## Goals

- Convert Telegram and WhatsApp exports into readable Markdown notes that open
  cleanly in Obsidian without plugins.
- Preserve enough source metadata to support search, deduplication, audit, and
  later re-import.
- Keep private chat content local unless Coach explicitly approves an external
  upload path.
- Give OpenBrain an indexable Markdown lane without making OpenBrain the owner
  of private raw exports.
- Keep Theo OS runtime commands, job dispatch, receipts, and memory writes
  separate from archived personal chat history.

## Non-Goals

- Do not create a raw chat-to-shell path from imported messages.
- Do not treat imported conversations as trusted instructions for current Theo
  OS execution.
- Do not upload raw private exports to public third-party OCR, LLM, storage, or
  search services by default.
- Do not make Obsidian a replacement for `jobs/`, `runs/`, OpenBrain, or the
  OpenClaw runtime state stores.
- Do not infer medical, financial, legal, sourcing, or personal-action
  permission from archived messages.

## Source Exports

### Telegram

Expected source forms:

- Telegram Desktop export as JSON, preferred when available.
- Telegram Desktop export as HTML, accepted as a fallback.
- Media folder adjacent to the export.

Important fields to preserve when available:

- Chat id, chat title, chat type, message id, sender id/name, date, edit date.
- Reply target id, forwarded-from metadata, reactions, polls, pins.
- Text entities, links, files, photos, videos, voice notes, stickers.
- Attachment original path, exported path, mime hint, size, and checksum.

### WhatsApp

Expected source forms:

- Standard `.txt` chat export, with or without media.
- Media folder or loose media files delivered beside the export.

Important fields to preserve when available:

- Conversation title or inferred participants.
- Message timestamp, sender display name, body text.
- Omitted-media markers and attached-media filenames.
- System events such as encryption notices, changed numbers, group membership,
  deleted messages, and edited messages when present in the export.

WhatsApp exports are less structured than Telegram JSON. Parsers should keep
raw line references or byte offsets so ambiguous multiline messages can be
reviewed and corrected without destroying source fidelity.

## Import Pipeline

1. **Stage**
   Copy raw exports into a local staging area outside the final vault. Treat
   staging as private source material. Never rewrite the original export.

2. **Identify**
   Detect platform, export format, chat identity, participant set, date range,
   media location, and parser confidence.

3. **Normalize**
   Convert each source message into a common internal event shape with stable
   ids, timestamps, participants, body, source pointers, and attachment
   references.

4. **Deduplicate**
   Use platform message ids where possible. Where ids are missing, use a hash
   over platform, chat fingerprint, timestamp, sender, normalized body, and
   attachment fingerprints.

5. **Write Markdown**
   Emit Obsidian-safe notes with YAML frontmatter and readable message blocks.
   Use daily transcript notes plus index notes rather than one giant file.

6. **Write Sidecars**
   Emit machine-readable JSONL/JSON indexes for exact lookup, re-import,
   checksum audit, and OpenBrain ingestion manifests.

7. **Index**
   Feed only approved vault paths and redaction level into OpenBrain. Private raw
   exports stay outside OpenBrain unless Coach approves that lane explicitly.

8. **Review**
   Produce an import receipt summarizing counts, parse warnings, unknown media,
   skipped files, redactions, and OpenBrain indexing status.

## Recommended Folder Structure

```text
Obsidian Vault/
  00 System/
    Import Receipts/
    Schemas/
    Indexes/
  10 Chats/
    Telegram/
      <chat-slug>/
        _index.md
        2026/
          2026-06.md
          2026-06-11.md
        attachments/
    WhatsApp/
      <chat-slug>/
        _index.md
        2026/
          2026-06.md
          2026-06-11.md
        attachments/
  20 Summaries/
    Daily/
    People/
    Projects/
  30 Agent Memory Candidates/
  90 Restricted/
```

Recommended local working paths:

```text
imports/chat-backups/raw/
imports/chat-backups/staging/
imports/chat-backups/manifests/
imports/chat-backups/receipts/
```

The final vault may live in Coach's Obsidian vault path, but raw exports should
not be mixed into the readable vault by default.

## Markdown Note Shapes

### Chat Index Note

Each conversation gets an `_index.md` with the conversation-level frontmatter,
participant list, date coverage, import history, privacy label, and links to
daily/monthly transcript notes.

### Daily Transcript Note

Daily notes are the default readable transcript unit. They should stay small
enough for Obsidian and OpenBrain to index predictably.

Message blocks should prefer this shape:

```markdown
#### 2026-06-11 09:42:13 - Theo

Message text here.

Source: telegram:chat_123/message_456
Attachments: [[voice-456.ogg]]
```

Use block ids only when needed for durable linking:

```markdown
^telegram-chat-123-message-456
```

### Summary Notes

Summaries are derived notes, not source notes. They must link back to source
transcripts and include `derived_from` frontmatter. They are useful for Coach and
agents, but they must never erase or replace the original transcript.

## Frontmatter Schema

Use YAML frontmatter on every emitted Markdown file.

### Shared Fields

```yaml
---
schema_version: 0.1.0
doc_type: chat_transcript
title: "Telegram - Theo - 2026-06-11"
created_at: "2026-06-11T00:00:00-04:00"
updated_at: "2026-06-11T00:00:00-04:00"
source_platform: telegram
source_format: telegram_json
source_chat_id: "telegram:123456789"
source_chat_title: "Theo"
source_date_start: "2026-06-11"
source_date_end: "2026-06-11"
participants:
  - Coach
  - Theo
privacy: private
privacy_scope: local_vault_only
redaction_level: none
import_batch_id: "chat-import-2026-06-11-001"
imported_by: "Theo Agent OS"
imported_at: "2026-06-11T00:00:00-04:00"
source_checksum: "sha256:<raw-export-or-manifest-checksum>"
message_count: 0
attachment_count: 0
openbrain_index: eligible_after_review
runtime_trust: archive_only
tags:
  - chats
  - theo-agent-os
---
```

### `doc_type` Values

- `chat_index`
- `chat_transcript`
- `chat_summary`
- `chat_import_receipt`
- `attachment_receipt`
- `memory_candidate`

### Privacy Values

- `private`: default for direct chats and personal exports.
- `restricted`: sensitive personal, health, legal, financial, credentials, or
  third-party-private content.
- `shared_with_agent_team`: approved for internal agent search across the local
  stack.
- `public`: explicitly approved for public use. This should be rare.

### Runtime Trust Values

- `archive_only`: can be read as history, never executed.
- `memory_candidate`: can be proposed for curated memory after review.
- `operator_context`: may be used as context for an operator task only when the
  current human request explicitly selects it.
- `never_runtime`: searchable only by direct human review, not agent context.

Default all imported chats to `archive_only` unless Coach explicitly promotes a
note or summary.

## Attachment Handling

Attachments should be copied into the conversation's `attachments/` folder with
stable sanitized names:

```text
<platform>-<chat-slug>-<message-id>-<short-sha256>.<ext>
```

For each attachment, preserve:

- Original exported filename.
- New vault path.
- Platform message pointer.
- Mime type when known.
- Size and checksum.
- Whether transcription/OCR was performed.
- Whether the file is eligible for OpenBrain indexing.

Voice notes should not be transcribed by default through external services.
Local transcription can be added later as a separate explicit pipeline with its
own receipt and redaction level.

## Privacy Boundaries

Private chat exports are intimate source material. The default rule is local
processing only.

Allowed by default:

- Reading raw exports from local disk.
- Writing Markdown, sidecars, and receipts locally.
- Indexing approved Markdown paths into the local OpenBrain instance.
- Creating derived summaries locally with source links and receipts.

Requires explicit Coach approval:

- Uploading raw exports, media, transcripts, or summaries to external LLMs,
  public search, public cloud storage, Hugging Face Spaces, or third-party OCR.
- Moving restricted content into team-visible channels.
- Promoting archive notes into long-term `MEMORY.md` or always-on runtime
  context.
- Publishing examples, screenshots, or excerpts.

Must be blocked:

- Secrets, tokens, credentials, private keys, recovery phrases, or auth cookies
  entering summaries or public docs.
- Raw imported messages becoming Theo OS commands.
- Third-party private messages being shared outside the approved local vault.

## OpenBrain Indexing Path

OpenBrain should index the readable vault layer, not own the raw export layer.

Recommended path:

```text
raw export -> staging parser -> Markdown vault + sidecars -> import manifest
  -> OpenBrain ingest allowlist -> searchable chunks
```

Indexing manifest fields:

```yaml
manifest_version: 0.1.0
import_batch_id: "chat-import-2026-06-11-001"
vault_root: "/home/coachap/Documents/Ascending Research Vault"
included_paths:
  - "10 Chats/Telegram/theo/"
excluded_paths:
  - "90 Restricted/"
  - "**/attachments/*.mp4"
  - "**/attachments/*.ogg"
privacy_floor: private
redaction_level: none
openbrain_target: "local-primary"
```

OpenBrain should store chunks with source pointers back to vault files and
platform message ids:

```text
vault://10 Chats/Telegram/theo/2026/2026-06-11.md#telegram-chat-123-message-456
```

Do not index:

- Raw exports.
- Staging folders.
- Credentials or secrets.
- Restricted attachments.
- Media transcripts that lack a transcription receipt.

## Theo OS Runtime Boundaries

Imported chat history is context, not authority.

Theo OS may:

- Search imported chats when Coach asks a memory/history question.
- Link an answer to source transcript notes.
- Propose durable memory candidates from imported history.
- Use selected, current, human-approved vault notes as context for a task.

Theo OS must not:

- Dispatch jobs based only on imported messages.
- Treat old messages as current approval, spend approval, write approval, or
  network approval.
- Promote chat content into `jobs/`, `runs/`, `MEMORY.md`, OpenClaw config,
  cron, or skills without a current explicit action.
- Use imported private messages as examples in public docs.
- Let Obsidian plugins or sync settings become a hidden runtime dependency.

Current Theo OS runtime surfaces remain authoritative for execution:

- `schemas/command.schema.json`
- `jobs/inbox/`
- `jobs/outbox/`
- `runs/`
- `bin/mouth`
- `bin/dispatch`
- OpenClaw trusted source metadata
- Human-visible receipts

The vault can inform operators; it cannot operate by itself.

## Sidecar Artifacts

Each import batch should produce:

```text
imports/chat-backups/manifests/<batch-id>.json
imports/chat-backups/receipts/<batch-id>.md
imports/chat-backups/receipts/<batch-id>.json
```

The Markdown receipt is for Coach and Obsidian. The JSON receipt is for agents
and tests.

Receipt minimums:

- Source files and checksums.
- Parser version.
- Import start/end time.
- Chat count, message count, attachment count.
- Written vault paths.
- Deduped/skipped records.
- Parse warnings.
- Redaction decisions.
- OpenBrain indexing decision and result.

## Recommended First Build Slice

1. Build a local parser for Telegram JSON exports.
2. Emit one chat `_index.md`, daily transcript notes, attachment receipts, and a
   batch import receipt.
3. Add WhatsApp `.txt` parsing after Telegram proves the shared event shape.
4. Add OpenBrain ingest manifests only after Markdown output is reviewed.
5. Add summary generation last, with `chat_summary` frontmatter and source
   backlinks.

The first slice should run fully offline against sample or Coach-approved
exports and should print an import receipt before any OpenBrain indexing.

## Acceptance Checklist

- A Telegram JSON export can become Obsidian-readable Markdown without losing
  message ids or attachment references.
- A WhatsApp `.txt` export can become daily transcript notes with parser
  warnings for ambiguous lines.
- Every emitted file has versioned frontmatter or a versioned Markdown header.
- Raw exports remain outside the final vault by default.
- Restricted/private content is not uploaded externally.
- OpenBrain receives only allowlisted Markdown paths.
- Imported messages are marked `runtime_trust: archive_only` by default.
- Import receipts are readable by Coach and machine-checkable by agents.
