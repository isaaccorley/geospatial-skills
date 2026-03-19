# Install

## Universal

Clone this repo and copy the portable skill source:

```bash
git clone https://github.com/isaaccorley/geospatial-skills.git
cp -R geospatial-skills/skills/geoparquet ~/.claude/skills/geoparquet
```

If your tool uses a different local skill folder, copy the same `skills/geoparquet`
directory there instead.

## Claude

This repo also ships a Claude marketplace adapter:

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
uv sync --group dev
uv run mkdocs serve
```
