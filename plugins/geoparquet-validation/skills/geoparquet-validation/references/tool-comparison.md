# GeoParquet Tool Comparison

## Feature Matrix

| Feature                   | gpio          | GDAL/ogr2ogr | GeoPandas   | DuckDB    |
| ------------------------- | ------------- | ------------ | ----------- | --------- |
| GeoParquet read/write     | Excellent     | Good         | Good        | Good      |
| Hilbert sorting           | Yes (default) | No           | No          | Manual    |
| Bbox column + covering    | Yes           | No           | No          | Manual    |
| STAC generation           | Yes           | No           | No          | No        |
| Cloud storage direct      | Yes           | Limited      | Via fsspec  | Yes       |
| BigQuery extraction       | Yes           | No           | No          | No        |
| ArcGIS Feature Service    | Yes           | No           | No          | No        |
| PMTiles output            | Yes (plugin)  | No           | No          | No        |
| Best practices by default | Yes           | No           | No          | No        |
| SQL queries               | Basic         | Limited      | Python only | Excellent |

## When to Use Each Tool

**Use gpio when:**

- Converting any geospatial format to GeoParquet
- You want best practices applied automatically
- Working with remote files/cloud storage
- Extracting from BigQuery or ArcGIS
- Publishing STAC metadata
- Creating PMTiles from GeoParquet

**Use DuckDB when:**

- Need complex SQL joins/aggregations
- Performing spatial analysis across multiple files
- Working interactively in notebooks
- Already have data in DuckDB tables
- Need custom transformations before final export

**Use GDAL/ogr2ogr when:**

- Converting obscure legacy formats
- Interfacing with PostGIS or databases
- Existing workflows already depend on GDAL

Then convert final output to optimized GeoParquet with gpio.

**Use GeoPandas when:**

- Interactive Python data exploration
- Data cleaning/transformation in pandas workflow
- Small to medium datasets that fit in memory

Then write final output with gpio for proper optimization.

## Key Differences

### gpio vs GDAL

GDAL can write Parquet/GeoParquet, but:

- Does not apply Hilbert sorting
- Does not add bbox covering metadata automatically
- No validation tools
- No STAC generation
- More complex CLI for common tasks

Example with GDAL:

```bash
ogr2ogr -f Parquet output.parquet input.geojson
# Must manually sort, set compression, etc.
```

With gpio:

```bash
gpio convert geoparquet input.geojson output.parquet
# Best practices applied automatically
```

### gpio vs GeoPandas

GeoPandas writes GeoParquet via PyArrow, but:

- Loads entire dataset into memory
- No spatial sorting
- No optimization helpers
- No validation

Example with GeoPandas:

```python
import geopandas as gpd

gdf = gpd.read_file("input.geojson")
gdf.to_parquet("output.parquet")
```

Good for interactive work, not ideal for production/distribution.

### gpio vs DuckDB

DuckDB is more flexible for SQL, but requires manual best practices:

```sql
COPY (
  SELECT
    *,
    ST_Extent(geometry) AS bbox
  FROM my_table
  ORDER BY ST_Hilbert(geometry)
) TO 'output.parquet'
(FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 15, ROW_GROUP_SIZE 100000);
```

This works, but you still need:

- Manual bbox covering metadata
- Validation with gpio
- Separate STAC generation

Recommended pattern:

1. Use DuckDB for transformations
1. Export intermediate result
1. Run `gpio add bbox` if needed
1. Run `gpio check all`
1. Run `gpio publish stac`

## Installation

### gpio

```bash
# Isolated install (recommended)
pipx install --pre geoparquet-io

# Or with pip/uv
pip install --pre geoparquet-io
uv pip install --pre geoparquet-io
```

### DuckDB

```bash
pip install "duckdb>=1.5"
```

### gpio-pmtiles plugin

```bash
# If gpio installed via pipx
pipx inject geoparquet-io gpio-pmtiles

# Or with pip
pip install gpio-pmtiles
```
