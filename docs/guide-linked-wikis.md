# Guide: creating and linking multiple wikis

Wikis are linked **automatically** when they are **sibling folders**: every folder next to
yours that contains a `wiki.config.yaml` is discovered (the framework repo itself is
skipped). Each wiki stays an independent git repo and only **reads** the others.

Commands use `/` (Copilot, Claude Code); in Codex use `$`.

## 1. One parent folder
```
~/wikis/
├── llm-wiki/          ← the framework (template)
├── platform-wiki/     id: platform
├── security-wiki/     id: security
└── product-wiki/      id: product
```

## 2. Create the wikis
```bash
cd ~/wikis/llm-wiki
python3 tools/wiki.py new ../platform-wiki --id platform --github my-org/platform-wiki
python3 tools/wiki.py new ../security-wiki --id security --github my-org/security-wiki
python3 tools/wiki.py new ../product-wiki  --id product  --github my-org/product-wiki
```
Ids must be **unique and stable** — they are the prefix of cross-wiki links (`[[security:zero-trust]]`).

## 3. Set up and feed each wiki
In each one: `/setup-wiki` — write the **scope** carefully, it is how agents decide which
wiki to ask — then add sources to `raw/` and `/ingest`.

## 4. Check they see each other
```bash
python3 tools/wiki.py wikis      # from any of them: lists the others with path and scope
```

## 5. Discover connections
Once the wikis have content, in each wiki:
```
/link discover
```
The agent compares indexes and overviews (one `wiki-researcher` per linked wiki), proposes
`[[wiki-id:slug]]` references (same-as, part-of, related, answers, contradicts) and, with
your OK, adds them to the pages. Contradictions and things the *other* wiki should add go
to `wiki/_meta/open-questions.md` — a wiki never edits another one.

## 6. Ask across wikis
```
/query How do our platform decisions comply with the security policies? --federated
```
Each relevant wiki is read in parallel; claims are cited as `[[security:…]]`. Even without
`--federated`, the agent consults a linked wiki when the question falls in its scope.

## 7. Keep links healthy
- `python3 tools/wiki.py xlinks` (or `/link check`) — verifies every `[[wiki-id:slug]]`.
- `/lint` reports references to unknown wikis.
- Re-run `/link discover` after a wiki grows significantly.

## Tips
- **Teams:** everyone clones all wikis into one parent folder. Missing wikis show as
  `NOT FOUND`/`SKIP` instead of failing.
- **Wikis elsewhere:** add `- {id: x, path: ../../other/x-wiki}` under `linked_wikis` in
  `wiki.config.yaml` (or `/link add <path>`). To ignore a sibling: `exclude_wikis: [id]`.
- **Hub wiki (optional):** a wiki with few sources that links to all others as the entry
  point for cross-cutting questions.
- **Obsidian:** each wiki is its own vault; `[[security:x]]` is not clickable there —
  `python3 tools/wiki.py xlinks` prints the file path of each reference.
