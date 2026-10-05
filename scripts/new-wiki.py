#!/usr/bin/env python3
"""Create a new, empty LLM wiki from this template (Windows, macOS, Linux).

Usage:   python3 scripts/new-wiki.py <target-dir> [wiki-id] ["Wiki Name"]
Example: python3 scripts/new-wiki.py ../platform-wiki platform "Platform Engineering Wiki"

Alternative: on GitHub, click "Use this template" on the template repository
(then run /setup-wiki; dates in the seed pages will be the template's).
"""

import datetime as dt
import os
import re
import shutil
import subprocess
import sys

TEMPLATE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORE = shutil.ignore_patterns(".git", "scripts", "__pycache__", "settings.local.json", "workspace*.json")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    target = os.path.abspath(sys.argv[1])
    wiki_id = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"[^a-z0-9]+", "-", os.path.basename(target).lower()).strip("-")
    name = sys.argv[3] if len(sys.argv) > 3 else wiki_id
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", wiki_id):
        sys.exit("error: wiki id must be kebab-case (got %r)" % wiki_id)
    if os.path.exists(target) and os.listdir(target):
        sys.exit("error: %s exists and is not empty" % target)
    today = dt.date.today().isoformat()

    shutil.copytree(TEMPLATE, target, ignore=IGNORE, dirs_exist_ok=True)

    cfg = os.path.join(target, "wiki.config.yaml")
    text = open(cfg, encoding="utf-8").read()
    text = re.sub(r"^id: \S+", "id: " + wiki_id, text, count=1, flags=re.M)
    text = re.sub(r"^name: .*$", "name: " + name, text, count=1, flags=re.M)
    open(cfg, "w", encoding="utf-8").write(text)

    for dirpath, _, filenames in os.walk(os.path.join(target, "wiki")):
        for fn in filenames:
            if fn.endswith(".md"):
                path = os.path.join(dirpath, fn)
                s = open(path, encoding="utf-8").read()
                s = re.sub(r"^(created|updated): \d{4}-\d{2}-\d{2}", r"\g<1>: " + today, s, flags=re.M)
                open(path, "w", encoding="utf-8").write(s)

    log = os.path.join(target, "wiki", "log.md")
    head = open(log, encoding="utf-8").read().split("\n## [", 1)[0]
    open(log, "w", encoding="utf-8").write(
        head.rstrip("\n") + "\n\n"
        "## [%s] setup | %s created from llm-wiki template\n"
        "- Initial structure, schema (AGENTS.md) and config (wiki.config.yaml).\n"
        "- Next step: run `/setup-wiki` to define the domain, then drop sources in `raw/inbox/` and run `/ingest`.\n"
        % (today, name)
    )

    if shutil.which("git"):
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        subprocess.run(["git", "add", "-A"], cwd=target, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "setup: %s created from llm-wiki template" % name], cwd=target, check=False)

    print("Created wiki '%s' (id: %s) in %s" % (name, wiki_id, target))
    print("Next: open it with your agent (Claude Code, Copilot in VS Code, Codex) and run /setup-wiki")
    return 0


if __name__ == "__main__":
    sys.exit(main())
