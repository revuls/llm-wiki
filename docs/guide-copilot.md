# Quick guide: LLM Wiki with GitHub Copilot

## 1. Requirements (once)
- **VS Code** with the **GitHub Copilot Chat** extension, signed in to GitHub.
- **Python 3.8+** (used by the helper scripts).
- Optional: **Obsidian** to browse the wiki (links, graph view).

## 2. Create a new wiki
- **From GitHub:** click **Use this template** on the template repo and clone the new repo, or
- **Locally:**
  ```bash
  python3 scripts/new-wiki.py ../platform-wiki platform "Platform Wiki"
  ```

Open the **wiki's root folder** in VS Code.

## 3. Select the agent
1. Open Copilot Chat (`Ctrl+Alt+I` / `⌃⌘I`) in **agent** mode.
2. In the agent picker below the input box, choose **Wiki**.
3. Type `/` — you should see `setup-wiki`, `ingest`, `query`, `lint`, `link`.

## 4. Set up the wiki (first time only)
```
/setup-wiki Platform team wiki: architecture, decisions and runbooks
```
Copilot asks about scope, audience and categories, and fills in `wiki.config.yaml`.

## 5. Daily use

| I want to… | Type in chat |
|---|---|
| Add a document | Copy it to `raw/inbox/` → `/ingest` |
| Add many at once | `/ingest --all` |
| Ask a question | `/query What did we decide about the service mesh?` |
| Save the answer as a page | `/query … --file` (or say "yes" when offered) |
| Health-check the wiki | `/lint` (`/lint --fix` to apply fixes) |
| Link another wiki | `/link add ../security-wiki` |
| Ask across linked wikis | `/query … --federated` |

Plain language works too: *"ingest the Q3 PDF I just put in the inbox"*.

**What an ingest looks like:** Copilot reads the source → summarizes the key points
and lists the pages it will create/update → **waits for your OK** → writes the pages,
updates `index.md` and `log.md`, and moves the file to `raw/processed/`.

Subagents (`wiki-ingester`, `wiki-researcher`, `wiki-linter`, `wiki-linker`) are
invoked automatically by the Wiki agent; you don't select them yourself.

## 6. Review and save
- Review the changes in VS Code's Source Control view (or in Obsidian).
- Commit, e.g. `ingest: <source title>`. Copilot won't commit on its own unless
  `auto_commit: true` is set in `wiki.config.yaml`.

## 7. Delegate from GitHub.com (optional)
Create an issue such as *"Ingest the files in raw/inbox"* and **assign it to Copilot**.
The Copilot coding agent reads the same rules (`AGENTS.md`,
`.github/copilot-instructions.md`, `.github/agents/`) and opens a PR for you to review.
Copilot CLI (`copilot` in the terminal) reads the same files as well.

## 8. Key rules
- `raw/` = your original sources (never modified). `wiki/` = written by Copilot; you don't edit it by hand.
- To change a command or subagent, edit `.agents/` and run `python3 tools/sync_agents.py`.

## Troubleshooting
- **No "Wiki" agent or `/` commands:** make sure the wiki's root folder is open
  (not a parent folder), chat is in agent mode, and your Copilot Chat extension is up to date.
- **Commands show up twice:** `.vscode/settings.json` hides the generated `.claude/`
  copies; check it hasn't been overridden by your user settings.
- **Copilot asks before running terminal commands:** expected — approve
  `python3 tools/wiki.py …` (you can allow it for the session).
