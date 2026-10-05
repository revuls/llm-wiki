---
name: ingest
description: Ingest new sources from raw/ into the wiki — read, discuss takeaways, write the source page and integrate the knowledge into entity/concept/topic pages. Use when the user says ingest, process or add a source/document/file to the wiki.
argument-hint: "[raw/<file> | --all]"
---

# Ingest

Arguments: the text typed after the command — a file in `raw/`, `--all`, or nothing.

## 1. Pick and read
- No argument → run `python3 tools/wiki.py pending` and ask which file(s) to ingest.
- `--all` or several files → **batch mode**: hand each file to the `wiki-ingester`
  subagent **one at a time** (never in parallel), or process them yourself one by one;
  skip step 2. Finish with step 4 once.
- Read `wiki.config.yaml` (scope, style_rules, confidentiality) and the source in full.
  For images (`raw/assets/`), read the text first, then view the images that carry information.
- Find what the wiki already knows: `python3 tools/wiki.py search "<key terms>"`, plus `wiki/index.md`.

## 2. Discuss (interactive mode)
Tell the user, briefly: 3–7 key takeaways; what's new, already known or contradicting;
the pages you'll create/update (slugs); anything out of scope you'll skip.
**Wait for their answer** before writing.

## 3. Write
1. Source page `wiki/sources/src-<today>-<short-title>.md` from `templates/source.md`,
   with `raw: raw/<file>` and a one-line `summary`.
2. Create or update each affected entity / concept / topic page (usually 5–15; respect
   `ingest.max_pages_touched`). Revise summaries so they reflect all sources, cite
   `[[src-…]]`, bump `updated`, keep `summary` accurate. Add links where pages relate.
3. Contradictions → callout + `status: disputed` + `_meta/open-questions.md`.
4. Update `wiki/overview.md` if the big picture changed.

## 4. Finish
```bash
python3 tools/wiki.py index
python3 tools/wiki.py lint --quick          # fix any error you introduced
python3 tools/wiki.py log add ingest "<Source title>" -m "Source: [[src-…]]" -m "Created: [[a]], [[b]]" -m "Updated: [[c]]"
```
Report pages created/updated, contradictions and suggested follow-ups. Commit if
`auto_commit: true` (`ingest: <title>`), otherwise suggest it.
