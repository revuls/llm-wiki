# Quick guide: LLM Wiki with Claude Code

## 1. Requirements (once)
- **Claude Code** (CLI `claude`, desktop app or IDE extension).
- **Python 3.8+** and **git**. Optional: **GitHub CLI** (`gh`), **Obsidian** side by side.

## 2. Create a wiki
```bash
python3 tools/wiki.py new ../platform-wiki                       # run inside the framework repo
python3 tools/wiki.py new ../platform-wiki --github my-org/platform-wiki   # + GitHub repo
```
Alternative: **Use this template** on GitHub → clone → `python3 tools/wiki.py init`.

## 3. Start Claude Code
```bash
cd ../platform-wiki && claude
```
`CLAUDE.md` imports `AGENTS.md`. Type `/` to see `/setup-wiki`, `/ingest`, `/query`, `/lint`, `/link`.

## 4. First time
```
/setup-wiki Platform team wiki: architecture, decisions and runbooks
```

## 5. Daily use

| I want to… | Type |
|---|---|
| Add documents | Copy them into `raw/` → `/ingest` or `/ingest raw/q3.pdf` |
| Add many at once | `/ingest --all` |
| Ask | `/query What did we decide about the service mesh?` |
| Keep the answer | `/query … --file`, or say "yes" when offered |
| Ask linked wikis too | `/query … --federated` |
| Health check | `/lint` (`--fix` to apply fixes) |
| Connect with other wikis | `/link discover` |

**An ingest:** Claude reads the source → proposes takeaways and the pages it will touch →
**waits for your OK** → writes pages → regenerates the index and logs the operation.

**Subagents:** `wiki-ingester` (batch ingests, sequential) and `wiki-researcher` (read-only,
parallel questions to linked wikis), used automatically.

## 6. Review and commit
`git diff`, your IDE or Obsidian — then commit, or ask Claude to. The pre-commit hook
refreshes the generated index.

## Notes
- `.claude/settings.json` pre-approves `python3 tools/wiki.py` and edits in `wiki/`, and
  denies edits in `raw/`. Put personal permission tweaks in `.claude/settings.local.json`
  (not overwritten by upgrades).
- **Commands missing:** start `claude` from the wiki root; restart after upgrades.
