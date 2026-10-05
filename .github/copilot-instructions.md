# GitHub Copilot instructions

This repository is an **LLM Wiki**: you maintain a persistent, interlinked markdown
knowledge base in `wiki/` built from immutable sources in `raw/`.

**The full schema is in [`AGENTS.md`](../AGENTS.md). Read it and follow it strictly** —
it defines the folder layout, page conventions, frontmatter, citations, the
`index.md` / `log.md` formats and the ingest / query / lint / link workflows.

Copilot-specific notes:
- Pick the **Wiki** agent in the agent picker (`.github/agents/wiki.agent.md`) for wiki work.
- Skills from `.agents/skills/` are available as slash commands in chat:
  `/setup-wiki`, `/ingest`, `/query`, `/lint`, `/link`. If a skill is not offered, read
  `.agents/skills/<name>/SKILL.md` and follow it.
- Subagents (`wiki-ingester`, `wiki-researcher`, `wiki-linter`, `wiki-linker`) are in
  `.github/agents/` and are invoked by the Wiki agent. They are generated — edit
  `.agents/agents/*.md` and run `python3 tools/sync_agents.py`.
- Use the terminal for `python3 tools/wiki.py …` (search, lint, stats, pending, xlinks, log).
- Never edit files in `raw/` (only move `raw/inbox/*` to `raw/processed/` after ingesting).
- Write wiki content in English, with `[[wikilinks]]` and YAML frontmatter as in `templates/`.
