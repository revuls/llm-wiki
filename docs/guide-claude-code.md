# Quick guide: LLM Wiki with Claude Code

## 1. Requirements (once)
- **Claude Code** (CLI `claude`, desktop app, or the VS Code / JetBrains extension).
- **Python 3.8+** (used by the helper scripts).
- Optional: **Obsidian** to browse the wiki side by side (links, graph view).

## 2. Create a new wiki
- **From GitHub:** click **Use this template** on the template repo and clone the new repo, or
- **Locally:**
  ```bash
  python3 scripts/new-wiki.py ../platform-wiki platform "Platform Wiki"
  ```

## 3. Start Claude Code
```bash
cd ../platform-wiki
claude
```
Claude loads `CLAUDE.md`, which imports `AGENTS.md` (the wiki's rules). Type `/` to see
`/setup-wiki`, `/ingest`, `/query`, `/lint`, `/link`.

## 4. Set up the wiki (first time only)
```
/setup-wiki Platform team wiki: architecture, decisions and runbooks
```
Claude asks about scope, audience and categories, and fills in `wiki.config.yaml`.

## 5. Daily use

| I want to… | Type in Claude Code |
|---|---|
| Add a document | Copy it to `raw/inbox/` → `/ingest` |
| Add many at once | `/ingest --all` |
| Ask a question | `/query What did we decide about the service mesh?` |
| Save the answer as a page | `/query … --file` (or say "yes" when offered) |
| Health-check the wiki | `/lint` (`/lint --fix` to apply fixes) |
| Link another wiki | `/link add ../security-wiki` |
| Ask across linked wikis | `/query … --federated` |

Plain language works too: *"ingest the Q3 PDF I just put in the inbox"*.

**What an ingest looks like:** Claude reads the source → summarizes the key points
and lists the pages it will create/update → **waits for your OK** → writes the pages,
updates `index.md` and `log.md`, and moves the file to `raw/processed/`.

**Subagents** (`.claude/agents/`): `wiki-ingester` (batch ingests, one at a time),
`wiki-researcher` (federated/deep questions, in parallel), `wiki-linter` and
`wiki-linker`. Claude uses them automatically; you can also ask, e.g.
*"use the wiki-linter agent to audit the wiki"*.

## 6. Review and save
- Review the changes with `git diff`, in your IDE, or in Obsidian.
- Commit, e.g. `ingest: <source title>` — or just ask Claude to commit. It won't do it
  on its own unless `auto_commit: true` is set in `wiki.config.yaml`.

## 7. Key rules
- `raw/` = your original sources (never modified; `.claude/settings.json` denies edits there).
  `wiki/` = written by Claude; you don't edit it by hand.
- `.claude/settings.json` pre-approves `python3 tools/wiki.py` and edits inside `wiki/`,
  so routine operations don't prompt for permission.
- `.claude/skills/` and `.claude/agents/` are **generated**: edit `.agents/` and run
  `python3 tools/sync_agents.py`.

## Troubleshooting
- **Commands missing:** start `claude` from the wiki's root folder; restart the session
  after running `sync_agents.py`.
- **Rules ignored:** check that `CLAUDE.md` still contains the `@AGENTS.md` import line.
