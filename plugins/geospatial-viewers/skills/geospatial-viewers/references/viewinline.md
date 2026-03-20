# viewinline

Non-interactive terminal-inline viewer for rasters, vectors, and CSV data. Renders via iTerm2 inline image protocol (OSC 1337). No GUI window required.

## General Options

| Option | Description |
|--------|-------------|
| `--display DISPLAY` | Resize displayed image (0.5=smaller, 2=bigger; default: auto-fit) |

## Raster Options

| Option | Description |
|--------|-------------|
| `--band BAND` | Band number (default: 1) |
| `--colormap` | Apply colormap (defaults to `terrain`) |
| `--rgb-bands R,G,B` | Comma-separated band numbers for RGB (e.g. `3,2,1`) |
| `--vmin VMIN` | Min pixel value for display scaling |
| `--vmax VMAX` | Max pixel value for display scaling |
| `--nodata NODATA` | Override nodata value |
| `--gallery [GRID]` | Show folder of images as thumbnails (e.g. `5x5`) |

## Vector Options

| Option | Description |
|--------|-------------|
| `--color-by COLUMN` | Column to color features by |
| `--colormap` | Apply colormap (defaults to `terrain`) |
| `--width WIDTH` | Line width for boundaries (default: 0.7) |
| `--edgecolor COLOR` | Edge color for outlines (default: `#F6FF00`) |
| `--layer LAYER` | Layer name for multi-layer files |

## CSV Options

| Option | Description |
|--------|-------------|
| `--describe [COLUMN]` | Summary statistics (all columns or one) |
| `--hist [COLUMN]` | Histograms (all columns or one) |
| `--bins BINS` | Histogram bin count (default: 20) |
| `--scatter X Y` | Scatter plot of two columns |
| `--unique COLUMN` | Unique values for a categorical column |
| `--where EXPR` | Filter rows via SQL WHERE (requires DuckDB) |
| `--sort COLUMN` | Sort rows by column (ascending; use `--desc` to reverse) |
| `--desc` | Descending sort (with `--sort`) |
| `--limit N` | Limit output rows |
| `--select COLUMNS` | Select specific columns (space-separated) |
| `--sql QUERY` | Full DuckDB SQL (use `data` as table name) |

## Supported Formats

- **Rasters:** GeoTIFF, PNG, JPEG
- **Vectors:** GeoJSON, Shapefile, GeoPackage
- **CSV:** Preview, describe, histograms, scatter plots, SQL queries
- **Gallery:** `--gallery 4x3` on a folder of PNG/JPG/TIF images

## Recipes

```bash
# Raster with colormap
uvx viewinline temperature.tif --colormap

# RGB composite from three files
uvx viewinline R.tif G.tif B.tif

# RGB bands from a single file
uvx viewinline sentinel2.tif --rgb-bands 4,3,2

# Vector colored by attribute
uvx viewinline boundaries.geojson --color-by population

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
```
