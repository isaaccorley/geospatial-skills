# geospatial-skills

A collection of separately installable geospatial `SKILL.md` packages.

## Current skills

- `geoparquet`: GeoParquet workflows with `gpio` and DuckDB

## Layout

```text
skills/
  geoparquet/
    SKILL.md
    references/
docs/
  ...
```

## Docs

```bash
uv sync --group dev
uv run mkdocs serve
```

Build:

```bash
uv run mkdocs build
```

## Install a skill manually

Copy a skill directory into your local skills/plugins folder, for example:

```bash
cp -R skills/geoparquet ~/.claude/skills/geoparquet
```

See the docs site for tool-specific install paths.

Contributor workflow, CI, and docs deploy notes live in `.github/CONTRIBUTING.md`.
