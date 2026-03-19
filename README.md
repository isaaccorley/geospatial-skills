# geospatial-skills

A collection of separately installable geospatial `SKILL.md` packages.

## Current skills

- `geoparquet-validation`: `gpio`-focused GeoParquet validation and distribution workflows
- `gdal`: GDAL command line workflows for raster and vector data
- `tessera`: Tessera embedding downloads with the `geotessera` CLI

## Layout

```text
skills/
  geoparquet-validation/
    SKILL.md
    references/
  gdal/
    SKILL.md
    references/
  tessera/
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
cp -R skills/geoparquet-validation ~/.agent/skills/geoparquet-validation
```

See the docs site for tool-specific install paths.

Contributor workflow, CI, and docs deploy notes live in `.github/CONTRIBUTING.md`.
