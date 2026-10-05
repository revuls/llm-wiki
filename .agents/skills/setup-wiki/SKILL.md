---
name: setup-wiki
description: Initialize a new wiki created from the llm-wiki template — interview the user about the domain and fill wiki.config.yaml, the DOMAIN sections of AGENTS.md and the overview. Use right after creating a new wiki from the template, or when the user wants to redefine the wiki's scope.
argument-hint: "[short description of the wiki]"
---

# Setup wiki

Use any text the user typed after the command as context.



1. Read `AGENTS.md`, `wiki.config.yaml` and `wiki/log.md`. If the config is already
   customized (id ≠ `my-wiki`), confirm the user wants to change it.
2. Interview the user (one compact round of questions, propose defaults from the
   context they gave):
   - Name, `id` (kebab-case, unique across their wikis), one-line description, owner.
   - Audience and what they need from the wiki.
   - Scope in / scope out. Confidentiality rules (e.g. no customer PII).
   - Typical source types (docs, Slack threads, meeting transcripts, tickets, papers…).
   - Extra page categories beyond the defaults (e.g. `decisions`, `meetings`,
     `runbooks`, `glossary`) — for each, create `wiki/<category>/.gitkeep`, a template
     in `templates/`, a row in the AGENTS.md page-types table and an index section.
   - Ingest mode (interactive/batch), `auto_commit`, linked wikis (→ `/link add`).
3. Write `wiki.config.yaml`. Fill the `<!-- DOMAIN -->` sections of `AGENTS.md`
   with domain style and confidentiality rules (keep the marker comments).
4. Rewrite `wiki/overview.md` "What this wiki covers" and update `README.md`'s title
   and first paragraph to describe this specific wiki.
5. Log: `## [YYYY-MM-DD] setup | <Wiki name>` with the key decisions.
6. Tell the user how to start: drop files into `raw/inbox/` and run `/ingest`.
