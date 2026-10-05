---
name: setup-wiki
description: Define or update this wiki's identity and local rules — interview the user and fill wiki.config.yaml (scope, style and confidentiality rules, extra categories), the overview and the README. Use right after creating a wiki or to change its scope.
argument-hint: "[short description of the wiki]"
---

# Setup wiki

Use any text typed after the command as context. Only edit **wiki-owned** files
(`wiki.config.yaml`, `README.md`, `wiki/`) — never `AGENTS.md`, `.agents/`, `tools/`
or `templates/` except to add new category templates.

1. Read `wiki.config.yaml` and run `python3 tools/wiki.py status`.
2. Ask in **one** compact round, proposing defaults from the context:
   - name, one-line description, owner, audience;
   - scope in / out;
   - style rules (terminology, units, naming) and confidentiality rules;
   - typical sources; extra page categories (e.g. decisions, meetings, runbooks, glossary);
   - ingest mode (interactive/batch), `auto_commit`.
   Don't change `id` once other wikis may link to it.
3. Write the answers to `wiki.config.yaml` (quote list items that contain a colon).
4. For each extra category: add it to `extra_categories`, create `wiki/<category>/.gitkeep`
   and `templates/<category-singular>.md` (based on the closest existing template).
5. Rewrite the "What this wiki covers" section of `wiki/overview.md` and the description
   paragraph of `README.md`.
6. `python3 tools/wiki.py index` and `python3 tools/wiki.py log add setup "<Wiki name>" -m "<key decisions>"`.
7. Tell the user: put files in `raw/` and run ingest.
