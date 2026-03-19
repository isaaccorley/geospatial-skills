# GeoParquet

Guide agents through GeoParquet workflows: create, optimize, validate, and
distribute cloud-native geospatial vector data.

<div class="skill-callout">
  <p class="skill-callout-label">Primary tools</p>
  <p><code>gpio</code> first. DuckDB for heavier SQL and geometry work.</p>
</div>

## Install

### Manual

```bash
cp -R skills/geoparquet ~/.claude/skills/geoparquet
```

### OpenSkills

```bash
npx openskills install geoparquet-io/geoparquet-skill
```

### Claude Code

```bash
/plugin marketplace add geoparquet-io/geoparquet-skill
/plugin install geoparquet@geoparquet-skill
```

### Claude Cowork CLI

```bash
claude plugin marketplace add geoparquet-io/geoparquet-skill
claude plugin install geoparquet@geoparquet-skill
```

## Prerequisites

Install `gpio` first:

```bash
pipx install --pre geoparquet-io
```

Alternatives:

```bash
pip install --pre geoparquet-io
uv pip install --pre geoparquet-io
```

Verify:

```bash
gpio --version
```

## Workflow

1. Understand source format, location, service type, and scale.
1. Inspect schema, geometry type, CRS, and size.
1. Convert with GeoParquet defaults.
1. Validate output.
1. Optimize row groups, sorting, and partitioning when datasets get large.
1. Publish with STAC metadata and cloud upload as needed.

## Essential commands

```bash
# Inspect
gpio inspect <file>
gpio inspect stats <file>

# Convert
gpio convert geoparquet <input> <output>
gpio convert geoparquet <input> <output> --compression-level 15

# Validate
gpio check all <file>
gpio check all <file> --fix --output <fixed>

# Extract
gpio extract <input> <output> --bbox "minx,miny,maxx,maxy"
gpio extract <input> <output> --where "column > value"

# Partition + publish
gpio partition kdtree <input> <output_dir> --max-rows-per-file 500000
gpio publish stac <input> <output.json>
```

## Distribution checklist

- zstd compression level 15
- Hilbert sorting
- bbox column plus covering metadata
- row groups in the 50k to 150k range
- partitioning for very large datasets
- `gpio check all` before publish

## Source

- Skill: [skills/geoparquet/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet/SKILL.md)
- Command reference: [skills/geoparquet/references/gpio-commands.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet/references/gpio-commands.md)
- Best practices: [skills/geoparquet/references/distribution-best-practices.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet/references/distribution-best-practices.md)
- Tool comparison: [skills/geoparquet/references/tool-comparison.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet/references/tool-comparison.md)
