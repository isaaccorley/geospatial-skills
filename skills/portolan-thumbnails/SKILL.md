---
name: portolan-thumbnails
description: Generate high-quality thumbnails from Portolan collections using chiitiler (MapLibre GL Native). Renders the collection's actual styles/default.json server-side with optional basemap. Requires Node.js 18+.
---

<!-- freshness: last-verified: 2026-06-12, maps-to: github.com/Kanahiro/chiitiler -->

# High-Quality Thumbnails with Chiitiler

Generate styled thumbnails from Portolan collections by rendering the actual `styles/default.json` server-side using [chiitiler](https://github.com/Kanahiro/chiitiler). This produces hero-quality images matching the browser portal — far better than the default matplotlib-based thumbnails.

**When to use**: For collections that need polished thumbnails (hero images, featured collections). This is opt-in and requires Node.js — the default `portolan check --fix` thumbnails remain the baseline.

**Requirements**:
- Node.js 18+ and npm
- Git (to clone chiitiler)
- A collection with `.pmtiles` and `styles/default.json`

## Quick Start

Run this script in the catalog directory. It renders thumbnails for all collections that have PMTiles and styles.

```bash
#!/usr/bin/env bash
set -euo pipefail

#############################################################################
# CONFIGURATION — edit these
#############################################################################
CATALOG_DIR="/path/to/catalog"           # Catalog root (contains collection dirs)
OUTPUT_FORMAT="png"                       # png | jpg | webp
SIZE=1024                                 # Longest edge in pixels
QUALITY=90                                # JPEG/WebP quality (ignored for PNG)
USE_BASEMAP=true                          # Add basemap under data layers
BASEMAP_URL="https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
# Alternative basemaps:
#   Carto Dark:  https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png
#   OSM:         https://tile.openstreetmap.org/{z}/{x}/{y}.png
#   Stadia:      https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png

#############################################################################
# SETUP — install chiitiler if needed
#############################################################################
CHIITILER_DIR="${CHIITILER_DIR:-/tmp/chiitiler}"

if [ ! -d "$CHIITILER_DIR/node_modules" ]; then
    echo "Installing chiitiler to $CHIITILER_DIR..."
    rm -rf "$CHIITILER_DIR"
    git clone --depth 1 https://github.com/Kanahiro/chiitiler "$CHIITILER_DIR"
    cd "$CHIITILER_DIR" && npm install --silent
fi

#############################################################################
# START SERVER
#############################################################################
PORT=13579
echo "Starting chiitiler on port $PORT..."
cd "$CHIITILER_DIR"

# Multi-process mode (CHIITILER_PROCESSES=0) prevents memory crashes on large batches
# Memory cache improves performance for repeated basemap tile fetches
CHIITILER_PROCESSES=0 npx tsx src/main.ts tile-server \
    --port $PORT \
    --cache memory \
    > /tmp/chiitiler.log 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
for i in {1..30}; do
    curl -s "http://localhost:$PORT/" > /dev/null 2>&1 && break
    sleep 1
done

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "ERROR: chiitiler failed to start. See /tmp/chiitiler.log"
    exit 1
fi
echo "Server ready (PID $SERVER_PID)"

# Ensure cleanup on exit
trap "kill $SERVER_PID 2>/dev/null; echo 'Server stopped'" EXIT

#############################################################################
# RENDER THUMBNAILS
#############################################################################
cd "$CATALOG_DIR"
COUNT=0

for COLLECTION_DIR in */; do
    COLLECTION_DIR="${COLLECTION_DIR%/}"
    
    # Skip if missing required files
    PMTILES_FILE=$(ls "$COLLECTION_DIR"/*.pmtiles 2>/dev/null | head -1) || continue
    [ -f "$COLLECTION_DIR/styles/default.json" ] || continue
    [ -f "$COLLECTION_DIR/collection.json" ] || continue
    
    PMTILES_PATH=$(realpath "$PMTILES_FILE")
    PMTILES_NAME=$(basename "$PMTILES_FILE" .pmtiles)
    
    # Extract bbox from collection.json
    BBOX=$(python3 -c "
import json
c = json.load(open('$COLLECTION_DIR/collection.json'))
bbox = c['extent']['spatial']['bbox'][0]
print(f'{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}')
")
    
    # Build render-ready style (preserves original styles/default.json exactly)
    python3 << PYSTYLE
import json

style = json.load(open('$COLLECTION_DIR/styles/default.json'))

# Configure sources
sources = {}

if $USE_BASEMAP:
    sources['basemap'] = {
        'type': 'raster',
        'tiles': ['$BASEMAP_URL'],
        'tileSize': 256
    }

sources['data'] = {
    'type': 'vector',
    'tiles': ['pmtiles://$PMTILES_PATH/{z}/{x}/{y}']
}

style['sources'] = sources

# Build layer stack
layers = []

if $USE_BASEMAP:
    layers.append({
        'id': 'basemap',
        'type': 'raster',
        'source': 'basemap'
    })
else:
    # White background when no basemap (avoids black in JPEG)
    layers.append({
        'id': 'background',
        'type': 'background',
        'paint': {'background-color': '#ffffff'}
    })

# Add original layers unchanged
layers.extend(style.get('layers', []))
style['layers'] = layers

with open('$COLLECTION_DIR/.render-style.json', 'w') as f:
    json.dump(style, f)
PYSTYLE
    
    # Render thumbnail
    OUTPUT_FILE="$COLLECTION_DIR/${PMTILES_NAME}.thumb.${OUTPUT_FORMAT}"
    
    curl -s -X POST \
        "http://localhost:$PORT/clip.${OUTPUT_FORMAT}?bbox=${BBOX}&size=${SIZE}&quality=${QUALITY}" \
        -H "Content-Type: application/json" \
        -d "{\"style\": $(cat "$COLLECTION_DIR/.render-style.json")}" \
        -o "$OUTPUT_FILE"
    
    # Cleanup temp file
    rm -f "$COLLECTION_DIR/.render-style.json"
    
    # Verify output (100 byte threshold handles edge cases with tiny bboxes)
    if [ -f "$OUTPUT_FILE" ] && [ $(stat -c%s "$OUTPUT_FILE") -gt 100 ]; then
        echo "✓ $COLLECTION_DIR → $(basename $OUTPUT_FILE) ($(stat -c%s "$OUTPUT_FILE") bytes)"
        ((COUNT++))
    else
        echo "✗ $COLLECTION_DIR — render failed"
        rm -f "$OUTPUT_FILE"
    fi
done

echo ""
echo "Done: $COUNT thumbnails generated"
```

## Single Collection

To render just one collection:

```bash
COLLECTION_DIR="/path/to/catalog/my_collection"
CHIITILER_DIR="/tmp/chiitiler"
PORT=13579

# Start server (if not already running)
cd "$CHIITILER_DIR"
CHIITILER_PROCESSES=0 npx tsx src/main.ts tile-server \
    --port $PORT --cache memory &
SERVER_PID=$!
sleep 3

# Render
cd "$COLLECTION_DIR"
PMTILES_PATH=$(realpath *.pmtiles)
PMTILES_NAME=$(basename "$PMTILES_PATH" .pmtiles)

BBOX=$(python3 -c "
import json
c = json.load(open('collection.json'))
bbox = c['extent']['spatial']['bbox'][0]
print(f'{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}')
")

python3 << PYSTYLE
import json
style = json.load(open('styles/default.json'))
style['sources'] = {
    'basemap': {
        'type': 'raster',
        'tiles': ['https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'],
        'tileSize': 256
    },
    'data': {
        'type': 'vector',
        'tiles': ['pmtiles://$PMTILES_PATH/{z}/{x}/{y}']
    }
}
style['layers'] = [
    {'id': 'basemap', 'type': 'raster', 'source': 'basemap'}
] + style.get('layers', [])
json.dump(style, open('.render-style.json', 'w'))
PYSTYLE

curl -s -X POST \
    "http://localhost:$PORT/clip.png?bbox=${BBOX}&size=1024" \
    -H "Content-Type: application/json" \
    -d "{\"style\": $(cat .render-style.json)}" \
    -o "${PMTILES_NAME}.thumb.png"

rm -f .render-style.json
kill $SERVER_PID 2>/dev/null

echo "Generated: ${PMTILES_NAME}.thumb.png"
```

## Basemap Options

The script defaults to **Carto Light**. To change, set `BASEMAP_URL`:

| Style | URL |
|-------|-----|
| **Carto Light** (default) | `https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png` |
| Carto Dark | `https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png` |
| Carto Voyager | `https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png` |
| OpenStreetMap | `https://tile.openstreetmap.org/{z}/{x}/{y}.png` |
| Stadia Smooth | `https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png` |
| Stadia Dark | `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png` |

Set `USE_BASEMAP=false` for a plain white background (smaller file size, no external requests).

## Output Formats

| Format | Use case |
|--------|----------|
| `png` | Lossless, supports transparency, larger files |
| `jpg` | Smaller files, no transparency, good for photos |
| `webp` | Best compression, modern browser support |

## How It Works

1. **Reads `styles/default.json`** — the collection's actual portal style
2. **Rewrites sources** — points to local PMTiles via `pmtiles://` protocol
3. **Adds basemap layer** — underneath original layers (optional)
4. **Renders via chiitiler** — MapLibre GL Native server-side rendering
5. **Preserves original styling** — colors, opacity, outlines unchanged

The original `styles/default.json` is never modified. Only a temporary `.render-style.json` is created and deleted after rendering.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "npm install" fails | Ensure Node.js 18+: `node --version` |
| Server won't start | Check port: `lsof -i :13579` |
| Server crashes mid-batch | Ensure `CHIITILER_PROCESSES=0` is set (enables multi-process mode) |
| Empty/black image | Verify PMTiles has data in the bbox extent |
| Very thin/small image | Collection has near-zero bbox height/width — this is valid |
| Basemap not loading | Check network access to tile server |
| Very slow rendering | Large bbox or high zoom — reduce `SIZE` |

## After Generating

The thumbnails are ready to use. To sync to remote:

```bash
cd /path/to/catalog
portolan push s3://bucket/catalog
```

The `versions.json` will auto-update with the new thumbnail checksums.
