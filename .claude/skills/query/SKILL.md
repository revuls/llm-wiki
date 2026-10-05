---
name: query
description: Answer a question from the wiki (and linked wikis when relevant) with citations, choosing the best output format, and offer to file valuable answers back as analysis pages. Use for "ask the wiki", "what do we know about…", comparisons and syntheses over wiki content.
argument-hint: "<question> [--file] [--federated]"
---

# Query

Follow `CLAUDE.md` §4 (Query) and §6. Question: `$ARGUMENTS`

## 1. Locate
1. Read `wiki/index.md`. Pick candidate pages by title and summary.
2. If unclear or the wiki is large: `python3 tools/wiki.py search "<terms>" --limit 15`.
3. Read candidates fully; follow wikilinks one or two hops where relevant.
4. Go to `raw/` only to verify a specific detail or quote.

## 2. Federate (if needed)
If `--federated` is given, or the question clearly touches the `scope` of a wiki in
`linked_wikis` (`wiki.config.yaml`): for each such wiki, read its `wiki/index.md`
(and `overview.md`), then the relevant pages. Read-only. For broad multi-wiki
questions, delegate each linked wiki to the `wiki-researcher` subagent in parallel
and merge the results.

## 3. Answer
- Lead with the direct answer, then supporting detail.
- Cite every claim: `[[slug]]` (this wiki), `[[wiki-id:slug]]` (linked wiki).
- Pick the format that fits: prose, table, comparison matrix, timeline, Mermaid
  diagram, Marp slide deck (`marp: true` frontmatter), or a matplotlib chart saved
  under `wiki/analyses/assets/`.
- State clearly what the wiki does **not** know, and suggest sources to fill the gap.

## 4. File back
- If `--file` was given, or the answer is a reusable synthesis (comparison,
  analysis, new connection, decision support), **offer** to file it.
- On yes: create `wiki/analyses/<slug>.md` from `templates/analysis.md`, link it from
  the pages it draws on (Related section), add it to `index.md` under Analyses.
- New gaps or questions → `wiki/_meta/open-questions.md`.
- Cross-wiki references used in a filed page → `wiki/_meta/external-links.md`.

## 5. Log
Always append: `## [YYYY-MM-DD] query | <short question>` with 1–3 bullets
(pages consulted, filed as [[…]] or not filed).
