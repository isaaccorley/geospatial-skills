# Install

## Manual

Copy a skill directory into your agent's local skills folder.

```bash
git clone https://github.com/isaaccorley/geospatial-skills.git
cp -R geospatial-skills/skills/geoparquet ~/.claude/skills/geoparquet
```

If your tool uses a different skill directory, copy the same folder there.

## Claude Code / Cowork

This repo now ships its own marketplace metadata:

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install geoparquet@geospatial-skills
```

CLI form:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install geoparquet@geospatial-skills
```

## Local docs

```bash
uv sync
uv run mkdocs serve
```
