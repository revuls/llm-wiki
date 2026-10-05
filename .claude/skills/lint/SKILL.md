---
name: lint
description: Health-check the wiki — broken links, orphans, missing pages, index drift, contradictions, stale claims, missing cross-references and data gaps — then write a lint report and fix safe issues. Use when the user says "lint", "health check", "clean up the wiki" or periodically after several ingests.
argument-hint: "[--fix] [--quick]"
---

# Lint

Arguments: `$ARGUMENTS`. For large wikis, delegate the semantic review to the
`wiki-linter` subagent and act on its report.

## 1. Mechanical checks
Run `python3 tools/wiki.py lint` and read the output. It reports:
broken wikilinks (missing pages), orphan pages (no inbound links), pages missing
from or stale in `index.md`, invalid/missing frontmatter, pages without source
citations, pages not updated in `stale_after_days`, raw files never ingested,
and unknown cross-wiki ids.

`--quick` stops here.

## 2. Semantic checks
Read `index.md`, `overview.md` and then sample pages, prioritizing hubs and
recently updated pages (`grep "^## \[" wiki/log.md | tail -20`):
- **Contradictions** between pages, or between a page and a newer source.
- **Stale claims** superseded by newer sources but not marked.
- **Missing pages**: entities/concepts mentioned in ≥3 pages without their own page.
- **Missing cross-references**: pages discussing the same thing without linking.
- **Duplicates**: two pages for the same thing (merge candidates).
- **Thin pages**: stubs that could be enriched from already-ingested sources.
- **Overview drift**: `overview.md` no longer reflects the wiki.
- **Data gaps** worth a web search or a new source; **new questions** worth asking.

## 3. Report
Overwrite `wiki/_meta/lint-report.md` (frontmatter `type: meta`, bump `updated`):
summary counts, then sections Errors / Warnings / Suggestions, each item with the
affected `[[pages]]` and a proposed fix.

## 4. Fix
- Always safe (do without asking): broken index entries, missing frontmatter fields,
  adding missing backlinks, adding pages to the index.
- With `--fix` or after the human's OK: creating missing pages, merging duplicates
  (leave a redirect stub), rewriting the overview, marking stale claims.
- Never delete pages or touch `raw/` content.

## 5. Log
`## [YYYY-MM-DD] lint | <N errors, M warnings>` with bullets on what was fixed and
what is pending. Update `_meta/open-questions.md` with new questions/sources.
