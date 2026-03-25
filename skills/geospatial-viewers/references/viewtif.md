# viewtif

Interactive Qt viewer for GeoTIFF, HDF/HDF5, NetCDF, and Esri FileGDB rasters.

Requires Python >= 3.10 and a graphical display environment.

## Options

| Option              | Description                                                                     |
| ------------------- | ------------------------------------------------------------------------------- |
| `--band N`          | Select band from multi-band file                                                |
| `--rgb R G B`       | RGB composite from bands in a single file                                       |
| `--rgbfiles R G B`  | RGB composite from three separate files                                         |
| `--subset N`        | Select HDF/NetCDF subdataset or variable (0-based index)                        |
| `--scale N`         | Downsample by factor N (loads 1/N² pixels)                                      |
| `--vmin X --vmax Y` | Fix display value range (without this, range adjusts per band/timestep)         |
| `--nodata VALUE`    | Override nodata masking value (auto-detected from file metadata by default)     |
| `--shapefile FILE`  | Vector overlay (repeatable for multiple layers; auto-reprojected to raster CRS) |
| `--shp-color COLOR` | Overlay color (default: cyan)                                                   |
| `--shp-width N`     | Overlay line width (default: 1.0)                                               |
| `--timestep N`      | Jump to NetCDF time index (1-based)                                             |
| `--cartopy on/off`  | Toggle cartopy projection for NetCDF (default: on)                              |
| `--qgis`            | Export and open directly in QGIS                                                |

## Supported Formats

- GeoTIFF (`.tif`, `.tiff`)
- HDF / HDF5 (`.hdf`, `.h5`, `.hdf5`) — requires GDAL
- NetCDF (`.nc`) — install with `uvx --from "viewtif[netcdf]" viewtif`; supports 2D and 3D (time, lat, lon) variables only
- Esri FileGDB (`.gdb`) — requires GDAL; use `"OpenFileGDB:/path/to.gdb:RasterName"` to open a specific raster
- Remote files via HTTPS, S3 (`s3://`), GCS (`/vsigs/`), Azure (`/vsiaz/`) — uses GDAL virtual filesystem drivers

## Extras

| Extra    | Install                                | Enables                                 |
| -------- | -------------------------------------- | --------------------------------------- |
| `geo`    | `uvx --from "viewtif[geo]" viewtif`    | Vector overlay support                  |
| `netcdf` | `uvx --from "viewtif[netcdf]" viewtif` | NetCDF support with cartopy projections |

HDF/FileGDB require a system GDAL installation (`brew install gdal` or `apt install gdal-bin`).

## Interactive Controls

| Key                      | Action                                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------- |
| `+` / `-` or mouse wheel | Zoom in / out                                                                               |
| Arrow keys or `WASD`     | Pan                                                                                         |
| `C` / `V`                | Increase / decrease contrast                                                                |
| `G` / `H`                | Increase / decrease gamma                                                                   |
| `M`                      | Toggle colormap (single-band: viridis/magma; NetCDF: RdBu_r/viridis/magma)                  |
| `[` / `]`                | Previous / next band or time step                                                           |
| `B`                      | Toggle basemap (Natural Earth boundaries; shows location info for incompatible projections) |
| `R`                      | Reset view                                                                                  |

## Performance

Datasets over 20 million pixels trigger a warning and confirmation prompt. Use `--scale N` to downsample large files safely. Size warnings are skipped for remote files.

## Limitations

- **NetCDF:** No vector overlays, basemap toggle, or QGIS export. Only 2D/3D variables supported.
- **HDF without CRS:** Vector overlays and basemap may not work if georeferencing is missing.
- **Remote files:** Vector overlay files must be local. NetCDF cannot be opened from HTTP/S3 URLs. HDF and FileGDB remote support is not guaranteed.
- **`--qgis`:** Ignores `--shapefile`, `--scale`, `--vmin/--vmax`, `--band`, and `--nodata`. Not supported for NetCDF.

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

# Multi-variable NetCDF — list variables then pick one
uvx --from "viewtif[netcdf]" viewtif data.nc
uvx --from "viewtif[netcdf]" viewtif data.nc --subset 1

# NetCDF with time step
uvx --from "viewtif[netcdf]" viewtif climate.nc --timestep 100

# NetCDF without cartopy projection
uvx --from "viewtif[netcdf]" viewtif climate.nc --cartopy off

# FileGDB raster
uvx viewtif "OpenFileGDB:/path/to/geodatabase.gdb:RasterName"

# Remote S3 file with vector overlay
AWS_NO_SIGN_REQUEST=YES uvx --from "viewtif[geo]" viewtif s3://bucket/raster.tif --shapefile local.shp

# Multiple vector overlays with custom styling
uvx --from "viewtif[geo]" viewtif image.tif \
  --shapefile boundaries.geojson \
  --shapefile roads.shp \
  --shp-color red --shp-width 2

# Override nodata value
uvx viewtif image.tif --nodata -9999

# Large file — downsample for performance
uvx viewtif huge_raster.tif --scale 10

# Open in QGIS
uvx viewtif raster.tif --qgis
```
