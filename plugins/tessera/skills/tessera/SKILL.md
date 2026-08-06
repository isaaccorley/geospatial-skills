---
name: tessera
description: Use when working with TESSERA satellite embeddings — downloading via CLI, sampling via the Python or R library, choosing between point-based and mosaic approaches, or exporting to GeoTIFF/NPY/Zarr.
---

# Tessera Embeddings Skill

Work with TESSERA satellite embeddings via the `geotessera` CLI, the Python library, or the R library.

## What this skill is for

Use this skill when the user needs to:

- check where TESSERA embeddings exist
- download embeddings for a bbox or region file
- sample embeddings at point locations (Python/R library)
- build mosaics for dense raster analysis (Python library)
- choose between GeoTIFF, NPY, and Zarr output
- configure registry and cache behavior
- preview or serve downloaded outputs locally

## Install

```bash
pip install geotessera                              # Python library + CLI
```
```r
remotes::install_github("lassa-sentinel/GeoTessera") # R library
```

## Key concepts

- embeddings are 128-channel dense vectors at 10m resolution per pixel
- tiles are 0.1° × 0.1° (~11km × 11km), stored as quantized int8 + float32 scales
- the Parquet registry (~few MB) is cached locally; tiles are fetched on demand
- all high-level API methods return dequantized float32 arrays
- hash verification is enabled by default

## Points vs mosaics — choose the right approach

**Prefer `sample_embeddings_at_points()` for most tasks.** It only downloads the tiles it needs and returns a compact (N, 128) array. Use it for labeled site extraction, validation, sparse classification, and any workflow where you have specific coordinates.

**Use `fetch_mosaic_for_region()` only when you need dense per-pixel coverage** — e.g. wall-to-wall land cover classification or spatial clustering over a contiguous area. Mosaics merge and reproject all tiles in a bbox into a single large array, which is memory-intensive for large regions.

```
Have specific point locations?
  YES → sample_embeddings_at_points()
  NO  → Need wall-to-wall raster output?
          YES → fetch_mosaic_for_region()
          NO  → CLI download + export
```

## Python library

```python
from geotessera import GeoTessera

gt = GeoTessera()  # uses default registry and current directory

# --- Point sampling (preferred for most tasks) ---
points = [(0.15, 52.05), (0.25, 52.15), (-1.3, 51.75)]
embeddings = gt.sample_embeddings_at_points(points, year=2024)
# Returns: (N, 128) float32 array, NaN for missing points

# With metadata (tile info, pixel coordinates, CRS)
embeddings, metadata = gt.sample_embeddings_at_points(
    points, year=2024, include_metadata=True
)

# --- Mosaic (dense raster analysis only) ---
bbox = (-0.2, 51.4, 0.1, 51.6)
mosaic, transform, crs = gt.fetch_mosaic_for_region(bbox, year=2024)
# Returns: (H, W, 128) float32 array

# --- Single tile ---
embedding, crs, transform = gt.fetch_embedding(lon=0.15, lat=52.05, year=2024)
# Returns: (H, W, 128) float32, CRS, Affine transform

# --- Export ---
gt.export_embedding_geotiff(lon=0.15, lat=52.05, output_path="tile.tif", year=2024)
gt.export_embedding_zarr(lon=0.15, lat=52.05, output_path="tile.zarr", year=2024)

# --- Registry queries ---
gt.registry.get_available_years()           # [2017, 2018, ..., 2025]
gt.registry.get_tile_counts_by_year()       # {2024: 1234567, ...}
tiles = gt.registry.load_blocks_for_region(bounds=bbox, year=2024)
```

Point inputs accept list of (lon, lat) tuples, GeoJSON FeatureCollections, or GeoPandas GeoDataFrames.

## R library

An R port by Simon Frost (Microsoft Research). Uses R6 classes, sf, terra, and arrow.

```r
remotes::install_github("lassa-sentinel/GeoTessera")
library(GeoTessera)

gt <- geotessera()
tiles <- gt$get_tiles(bbox = c(-0.2, 51.4, 0.1, 51.6), year = 2024)
gt$export_embedding_geotiffs(tiles = tiles, output_dir = "london_tiles")
```

Full R docs: https://lassa-sentinel.github.io/GeoTessera

## CLI workflow

### 1. Check coverage first

```bash
geotessera coverage --output coverage_map.png
geotessera coverage --year 2024 --country uk
```

### 2. Download for a region

```bash
geotessera download --bbox "-0.2,51.4,0.1,51.6" --year 2024 --output ./tiffs
geotessera download --region-file cambridge.geojson --year 2024 --output ./tiffs
```

### 3. Pick output format

```bash
geotessera download --bbox "..." --format tiff --year 2024 --output ./tiffs  # GIS-ready
geotessera download --bbox "..." --format npy  --year 2024 --output ./arrays # ML-friendly
geotessera download --bbox "..." --format zarr --year 2024 --output ./zarr   # cloud-native
```

### 4. Select bands if needed

```bash
geotessera download --bbox "..." --bands "0,1,2" --year 2024 --output ./subset
```

### 5. Visualize or serve

```bash
geotessera visualize ./tiffs --type web --output ./web
geotessera serve ./web --open
```

## Tips

- prefer `sample_embeddings_at_points()` over mosaics for sparse locations
- prefer `coverage` before large CLI downloads
- use `--format tiff` for GIS-ready outputs, `--format npy` for array-first ML
- use `--bands` to reduce output size when only a few channels are needed
- keep `--year` explicit — data is available from 2017 to 2025
- use a fixed registry path or URL for reproducibility

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Building a mosaic just to extract a few points | Use `sample_embeddings_at_points()` instead |
| Downloading all 128 bands when only a few are needed | Use `--bands` (CLI) or the `bands` parameter |
| Not checking coverage before a large download | Run `geotessera coverage` first |
| Forgetting `--year` and getting default year | Always specify `--year` explicitly |

## References

- `references/geotessera-cli.md` — full CLI flag reference
- `references/geotessera-library.md` — Python library API reference
