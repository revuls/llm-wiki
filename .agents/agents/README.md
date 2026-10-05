# Canonical subagent definitions

Each `*.md` file here defines one subagent, independent of any agent tool:

```yaml
---
name: wiki-example          # kebab-case, unique
description: When to use this subagent (shown to the orchestrating agent).
access: read-only | write
---
Instructions (markdown body).
```

`access` maps to tool permissions:

| access | Claude Code tools | Copilot tools | Codex sandbox |
|---|---|---|---|
| `read-only` | Read, Glob, Grep, Bash | read, search, execute | read-only |
| `write` | Read, Write, Edit, Glob, Grep, Bash | read, edit, search, execute, todo | workspace-write |

After editing, run `python3 tools/wiki.py sync` (the pre-commit hook does it too) to
regenerate `.claude/agents/`, `.github/agents/` and `.codex/agents/` (plus `.claude/skills/`).
