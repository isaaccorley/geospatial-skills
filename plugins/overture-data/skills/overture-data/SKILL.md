---
name: overture-data
description: >
  Download Overture Maps data (buildings, places, roads, land use, water, etc.)
  for a bounding box. Returns a GeoDataFrame saved as GeoJSON or GeoPackage.
argument-hint: <data_type> --bbox <minx,miny,maxx,maxy> [--output FILE]
allowed-tools: Bash
---

You are helping the user download Overture Maps data using geoai.

Input: `$@`

Follow these steps in order.

## Step 1 -- Parse arguments

Extract:
- `$0` or the first positional argument as the Overture data type
- `--bbox minx,miny,maxx,maxy` as the bounding box (required)
- `--output FILE` as the output file path (optional, default: `./<data_type>_overture.gpkg`)

Valid Overture data types:
`address`, `building`, `building_part`, `division`, `division_area`,
`division_boundary`, `place`, `segment`, `connector`, `infrastructure`,
`land`, `land_cover`, `land_use`, `water`

If the data type is not recognized, print the list of valid types and ask the user to pick one.

If the user provided natural language (e.g. "get buildings in downtown Nashville"), extract the data type and either infer or ask for the bounding box.

## Step 2 -- Validate the bounding box

Confirm the bounding box has 4 numeric values:
- `minx < maxx` and `miny < maxy`
- Values within WGS84 range

If validation fails, report the issue and ask for corrected coordinates.

## Step 3 -- Download the data

### For building data specifically

```bash
python3 -c "
import geoai

gdf = geoai.download_overture_buildings(
    bbox=(MINX, MINY, MAXX, MAXY),
    output='OUTPUT_PATH',
)
print(f'Features: {len(gdf)}')
print(f'Columns: {list(gdf.columns)}')
print(f'CRS: {gdf.crs}')
print(f'Bounds: {gdf.total_bounds.tolist()}')
print('---')
print('Sample (first 5 rows):')
print(gdf.head().to_string())
"
```

### For all other data types

```bash
python3 -c "
import geoai

gdf = geoai.get_overture_data(
    overture_type='DATA_TYPE',
    bbox=(MINX, MINY, MAXX, MAXY),
    output='OUTPUT_PATH',
)
print(f'Features: {len(gdf)}')
print(f'Columns: {list(gdf.columns)}')
print(f'CRS: {gdf.crs}')
print(f'Bounds: {gdf.total_bounds.tolist()}')
print('---')
print('Sample (first 5 rows):')
print(gdf.head().to_string())
"
```

Replace `DATA_TYPE`, `MINX`, `MINY`, `MAXX`, `MAXY`, and `OUTPUT_PATH` with actual values.

## Step 4 -- Update state

If a state directory exists, update it:

```bash
STATE_DIR=""
test -f .geoai-skills/state.json && STATE_DIR=".geoai-skills"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
PROJECT_ID="$(echo "$PROJECT_ROOT" | tr '/' '-')"
test -f "$HOME/.geoai-skills/$PROJECT_ID/state.json" && STATE_DIR="$HOME/.geoai-skills/$PROJECT_ID"
```

If `STATE_DIR` is set:

```bash
python3 -c "
import json, os
state_file = 'STATE_DIR/state.json'
state = {}
if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)
state.setdefault('downloaded_files', [])
state['downloaded_files'].append('OUTPUT_PATH')
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)
"
```

## Step 5 -- Report results

Summarize:
- Data type downloaded
- Number of features
- Output file path and size
- Column summary
- CRS and spatial extent

Then suggest: *"Use the `gdal` skill to examine the downloaded data, or the `geospatial-viewers` skill to view it."*

## Error handling

- **`import geoai` fails** -> suggest `pip install "geoai-py[extra]"` (the Overture helpers need the extra).
- **`overturemaps` not installed** -> suggest `pip install "geoai-py[extra]"` which includes the overturemaps dependency.
- **No features found** -> suggest expanding the bounding box or trying a different data type.
- **Network error** -> report and suggest retrying.
