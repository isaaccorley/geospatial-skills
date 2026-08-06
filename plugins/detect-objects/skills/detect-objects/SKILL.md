---
name: detect-objects
description: >
  Run pre-trained AI models on geospatial imagery. Detect buildings, cars,
  ships, solar panels, agriculture fields, or use text-prompted segmentation
  with GroundedSAM. Requires GPU for best performance.
argument-hint: <model> <input_raster> [--text PROMPT] [--output FILE]
allowed-tools: Bash
---

You are helping the user run AI object detection on geospatial imagery using geoai.

Input: `$@`

Follow these steps in order.

## Step 1 -- Parse arguments

Extract:
- `$0` as the model name: `buildings`, `cars`, `ships`, `solar-panels`, `parking-lots`, `agriculture`, or `grounded-sam`
- `$1` as the input raster path
- `--text PROMPT` for GroundedSAM text-prompted segmentation (required when model is `grounded-sam`)
- `--output FILE` for the output vector file (default: `./<model>_detections.gpkg`)

If the model name is not recognized, list the available models and ask the user to pick one.

Model mapping:

| Argument | GeoAI Class |
|---|---|
| `buildings` | `geoai.BuildingFootprintExtractor` |
| `cars` | `geoai.CarDetector` |
| `ships` | `geoai.ShipDetector` |
| `solar-panels` | `geoai.SolarPanelDetector` |
| `parking-lots` | `geoai.ParkingSplotDetector` |
| `agriculture` | `geoai.AgricultureFieldDelineator` |
| `grounded-sam` | `geoai.GroundedSAM` |

## Step 2 -- Check GPU availability

```bash
python3 -c "
import torch
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'CUDA: {torch.version.cuda}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB')
else:
    print('GPU: not available (CPU mode)')
    print('Warning: inference will be significantly slower without a GPU')
"
```

If no GPU is available, warn the user but continue.

## Step 3 -- Resolve the input file

If `$1` looks like an absolute path, use it directly. Otherwise:

```bash
find "$PWD" -name "$1" -not -path '*/.git/*' 2>/dev/null
```

If no file specified and state exists, check for recently inspected/downloaded files:

```bash
STATE_DIR=""
test -f .geoai-skills/state.json && STATE_DIR=".geoai-skills"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
PROJECT_ID="$(echo "$PROJECT_ROOT" | tr '/' '-')"
test -f "$HOME/.geoai-skills/$PROJECT_ID/state.json" && STATE_DIR="$HOME/.geoai-skills/$PROJECT_ID"
```

## Step 4 -- Run the detector

### Pre-trained detectors (buildings, cars, ships, solar-panels, parking-lots, agriculture)

```bash
python3 -c "
import geoai

detector = geoai.DETECTOR_CLASS()
gdf = detector.predict(
    'INPUT_PATH',
    output_path='OUTPUT_PATH',
)
print(f'Detections: {len(gdf)}')
print(f'Output: OUTPUT_PATH')
print(f'Columns: {list(gdf.columns)}')
if len(gdf) > 0:
    print('---')
    print('Sample (first 5):')
    print(gdf.head().to_string())
"
```

Replace `DETECTOR_CLASS` with the appropriate class from the mapping table (e.g. `BuildingFootprintExtractor`).

### GroundedSAM (text-prompted segmentation)

```bash
python3 -c "
import geoai

sam = geoai.GroundedSAM()
gdf = sam.predict(
    'INPUT_PATH',
    text_prompt='TEXT_PROMPT',
    output_path='OUTPUT_PATH',
)
print(f'Segments: {len(gdf)}')
print(f'Output: OUTPUT_PATH')
print(f'Columns: {list(gdf.columns)}')
if len(gdf) > 0:
    print('---')
    print('Sample (first 5):')
    print(gdf.head().to_string())
"
```

Replace `TEXT_PROMPT` with the user's text prompt.

Replace `INPUT_PATH` and `OUTPUT_PATH` with actual values before running.

## Step 5 -- Report results

Summarize:
- Model used
- Number of detections/segments
- Output file path
- Sample of results

Then suggest: *"Use the `gdal` skill to inspect the detection output, or the `geospatial-viewers` skill to view it."*

## Error handling

- **`import geoai` fails** -> suggest `pip install geoai-py` (plus `pip install torch torchvision` for the detection models).
- **`import torch` fails** -> suggest installing PyTorch: `pip install torch torchvision`.
- **CUDA out of memory** -> suggest reducing the tile size or processing a smaller area. If the detector accepts a `tile_size` parameter, recommend a smaller value.
- **Model download fails** -> check network connectivity. Models are downloaded from Hugging Face on first use.
- **Input is not a raster** -> suggest using a GeoTIFF file. If the user has a vector file, suggest rasterizing it first (see the `gdal` skill).
- **GroundedSAM without --text** -> ask the user for a text prompt describing what to detect.
