#!/usr/bin/env bash
# Theo Agent OS Hermes sandbox installer v0.1.0 - Noted by Theo - 2026-06-09
# Installs Hermes Agent into repo-local .sandbox paths only.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX_DIR="$ROOT_DIR/.sandbox"
VENV_DIR="$SANDBOX_DIR/hermes-venv"
HERMES_HOME_DIR="$SANDBOX_DIR/hermes-home"

mkdir -p "$SANDBOX_DIR" "$HERMES_HOME_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install "hermes-agent"

cat > "$HERMES_HOME_DIR/README.md" <<'EOF'
# Hermes Sandbox Home

This directory is intentionally local-only and ignored by git.

Do not connect real Telegram, Discord, email, social, Obsidian, OpenBrain, or
production repo credentials here during the scout.
EOF

export HERMES_HOME="$HERMES_HOME_DIR"

"$VENV_DIR/bin/hermes" --help >/dev/null

echo "Hermes sandbox installed."
echo "Hermes binary: $VENV_DIR/bin/hermes"
echo "Hermes home: $HERMES_HOME_DIR"
echo "Run with:"
echo "  HERMES_HOME=\"$HERMES_HOME_DIR\" \"$VENV_DIR/bin/hermes\" --help"

