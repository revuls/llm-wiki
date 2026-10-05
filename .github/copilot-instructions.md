This repository is an LLM-maintained wiki. Follow `AGENTS.md` (the schema) and
`wiki.config.yaml` (this wiki's scope and local rules) for every request.
Use the **Wiki** agent, and run the procedures in `.agents/skills/` (`/ingest`, `/query`,
`/lint`, `/link`, `/setup-wiki`). Never edit files in `raw/`, and never edit `wiki/index.md`
by hand — run `python3 tools/wiki.py index`.
