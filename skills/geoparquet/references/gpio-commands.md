# gpio Command Reference

Quick reference for the most common `gpio` commands when working with GeoParquet.

## Inspection & Analysis

```bash
# Quick overview
gpio inspect file.parquet

# Preview rows
gpio inspect head file.parquet

# Statistics
gpio inspect stats file.parquet

# Full metadata (GeoParquet spec, Parquet structure)
gpio inspect metadata file.parquet
```

## Validation

```bash
# Run all checks
gpio check all file.parquet

# Individual checks
gpio check metadata file.parquet
gpio check bbox file.parquet
gpio check encoding file.parquet
gpio check covering file.parquet

# Auto-fix issues
gpio check all input.parquet --fix --output fixed.parquet
```

## Format Conversion

```bash
# Convert to GeoParquet (Hilbert sorted by default)
gpio convert geoparquet input.geojson output.parquet

# Skip Hilbert sorting (faster, less optimized)
gpio convert geoparquet input.geojson output.parquet --no-sort

# High compression for distribution
gpio convert geoparquet input.geojson output.parquet --compression-level 15

# Convert GeoParquet to GeoJSON
gpio convert geojson input.parquet output.geojson

# Reproject
gpio convert geoparquet input.geojson output.parquet --to-crs EPSG:4326
```

## Data Extraction & Subsetting

Works on local files, URLs, and cloud storage paths.

```bash
# Extract by bounding box (uses bbox column for fast filtering)
gpio extract input.parquet output.parquet --bbox "-74.1,40.7,-73.9,40.8"

# Extract by geometry (GeoJSON, WKT, or file)
gpio extract input.parquet output.parquet --geometry polygon.geojson

# Select specific columns
gpio extract input.parquet output.parquet --select "id,name,geometry"

# Exclude columns
gpio extract input.parquet output.parquet --exclude "large_blob"

# SQL WHERE filter
gpio extract input.parquet output.parquet --where "population > 100000"

# Limit rows
gpio extract input.parquet output.parquet --limit 1000

# Combine filters
gpio extract input.parquet output.parquet \
  --bbox "-74.1,40.7,-73.9,40.8" \
  --where "population > 100000" \
  --select "id,name,population,geometry"
```

## Merging Files

```bash
# Merge multiple files with glob pattern
gpio merge "tiles/*.parquet" merged.parquet

# Extract from remote files (efficient - only downloads needed data)
gpio merge "s3://bucket/tiles/*.parquet" merged.parquet \
  --bbox "-74.1,40.7,-73.9,40.8"
```

## Extract from BigQuery

Requires BigQuery access and credentials configured.

```bash
# Extract entire table
gpio extract bigquery project.dataset.table output.parquet

# With filtering (pushed to BigQuery for efficiency)
gpio extract bigquery project.dataset.table output.parquet \
  --where "state = 'CA'" \
  --select "id,name,geometry"

# Select specific columns
gpio extract bigquery project.dataset.table output.parquet \
  --select "id,geometry"

# Using service account
GOOGLE_APPLICATION_CREDENTIALS=key.json \
  gpio extract bigquery project.dataset.table output.parquet
```

## Extract from ArcGIS Feature Services

```bash
# Public service (no auth)
gpio extract arcgis \
  "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Census/MapServer/3" \
  output.parquet

# With server-side filtering (efficient - reduces download)
gpio extract arcgis \
  "https://...FeatureServer/0" \
  output.parquet \
  --where "POPULATION > 100000"

# With authentication
gpio extract arcgis \
  "https://...FeatureServer/0" \
  output.parquet \
  --token "$ARCGIS_TOKEN"
```

## Sorting

```bash
# Hilbert curve (best for spatial queries)
gpio sort hilbert input.parquet output.parquet

# Sort by column
gpio sort values input.parquet output.parquet --by "timestamp"

# Quadkey ordering
gpio sort quadkey input.parquet output.parquet --zoom 8
```

## Adding Columns & Spatial Indices

```bash
# Bbox column + covering metadata
gpio add bbox input.parquet output.parquet

# H3 hexagonal cells (resolution 0-15, default 9)
# Res 7: ~5km2, Res 9: ~105m2, Res 11: ~2m2
gpio add h3 input.parquet output.parquet --resolution 9

# S2 spherical cells (level 0-30, default 13)
# Level 8: ~1,250km2, Level 13: ~1.2km2, Level 18: ~1,200m2
gpio add s2 input.parquet output.parquet --level 13

# Quadkey (Bing Maps tiles)
gpio add quadkey input.parquet output.parquet --zoom 12

# A5 cells
gpio add a5 input.parquet output.parquet --resolution 9

# KD-tree cell IDs (for balanced partitioning)
gpio add kdtree input.parquet output.parquet --max-features-per-cell 500000

# Administrative divisions via spatial join
# GAUL dataset: adds gaul_continent, gaul_country, gaul_department
gpio add admin-divisions input.parquet output.parquet --dataset gaul

# Overture Maps: adds overture_country, overture_region
gpio add admin-divisions input.parquet output.parquet --dataset overture

# Select specific levels
gpio add admin-divisions input.parquet output.parquet \
  --dataset gaul --levels country,department

# Custom column prefix
gpio add admin-divisions input.parquet output.parquet \
  --dataset gaul --prefix admin_
```

## Partitioning

```bash
# KD-tree (balanced file sizes)
gpio partition kdtree input.parquet output_dir/ --max-rows-per-file 500000

# Admin boundaries
gpio partition admin input.parquet output_dir/ --by country

# Quadkey grid
gpio partition quadkey input.parquet output_dir/ --zoom 8

# By column value
gpio partition values input.parquet output_dir/ --by state
```

## Publishing

```bash
# Generate STAC metadata
gpio publish stac input.parquet output.stac.json

# Upload to S3
gpio publish upload input.parquet s3://my-bucket/data/
```

## Remote Files

```bash
# gpio can read from cloud storage directly
gpio inspect s3://bucket/data.parquet
gpio inspect https://example.com/data.parquet

# Private S3 with profile
AWS_PROFILE=myprofile gpio inspect s3://private-bucket/data.parquet
```

## Convert to PMTiles (Vector Tiles)

Requires `gpio-pmtiles` plugin and `tippecanoe`.

```bash
# If gpio installed via pipx
pipx inject geoparquet-io gpio-pmtiles

# Or with pip
pip install gpio-pmtiles

# Basic conversion
gpio pmtiles create input.parquet output.pmtiles

# With filtering (applied before tile generation)
gpio pmtiles create input.parquet output.pmtiles \
  --where "population > 100000" \
  --minzoom 0 --maxzoom 12

# Stream GeoJSON to tippecanoe (no intermediate files)
gpio convert geojson input.parquet - | \
  tippecanoe -o output.pmtiles -zg --read-parallel

# With filtering and reduced precision for smaller output
gpio convert geojson input.parquet - --where "class = 'road'" | \
  tippecanoe -o roads.pmtiles -zg -ps -pk --drop-densest-as-needed
```

## Common Options

- `--verbose`: Detailed progress output
- `--json`: Machine-readable output
- `--dry-run`: Preview operation without writing
- `--overwrite`: Replace output if it exists
