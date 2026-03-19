# GeoParquet Distribution Best Practices

When preparing GeoParquet files for public distribution or cloud storage, optimize for query performance and size efficiency.

## Compression

Use zstd compression at level 15 for distribution:

```bash
# gpio uses zstd by default (level 3 for speed during development)
# For distribution, use higher compression:
gpio convert geoparquet input.geojson output.parquet --compression-level 15
```

This typically reduces file size by 10-30% compared to the default level 3, with slower write times but similar read performance.

## Spatial Ordering (Critical)

Always apply spatial sorting to improve query locality and compression:

```bash
# gpio applies Hilbert sorting by default
gpio convert geoparquet input.geojson output.parquet

# Explicit Hilbert sort on existing file
gpio sort hilbert input.parquet output.parquet
```

Hilbert sorting places nearby features close together in the file, which:

- Improves bbox filter performance
- Increases compression ratio
- Makes row groups spatially coherent

## Bbox Column + Covering Metadata

Add a bbox column for fast spatial filtering:

```bash
# Add bbox column
gpio add bbox input.parquet output.parquet

# Add covering metadata to existing bbox column
gpio add bbox input.parquet output.parquet --bbox-column bbox
```

The bbox column stores feature bounding boxes as a fixed-size list column. Covering metadata tells query engines how to use it for predicate pushdown.

## Row Group Size

For queryable cloud-native files, target row groups of 50k-150k rows:

- **Too small** (\<10k): Too much metadata overhead
- **Too large** (>500k): Poor query selectivity, reads too much data
- **Sweet spot**: 100k rows for most datasets

With DuckDB:

```sql
COPY my_table TO 'output.parquet'
(FORMAT parquet, ROW_GROUP_SIZE 100000, COMPRESSION zstd, COMPRESSION_LEVEL 15);
```

## Partitioning Large Datasets

For datasets >2GB or >10M features, partition into multiple files:

```bash
# KD-tree partitioning (recommended for balanced files)
gpio partition kdtree input.parquet output_dir/ --max-rows-per-file 500000

# Admin boundary partitioning
gpio partition admin input.parquet output_dir/ --by country

# Quadkey grid partitioning
gpio partition quadkey input.parquet output_dir/ --zoom 8
```

Use partitioning when:

- Single file exceeds 2GB
- Features are geographically distributed across continents/countries
- Users typically query subsets by region

## STAC Metadata

Generate STAC for discoverability:

```bash
# Single file
gpio publish stac output.parquet output.stac.json

# Partitioned directory (creates Collection + Items)
gpio publish stac output_dir/ stac/
```

Include in STAC:

- Spatial extent
- Temporal extent (if applicable)
- CRS
- Geometry types
- License
- Provider/creator metadata

## Summary Checklist

Before distribution:

- [ ] zstd compression level 15
- [ ] Hilbert sorted
- [ ] bbox column added
- [ ] Covering metadata present
- [ ] Row groups ~100k rows
- [ ] Partitioned if >2GB
- [ ] STAC metadata generated
- [ ] Uploaded to cloud/object storage
- [ ] Validated with `gpio check all`
