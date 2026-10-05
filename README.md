# LLM Wiki — framework

A reusable framework for **LLM-maintained knowledge bases**, based on
[Andrej Karpathy's "LLM Wiki" pattern](https://gist.github.com/karpathy).
Instead of RAG rediscovering knowledge on every question, an AI agent **incrementally
builds and maintains a persistent, interlinked markdown wiki** from your sources. You
curate sources and ask questions; the agent does the summarizing, cross-referencing and
filing — and wikis can be linked and queried together.

> Obsidian is the IDE, the LLM is the programmer, the wiki is the codebase.

Works with **GitHub Copilot**, **Codex** and **Claude Code**.

**Guides:** [GitHub Copilot](docs/guide-copilot.md) · [Codex](docs/guide-codex.md) ·
[Claude Code](docs/guide-claude-code.md) · [Linking wikis](docs/guide-linked-wikis.md) ·
[Framework, upgrades & maintenance](docs/framework.md)

## Quick start

```bash
git clone https://github.com/revuls/llm-wiki.git ~/wikis/llm-wiki
cd ~/wikis/llm-wiki
python3 tools/wiki.py new ../platform-wiki          # asks for id, name, description, scope
# optional: --github your-org/platform-wiki  creates the GitHub repo (via gh) and pushes
```
Or click **Use this template** on GitHub, clone the new repo and run `python3 tools/wiki.py init`.

Then open the new wiki with your agent and:
1. `setup-wiki` — define scope and local rules (`/setup-wiki`, or `$setup-wiki` in Codex).
2. Drop files into `raw/` → `ingest`.
3. `query` your wiki; `lint` it every few ingests; `link` it with other wikis.

## How it works

```
raw/                 Your sources (immutable): docs, PDFs, transcripts, exports; images in raw/assets/
wiki/                The LLM-maintained wiki
  index.md           Catalog — GENERATED from each page's `summary:`
  log.md             Append-only activity log
  overview.md        Front page / big-picture synthesis
  sources/ entities/ concepts/ topics/ analyses/   Pages ([[wikilinks]], YAML frontmatter)
  _meta/             open-questions.md, lint-report.md
wiki.config.yaml     This wiki: id, scope, style & confidentiality rules, settings
```

| Operation | What the agent does |
|---|---|
| **setup-wiki** | Interviews you; fills `wiki.config.yaml`, overview and README |
| **ingest** | Reads a source, discusses takeaways, writes a source page and updates 5–15 related pages |
| **query** | Answers with `[[citations]]` (optionally across linked wikis) and offers to file good answers |
| **lint** | Finds contradictions, stale claims, orphans, missing pages and gaps; writes a report |
| **link** | Discovers connections with sibling wikis and adds `[[wiki-id:slug]]` references |

Bookkeeping that a script does better than an LLM is automated by `tools/wiki.py`: the
index, source counts, pending-source detection, log formatting, cross-wiki resolution and
health checks. A **pre-commit hook** keeps the generated files current.

## Framework vs. wiki content

| | Files | Changed by |
|---|---|---|
| **Framework** (same in every wiki) | `AGENTS.md`, `CLAUDE.md`, `.agents/`, `templates/`, `tools/`, `docs/`, tool configs | `python3 tools/wiki.py upgrade` |
| **Wiki** (yours) | `wiki.config.yaml`, `README.md`, `raw/`, `wiki/` | you and the agent |
| **Generated** | `wiki/index.md`, `.claude/agents` & `skills`, `.github/agents/wiki-*`, `.codex/agents` | `wiki.py index` / `wiki.py sync` (pre-commit hook) |

Improve the framework here once, then run `python3 tools/wiki.py upgrade` in each wiki.
Details in [docs/framework.md](docs/framework.md).

## Helper CLI

```bash
python3 tools/wiki.py status            # pages, pending sources, recent log, linked wikis, health
python3 tools/wiki.py search "mesh"     # ranked page search
python3 tools/wiki.py pending           # raw files not yet ingested
python3 tools/wiki.py index             # regenerate the index
python3 tools/wiki.py lint              # health checks (exit 1 on errors)
python3 tools/wiki.py wikis             # linked wikis (siblings auto-discovered)
python3 tools/wiki.py xlinks            # verify [[wiki-id:slug]] references
python3 tools/wiki.py upgrade           # pull framework updates
python3 tools/wiki.py --help            # everything else (log, sync, new, init)
```
Standard library only, Python 3.8+, Windows/macOS/Linux (use `python` if `python3` isn't available).

## Tips
- Open each wiki as an **Obsidian** vault for graph view and backlinks; point Web Clipper /
  attachments to `raw/` and `raw/assets/`. Dataview can query the frontmatter.
- When a wiki outgrows its index and `wiki.py search`, consider [qmd](https://github.com/tobi/qmd).
- The schema co-evolves: when a convention doesn't fit, improve it here and upgrade the wikis.
