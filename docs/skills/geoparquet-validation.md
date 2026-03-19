# GeoParquet Validation

Inspect, validate, optimize, and distribute GeoParquet data with `gpio`.

<div class="skill-callout">
  <p class="skill-callout-label">Tools</p>
  <p><code>gpio</code> first. DuckDB for heavier SQL.</p>
</div>

## Install

### Universal

```bash
cp -R skills/geoparquet-validation ~/.agent/skills/geoparquet-validation
```

### Claude

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install geoparquet-validation@geospatial-skills
```

CLI:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install geoparquet-validation@geospatial-skills
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

1. Inspect source format, CRS, geometry type, and size.
1. Convert with GeoParquet defaults.
1. Validate output.
1. Optimize sorting, row groups, and partitioning if the dataset is large.
1. Publish with STAC metadata when needed.

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

- Skill: [skills/geoparquet-validation/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet-validation/SKILL.md)
- Command reference: [skills/geoparquet-validation/references/gpio-commands.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet-validation/references/gpio-commands.md)
- Best practices: [skills/geoparquet-validation/references/distribution-best-practices.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet-validation/references/distribution-best-practices.md)
- Tool comparison: [skills/geoparquet-validation/references/tool-comparison.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geoparquet-validation/references/tool-comparison.md)
- Upstream reference: [geoparquet-io/geoparquet-skill](https://github.com/geoparquet-io/geoparquet-skill)
