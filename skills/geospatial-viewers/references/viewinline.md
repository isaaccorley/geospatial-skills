# viewinline

Non-interactive terminal-inline viewer for rasters, vectors, and tabular data. Renders via iTerm2 inline image protocol (OSC 1337). No GUI window required.

Requires Python >= 3.9. Particularly useful on HPC systems and remote servers via SSH — images render on your local terminal without X11 forwarding, VNC, or file downloads.

## Compatible Terminals

**Supported:** iTerm2 (macOS), WezTerm, Konsole (Linux/KDE), Rio, Contour.

**Not compatible:** Mac Terminal, GNOME Terminal, Kitty (uses different protocol), Ghostty, Alacritty.

**tmux/screen:** Inline images do not work inside tmux or screen sessions, even with `allow-passthrough on`. Use a plain terminal tab.

## General Options

| Option              | Description                                                       |
| ------------------- | ----------------------------------------------------------------- |
| `--display DISPLAY` | Resize displayed image (0.5=smaller, 2=bigger; default: auto-fit) |

## Raster Options

| Option               | Description                                                              |
| -------------------- | ------------------------------------------------------------------------ |
| `--band BAND`        | Band number (default: 1), or slice number for NetCDF                     |
| `--timestep INTEGER` | Alias for `--band` when working with NetCDF files                        |
| `--subset INTEGER`   | Variable index for NetCDF/HDF files (e.g. `--subset 1`)                  |
| `--colormap`         | Apply colormap (defaults to `terrain`)                                   |
| `--rgb R G B`        | Three band numbers for RGB from a multi-band file (e.g. `--rgb 4 3 2`)   |
| `--rgbfiles R G B`   | Three single-band rasters for RGB composite (or pass as positional args) |
| `--vmin VMIN`        | Min pixel value for display scaling                                      |
| `--vmax VMAX`        | Max pixel value for display scaling                                      |
| `--nodata NODATA`    | Override nodata value                                                    |
| `--gallery [GRID]`   | Show folder of images as thumbnails (e.g. `5x5`)                         |

## Vector Options

| Option              | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| `--color-by COLUMN` | Column to color features by                                               |
| `--colormap`        | Apply colormap (defaults to `terrain`)                                    |
| `--width WIDTH`     | Line width for boundaries (default: 0.7)                                  |
| `--edgecolor COLOR` | Edge color for outlines (default: white)                                  |
| `--layer LAYER`     | Layer name for GeoPackage/multi-layer files                               |
| `--table`           | Display vector/parquet file as tabular data instead of rendering geometry |

## CSV and Parquet Options

| Option                | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `--describe [COLUMN]` | Summary statistics (all columns or one)                  |
| `--hist [COLUMN]`     | Histograms (all columns or one)                          |
| `--bins BINS`         | Histogram bin count (default: 20)                        |
| `--scatter X Y`       | Scatter plot of two columns                              |
| `--unique COLUMN`     | Unique values for a categorical column                   |
| `--where EXPR`        | Filter rows via SQL WHERE (requires DuckDB)              |
| `--sort COLUMN`       | Sort rows by column (ascending; use `--desc` to reverse) |
| `--desc`              | Descending sort (with `--sort`)                          |
| `--limit N`           | Limit output rows                                        |
| `--select COLUMNS`    | Select specific columns (space-separated)                |
| `--sql QUERY`         | Full DuckDB SQL (use `data` as table name)               |

## Supported Formats

- **Rasters:** GeoTIFF (`.tif`), PNG, JPEG, NetCDF (`.nc`), HDF5 (`.h5`, `.hdf5`), HDF4 (`.hdf` — requires GDAL with HDF4 support)
- **Vectors:** GeoJSON, Shapefile, GeoPackage, GeoParquet (`.parquet`, `.geoparquet`)
- **Tabular:** CSV (`.csv`), Parquet (`.parquet` — requires pyarrow)
- **Gallery:** `--gallery 4x3` on a folder of PNG/JPG/TIF images
- **Tabular view of vectors:** Use `--table` to access CSV-style operations on any vector file

## Optional Dependencies

| Package   | Enables                                                |
| --------- | ------------------------------------------------------ |
| `duckdb`  | `--where`, `--sort`, `--sql`, `--limit` with filtering |
| `pyarrow` | Parquet/GeoParquet file support                        |
| `h5py`    | Fallback for HDF5 if GDAL lacks HDF5 support           |

## Recipes

```bash
# Raster with colormap
uvx viewinline temperature.tif --colormap

# RGB composite from three files
uvx viewinline R.tif G.tif B.tif

# RGB bands from a single file
uvx viewinline sentinel2.tif --rgb 4 3 2

# NetCDF — list variables then display one
uvx viewinline file.nc
uvx viewinline file.nc --subset 2
uvx viewinline temp.nc --subset 1 --colormap plasma --vmin 273 --vmax 310

# NetCDF with timestep
uvx viewinline file.nc --subset 1 --timestep 10

# Vector colored by attribute
uvx viewinline boundaries.geojson --color-by population

# GeoParquet vector
uvx viewinline boundaries.geoparquet --color-by population --colormap viridis

# Image gallery
uvx viewinline outputs/ --gallery 4x3

# CSV summary statistics
uvx viewinline data.csv --describe

# CSV histogram for one column
uvx viewinline data.csv --hist area_km2 --bins 30

# CSV scatter plot
uvx viewinline data.csv --scatter longitude latitude

# CSV with SQL query (DuckDB required)
uvx viewinline data.csv --sql "SELECT State, AVG(Income) FROM data GROUP BY State"

# CSV filtering and sorting
uvx viewinline data.csv --where "year > 2010" --sort population --desc --limit 50

# View vector as table (enables CSV-style operations on shapefiles etc.)
uvx viewinline counties.shp --table
uvx viewinline counties.shp --table --describe
uvx viewinline data.geoparquet --table --where "POP > 100000" --sort POP --desc
```
