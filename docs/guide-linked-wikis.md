# Guide: creating and linking multiple wikis

Cross-wiki links use **relative paths** (`../other-wiki`), so all wikis must live as
**sibling folders** under the same parent directory. Each wiki stays an independent git
repo: linking never merges content — a wiki only **reads** the others.

Commands below use `/` (Claude Code, GitHub Copilot); in Codex use `$` instead
(`$link`, `$query`…).

## 1. Organize a common parent folder
```
~/wikis/
├── llm-wiki/          ← the template
├── platform-wiki/     id: platform
├── security-wiki/     id: security
└── product-wiki/      id: product
```

## 2. Create each wiki from the template
Every wiki needs a **unique, kebab-case `id`** — it is the prefix of cross-wiki links
(`[[security:zero-trust]]`).
```bash
cd ~/wikis/llm-wiki
python3 scripts/new-wiki.py ../platform-wiki platform "Platform Wiki"
python3 scripts/new-wiki.py ../security-wiki security "Security Wiki"
python3 scripts/new-wiki.py ../product-wiki product "Product Wiki"
```
Then create an empty GitHub repo for each one and push it:
```bash
git -C ../platform-wiki remote add origin git@github.com:your-org/platform-wiki.git
git -C ../platform-wiki push -u origin main
```

## 3. Set up and feed each wiki separately
In each wiki, run `/setup-wiki` and **define the scope carefully** — the agent uses
each wiki's `scope` to decide which wikis to consult in federated queries. Then ingest
its sources (`/ingest`).

Link wikis once they have some content: discovery finds nothing in empty wikis.

## 4. Link them (in both directions)
Links are one-way, so register each relationship from both sides. From `platform-wiki`:
```
/link add ../security-wiki
```
This command:
1. Reads the other wiki's `wiki.config.yaml` and `wiki/index.md`.
2. Adds an entry to `linked_wikis` in `wiki.config.yaml`:
   ```yaml
   linked_wikis:
     - id: security
       name: Security Wiki
       path: ../security-wiki
       repo: git@github.com:your-org/security-wiki.git
       scope: Security policies, threat models, controls
   ```
3. Runs `discover`: the `wiki-linker` subagent compares both wikis and proposes
   connections — shared entities, related concepts, pages that answer the other wiki's
   open questions, and contradictions.
4. With your OK, adds `[[security:slug]]` references to the relevant pages and records
   them in `wiki/_meta/external-links.md`.

Then do the reverse from `security-wiki`: `/link add ../platform-wiki`.
With three or more wikis, repeat for every pair that is actually related.

## 5. Query across wikis
```
/query How do our platform decisions comply with the security policies? --federated
```
The agent reads each linked wiki's `index.md` and `overview.md`, runs one
`wiki-researcher` subagent per wiki in parallel, and merges the answers, citing each
claim with its wiki prefix (`[[security:…]]`). If you file the answer, it is stored in
the wiki where you asked the question.

Without `--federated`, the agent still consults a linked wiki when the question clearly
falls within its `scope`.

## 6. Maintenance
| Task | Command |
|---|---|
| Find new connections after a wiki has grown | `/link discover security` |
| Verify cross-wiki links still resolve (e.g. after renaming pages) | `/link check` or `python3 tools/wiki.py xlinks` |
| Check overall health, including unknown wiki ids | `/lint` |

A wiki never modifies another one. When it spots something the other wiki should fix
or add, it records it under **"Suggestions for other wikis"** in
`wiki/_meta/external-links.md` — apply those from the other wiki
(e.g. *"review the suggestions from platform in its external-links page"*).

## Tips
- **Teams:** everyone must clone all wikis into the same parent folder so `../x` paths
  resolve. If one is missing, `xlinks` reports it as `SKIP` instead of failing.
- **Hub wiki (optional):** a wiki with few or no sources of its own that links to all
  the others and serves as the entry point for cross-cutting questions.
- **Obsidian:** each wiki is its own vault. `[[security:x]]` won't resolve in Obsidian,
  but the `([↗](../security-wiki/...))` link added next to it on first use does open the file.
- **Unique ids:** never reuse or rename a wiki `id` once other wikis link to it — all
  their `[[id:slug]]` references would break.
