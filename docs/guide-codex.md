# Quick guide: LLM Wiki with Codex

## 1. Requirements (once)
- **Codex CLI** (`codex`) or the **Codex IDE extension**, signed in.
- **Python 3.8+** and **git**. Optional: **GitHub CLI** (`gh`), **Obsidian**.

## 2. Create a wiki
```bash
python3 tools/wiki.py new ../platform-wiki                       # run inside the framework repo
python3 tools/wiki.py new ../platform-wiki --github my-org/platform-wiki   # + GitHub repo
```
Alternative: **Use this template** on GitHub → clone → `python3 tools/wiki.py init`.

## 3. Start Codex
```bash
cd ../platform-wiki && codex
```
Codex loads `AGENTS.md` automatically. Skills are invoked with **`$`**; `/skills` lists them.

## 4. First time
```
$setup-wiki Platform team wiki: architecture, decisions and runbooks
```

## 5. Daily use

| I want to… | Type in Codex |
|---|---|
| Add documents | Copy them into `raw/` → `$ingest` or `$ingest raw/q3.pdf` |
| Add many at once | `$ingest --all` |
| Ask | `$query What did we decide about the service mesh?` |
| Keep the answer | `$query … --file`, or say "yes" when offered |
| Ask linked wikis too | `$query … --federated` |
| Health check | `$lint` (`--fix` to apply fixes) |
| Connect with other wikis | `$link discover` |

**An ingest:** Codex reads the source → proposes takeaways and the pages it will touch →
**waits for your OK** → writes pages → regenerates the index and logs the operation.

**Subagents** (`.codex/agents/`): `wiki-ingester` for batch ingests (one at a time) and
`wiki-researcher` for parallel questions to linked wikis. Ask explicitly if needed:
*"use wiki-researcher agents, one per linked wiki"*. Without subagents Codex does the work itself.

## 6. Review and commit
`/diff` or `git diff`, then commit — the pre-commit hook refreshes the generated index.

## Notes
- The default `workspace-write` sandbox is enough. Linked wikis live in sibling folders
  (`../x-wiki`): approve reads outside the workspace if your sandbox asks.
- **`$ingest` not found:** start `codex` inside the wiki folder; restart after upgrades.
