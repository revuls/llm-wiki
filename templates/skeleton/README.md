# {{NAME}}

{{DESCRIPTION}}

An **LLM-maintained wiki** built with the [llm-wiki framework]({{FRAMEWORK_REPO}}):
an AI agent reads the sources in `raw/` and maintains the interlinked pages in `wiki/`.
Start at [wiki/overview.md](wiki/overview.md) or [wiki/index.md](wiki/index.md).

## Use it
Open this folder with GitHub Copilot (VS Code, agent **Wiki**), Codex or Claude Code:

| Action | Copilot / Claude Code | Codex |
|---|---|---|
| Add a source | put it in `raw/`, then `/ingest` | `$ingest` |
| Ask | `/query <question>` | `$query <question>` |
| Health check | `/lint` | `$lint` |
| Linked wikis | `/link` | `$link` |

Guides: [Copilot](docs/guide-copilot.md) · [Codex](docs/guide-codex.md) ·
[Claude Code](docs/guide-claude-code.md) · [Linked wikis](docs/guide-linked-wikis.md) ·
[Framework & upgrades](docs/framework.md)

`python3 tools/wiki.py status` shows pages, pending sources, recent activity and health.
