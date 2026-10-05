# Quick guide: LLM Wiki with GitHub Copilot

## 1. Requirements (once)
- **VS Code** with **GitHub Copilot Chat**, signed in to GitHub.
- **Python 3.8+** and **git**. Optional: **GitHub CLI** (`gh`) to create repos, **Obsidian** to browse.

## 2. Create a wiki
```bash
python3 tools/wiki.py new ../platform-wiki                       # run inside the framework repo
python3 tools/wiki.py new ../platform-wiki --github my-org/platform-wiki   # + GitHub repo
```
It asks for id, name, description and scope (or pass `--id --name --description --scope-in`).
Alternative: **Use this template** on GitHub → clone → `python3 tools/wiki.py init`.

Open the **wiki's root folder** in VS Code.

## 3. Select the agent
Open Copilot Chat (`Ctrl+Alt+I` / `⌃⌘I`), pick **Wiki** in the agent picker, and type `/`
to see `setup-wiki`, `ingest`, `query`, `lint`, `link`.

## 4. First time
```
/setup-wiki Platform team wiki: architecture, decisions and runbooks
```

## 5. Daily use

| I want to… | Type in chat |
|---|---|
| Add documents | Copy them into `raw/` → `/ingest` (asks which) or `/ingest raw/q3.pdf` |
| Add many at once | `/ingest --all` |
| Ask | `/query What did we decide about the service mesh?` |
| Keep the answer | `/query … --file`, or say "yes" when offered |
| Ask linked wikis too | `/query … --federated` |
| Health check | `/lint` (`--fix` to apply fixes) |
| Connect with other wikis | `/link discover` |
| See the state | "status" (runs `python3 tools/wiki.py status`) |

Plain language works too: *"ingest the Q3 PDF I just added"*.

**An ingest:** Copilot reads the source → proposes takeaways and the pages it will touch →
**waits for your OK** → writes pages → regenerates the index and logs the operation.

## 6. Review and commit
Review in Source Control (or Obsidian) and commit. The pre-commit hook refreshes the
generated index automatically.

## 7. From GitHub.com (optional)
Assign an issue like *"Ingest the files added in raw/ this week"* to **Copilot**: the coding
agent reads `AGENTS.md` and `.github/agents/` and opens a PR. Copilot CLI reads them too.

## Troubleshooting
- **No "Wiki" agent or `/` commands:** open the wiki root folder (not a parent), use agent
  mode, update Copilot Chat.
- **Commands appear twice:** `.vscode/settings.json` hides the generated `.claude/` copies;
  check your user settings don't override it.
- **Terminal approvals:** approve `python3 tools/wiki.py …` (you can allow it for the session).
