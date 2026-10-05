# LLM Wiki — template

A reusable starter kit for **LLM-maintained knowledge bases**, based on
[Andrej Karpathy's "LLM Wiki" pattern](https://gist.github.com/karpathy).
Instead of RAG rediscovering knowledge on every question, an LLM agent
**incrementally builds and maintains a persistent, interlinked markdown wiki** from
your raw sources. You curate sources and ask questions; the agent does the
summarizing, cross-referencing, filing and bookkeeping.

> Obsidian is the IDE, the LLM is the programmer, the wiki is the codebase.

Use this repository as a template for every new wiki (team docs, a project, a
customer, a research topic…) so the schema, agents and tooling never need to be
re-explained. Wikis created from it can be **linked to each other** and queried
together.

## Contents

```
CLAUDE.md            Schema: structure, conventions and workflows (the agent's contract)
AGENTS.md            Pointer to CLAUDE.md for Codex / OpenCode / other agents
wiki.config.yaml     Domain config: id, scope, categories, linked wikis
raw/                 Immutable sources — inbox/ (to ingest), processed/, assets/
wiki/                LLM-owned wiki: index, log, overview, sources, entities,
                     concepts, topics, analyses, _meta/
templates/           Page templates (source, entity, concept, topic, analysis)
tools/wiki.py        Helper CLI: search, lint, stats, pending, xlinks, log (stdlib only)
scripts/new-wiki.sh  Bootstrap a new wiki from this template
.claude/skills/      Slash commands: /setup-wiki /ingest /query /lint /link
.claude/agents/      Subagents: wiki-ingester, wiki-researcher, wiki-linter, wiki-linker
.obsidian/           Minimal vault config (attachments → raw/assets)
```

## Quick start

1. **Create a wiki** — either click **Use this template** on GitHub, or:
   ```bash
   scripts/new-wiki.sh ../platform-wiki platform "Platform Engineering Wiki"
   ```
2. **Open it** in Claude Code (`cd ../platform-wiki && claude`) and, optionally, open
   the folder as an Obsidian vault next to it.
3. **Define the domain:** `/setup-wiki <what this wiki is about>`.
4. **Add sources:** drop files (markdown, PDFs, transcripts, exports, images…) into
   `raw/inbox/`. [Obsidian Web Clipper](https://obsidian.md/clipper) is handy for web pages.
5. **Ingest:** `/ingest` (one at a time, interactive) or `/ingest --all` (batch).
6. **Ask:** `/query How does X compare to Y?` — good answers can be filed back into
   `wiki/analyses/` so explorations compound.
7. **Maintain:** `/lint` every few ingests.
8. **Connect wikis:** `/link add ../security-wiki`, then `/query --federated …`.

## Operations

| Command | What it does | Subagent used |
|---|---|---|
| `/setup-wiki` | Interviews you and fills `wiki.config.yaml` + domain rules in `CLAUDE.md` | — |
| `/ingest [file\|--all]` | Reads a source, discusses takeaways, writes the source page, updates 5–15 entity/concept/topic pages, index, overview and log | `wiki-ingester` (batch, sequential) |
| `/query <q> [--file] [--federated]` | Answers from the wiki with `[[citations]]`; offers to file the answer as an analysis page | `wiki-researcher` (per linked wiki, parallel) |
| `/lint [--fix]` | Broken links, orphans, index drift, contradictions, stale claims, missing pages, gaps | `wiki-linter` |
| `/link add\|discover\|check` | Registers other wikis and proposes/verifies cross-wiki references | `wiki-linker` |

Other agents (Codex, OpenCode…) read `AGENTS.md` → `CLAUDE.md`; the skill files are
plain markdown procedures any agent can follow ("follow `.claude/skills/ingest/SKILL.md`").

## Linking wikis

Every wiki has a unique `id` in `wiki.config.yaml`. Register other wikis under
`linked_wikis` (keep them as sibling folders, e.g. `~/wikis/<name>`):

```yaml
linked_wikis:
  - id: security
    name: Security Wiki
    path: ../security-wiki
    repo: git@github.com:your-org/security-wiki.git
    scope: Security policies, threat models, controls
```

- Reference a page of another wiki with `[[security:zero-trust]]`.
- Linked wikis are **read-only** from this one; suggestions for them are recorded in
  `wiki/_meta/external-links.md`.
- `python3 tools/wiki.py xlinks` verifies every cross-wiki reference.
- `/query --federated` reads each linked wiki's index and overview, then drills in.

## Helper CLI

```bash
python3 tools/wiki.py search "service mesh"   # ranked page search
python3 tools/wiki.py lint                    # mechanical health check (exit 1 on errors)
python3 tools/wiki.py stats                   # counts, hub pages, pending sources
python3 tools/wiki.py pending                 # raw files not yet ingested
python3 tools/wiki.py xlinks                  # verify cross-wiki links
python3 tools/wiki.py log -n 5                # recent activity
python3 tools/wiki.py --root ../other-wiki stats
```

When a wiki outgrows `index.md` + this search, consider [qmd](https://github.com/tobi/qmd)
(local hybrid BM25/vector search with CLI and MCP server).

## Obsidian tips

- Open the repo root as a vault; `templates/`, `tools/` and `scripts/` are excluded.
- Attachments go to `raw/assets/`. Bind *Download attachments for current file* to a
  hotkey to localize images after clipping.
- Graph view shows hubs and orphans; **Dataview** can query page frontmatter
  (`type`, `tags`, `sources`, `status`, `updated`); **Marp** renders slide decks produced by `/query`.

## Conventions in one minute

- `raw/` is immutable; `wiki/` is written only by the LLM.
- Kebab-case unique file names; link with `[[slug]]`; cite sources with `[[src-…]]`.
- YAML frontmatter on every page (`title, type, tags, created, updated, sources, status`).
- Contradictions are flagged, never silently overwritten.
- `wiki/log.md` entries: `## [YYYY-MM-DD] op | title` → `grep "^## \[" wiki/log.md | tail -5`.

The schema is meant to **co-evolve**: when a convention doesn't fit your domain, ask
the agent to propose a change to `CLAUDE.md`, and backport generally useful
improvements to this template.
