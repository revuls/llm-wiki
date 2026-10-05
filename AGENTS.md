# LLM Wiki — Schema (AGENTS.md)

You maintain this wiki. The human curates sources, asks questions and steers emphasis;
you do the reading, summarizing, cross-referencing and filing. These rules apply to every
agent (Copilot, Codex, Claude Code…). **Wiki-specific rules** — scope, `style_rules`,
`confidentiality` — are in `wiki.config.yaml`: read it at the start of every session and
follow it as part of this schema.

**Session start:** run `python3 tools/wiki.py status` (pages, pending sources, recent log,
linked wikis, health). Use `python` instead of `python3` if that's what the system has.

## Layout

| Path | Owner | Rule |
|---|---|---|
| `raw/` | Human | Immutable sources. Never edit, move, rename or delete. `raw/assets/` holds images. |
| `wiki/` | You | All pages. `wiki/index.md` is **generated** — never edit it by hand. |
| `wiki.config.yaml` | Both | This wiki's identity, scope and local rules. |
| `AGENTS.md`, `.agents/`, `templates/`, `tools/`, `docs/` | Framework | Shared by all wikis; changed only via `tools/wiki.py upgrade`. Propose improvements upstream instead of editing locally. |

Pages live in `wiki/sources/`, `entities/` (people, teams, systems, products…),
`concepts/` (ideas, methods, terms), `topics/` (broad themes), `analyses/` (answers filed
from queries), any `extra_categories` from the config, `overview.md` (front page) and
`_meta/` (`open-questions.md`, `lint-report.md`).

## Pages
- **File names:** kebab-case, unique across `wiki/`. The slug is the file name without `.md`.
  Source pages: `src-YYYY-MM-DD-short-title` (ingest date).
- **Templates:** start new pages from `templates/<type>.md`; omit sections that would be empty.
- **Frontmatter** (required: `title`, `type`, `summary`, `updated`):
  ```yaml
  ---
  title: Acme Corp
  type: entity          # source | entity | concept | topic | analysis | overview | meta
  summary: One line — shown in the generated index.
  created: 2026-10-05
  updated: 2026-10-05   # bump on every change
  # optional: tags, aliases, status (draft|stable|stale|disputed), confidence (high|medium|low)
  # source pages also need: raw: raw/<file>  (path from the repo root)
  ---
  ```
- **Links:** `[[slug]]` or `[[slug|label]]` — never paths. Link the first mention of anything
  that has (or deserves) a page; links to missing pages are fine and mark pages to create.
- **Citations:** every non-trivial claim cites its source page: `… grew 12% ([[src-2026-10-05-q3-report]])`.
  The number of sources per page is computed from these links.
- **Other wikis:** `[[wiki-id:slug]]`. They are read-only. `python3 tools/wiki.py wikis`
  lists them (sibling folders are discovered automatically) with their scope.

## Content rules
- English, concise, factual; bullets and tables over long prose.
- Separate facts (cited) from your synthesis (`## Synthesis`) and unknowns (`## Open questions`).
- Never invent facts. Integrate new information by **revising** pages, not appending blindly.
- **Contradictions:** never overwrite silently. Keep both claims with citations, add
  `> [!warning] Contradiction`, set `status: disputed`, list it in `_meta/open-questions.md`.
- **Superseded claims:** `~~old claim~~ (superseded by [[src-…]], YYYY-MM-DD)`.
- Never delete pages without the human's OK; prefer merging and leaving a stub
  ("Merged into [[x]]", `status: stale`).

## Operations
Each one has a procedure in `.agents/skills/<name>/SKILL.md`; read it before acting.

| Operation | Command | When |
|---|---|---|
| setup-wiki | `/setup-wiki` · `$setup-wiki` | Define or change this wiki's identity and rules |
| ingest | `/ingest` · `$ingest` | Integrate new files from `raw/` |
| query | `/query` · `$query` | Answer questions (optionally across linked wikis); file good answers |
| lint | `/lint` · `$lint` | Health check and cleanup |
| link | `/link` · `$link` | Discover and verify connections with other wikis |

**After every operation that changes `wiki/`:** run `python3 tools/wiki.py index`, then
`python3 tools/wiki.py log add <op> "<title>" -m "<bullet>" …`. If `auto_commit: true`,
commit (`<op>: <title>`); otherwise suggest a commit.

**Subagents** (if your tool supports them): `wiki-ingester` for batch ingests — one source
at a time, never two writers in parallel; `wiki-researcher` (read-only) for parallel
questions to other wikis or large scans. Without subagent support, do the work yourself
following `.agents/agents/<name>.md`.

## Helper CLI (`python3 tools/wiki.py …`)
`status` · `search "<terms>"` · `pending` · `index` · `lint [--quick]` · `log [-n N]` ·
`log add …` · `wikis` · `xlinks` — run `--help` for details. Prefer them over manual
bookkeeping.

If a situation isn't covered, make a sensible choice, note it in the log, and suggest a
schema improvement for the framework at the end of the session.
