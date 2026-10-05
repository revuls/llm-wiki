---
name: link
description: Manage cross-wiki relationships — register another LLM wiki, discover connections between this wiki and linked wikis, add [[wiki-id:slug]] references, and verify existing ones. Use when the user wants to connect, link or relate this wiki with other wikis.
argument-hint: "add <path|repo> | discover [wiki-id] | check"
---

# Link (cross-wiki)

Follow `AGENTS.md` §6. Subcommand and arguments are the text after the command.

## add <path-or-repo>
1. Locate the other wiki. If a git URL is given and no local copy exists, ask the
   human where to clone it (suggest a sibling folder `../<name>`); clone only with OK.
2. Read its `wiki.config.yaml` (id, name, description, scope) and `wiki/index.md`.
   Refuse if its `id` equals this wiki's id or one already registered.
3. Append to `linked_wikis` in `wiki.config.yaml`: `id`, `name`, `path`, `repo`, `scope`.
4. Run `discover` for it. Suggest that the other wiki register this one too
   (note it under "Suggestions for other wikis" in `_meta/external-links.md`).

## discover [wiki-id]
Delegate to the `wiki-linker` subagent (one per linked wiki, in parallel if several;
if subagents aren't available, follow `.agents/agents/wiki-linker.md` yourself).
It compares indexes and overviews to find shared entities, concepts and topics,
complementary pages and contradictions. Then, with the human's OK:
- Add `[[wiki-id:slug]]` references (plus a resolvable `([↗](path))` link on first
  use) to the Related sections of local pages.
- Record each in the table in `wiki/_meta/external-links.md`.
- Record contradictions in `_meta/open-questions.md`.
- Mention the linked wikis in `overview.md` ("Related wikis").

## check
Run `python3 tools/wiki.py xlinks` — verifies every `[[wiki-id:slug]]` resolves to
an existing page in a registered, locally available wiki. Fix or flag broken ones.

## Log
`## [YYYY-MM-DD] link | <action> <wiki-id>` with bullets on references added.
