---
name: geospatial-viewers
description: This skill should be used when viewing, previewing, or inspecting geospatial files from the command line. Covers interactive raster viewing (viewtif), interactive vector viewing (viewgeom), and non-interactive terminal-inline viewing (viewinline) for GeoTIFF, Shapefile, GeoJSON, GeoPackage, GeoParquet, CSV, HDF, NetCDF, and more.
---

# Geospatial Viewers

Three CLI tools for quick-look inspection of geospatial data. Always run them via `uvx` so they are auto-installed without polluting the project environment.

| Tool | Purpose | PyPI |
|------|---------|------|
| **viewtif** | Interactive Qt viewer for rasters (GeoTIFF, HDF, NetCDF, FileGDB) | `uvx viewtif` |
| **viewgeom** | Interactive Qt viewer for vector datasets | `uvx viewgeom` |
| **viewinline** | Non-interactive terminal-inline viewer (rasters, vectors, CSV) | `uvx viewinline` |

## Choosing the Right Tool

- **Need interactive zoom/pan/contrast?** Use `viewtif` (rasters) or `viewgeom` (vectors).
- **Quick inline preview in iTerm2/WezTerm?** Use `viewinline` (no GUI window, renders in terminal).
- **CSV analysis (stats, histograms, SQL)?** Use `viewinline`.
- **Headless server / no display?** Use `viewinline` (requires iTerm2-protocol-compatible terminal).

## Running with uvx

Always prepend `uvx` to auto-install and run without modifying the local environment:

```bash
uvx viewtif file.tif
uvx viewgeom boundaries.geojson
uvx viewinline file.tif
```

For optional extras, use the `--from` flag:

```bash
uvx --from "viewtif[geo]" viewtif raster.tif --shapefile overlay.shp
uvx --from "viewtif[netcdf]" viewtif data.nc
uvx --from "viewgeom[parquet]" viewgeom data.geoparquet
```

## Quick Reference

```bash
# Raster inspection
uvx viewtif image.tif
uvx viewtif image.tif --shapefile boundaries.shp
uvx viewtif image.tif --rgb 4 3 2
uvx viewtif image.tif --vmin 280 --vmax 320
uvx viewtif huge_raster.tif --scale 10

# Vector inspection
uvx viewgeom boundaries.geojson
uvx viewgeom landuse.shp --column area_sqkm
uvx viewgeom earthquake.geojson --filter "mag > 5"
uvx viewgeom earthquake.geojson --duckdb "SELECT * FROM data WHERE mag > 5"

# Terminal-inline preview
uvx viewinline file.tif
uvx viewinline file.tif --colormap
uvx viewinline boundaries.geojson --color-by population
uvx viewinline data.csv --describe
uvx viewinline data.csv --hist area_km2 --bins 30
uvx viewinline data.csv --scatter longitude latitude
uvx viewinline outputs/ --gallery 4x3
```

## References

- `references/viewtif.md`
- `references/viewgeom.md`
- `references/viewinline.md`
