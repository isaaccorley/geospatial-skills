# viewtif

Interactive Qt viewer for GeoTIFF, HDF/HDF5, NetCDF, and Esri FileGDB rasters.

## Options

| Option | Description |
|--------|-------------|
| `--band N` | Select band from multi-band file |
| `--rgb R G B` | RGB composite from bands in a single file |
| `--rgbfiles R G B` | RGB composite from three separate files |
| `--subset N` | Select HDF/NetCDF subdataset (0-based index) |
| `--scale N` | Downsample by factor N (loads 1/N² pixels) |
| `--vmin X --vmax Y` | Fix display value range |
| `--nodata VALUE` | Override nodata masking value |
| `--shapefile FILE` | Vector overlay (repeatable for multiple layers) |
| `--shp-color COLOR` | Overlay color (default: cyan) |
| `--shp-width N` | Overlay line width (default: 1.0) |
| `--timestep N` | Jump to NetCDF time index (1-based) |
| `--cartopy on\|off` | Toggle cartopy projection for NetCDF (default: on) |
| `--qgis` | Export and open directly in QGIS |

## Supported Formats

- GeoTIFF (`.tif`, `.tiff`)
- HDF / HDF5 (`.hdf`, `.h5`, `.hdf5`) — requires GDAL
- NetCDF (`.nc`) — install with `uvx --from "viewtif[netcdf]" viewtif`
- Esri FileGDB (`.gdb`) — requires GDAL
- Remote files via HTTPS, S3 (`s3://`), GCS (`/vsigs/`), Azure (`/vsiaz/`)

## Interactive Controls

| Key | Action |
|-----|--------|
| `+` / `-` or mouse wheel | Zoom in / out |
| Arrow keys or `WASD` | Pan |
| `C` / `V` | Increase / decrease contrast |
| `G` / `H` | Increase / decrease gamma |
| `M` | Toggle colormap |
| `[` / `]` | Previous / next band or time step |
| `B` | Toggle basemap |
| `R` | Reset view |

## Recipes

```bash
# Single band with custom range
uvx viewtif temperature.tif --vmin 280 --vmax 320

# Multi-band RGB composite
uvx viewtif sentinel2.tif --rgb 4 3 2

# RGB from separate files
uvx viewtif --rgbfiles red.tif green.tif blue.tif

# HDF subdataset
uvx viewtif data.h5 --subset 1 --band 3

# NetCDF with time step
uvx --from "viewtif[netcdf]" viewtif climate.nc --timestep 100

# Remote S3 file with vector overlay
AWS_NO_SIGN_REQUEST=YES uvx --from "viewtif[geo]" viewtif s3://bucket/raster.tif --shapefile local.shp

# Large file — downsample for performance
uvx viewtif huge_raster.tif --scale 10

# Open in QGIS
uvx viewtif raster.tif --qgis
```
