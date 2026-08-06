---
name: portolan-cli
description: Use when publishing, managing, or converting cloud-native geospatial data catalogs with the Portolan CLI. Covers init, add, check, push, pull, sync, partitioning, and format conversion workflows.
---

# Portolan CLI

Publish and manage cloud-native geospatial data catalogs.

Portolan is a CLI for publishing and managing **cloud-native geospatial data catalogs**. It orchestrates format conversion (GeoParquet, COG), versioning, and sync to object storage (S3, GCS, Azure) — no running servers, just static files.

**Specification:** The [Portolan Spec](https://github.com/portolan-sdi/portolan-spec) defines catalog structure, format requirements, and versioning rules. When in doubt about requirements, read the spec files directly (`core.md`, `structure.md`, `versions.md`, `formats/vector.md`, `formats/raster.md`, `formats/pointcloud.md`, `best-practices.md`) for the most up-to-date information.

**Key concepts:**
- **STAC** (SpatioTemporal Asset Catalog) — The catalog metadata spec. Portolan is a STAC profile, not a competing spec.
- **GeoParquet** — Cloud-optimized vector data (columnar, spatial indexing)
- **COG** (Cloud-Optimized GeoTIFF) — Cloud-optimized raster data (HTTP range requests)
- **COPC** (Cloud-Optimized Point Cloud) — Cloud-optimized point cloud data
- **PMTiles** — Cloud-optimized vector/raster tiles for web map rendering
- **versions.json** — Single source of truth for version history, sync state, and checksums

## Installation

```bash
pipx install portolan-cli    # Isolated (recommended)
pip install portolan-cli     # Or with pip
uv pip install portolan-cli  # Or with uv
```

If portolan is not installed, guide the user through installation before proceeding.

## Catalog Structure

Portolan catalogs use a flat hierarchy with STAC metadata:

```
project/
├── .portolan/
│   ├── config.yaml              # Internal config (sentinel file)
│   └── state.json               # Local sync state
├── catalog.json                 # STAC Catalog (root metadata)
├── versions.json                # Catalog-level version tracking
└── {collection_id}/
    ├── collection.json          # STAC Collection metadata
    ├── versions.json            # Collection-level versioning
    ├── {data}.parquet           # Single-file collection asset
    ├── {data}.pmtiles           # Visualization derivative
    └── thumbnail.png            # Preview image
```

**Single-file collections** (one GeoParquet/COG) use collection-level assets directly — no item directory needed.

**Partitioned collections** (>2GB) use item subdirectories per partition.

All STAC links use relative paths (`SELF_CONTAINED`) — catalogs are portable across hosting locations.

## CLI Commands

### `portolan init`
Initialize a new Portolan catalog.

```bash
portolan init                       # Initialize in current directory
portolan init --auto                # Skip prompts, use defaults
portolan init --title "My Catalog"  # Set title
portolan init /path/to/data --auto  # Initialize in specific directory
```

### `portolan scan`
Scan a directory for geospatial files and potential issues.

```bash
portolan scan                         # Scan current directory
portolan scan --json                  # JSON output
portolan scan /data/geospatial
portolan scan /large/tree --max-depth=2
```

### `portolan check`
Validate a Portolan catalog or check files for cloud-native status.

```bash
portolan check                        # Validate all (metadata + geo-assets)
portolan check --metadata             # Validate metadata only
portolan check --geo-assets           # Check geo-assets only
portolan check --fix                  # Fix both metadata and geo-assets
```

### `portolan add`
Track files in the catalog.

```bash
portolan add demographics/census.parquet
portolan add file1.geojson file2.geojson   # Add multiple files
portolan add imagery/                      # Add all files in directory
portolan add .                             # Add all files in catalog
```

### `portolan push`
Push local catalog changes to cloud object storage.

```bash
portolan push s3://mybucket/catalog --collection demographics
portolan push gs://mybucket/catalog -c imagery --dry-run
portolan push s3://mybucket/catalog
portolan push --dry-run  # Uses configured remote
```

### `portolan pull`
Pull updates from a remote catalog.

```bash
portolan pull s3://mybucket/my-catalog --collection demographics
portolan pull s3://mybucket/catalog -c imagery --dry-run
portolan pull s3://mybucket/catalog
portolan pull s3://mybucket/catalog --workers 4
```

### `portolan sync`
Sync local catalog with remote storage (pull + push).

```bash
portolan sync s3://mybucket/catalog --collection demographics
portolan sync s3://mybucket/catalog -c imagery --dry-run
portolan sync s3://mybucket/catalog -c data --fix --force
```

### `portolan clone`
Clone a remote catalog to a local directory.

```bash
portolan clone s3://mybucket/my-catalog
portolan clone s3://mybucket/my-catalog .
portolan clone s3://mybucket/catalog -c demographics
```

### `portolan status`
Show local vs remote version state for collections.

```bash
portolan status                    # Status for all collections
portolan status -c demographics    # Status for one collection
portolan status --offline          # Skip remote check
portolan status --json             # JSON output for agents
```

### `portolan list`
List all files in the catalog with tracking status.

```bash
portolan list                           # List all files with status
portolan list --collection demographics # Filter by collection
portolan list --tracked-only            # Show only tracked files
```

### `portolan info`
Show information about a file, collection, or catalog.

```bash
portolan info demographics/census.parquet  # File info
portolan info demographics/                # Collection info
portolan info                              # Catalog info
portolan info demographics/census.parquet --json
```

### `portolan rm`
Remove files from tracking.

```bash
portolan rm --keep imagery/old_data.tif     # Safe: untrack only
portolan rm --dry-run vectors/              # Preview
portolan rm -f demographics/census.parquet  # Force delete and untrack
```

### `portolan partition`
Partition a large GeoParquet file for better query performance.

```bash
portolan partition buildings.parquet --preview
portolan partition buildings.parquet output/
portolan partition buildings.parquet output/ --target-rows 50000
```

### `portolan extract`
Extract data from external sources into Portolan catalogs.

```bash
portolan extract arcgis https://services.arcgis.com/.../FeatureServer ./output
portolan extract arcgis URL --layers "Census*" --dry-run
portolan extract arcgis URL --filter "sdn_*" --resume
```

### `portolan metadata`
Manage catalog metadata for README generation.

```bash
portolan metadata init                # Create template at catalog root
portolan metadata init demographics   # Create template for collection
portolan metadata validate            # Validate metadata.yaml
```

### `portolan readme`
Generate README.md from STAC metadata and metadata.yaml.

```bash
portolan readme                    # Generate at catalog root
portolan readme demographics       # Generate for collection
portolan readme --stdout           # Print without writing
portolan readme --check            # CI mode: exit 1 if stale
```

### `portolan stac-geoparquet`
Generate items.parquet for efficient STAC queries.

```bash
portolan stac-geoparquet                       # Generate for ALL collections
portolan stac-geoparquet -c landsat            # Generate for one collection
portolan stac-geoparquet -c imagery --dry-run  # Preview
```

### `portolan config`
Manage catalog configuration.

```bash
portolan config set backend iceberg
portolan config get remote
portolan config list
```

### `portolan clean`
Remove all Portolan metadata while preserving data files.

```bash
portolan clean           # Remove all metadata
portolan clean --dry-run # Preview what would be removed
```

## Common Workflows

### Publishing a New Catalog

```bash
portolan init --title "My Geospatial Data"
portolan scan /data/geospatial
portolan check --geo-assets --fix    # Convert to cloud-native formats
portolan add demographics/
portolan push s3://mybucket/my-catalog --collection demographics
```

### Full Sync (Recommended)

Single command: pull -> init -> scan -> check -> push:

```bash
portolan sync s3://mybucket/my-catalog --collection demographics
portolan sync s3://mybucket/my-catalog -c demographics --fix
```

## Versioning

Versions follow Semantic Versioning per collection:
- **Major**: Breaking changes (schema changes, column removals, CRS changes)
- **Minor**: New features (new columns, new items)
- **Patch**: Data updates (same schema, new data)

Each collection's `versions.json` tracks version history with SHA-256 checksums per asset.

## JSON Output

All commands support `--json` or `--format json`:

```bash
portolan scan . --json
portolan check --format json
portolan --format json init --auto
```

Consistent envelope: `{"success": true, "command": "...", "data": {...}, "errors": []}`.

## Python API

```python
from portolan_cli import Catalog, FormatType, detect_format

catalog = Catalog("/path/to/data")
format_type = detect_format("data.parquet")  # Returns FormatType.GEOPARQUET
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Not inside a Portolan catalog" | Run `portolan init` or navigate into existing catalog |
| "Catalog already exists" | Remove `catalog.json` and `.portolan/` to reinitialize |
| "Push conflict: remote has newer version" | Run `portolan pull` first, or `--force` to overwrite |
| "Pull blocked by uncommitted changes" | Push local changes first, or `--force` to discard |
| Shapefile missing components | Ensure .shp, .shx, .dbf files are all present |
| Non-cloud-native files | Use `portolan check --fix` to convert (vectors -> GeoParquet, rasters -> COG) |
