# GeoTessera Python Library Reference

API reference for using `geotessera` as a Python library.

## Initialization

```python
from geotessera import GeoTessera

gt = GeoTessera(
    dataset_version="v1",      # Tessera version
    cache_dir=None,            # Registry cache (platform default)
    embeddings_dir=None,       # Tile storage (defaults to cwd)
    registry_url=None,         # Custom registry URL
    registry_path=None,        # Local registry.parquet path
    verify_hashes=True         # SHA256 verification
)
```

## Point Sampling

Preferred for most tasks. Only downloads needed tiles.

```python
# Basic: returns (N, 128) float32 array
points = [(0.15, 52.05), (0.25, 52.15)]
embeddings = gt.sample_embeddings_at_points(points, year=2024)

# With metadata: returns (embeddings, metadata_list)
embeddings, metadata = gt.sample_embeddings_at_points(
    points, year=2024, include_metadata=True
)
# metadata[i]: {tile_lon, tile_lat, pixel_row, pixel_col, crs}

# Control downloads
embeddings = gt.sample_embeddings_at_points(
    points, year=2024, auto_download=False  # fail if tiles missing
)
```

**Point input formats:**
- List of `(lon, lat)` tuples
- GeoJSON FeatureCollection with Point geometries
- GeoPandas GeoDataFrame

## Mosaic

For dense raster analysis over a contiguous region.

```python
bbox = (min_lon, min_lat, max_lon, max_lat)
mosaic, transform, crs = gt.fetch_mosaic_for_region(
    bbox=bbox,
    year=2024,
    target_crs="EPSG:4326",
    auto_download=True
)
# mosaic: (H, W, 128) float32
# transform: rasterio Affine
# crs: target CRS string
```

## Single Tile

```python
# Fetch and dequantize
embedding, crs, transform = gt.fetch_embedding(lon=0.15, lat=52.05, year=2024)
# embedding: (H, W, 128) float32

# Download to embeddings_dir
success = gt.download_tile(lon=0.15, lat=52.05, year=2024)
```

## Batch Tile Iteration

```python
tiles = gt.registry.load_blocks_for_region(bounds=bbox, year=2024)

for year, tile_lon, tile_lat, embedding, crs, transform in gt.fetch_embeddings(tiles):
    # Process tile-by-tile, memory-efficient
    pass
```

## Export

```python
# GeoTIFF
gt.export_embedding_geotiff(lon=0.15, lat=52.05, output_path="tile.tif",
                            year=2024, bands=None, compress="lzw")

# Zarr
gt.export_embedding_zarr(lon=0.15, lat=52.05, output_path="tile.zarr",
                         year=2024, bands=None, compress=True)

# Batch export
tiles = gt.registry.load_blocks_for_region(bounds=bbox, year=2024)
gt.export_embedding_geotiffs(tiles_to_fetch=tiles, output_dir="./out",
                             bands=[0, 1, 2], compress="lzw")

# Merge to mosaic GeoTIFF
gt.merge_geotiffs_to_mosaic(
    geotiff_paths=["tile1.tif", "tile2.tif"],
    output_path="mosaic.tif",
    target_crs="EPSG:3857"
)
```

## Registry

```python
gt.registry.get_available_years()           # [2017, ..., 2025]
gt.registry.get_tile_counts_by_year()       # {year: count}
gt.registry.get_landmask_count()            # int

# Discover tiles for a region
tiles = gt.registry.load_blocks_for_region(
    bounds=(min_lon, min_lat, max_lon, max_lat),
    year=2024
)  # Returns [(year, lon, lat), ...]
```

## Tile Abstraction

Format-agnostic tile access:

```python
from geotessera.tiles import Tile

tile = Tile.from_geotiff("path.tif")
tile = Tile.from_npy("path.npy", base_dir=".")
tile = Tile.from_zarr("path.zarr")

embedding = tile.load_embedding()  # (H, W, 128) dequantized
tile.crs, tile.transform, tile.bounds
tile.lon, tile.lat, tile.year, tile.grid_name
```

## Visualization

```python
from geotessera.visualization import (
    visualize_global_coverage,
    create_rgb_mosaic,
    create_pca_mosaic
)

visualize_global_coverage(gt, output_path="coverage.png", year=2024)
create_rgb_mosaic(["tile1.tif", "tile2.tif"], "mosaic_rgb.tif", bands=(0, 1, 2))
create_pca_mosaic(["tile1.tif", "tile2.tif"], "mosaic_pca.tif")
```

## Manual Dequantization

All high-level methods return dequantized data. Only needed for raw NPY files:

```python
from geotessera import dequantize_embedding
import numpy as np

quantized = np.load("grid_0.15_52.05.npy")          # int8
scales = np.load("grid_0.15_52.05_scales.npy")      # float32
dequantized = dequantize_embedding(quantized, scales) # float32
```

## Notes

- Coordinates auto-snap to nearest valid tile center (0.05° offsets)
- Missing points return NaN in the embeddings array
- Progress callbacks accept `(current, total, status)` signature
- Set `GEOTESSERA_SKIP_HASH=1` to disable hash verification via env var
- CRS info comes from separate landmask tiles
