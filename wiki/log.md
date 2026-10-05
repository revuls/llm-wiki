# Log

Append-only chronological record. Every entry starts with `## [YYYY-MM-DD] <op> | <title>`
(`op` ∈ setup, ingest, query, lint, link, refactor, schema).
Recent activity: `grep "^## \[" wiki/log.md | tail -5`

## [2026-10-05] setup | Wiki created from llm-wiki template
- Initial structure, schema (CLAUDE.md) and config (wiki.config.yaml).
- Next step: run `/setup-wiki` to define the domain, then drop sources in `raw/inbox/` and run `/ingest`.
