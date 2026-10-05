# CLAUDE.md

The schema of this wiki is tool-neutral and lives in `AGENTS.md` — follow it strictly.

@AGENTS.md

## Claude Code notes
- Slash commands: `/setup-wiki`, `/ingest`, `/query`, `/lint`, `/link` (from `.claude/skills/`).
- Subagents: `wiki-ingester`, `wiki-researcher`, `wiki-linter`, `wiki-linker` (from `.claude/agents/`).
- Both folders are **generated** from `.agents/` — edit there and run `python3 tools/sync_agents.py`.
