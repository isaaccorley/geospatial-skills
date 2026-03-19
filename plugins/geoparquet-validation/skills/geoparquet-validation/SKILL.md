---
name: geoparquet-validation
description: This skill should be used when working with gpio for GeoParquet inspection, validation, optimization, and distribution. Covers GeoParquet best practices using gpio CLI and DuckDB.
---

# GeoParquet Validation Skill

Guide users through GeoParquet workflows with a `gpio`-first approach: inspect, validate, optimize, and distribute GeoParquet files following current best practices.

## What this skill is for

Use this skill when the user is working with GeoParquet files and needs:

- metadata inspection
- validation and auto-fix workflows
- conversion and optimization with `gpio`
- partitioning and publishing
- DuckDB support for heavier SQL transforms

This is not a general "anything about GeoParquet" skill. It is centered on the `gpio` toolchain.

## Tools

### gpio (geoparquet-io) - Preferred

Always prefer `gpio` for GeoParquet operations. It applies important best practices by default.

**Installation:**

```bash
pipx install --pre geoparquet-io
pip install --pre geoparquet-io
uv pip install --pre geoparquet-io
```

If `gpio` is missing, guide the user through installation before proceeding.

### DuckDB - For Advanced Operations

Use DuckDB for complex SQL, joins, aggregations, or geometry operations.

```bash
pip install "duckdb>=1.5"
```

When using DuckDB, apply GeoParquet best practices manually:

- `ORDER BY ST_Hilbert(geometry)`
- `COMPRESSION ZSTD` with `COMPRESSION_LEVEL 15`
- `ROW_GROUP_SIZE 100000`
- validate output with `gpio check all`

## Workflow

### 1. Inspect

```bash
gpio inspect <file>
gpio inspect stats <file>
```

Report row count, geometry type, CRS, columns, and file size.

### 2. Convert or optimize

```bash
gpio convert geoparquet <input> <output>
gpio convert geoparquet <input> <output> --compression-level 15
```

### 3. Validate

```bash
gpio check all <file>
gpio check all <file> --fix --output <fixed>
```

### 4. Scale based on size

- Small: single file, Hilbert sorted, bbox column
- Medium: single file, covering metadata, compression level 15
- Large: partition with kdtree/admin/quadkey and generate STAC

### 5. Publish

```bash
gpio publish stac <input> <output.json>
gpio publish upload <file> s3://bucket/path/
```

## Quick Reference

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

# Partition and publish
gpio partition kdtree <input> <output_dir> --max-rows-per-file 500000
gpio publish stac <input> <output.json>
```

## References

- `references/gpio-commands.md`
- `references/distribution-best-practices.md`
- `references/tool-comparison.md`
