# Quick guide: LLM Wiki with Codex

## 1. Requirements (once)
- **Codex CLI** (`codex`) or the **Codex IDE extension** for VS Code, signed in.
- **Python 3.8+** (used by the helper scripts).
- Optional: **Obsidian** to browse the wiki (links, graph view).

## 2. Create a new wiki
- **From GitHub:** click **Use this template** on the template repo and clone the new repo, or
- **Locally:**
  ```bash
  python3 scripts/new-wiki.py ../platform-wiki platform "Platform Wiki"
  ```

## 3. Start Codex
```bash
cd ../platform-wiki
codex
```
Codex loads `AGENTS.md` (the wiki's rules) automatically. Run `/skills` to check that
`setup-wiki`, `ingest`, `query`, `lint` and `link` are listed. In Codex, skills are
invoked with **`$`**, not `/`.

## 4. Set up the wiki (first time only)
```
$setup-wiki Platform team wiki: architecture, decisions and runbooks
```
Codex asks about scope, audience and categories, and fills in `wiki.config.yaml`.

## 5. Daily use

| I want to… | Type in Codex |
|---|---|
| Add a document | Copy it to `raw/inbox/` → `$ingest` |
| Add many at once | `$ingest --all` |
| Ask a question | `$query What did we decide about the service mesh?` |
| Save the answer as a page | `$query … --file` (or say "yes" when offered) |
| Health-check the wiki | `$lint` (`$lint --fix` to apply fixes) |
| Link another wiki | `$link add ../security-wiki` |
| Ask across linked wikis | `$query … --federated` |

Plain language works too: *"ingest the Q3 PDF I just put in the inbox"*.

**What an ingest looks like:** Codex reads the source → summarizes the key points
and lists the pages it will create/update → **waits for your OK** → writes the pages,
updates `index.md` and `log.md`, and moves the file to `raw/processed/`.

**Subagents:** custom agents are defined in `.codex/agents/` (`wiki-ingester`,
`wiki-researcher`, `wiki-linter`, `wiki-linker`). Codex spawns them for batch ingests
and federated queries; you can also ask explicitly, e.g. *"use wiki-researcher agents
to ask each linked wiki in parallel"*. If subagents aren't available in your Codex
version, it does the same work itself.

## 6. Review and save
- Review the changes with `git diff` (or `/diff` in Codex), or in Obsidian.
- Commit, e.g. `ingest: <source title>`. Codex won't commit on its own unless
  `auto_commit: true` is set in `wiki.config.yaml`.

## 7. Key rules
- `raw/` = your original sources (never modified). `wiki/` = written by Codex; you don't edit it by hand.
- Codex needs write access to the workspace (the default `workspace-write` sandbox is enough).
- Linking wikis reads sibling folders (e.g. `../security-wiki`); if Codex can't read
  them in your sandbox mode, approve the read when asked.
- To change a skill or subagent, edit `.agents/` and run `python3 tools/sync_agents.py`.

## Troubleshooting
- **`$ingest` not found:** start `codex` inside the wiki folder (it scans
  `.agents/skills/` from the current folder up to the repo root) and restart the session
  after adding skills.
- **Rules ignored:** check that `AGENTS.md` is at the repo root and that you started
  Codex inside the repo.
