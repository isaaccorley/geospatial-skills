---
name: reading-portolan
description: Use when exploring, querying, analyzing, or visualizing data from a Portolan catalog (STAC-based cloud-native geospatial data). Covers navigating STAC metadata, querying GeoParquet with DuckDB, cross-dataset joins, geospatial analysis, and creating interactive maps with PMTiles/MapLibre/deck.gl/Potree.
---

# Reading Portolan Data

Explore, analyze, and visualize cloud-native geospatial data from Portolan catalogs.

A Portolan catalog is a STAC-based collection of cloud-native geospatial data — GeoParquet files for vectors, COGs for rasters, COPC for point clouds — served as static files from object storage. No API server needed. You query the data directly with DuckDB, read metadata from STAC JSON, and visualize with PMTiles.

**Specification:** Portolan is defined by the [Portolan Spec](https://github.com/portolan-sdi/portolan-spec). For the most up-to-date details on catalog structure, format requirements, versioning, and best practices, read the spec files directly — especially `core.md`, `structure.md`, `versions.md`, and the format-specific docs under `formats/`. This skill summarizes the key points, but the spec is the authoritative source.

## Tools & Installation

Check which tools are available before starting. Install what's missing.

### Required

**DuckDB** — Primary analysis engine. Handles SQL queries, spatial operations, Parquet reads, and HTTP range requests against remote files.

```bash
# Check
duckdb --version

# Install
brew install duckdb          # macOS
pip install duckdb           # Python
```

DuckDB 1.2+ required. 1.3+ recommended for full spatial/CRS support.

### Recommended

**gpio (geoparquet-io)** — Inspect, validate, convert, and extract GeoParquet files.

```bash
# Check
gpio --version

# Install
pipx install --pre geoparquet-io   # Isolated (recommended)
pip install --pre geoparquet-io    # Or with pip
```

**GDAL/OGR** — Read/convert any geospatial format. Useful for format conversion, reprojection, and accessing formats DuckDB can't read natively.

```bash
# Check
ogr2ogr --version

# Install
brew install gdal            # macOS
conda install -c conda-forge gdal  # conda
pip install gdal             # pip (may need system libs)
```

---

## Step 1: Navigate the Catalog

A Portolan catalog is a directory tree with STAC metadata. Start by reading the catalog structure.

### Catalog Layout

```
catalog-root/
├── catalog.json                 # Root STAC Catalog — lists all collections
├── versions.json                # Catalog-level version tracking
└── {collection_id}/
    ├── collection.json          # STAC Collection — metadata, spatial/temporal extent, assets
    ├── versions.json            # Collection version history + checksums
    ├── {data}.parquet           # Vector data (GeoParquet)
    ├── {data}.pmtiles           # Visualization tiles
    ├── llms.txt                 # AI-readable documentation (if present)
    └── README.md                # Human-readable documentation
```

### Reading STAC Metadata

**Start with `catalog.json`** to discover collections:

```bash
# Local catalog
cat catalog.json | python3 -m json.tool

# Remote catalog (e.g., on Source Cooperative or S3)
curl -s https://data.source.coop/user/catalog-name/catalog.json | python3 -m json.tool
```

The catalog's `links` array lists collections (where `rel` is `"child"`). Each link's `href` points to a `collection.json`.

**Read a collection** to understand the dataset:

```python
import json, urllib.request

collection = json.loads(urllib.request.urlopen(
    "https://data.source.coop/user/catalog/collection-name/collection.json"
).read())

# Key fields
print(collection["title"])           # Human-readable name
print(collection["description"])     # What the data is
print(collection["extent"])          # Spatial bbox + temporal range
print(collection["assets"])          # Available files (parquet, pmtiles, etc.)
print(collection.get("item_assets")) # Schema for item-level assets (partitioned datasets)
```

**Important STAC fields for analysis:**
- `assets.data.href` — Path to the GeoParquet file (relative to collection.json)
- `assets.pmtiles.href` — Path to PMTiles visualization file
- `portolan:styles` — Array of style identifiers (e.g., `["styles/default", "styles/by-category"]`)
- Assets with `"roles": ["style"]` — MapLibre GL style JSONs for visualization (see Step 5)
- `extent.spatial.bbox` — Bounding box `[west, south, east, north]`
- `extent.temporal.interval` — Time range of the data

### Check for llms.txt

Many Portolan collections include an `llms.txt` file with AI-readable documentation about the dataset — column descriptions, usage examples, and context. Always check for it:

```bash
curl -s https://data.source.coop/user/catalog/collection-name/llms.txt
```

---

## Step 2: Query Data with DuckDB

DuckDB reads GeoParquet files directly — local or remote via HTTP. Load the spatial extension for geometry operations.

### Setup

```sql
INSTALL spatial;
LOAD spatial;
INSTALL httpfs;
LOAD httpfs;
```

### Read Local Files

```sql
SELECT * FROM read_parquet('path/to/data.parquet') LIMIT 10;

-- Schema inspection
DESCRIBE SELECT * FROM read_parquet('path/to/data.parquet');

-- Row count
SELECT count(*) FROM read_parquet('path/to/data.parquet');
```

### Read Remote Files

DuckDB supports HTTP range requests — it only downloads the bytes needed:

```sql
SELECT count(*)
FROM read_parquet('https://data.source.coop/user/catalog/collection/data.parquet');

-- S3
SELECT *
FROM read_parquet('s3://bucket/catalog/collection/data.parquet')
LIMIT 10;
```

For S3, configure credentials:
```sql
SET s3_region = 'us-west-2';
-- For public data, no credentials needed if bucket allows anonymous access
SET s3_access_key_id = '';
SET s3_secret_access_key = '';
```

### Common Analytical Queries

**Counting and aggregation:**
```sql
-- How many features?
SELECT count(*) FROM read_parquet('data.parquet');

-- Group by a category
SELECT category, count(*) as n
FROM read_parquet('data.parquet')
GROUP BY category
ORDER BY n DESC;

-- Top N by a numeric field
SELECT name, height
FROM read_parquet('buildings.parquet')
ORDER BY height DESC
LIMIT 5;
```

**Filtering:**
```sql
-- By attribute
SELECT * FROM read_parquet('data.parquet')
WHERE status = 'active' AND year >= 2020;

-- By bounding box (spatial filter)
SELECT * FROM read_parquet('data.parquet')
WHERE ST_Intersects(
    geometry,
    ST_MakeEnvelope(5.0, 52.0, 6.0, 53.0)
);
```

### Geospatial Analysis

```sql
LOAD spatial;

-- Area calculation (use ST_Area on projected geometries)
SELECT name, ST_Area(geometry) as area_m2
FROM read_parquet('polygons.parquet')
ORDER BY area_m2 DESC
LIMIT 10;

-- Distance between features
SELECT a.name, b.name, ST_Distance(a.geometry, b.geometry) as dist
FROM read_parquet('points_a.parquet') a
CROSS JOIN read_parquet('points_b.parquet') b
WHERE ST_Distance(a.geometry, b.geometry) < 1000;

-- Spatial join — which polygon contains each point?
SELECT p.name as point_name, poly.name as region
FROM read_parquet('points.parquet') p
JOIN read_parquet('regions.parquet') poly
  ON ST_Within(p.geometry, poly.geometry);

-- Buffer and intersect
SELECT a.name, count(*) as nearby_count
FROM read_parquet('parks.parquet') a
JOIN read_parquet('buildings.parquet') b
  ON ST_Intersects(ST_Buffer(a.geometry, 500), b.geometry)
GROUP BY a.name;
```

### Cross-Dataset Joins

One of the most powerful features — join datasets across collections in the same catalog:

```sql
-- Example: Which national park has the most buildings?
SELECT
    parks.name as park_name,
    count(*) as building_count
FROM read_parquet('national-parks/national-parks.parquet') parks
JOIN read_parquet('buildings/buildings.parquet') buildings
    ON ST_Within(buildings.geometry, parks.geometry)
GROUP BY parks.name
ORDER BY building_count DESC;

-- Example: Which park has the most monuments?
SELECT
    parks.name as park_name,
    count(*) as monument_count
FROM read_parquet('national-parks/national-parks.parquet') parks
JOIN read_parquet('monuments/monuments.parquet') monuments
    ON ST_Within(monuments.geometry, parks.geometry)
GROUP BY parks.name
ORDER BY monument_count DESC;
```

For very large datasets, spatial joins can be slow. Strategies:
1. **Filter first**: Reduce rows with WHERE clauses or bbox filters before joining
2. **Use bbox columns**: If the parquet has bbox covering columns, DuckDB can use them for predicate pushdown
3. **Materialize subsets**: `CREATE TABLE subset AS SELECT ... WHERE ...` then join the subset

### Partitioned Datasets

When a collection has multiple parquet files (partitioned datasets >2GB), read them with a glob:

```sql
-- Read all partitions
SELECT * FROM read_parquet('buildings/*.parquet') LIMIT 10;

-- Count across all partitions
SELECT count(*) FROM read_parquet('buildings/*.parquet');

-- Remote glob (S3)
SELECT count(*)
FROM read_parquet('s3://bucket/catalog/buildings/*.parquet');
```

### Export Results

```sql
-- To GeoParquet
COPY (SELECT * FROM read_parquet('data.parquet') WHERE ...)
TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);

-- To GeoJSON (for small datasets / web use)
COPY (SELECT * FROM read_parquet('data.parquet') WHERE ...)
TO 'output.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');

-- To CSV (drops geometry)
COPY (SELECT name, value FROM read_parquet('data.parquet'))
TO 'output.csv' (HEADER, DELIMITER ',');
```

---

## Step 3: Inspect with gpio

Use gpio for quick file inspection without writing SQL:

```bash
# File overview
gpio inspect data.parquet

# Detailed stats (row count, bbox, geometry types, CRS, column stats)
gpio inspect stats data.parquet

# Validate cloud-native compliance
gpio check all data.parquet

# Extract a spatial subset
gpio extract data.parquet subset.parquet --bbox "5.0,52.0,6.0,53.0"

# Extract by attribute
gpio extract data.parquet subset.parquet --where "status = 'active'"
```

---

## Step 4: Convert to Legacy Formats with GDAL/OGR

When users need data in traditional GIS formats (Shapefile, GeoPackage, GeoJSON, GeoTIFF, etc.), use GDAL/OGR to convert from Portolan's cloud-native formats.

### Vector Conversion (GeoParquet to legacy)

```bash
# To Shapefile
ogr2ogr output.shp data.parquet

# To GeoPackage
ogr2ogr output.gpkg data.parquet

# To GeoJSON
ogr2ogr output.geojson data.parquet

# To GeoPackage with reprojection
ogr2ogr -t_srs EPSG:4326 output.gpkg data.parquet

# Convert a spatial subset
ogr2ogr -spat 5.0 52.0 6.0 53.0 output.gpkg data.parquet

# Convert with attribute filter
ogr2ogr -where "status = 'active'" output.gpkg data.parquet
```

### Raster Conversion (COG to legacy)

```bash
# COG to standard GeoTIFF
gdal_translate input.tif output.tif -co TILED=NO

# COG to PNG (for preview)
gdal_translate -of PNG -scale input.tif output.png

# Reproject a raster
gdalwarp -t_srs EPSG:4326 input.tif output.tif

# Clip raster to extent
gdalwarp -te 5.0 52.0 6.0 53.0 input.tif output.tif
```

### Reading Remote Files

Use GDAL virtual filesystem prefixes for remote data:

```bash
# HTTP/HTTPS
ogrinfo /vsicurl/https://data.source.coop/user/catalog/collection/data.parquet
ogr2ogr output.gpkg /vsicurl/https://example.com/data.parquet

# S3
ogr2ogr output.gpkg /vsis3/bucket/catalog/collection/data.parquet

# Google Cloud Storage
ogr2ogr output.gpkg /vsigs/bucket/path/data.parquet

# Azure Blob Storage
ogr2ogr output.gpkg /vsiaz/container/path/data.parquet
```

---

## Step 5: Visualize

### IMPORTANT: Always Use PMTiles for Maps

**DO NOT export GeoJSON or bundle data inline for interactive maps.** Portolan collections already include PMTiles files optimized for web display. Use them directly — they stream efficiently via HTTP range requests, handle millions of features, and require zero data processing.

**Always use MapLibre GL JS + PMTiles protocol** for interactive maps. This is the standard stack for Portolan visualization.

### Check for Style JSONs First

Many Portolan collections ship pre-built MapLibre GL style JSONs in a `styles/` directory. **Always check for these before writing styles from scratch** — they provide curated, data-driven cartography that's ready to use or adapt.

#### Discovering Styles

Styles are referenced in `collection.json` in two ways:

1. **`portolan:styles` array** — lists available style identifiers:
   ```json
   "portolan:styles": ["styles/default", "styles/by-category", "styles/by-crop"]
   ```

2. **Assets with `"roles": ["style"]`** — each style has an asset entry with href, title, and description:
   ```json
   {
     "assets": {
       "styles/default": {
         "href": "./styles/default.json",
         "type": "application/json",
         "title": "Default",
         "description": "Agricultural landscape with greens for grassland, yellow for arable crops.",
         "roles": ["style"]
       },
       "styles/by-category": {
         "href": "./styles/by-category.json",
         "type": "application/json",
         "title": "By Crop Category",
         "description": "Distinct colors for each broad crop category.",
         "roles": ["style"]
       }
     }
   }
   ```

To find style files: scan the `assets` object in `collection.json` for entries where `roles` includes `"style"`. The `href` is relative to the collection.json location.

#### Style JSON Format

Each style JSON is a complete MapLibre GL style document (version 8) with sources and layers. Example:

```json
{
  "version": 8,
  "name": "BRP Gewaspercelen — Default",
  "sources": {
    "data": {
      "type": "vector",
      "url": "pmtiles://../brp_gewaspercelen.pmtiles"
    }
  },
  "layers": [
    {
      "id": "parcels-fill",
      "type": "fill",
      "source": "data",
      "source-layer": "brp_gewaspercelen",
      "paint": {
        "fill-color": [
          "match", ["get", "category"],
          "Grasland", "#7EC850",
          "Bouwland", "#E8D44D",
          "Landschapselement", "#4AA02C",
          "#90C060"
        ],
        "fill-opacity": 0.75
      }
    },
    {
      "id": "parcels-outline",
      "type": "line",
      "source": "data",
      "source-layer": "brp_gewaspercelen",
      "paint": { "line-color": "#3D6B2E", "line-width": 0.5 }
    }
  ]
}
```

#### Resolving Relative PMTiles URLs

Style JSONs use relative paths for their PMTiles sources (e.g., `pmtiles://../data.pmtiles`). When using them in a web map, resolve these to absolute URLs based on the collection's base URL:

```javascript
async function loadStyle(collectionBaseUrl, styleRelPath) {
    const styleUrl = new URL(styleRelPath, collectionBaseUrl + "/").href;
    const resp = await fetch(styleUrl);
    const style = await resp.json();

    for (const [key, source] of Object.entries(style.sources)) {
        if (source.url && source.url.startsWith("pmtiles://")) {
            const relativePmtiles = source.url.replace("pmtiles://", "");
            const absolutePmtiles = new URL(relativePmtiles, styleUrl).href;
            source.url = "pmtiles://" + absolutePmtiles;
        }
    }
    return style;
}
```

#### Using a Style JSON Directly

When a collection has style JSONs, use them as the map's style — the simplest approach:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/maplibre-gl/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl/dist/maplibre-gl.css" rel="stylesheet" />
    <script src="https://unpkg.com/pmtiles/dist/pmtiles.js"></script>
    <style>body { margin: 0; } #map { width: 100%; height: 100vh; }</style>
</head>
<body>
<div id="map"></div>
<script>
const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const COLLECTION_BASE = "https://data.source.coop/user/catalog/collection";

async function initMap() {
    const resp = await fetch(`${COLLECTION_BASE}/styles/default.json`);
    const style = await resp.json();

    // Resolve relative PMTiles URLs to absolute
    for (const source of Object.values(style.sources)) {
        if (source.url && source.url.startsWith("pmtiles://")) {
            const rel = source.url.replace("pmtiles://", "");
            const abs = new URL(rel, `${COLLECTION_BASE}/styles/`).href;
            source.url = "pmtiles://" + abs;
        }
    }

    const map = new maplibregl.Map({ container: "map", style });
    map.addControl(new maplibregl.NavigationControl());
}
initMap();
</script>
</body>
</html>
```

#### Using Styles as Inspiration

When building custom visualizations, **read the available style JSONs even if you don't use them directly**. They contain:
- The correct `source-layer` name for the PMTiles file
- Curated color palettes matched to the dataset's attribute values
- Data-driven `match` expressions showing which attribute values exist and how they map to categories
- Filter expressions for thematic views (e.g., showing only landscape elements)

Extract the paint properties and expressions from a style JSON to use in your own map, or adapt the color scheme for a different visualization (e.g., using a style's color mapping in a deck.gl layer).

#### Style Switcher

When multiple styles are available, offer the user a way to switch between them:

```javascript
async function switchStyle(styleName) {
    const resp = await fetch(`${COLLECTION_BASE}/styles/${styleName}.json`);
    const style = await resp.json();
    // Resolve relative URLs (same as above)
    for (const source of Object.values(style.sources)) {
        if (source.url && source.url.startsWith("pmtiles://")) {
            const rel = source.url.replace("pmtiles://", "");
            const abs = new URL(rel, `${COLLECTION_BASE}/styles/`).href;
            source.url = "pmtiles://" + abs;
        }
    }
    map.setStyle(style);
}
```

### MapLibre + PMTiles (No Style JSON Available)

When a collection has no style JSONs, fall back to building the style inline. This is the template:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/maplibre-gl/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl/dist/maplibre-gl.css" rel="stylesheet" />
    <script src="https://unpkg.com/pmtiles/dist/pmtiles.js"></script>
    <style>body { margin: 0; } #map { width: 100%; height: 100vh; }</style>
</head>
<body>
<div id="map"></div>
<script>
const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const map = new maplibregl.Map({
    container: "map",
    style: {
        version: 8,
        sources: {
            data: {
                type: "vector",
                url: "pmtiles://https://data.source.coop/user/catalog/collection/data.pmtiles"
            }
        },
        layers: [{
            id: "data-layer",
            type: "fill",
            source: "data",
            "source-layer": "data",
            paint: {
                "fill-color": "#3388ff",
                "fill-opacity": 0.6,
                "fill-outline-color": "#2266cc"
            }
        }]
    }
});

map.addControl(new maplibregl.NavigationControl());
</script>
</body>
</html>
```

### Multiple Layers from Different Collections

When visualizing data from multiple collections (e.g., parks + buildings), add each as a separate PMTiles source. If either collection has style JSONs, extract their layer definitions and merge them into a single style:

```javascript
const map = new maplibregl.Map({
    container: "map",
    style: {
        version: 8,
        sources: {
            parks: {
                type: "vector",
                url: "pmtiles://https://example.com/catalog/parks/parks.pmtiles"
            },
            buildings: {
                type: "vector",
                url: "pmtiles://https://example.com/catalog/buildings/buildings.pmtiles"
            }
        },
        layers: [
            {
                id: "parks-fill",
                type: "fill",
                source: "parks",
                "source-layer": "parks",
                paint: {
                    "fill-color": "#2d6a4f",
                    "fill-opacity": 0.3
                }
            },
            {
                id: "parks-outline",
                type: "line",
                source: "parks",
                "source-layer": "parks",
                paint: {
                    "line-color": "#1b4332",
                    "line-width": 2
                }
            },
            {
                id: "buildings-fill",
                type: "fill",
                source: "buildings",
                "source-layer": "buildings",
                paint: {
                    "fill-color": ["match", ["get", "gebruiksdoel"],
                        "woonfunctie", "#4361ee",
                        "industriefunctie", "#e63946",
                        "kantoorfunctie", "#f4a261",
                        "winkelfunctie", "#e9c46a",
                        "logiesfunctie", "#2a9d8f",
                        "#999999"
                    ],
                    "fill-opacity": 0.7
                }
            }
        ]
    }
});
```

### Finding PMTiles URLs

Look in `collection.json` for PMTiles assets:

```json
{
  "assets": {
    "pmtiles": {
      "href": "./data.pmtiles",
      "type": "application/vnd.pmtiles",
      "roles": ["visual"]
    }
  }
}
```

The `href` is relative to the collection.json location. Construct the full URL by combining the catalog base URL with the collection path and the href.

### Finding the source-layer Name

The `source-layer` in MapLibre must match the layer name inside the PMTiles file. Common patterns:
- **Check a style JSON first** — if the collection has styles, the `source-layer` value is already set correctly in the layer definitions
- Often matches the filename stem (e.g., `buildings.pmtiles` → source-layer `"buildings"`)
- Check PMTiles metadata if unsure: use the pmtiles JS library or `pmtiles show data.pmtiles` CLI

### Data-Driven Styling

Use MapLibre expressions to style features by their attributes — color by category, size by value, filter interactively:

```javascript
// Color by category
"fill-color": ["match", ["get", "category"],
    "residential", "#4361ee",
    "commercial", "#e63946",
    "#999999"
]

// Opacity by numeric value
"fill-opacity": ["interpolate", ["linear"], ["get", "value"], 0, 0.1, 100, 0.9]

// Filter to show only specific features
"filter": ["==", ["get", "status"], "active"]
```

### Interactive Features

Add popups, hover effects, and click handlers for exploration:

```javascript
// Popup on click
map.on("click", "buildings-fill", (e) => {
    const props = e.features[0].properties;
    new maplibregl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`<strong>${props.name}</strong><br/>Type: ${props.category}`)
        .addTo(map);
});

// Highlight on hover
map.on("mouseenter", "buildings-fill", () => map.getCanvas().style.cursor = "pointer");
map.on("mouseleave", "buildings-fill", () => map.getCanvas().style.cursor = "");
```

### deck.gl (for 3D / Analytical Overlays)

Use deck.gl only when you need 3D extrusion, heatmaps, or analytical overlays that MapLibre can't handle. Still use PMTiles as the data source via `MVTLayer`:

```javascript
import { Deck } from '@deck.gl/core';
import { MVTLayer } from '@deck.gl/geo-layers';

new Deck({
    initialViewState: { longitude: 5.5, latitude: 52.0, zoom: 7, pitch: 45 },
    controller: true,
    layers: [
        new MVTLayer({
            data: "https://example.com/catalog/buildings/buildings.pmtiles",
            getFillColor: [51, 136, 255, 160],
            getElevation: d => d.properties.height * 10,
            extruded: true,
            pickable: true
        })
    ]
});
```

### COG (Cloud-Optimized GeoTIFF) Visualization

For raster data served as COGs:

```javascript
const map = new maplibregl.Map({ /* ... */ });
map.addSource("raster", {
    type: "raster",
    tiles: ["https://titiler.xyz/cog/tiles/{z}/{x}/{y}?url=https://path/to/data.tif"],
    tileSize: 256
});
map.addLayer({ id: "raster-layer", type: "raster", source: "raster" });
```

### Point Clouds with COPC & Potree

For COPC (Cloud-Optimized Point Cloud) data:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/potree-core/dist/potree.js"></script>
    <style>body { margin: 0; } #viewer { width: 100%; height: 100vh; }</style>
</head>
<body>
<div id="viewer"></div>
<script>
const viewer = new Potree.Viewer(document.getElementById("viewer"));
Potree.loadPointCloud("https://path/to/data.copc.laz", "pointcloud", (e) => {
    viewer.scene.addPointCloud(e.pointcloud);
    viewer.fitToScreen();
});
</script>
</body>
</html>
```

---

## Workflow: Answering Questions About a Catalog

When a user points you at a Portolan catalog and asks questions:

1. **Crawl the catalog tree** — Start with `catalog.json`. Follow all `links` where `rel` is `"child"`. Children can be either **collections** (have `type: "Collection"`) or **sub-catalogs** (have `type: "Catalog"`). Sub-catalogs contain their own `links` to more children — recurse until you've found all collections. Build a full inventory of available datasets before answering.

   ```
   catalog.json
   ├── link (child) → rijkswaterstaat/catalog.json    # sub-catalog
   │   ├── link (child) → tunnels/collection.json     # collection
   │   └── link (child) → bridges/collection.json     # collection
   ├── link (child) → kadaster/catalog.json            # sub-catalog
   │   └── link (child) → bag_light/collection.json   # collection
   └── link (child) → parks/collection.json            # collection (direct child)
   ```

2. **Read `collection.json`** for relevant collection(s) — understand fields, spatial/temporal extent, and assets
3. **Check for `llms.txt`** in each collection — get AI-readable documentation about columns and usage
4. **Identify the right parquet file(s)** from the collection assets (look for `assets.data.href` or browse asset entries with `type: "application/vnd.apache.parquet"`)
5. **Query with DuckDB** — answer the question with SQL
6. **For cross-dataset questions** — join across collection parquet files using spatial predicates
7. **For visualization** — check for style JSONs (assets with `"roles": ["style"]`) before building custom styles. Use them directly or extract their color palettes and expressions as a starting point.

### Example: "How many national parks are in the Netherlands?"

```sql
LOAD spatial;
SELECT count(*) FROM read_parquet('national-parks/national-parks.parquet');
```

### Example: "What are the tallest 5 buildings?"

```sql
SELECT identificatie, bouwjaar, oppervlakte_max
FROM read_parquet('kadaster/bag_light/bag-light.parquet')
ORDER BY oppervlakte_max DESC
LIMIT 5;
```

### Example: "Which national park has the most buildings?"

```sql
LOAD spatial;

SELECT
    np.name as park_name,
    count(*) as building_count
FROM read_parquet('national-parks/national-parks.parquet') np
JOIN read_parquet('kadaster/bag_light/bag-light.parquet') b
    ON ST_Within(b.geom, np.geometry)
GROUP BY np.name
ORDER BY building_count DESC
LIMIT 10;
```

For cross-dataset joins on large datasets, filter spatially first to reduce the join cardinality.

---

## Tips

- **Always `LOAD spatial;`** before any geometry operations in DuckDB
- **Check the CRS** — if data is in a projected CRS (like EPSG:28992 for Netherlands), distance/area calculations are in meters. If in EPSG:4326, they're in degrees.
- **Use `DESCRIBE`** to inspect column names and types before querying
- **bbox covering** in GeoParquet enables predicate pushdown — DuckDB skips row groups outside your spatial filter automatically
- **For very large joins**, materialize filtered subsets first rather than joining full tables
- **Remote reads are fast** — DuckDB's HTTP range request support means you don't need to download entire files
- **`--json` output** from portolan and gpio commands is useful for programmatic catalog exploration
- **Partitioned data** — use glob patterns (`*.parquet`) to read all partitions as one table
