# viewgeom

Interactive Qt viewer for vector datasets with attribute filtering, DuckDB SQL, and QGIS export.

Requires Python >= 3.9.

## Options

| Option                 | Description                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------- |
| `--column <name>`      | Numeric or categorical column for coloring                                             |
| `--layer <name>`       | Layer name for multi-layer files (`.gpkg`, `.gdb`)                                     |
| `--limit N`            | Max features to load (default: 100000; use `0` for no limit)                           |
| `--simplify <tol/off>` | Geometry simplification tolerance (default: 0.01), or `off` to disable                 |
| `--point-size px`      | Override automatic point sizing                                                        |
| `--filter "<expr>"`    | Filter with pandas query syntax                                                        |
| `--duckdb "<SQL>"`     | Attribute-only SQL filtering via DuckDB (use `data` as table name; no spatial queries) |
| `--qgis`               | Export to temp GeoPackage and open in QGIS                                             |
| `--save <path>`        | Save result to file (format from extension; KML/KMZ/FileGDB saving not supported)      |
| `--version`            | Show version                                                                           |

## Supported Formats

- Shapefile (`.shp`)
- GeoJSON (`.geojson`, `.json`)
- GeoPackage (`.gpkg`)
- GeoParquet (`.parquet`, `.geoparquet`) — install with `uvx --from "viewgeom[parquet]" viewgeom`
- FileGDB (`.gdb`) — use `--layer` to select if multiple layers
- KML / KMZ (`.kml`, `.kmz`) — attribute columns can be used for coloring

## Extras

| Extra     | Install                                   | Enables                      |
| --------- | ----------------------------------------- | ---------------------------- |
| `parquet` | `uvx --from "viewgeom[parquet]" viewgeom` | GeoParquet support (pyarrow) |

DuckDB must be installed separately for `--duckdb` support (`pip install duckdb`).

## Interactive Controls

| Key        | Action                                                   |
| ---------- | -------------------------------------------------------- |
| `+` / `-`  | Zoom in / out                                            |
| Arrow keys | Pan                                                      |
| `[` / `]`  | Switch columns                                           |
| `M`        | Switch colormap                                          |
| `B`        | Toggle basemap (skipped if internet is slow/unavailable) |
| `R`        | Reset view                                               |

## Performance

- Default limit: 100,000 features. High-density datasets may be further limited to 1,000 features.
- Geometries are simplified by default (`--simplify 0.01`). Use `--simplify off` to disable.
- Drawing timeout: 30 seconds. If exceeded, viewgeom exits automatically.

## Column Visualization

- **Numeric columns:** Prints data range and visualization stretch range.
- **Categorical columns:** Prints number of unique categories and shows up to five.
- **Outlines only:** Enter `x` when prompted to skip column coloring.
- **Point data:** Automatic point sizing, overridable with `--point-size`.

## Recipes

```bash
# Color by numeric attribute
uvx viewgeom landuse.shp --column area_sqkm

# Multi-layer GeoPackage
uvx viewgeom countries.gpkg --layer ADM_ADM_2

# GeoParquet with high feature limit
uvx --from "viewgeom[parquet]" viewgeom data.geoparquet --limit 150000 --simplify off

# Pandas filter
uvx viewgeom earthquake.geojson --filter "mag > 5"

# DuckDB SQL query and open in QGIS
uvx viewgeom earthquake.geojson --duckdb "SELECT * FROM data WHERE mag > 5" --qgis

# Save filtered output
uvx viewgeom earthquake.geojson --duckdb "SELECT mag FROM data WHERE mag > 5" --save filtered.geojson

# FileGDB with layer selection
uvx viewgeom /path/to/data.gdb --layer boundaries
```
