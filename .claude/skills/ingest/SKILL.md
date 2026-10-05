---
name: ingest
description: Ingest one or more raw sources into the wiki — read the source, discuss takeaways, write the source page, integrate it into entity/concept/topic pages, update index, overview and log. Use when the user says "ingest", "process this source", "add this to the wiki" or drops files in raw/inbox.
argument-hint: "[path in raw/ | --all | --batch]"
---

# Ingest

Follow `CLAUDE.md` §2–§4. Arguments: `$ARGUMENTS`

## 0. Select sources
- A path → ingest that file.
- Empty → list `raw/inbox/` (and any file in `raw/` not referenced by a source page:
  `python3 tools/wiki.py pending`) and ask which one(s).
- `--all` / `--batch` → all pending files, unsupervised mode (skip step 2 discussion,
  but still report at the end). For more than one file, delegate each file
  **sequentially** to the `wiki-ingester` subagent (never in parallel), then do a
  final consistency pass on `index.md` and `overview.md`.

## 1. Read
- Read `wiki.config.yaml` (scope in/out) and `wiki/index.md`.
- Read the source completely. For long sources, read in chunks and take notes.
- If it references images in `raw/assets/`, read the text first, then view the
  images that carry information (diagrams, charts, tables).
- Find related existing pages: `python3 tools/wiki.py search "<key terms>"`.

## 2. Discuss (interactive mode only)
Present to the human, briefly:
- 3–7 key takeaways.
- What is new vs. already known vs. contradicting existing pages.
- Planned changes: pages to create and pages to update (with slugs).
- Anything out of scope you will skip.
Ask what to emphasize or skip. **Wait for the answer.**

## 3. Write
1. Source page `wiki/sources/src-<today>-<short-title>.md` from `templates/source.md`.
   Its `raw:` field and link point to the file's final location (`raw/processed/…`
   if it came from the inbox).
2. For each affected entity/concept/topic: create from template or update in place.
   - Integrate: rewrite summaries so they reflect all sources, don't just append.
   - Add the source slug to `sources:` frontmatter and bump `updated:`.
   - Add bidirectional links (if A mentions B, B's Related/Relationships mentions A).
   - Contradictions → callout + `status: disputed` + entry in `_meta/open-questions.md`.
3. Update `wiki/overview.md` if the big picture changed.
4. Update `wiki/index.md` for every created page and refresh summaries/counts of
   updated ones.
5. Move the raw file `raw/inbox/<f>` → `raw/processed/<f>` (`git mv` if tracked, else `mv`).
6. Append to `wiki/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <Source title>
   - Source page: [[src-…]]
   - Created: [[a]], [[b]]
   - Updated: [[c]], [[d]], [[e]]
   - Notable: contradiction with … / new open question …
   ```

## 4. Verify and report
- Run `python3 tools/wiki.py lint --quick` and fix broken links / missing frontmatter
  you introduced.
- Report: pages created/updated (as a short list), contradictions found, suggested
  follow-up questions or sources.
- If `auto_commit: true`, commit with `ingest: <source title>`; otherwise suggest it.
