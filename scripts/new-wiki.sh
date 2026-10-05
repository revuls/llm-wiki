#!/usr/bin/env bash
# Create a new, empty LLM wiki from this template.
#
# Usage: scripts/new-wiki.sh <target-dir> [wiki-id] ["Wiki Name"]
# Example: scripts/new-wiki.sh ../platform-wiki platform "Platform Engineering Wiki"
#
# Alternative: on GitHub, click "Use this template" on the template repository.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
  exit 1
fi

TEMPLATE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$1"
ID="${2:-$(basename "$TARGET" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g')}"
NAME="${3:-$ID}"
TODAY="$(date +%Y-%m-%d)"

if [[ -e "$TARGET" && -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  echo "error: $TARGET exists and is not empty" >&2
  exit 1
fi
mkdir -p "$TARGET"

rsync -a \
  --exclude '.git/' \
  --exclude '.claude/settings.local.json' \
  --exclude '.obsidian/workspace*.json' \
  --exclude '__pycache__/' \
  "$TEMPLATE_DIR/" "$TARGET/"

cd "$TARGET"

# Reset dates and identity.
sed -i.bak -E "s/^id: [a-z0-9-]+/id: $ID/; s/^name: .*/name: $NAME/" wiki.config.yaml
find wiki -name '*.md' -exec sed -i.bak -E "s/^(created|updated): [0-9]{4}-[0-9]{2}-[0-9]{2}/\1: $TODAY/" {} +
cat > wiki/log.md <<LOG
# Log

Append-only chronological record. Every entry starts with \`## [YYYY-MM-DD] <op> | <title>\`
(\`op\` ∈ setup, ingest, query, lint, link, refactor, schema).
Recent activity: \`grep "^## \\[" wiki/log.md | tail -5\`

## [$TODAY] setup | $NAME created from llm-wiki template
- Initial structure, schema (CLAUDE.md) and config (wiki.config.yaml).
- Next step: run \`/setup-wiki\` to define the domain, then drop sources in \`raw/inbox/\` and run \`/ingest\`.
LOG
find . -name '*.bak' -delete

# The new wiki doesn't need the template's own bootstrap script or docs about it.
rm -f scripts/new-wiki.sh
rmdir scripts 2>/dev/null || true

git init -q
git add -A
git commit -q -m "setup: $NAME created from llm-wiki template"

echo "Created wiki '$NAME' (id: $ID) in $(pwd)"
echo "Next: cd $TARGET && claude   then run  /setup-wiki"
