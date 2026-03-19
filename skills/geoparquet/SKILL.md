______________________________________________________________________

## name: geoparquet description: This skill should be used when working with GeoParquet files - the cloud-native format for geospatial vector data. Covers best practices for creating, optimizing, and distributing GeoParquet using gpio CLI and DuckDB.

# GeoParquet Skill

Guide users through GeoParquet workflows: creating, optimizing, validating, and distributing GeoParquet files following official best practices.

## What is GeoParquet?

GeoParquet is Apache Parquet with standardized geospatial metadata. It combines Parquet's columnar efficiency with proper geometry encoding (WKB), coordinate reference system metadata, and bounding box optimizations.

**Key advantages over legacy formats:**

- **Cloud-native**: Efficient partial reads via HTTP range requests
- **Columnar**: Read only the columns needed
- **Compressed**: zstd compression typically achieves 5-10x reduction
- **Typed**: Strong schema with geometry type enforcement
- **Indexed**: Bbox covering enables fast spatial queries

______________________________________________________________________

## Tools

### gpio (geoparquet-io) - Preferred

Always prefer gpio for GeoParquet operations. It implements all best practices by default.

**Installation:**

```bash
pipx install --pre geoparquet-io   # Isolated (recommended)
pip install --pre geoparquet-io    # Or with pip
uv pip install --pre geoparquet-io # Or with uv
```

Note: Use `--pre` for latest beta releases (1.0 not yet released).

If gpio is not installed, guide the user through installation before proceeding.

### DuckDB - For Advanced Operations

Use DuckDB for complex SQL, joins, aggregations, or geometry operations. Requires DuckDB 1.5+ for projection/CRS.

```bash
pip install "duckdb>=1.5"
```

When using DuckDB, apply best practices manually:

- `ORDER BY ST_Hilbert(geometry)` for spatial sorting
- `COMPRESSION ZSTD` with `COMPRESSION_LEVEL 15`
- `ROW_GROUP_SIZE 100000`
- Always validate output with `gpio check all`

For detailed tool comparison, see `references/tool-comparison.md`.

______________________________________________________________________

## Core Workflow

When a user provides spatial data:

### 1. Understand the Source

- Format: GeoJSON, Shapefile, FlatGeobuf, GeoPackage, CSV, Parquet
- Location: Local file, URL, cloud storage (S3/GCS/Azure)
- External service: BigQuery table, ArcGIS Feature Service
- Size: Row count and file size

### 2. Explore the Data

```bash
gpio inspect <file>
gpio inspect stats <file>
```

Report: row count, geometry type, CRS, columns, file size.

### 3. Convert with Best Practices

```bash
# Standard (fast, for development)
gpio convert geoparquet <input> <output>

# For distribution (higher compression)
gpio convert geoparquet <input> <output> --compression-level 15
```

### 4. Validate

```bash
gpio check all <output>

# Fix issues if found
gpio check all <output> --fix --output <fixed>
```

### 5. Optimize Based on Size

**Small (\<100MB, \<100k rows):**

- Single file, Hilbert sorted, bbox column

**Medium (100MB-2GB, 100k-10M rows):**

- Single file, Hilbert sorted, bbox + covering metadata
- Row groups 100k, compression level 15

**Large (>2GB, >10M rows):**

- Partition using kdtree, admin, or quadkey
- Generate STAC metadata
- Consider if full dataset is needed or extraction suffices

### 6. Publish

```bash
gpio publish stac <file> <file.stac.json>
gpio publish upload <file> s3://bucket/path/
```

______________________________________________________________________

## Quick Reference

### Essential Commands

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

# Extract subset (works with remote files)
gpio extract <input> <output> --bbox "minx,miny,maxx,maxy"
gpio extract <input> <output> --where "column > value"

# Extract from services
gpio extract bigquery project.dataset.table output.parquet
gpio extract arcgis https://...FeatureServer/0 output.parquet

# Add spatial indices
gpio add bbox <input> <output>
gpio add h3 <input> <output> --resolution 9
gpio add admin-divisions <input> <output> --dataset gaul

# Partition large files
gpio partition kdtree <input> <output_dir> --max-rows-per-file 500000

# Publish
gpio publish stac <input> <output.json>
gpio publish upload <file> s3://bucket/path/
```

For complete command reference, see `references/gpio-commands.md`.

### Distribution Checklist

Before publishing GeoParquet files:

- [ ] zstd compression at level 15
- [ ] Hilbert spatial sorting applied
- [ ] bbox column with covering metadata
- [ ] Row groups 50k-150k rows
- [ ] Partitioned if >2GB
- [ ] STAC metadata generated
- [ ] Validated with `gpio check all`

For detailed best practices, see `references/distribution-best-practices.md`.

______________________________________________________________________

## Common Tasks

| Task                   | Command                                      |
| ---------------------- | -------------------------------------------- |
| Convert to GeoParquet  | `gpio convert geoparquet <input> <output>`   |
| Extract subset by bbox | `gpio extract <input> <output> --bbox "..."` |
| Extract from BigQuery  | `gpio extract bigquery <table> <output>`     |
| Extract from ArcGIS    | `gpio extract arcgis <url> <output>`         |
| Add spatial index      | \`gpio add h3                                |
| Add admin boundaries   | `gpio add admin-divisions <input> <output>`  |
| Validate file          | `gpio check all <file>`                      |
| Partition large file   | `gpio partition kdtree <input> <dir>`        |
| Generate STAC          | `gpio publish stac <input> <output>`         |
| Upload to S3           | `gpio publish upload <file> s3://...`        |
| Convert to PMTiles     | `gpio pmtiles create <input> <output>`       |

______________________________________________________________________

## Tips

- `--verbose` for detailed output
- `--dry-run` to preview operations
- `--json` for machine-readable output
- Always validate with `gpio check all` before publishing
- For large files, warn user about processing time
