# Framework, upgrades & maintenance

## What is what

| Kind | Paths | Who changes it |
|---|---|---|
| **Framework** | listed in `tools/framework-manifest.txt`: `AGENTS.md`, `CLAUDE.md`, `.agents/`, `templates/`, `tools/`, `docs/`, `.githooks/`, `.github/copilot-instructions.md`, `.github/agents/wiki.agent.md`, `.github/workflows/`, `.vscode/`, `.obsidian/app.json`, `.claude/settings.json`, `.gitignore` | Only the framework repo; wikis receive changes via `upgrade` |
| **Wiki-owned** | `wiki.config.yaml`, `README.md`, `raw/`, `wiki/` | The wiki's users and agent |
| **Generated** | `wiki/index.md` (+ `wiki/_meta/index-*.md` when split), `.claude/agents/`, `.claude/skills/`, `.github/agents/wiki-*.agent.md`, `.codex/agents/` | `wiki.py index` and `wiki.py sync`, run by the pre-commit hook |

Local rules belong in `wiki.config.yaml` (`scope`, `style_rules`, `confidentiality`,
`extra_categories`) — never in `AGENTS.md`, so upgrades never conflict.

## Upgrading a wiki
```bash
python3 tools/wiki.py upgrade --dry-run   # what would change
python3 tools/wiki.py upgrade             # clone framework.repo@framework.ref and apply
python3 tools/wiki.py upgrade --from ../llm-wiki   # use a local checkout instead
git diff && git commit -am "upgrade: framework"
```
Upgrade overwrites framework files, **adds** new ones, **keeps** local-only files (e.g. a
custom template — reported as `kept`), regenerates the generated files, writes
`.agents/framework.lock` (repo, commit, date) and logs the upgrade. It never touches
wiki-owned files. If the framework repo is private, set `framework.repo` to an SSH URL.

## Changing the framework
1. Work in the framework repo (`llm-wiki`).
2. Edit the canonical sources only:
   - schema → `AGENTS.md` (keep it short: conventions only; procedures go in skills);
   - operations → `.agents/skills/<name>/SKILL.md`;
   - subagents → `.agents/agents/<name>.md` (`access: read-only | write`);
   - page templates → `templates/`; new-wiki skeleton → `templates/skeleton/`;
   - tooling → `tools/wiki.py` (stdlib only, Python 3.8+); new framework paths → `tools/framework-manifest.txt`.
3. `python3 tools/wiki.py sync` (or just commit — the hook runs it).
4. `python3 -m unittest discover -s tests -v`.
5. Push; then `python3 tools/wiki.py upgrade` in each wiki.

CI (`.github/workflows/wiki-check.yml`) runs on every repo: `sync --check`, `index --check`,
`lint --quick`, and the tests in the framework repo.

## How each agent tool loads the framework

| | GitHub Copilot | Codex | Claude Code |
|---|---|---|---|
| Schema | `AGENTS.md` (+ short `.github/copilot-instructions.md`) | `AGENTS.md` | `CLAUDE.md` → `@AGENTS.md` |
| Operations | `.agents/skills/` → `/ingest` | `.agents/skills/` → `$ingest` | `.claude/skills/` (generated) → `/ingest` |
| Main agent | `.github/agents/wiki.agent.md` ("Wiki") | default session | default session |
| Subagents | `.github/agents/wiki-*.agent.md` | `.codex/agents/*.toml` | `.claude/agents/*.md` |

`.vscode/settings.json` makes Copilot ignore the generated `.claude/` copies so nothing
appears twice.

## Git hook
`.githooks/pre-commit` runs `wiki.py sync` and `wiki.py index` and stages their output.
`new`, `init` and `upgrade` enable it; on a fresh clone run
`git config core.hooksPath .githooks` (`wiki.py status` reminds you).

## Scaling
- The index splits per section above `index.split_after` pages (default 300); agents then
  read only the relevant `wiki/_meta/index-<section>.md`.
- `wiki.py search` is a simple ranked keyword search. For large wikis add
  [qmd](https://github.com/tobi/qmd) (hybrid BM25/vector, CLI + MCP).
