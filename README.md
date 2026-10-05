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

## Works with GitHub Copilot, Codex and Claude Code

The schema and procedures are **tool-neutral** and written once; each agent picks them
up from the place it natively reads:

| | GitHub Copilot (VS Code / CLI / coding agent) | Codex (CLI / IDE) | Claude Code |
|---|---|---|---|
| Schema | `AGENTS.md` + `.github/copilot-instructions.md` | `AGENTS.md` | `CLAUDE.md` → imports `AGENTS.md` |
| Commands | `/ingest`, `/query`… (skills in `.agents/skills/`) | `$ingest`, `$query`… or `/skills` | `/ingest`, `/query`… |
| Main agent | **Wiki** in the agent picker (`.github/agents/wiki.agent.md`) | default session | default session |
| Subagents | `.github/agents/*.agent.md` | `.codex/agents/*.toml` | `.claude/agents/*.md` |

**Edit only the canonical files** — `AGENTS.md`, `.agents/skills/`, `.agents/agents/` —
then run `python3 tools/sync_agents.py` to regenerate the tool-specific copies
(`.claude/`, `.github/agents/`, `.codex/agents/`). CI (`.github/workflows/wiki-check.yml`)
fails if they are out of date. `.vscode/settings.json` tells Copilot to ignore the
generated Claude copies so nothing shows up twice.

### GitHub Copilot (VS Code)
1. Open the wiki folder in VS Code with GitHub Copilot Chat (agent mode).
2. In the chat's agent picker choose **Wiki**.
3. Type `/` to see the skills: `/setup-wiki`, `/ingest`, `/query`, `/lint`, `/link`.
   You can also just ask: *"ingest raw/inbox/q3-report.pdf"*, *"what do we know about X?"*.
4. Subagents run automatically when the Wiki agent delegates (batch ingest, federated
   queries, lint, link discovery).
5. The Copilot coding agent on github.com and Copilot CLI also read `AGENTS.md`,
   `.github/copilot-instructions.md` and `.github/agents/` — you can assign an issue
   like *"Ingest the files in raw/inbox"* and review the PR.

### Codex
1. Run `codex` in the wiki folder (or use the Codex IDE extension).
2. It reads `AGENTS.md` automatically. Invoke skills with `$ingest`, `$query`, `$lint`,
   `$link`, `$setup-wiki` (or list them with `/skills`), or ask in plain language.
3. Custom subagents (`.codex/agents/`) are used for batch ingest and federated queries.

## Contents

```
AGENTS.md            Schema: structure, conventions and workflows (canonical, tool-neutral)
CLAUDE.md            Imports AGENTS.md for Claude Code
wiki.config.yaml     Domain config: id, scope, categories, linked wikis
raw/                 Immutable sources — inbox/ (to ingest), processed/, assets/
wiki/                LLM-owned wiki: index, log, overview, sources, entities,
                     concepts, topics, analyses, _meta/
templates/           Page templates (source, entity, concept, topic, analysis)
.agents/skills/      Canonical skills: setup-wiki, ingest, query, lint, link
.agents/agents/      Canonical subagents: wiki-ingester, wiki-researcher, wiki-linter, wiki-linker
.github/             Copilot instructions, Wiki agent, generated Copilot subagents, CI
.codex/agents/       Generated Codex subagents
.claude/             Generated Claude Code skills and subagents, project permissions
.vscode/             Copilot settings (canonical locations only), recommended extensions
.obsidian/           Minimal vault config (attachments → raw/assets)
tools/wiki.py        Helper CLI: search, lint, stats, pending, xlinks, log (stdlib only)
tools/sync_agents.py Regenerates tool-specific agent files from .agents/
scripts/new-wiki.py  Bootstrap a new wiki from this template (cross-platform)
```

## Quick start

1. **Create a wiki** — either click **Use this template** on GitHub, or:
   ```bash
   python3 scripts/new-wiki.py ../platform-wiki platform "Platform Engineering Wiki"
   ```
2. **Open it** with your agent (VS Code + Copilot, `codex`, or `claude`) and, optionally,
   open the folder as an Obsidian vault next to it.
3. **Define the domain:** `/setup-wiki <what this wiki is about>` (`$setup-wiki` in Codex).
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
| `/setup-wiki` | Interviews you and fills `wiki.config.yaml` + domain rules in `AGENTS.md` | — |
| `/ingest [file\|--all]` | Reads a source, discusses takeaways, writes the source page, updates 5–15 entity/concept/topic pages, index, overview and log | `wiki-ingester` (batch, sequential) |
| `/query <q> [--file] [--federated]` | Answers from the wiki with `[[citations]]`; offers to file the answer as an analysis page | `wiki-researcher` (per linked wiki, parallel) |
| `/lint [--fix]` | Broken links, orphans, index drift, contradictions, stale claims, missing pages, gaps | `wiki-linter` |
| `/link add\|discover\|check` | Registers other wikis and proposes/verifies cross-wiki references | `wiki-linker` |

In Codex use `$` instead of `/`. Any other agent can follow the procedures directly:
*"follow `.agents/skills/ingest/SKILL.md` for raw/inbox/x.pdf"*.

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
  Dot-folders (`.agents/`, `.github/`…) are hidden by Obsidian automatically.
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
the agent to propose a change to `AGENTS.md`, and backport generally useful
improvements to this template.
