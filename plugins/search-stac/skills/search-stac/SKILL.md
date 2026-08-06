---
name: search-stac
description: >
  Search and download satellite imagery from Microsoft Planetary Computer.
  Browse available collections, search by bbox and time range, list assets,
  and download specific items.
argument-hint: <collection|list> [--bbox <minx,miny,maxx,maxy>] [--datetime <range>] [--download] [--output DIR]
allowed-tools: Bash
---

You are helping the user search and download satellite imagery from the
Planetary Computer STAC catalog using geoai.

Input: `$@`

Follow these steps in order.

## Step 1 -- Determine the action

Parse `$@` to identify what the user wants:

- If the input is `list`, `collections`, or asks "what is available": **list collections**.
- If a collection name and `--bbox` are provided: **search for items**.
- If `--download` is present: **download items** after searching.

## Step 2 -- List collections (if requested)

```bash
python3 -c "
import geoai
df = geoai.pc_collection_list()
print(df.to_string())
"
```

If the user provided a filter keyword, pass it:

```bash
python3 -c "
import geoai
df = geoai.pc_collection_list(filter_by='FILTER')
print(df.to_string())
"
```

Report the available collections and stop (unless the user also specified a search).

## Step 3 -- Search for items

Parse the collection name, bounding box (`--bbox`), and optional datetime range (`--datetime`).

The datetime range should be in the format `YYYY-MM-DD/YYYY-MM-DD` (start/end).

```bash
python3 -c "
import geoai

items = geoai.pc_stac_search(
    collection='COLLECTION',
    bbox=[MINX, MINY, MAXX, MAXY],
    time_range='TIME_RANGE',
    limit=LIMIT,
)
print(f'Found {len(items)} items')
print('---')
for item in items[:20]:
    assets = list(item.assets.keys())
    print(f'  {item.id}: {item.datetime} - assets: {assets}')
"
```

Replace `COLLECTION`, `MINX`, `MINY`, `MAXX`, `MAXY`, `TIME_RANGE`, and `LIMIT` with actual values. Use `limit=10` by default.

If `time_range` was not specified, omit it or pass `None`.

## Step 4 -- List assets for an item (optional)

If the user asks about available assets or bands for a specific item:

```bash
python3 -c "
import geoai
assets = geoai.pc_item_asset_list(item_id='ITEM_ID', collection='COLLECTION')
for name, info in assets.items():
    print(f'  {name}: {info}')
"
```

## Step 5 -- Download items (if --download flag or user confirms)

```bash
python3 -c "
import geoai, os

items = geoai.pc_stac_search(
    collection='COLLECTION',
    bbox=[MINX, MINY, MAXX, MAXY],
    time_range='TIME_RANGE',
    limit=LIMIT,
)

output_dir = 'OUTPUT_DIR'
os.makedirs(output_dir, exist_ok=True)

result = geoai.pc_stac_download(
    items,
    output_dir=output_dir,
)
print(f'Downloaded to: {output_dir}')
for f in os.listdir(output_dir):
    fpath = os.path.join(output_dir, f)
    if os.path.isfile(fpath):
        size_mb = os.path.getsize(fpath) / (1024 * 1024)
        print(f'  {f} ({size_mb:.1f} MB)')
"
```

Default output directory: `./stac_data/`

## Step 6 -- Report and suggest follow-ups

Summarize the search or download results. Then suggest:

- *"Use the `gdal` skill to examine any downloaded files."*
- *"Use the `gdal` skill to clip or mosaic the imagery."*

## Error handling

- **`import geoai` fails** -> suggest `pip install geoai-py`.
- **Invalid collection name** -> list available collections and suggest the closest match.
- **No items found** -> suggest expanding the bbox, adjusting the date range, or trying a different collection.
- **Download failure** -> report the error and suggest retrying with fewer items.
