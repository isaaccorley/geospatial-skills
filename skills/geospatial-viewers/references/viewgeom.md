# viewgeom

Interactive Qt viewer for vector datasets with attribute filtering, DuckDB SQL, and QGIS export.

## Options

| Option | Description |
|--------|-------------|
| `--column <name>` | Numeric or categorical column for coloring |
| `--layer <name>` | Layer name for multi-layer files (`.gpkg`, `.gdb`) |
| `--limit N` | Max features to load (default: 100000) |
| `--simplify <tol\|off>` | Geometry simplification tolerance, or `off` |
| `--point-size px` | Override automatic point sizing |
| `--filter "<expr>"` | Filter with pandas query syntax |
| `--duckdb "<SQL>"` | SQL filtering via DuckDB (use `data` as table name) |
| `--qgis` | Export to temp GeoPackage and open in QGIS |
| `--save <path>` | Save result to file (format from extension) |
| `--version` | Show version |

## Supported Formats

- Shapefile (`.shp`)
- GeoJSON (`.geojson`, `.json`)
- GeoPackage (`.gpkg`)
- GeoParquet (`.parquet`, `.geoparquet`) — install with `uvx --from "viewgeom[parquet]" viewgeom`
- FileGDB (`.gdb`)
- KML / KMZ (`.kml`, `.kmz`)

## Interactive Controls

| Key | Action |
|-----|--------|
| `+` / `-` | Zoom in / out |
| Arrow keys | Pan |
| `[` / `]` | Switch columns |
| `M` | Switch colormap |
| `B` | Toggle basemap |
| `R` | Reset view |

## Recipes

```bash
# Color by attribute
uvx viewgeom landuse.shp --column area_sqkm

# GeoParquet with high feature limit
uvx --from "viewgeom[parquet]" viewgeom data.geoparquet --limit 150000 --simplify off

# Pandas filter
uvx viewgeom earthquake.geojson --filter "mag > 5"

# DuckDB SQL query and open in QGIS
uvx viewgeom earthquake.geojson --duckdb "SELECT * FROM data WHERE mag > 5" --qgis

# Save filtered output
uvx viewgeom earthquake.geojson --duckdb "SELECT mag FROM data WHERE mag > 5" --save filtered.geojson

# Multi-layer GeoPackage
uvx viewgeom countries.gpkg --layer ADM_ADM_2
```
