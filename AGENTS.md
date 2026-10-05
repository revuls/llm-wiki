# AGENTS.md

This repository is an **LLM Wiki**. The full schema and workflows for any coding agent
(Codex, OpenCode, Pi, Cursor, Gemini CLI, ...) are in [`CLAUDE.md`](CLAUDE.md).
Read it completely before doing anything, and treat it as if it were this file.

Quick reference:
- `raw/` is immutable (only move `raw/inbox/*` → `raw/processed/` after ingesting).
- `wiki/` is yours to write. Read `wiki.config.yaml`, then `wiki/index.md` first.
- Operations: **ingest**, **query**, **lint**, **link** — procedures in
  `.claude/skills/*/SKILL.md` (plain markdown, usable by any agent).
- Helper CLI: `python3 tools/wiki.py --help`.
