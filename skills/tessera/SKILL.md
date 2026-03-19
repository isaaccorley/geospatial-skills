---
name: tessera
description: This skill should be used when downloading Tessera embeddings with the geotessera CLI. Covers coverage inspection, bbox and region downloads, GeoTIFF vs NPY export, band selection, registry configuration, cache behavior, and local visualization.
---

# Tessera Download Skill

Use the `geotessera` CLI to inspect coverage and download Tessera embeddings for a region.

## What this skill is for

Use this skill when the user needs to:

- check where Tessera embeddings exist
- download embeddings for a bbox or region file
- choose between GeoTIFF and NPY output
- download specific embedding bands
- configure registry and cache behavior
- preview or serve downloaded outputs locally

This skill is centered on the `geotessera` CLI, not the training code for the Tessera model itself.

## Install

```bash
pip install geotessera
```

If the CLI is not installed, guide the user through installation first.

## Key behavior

- only the Parquet registry is cached locally
- embedding tiles are downloaded on demand to temporary files
- downloaded tiles are dequantized during processing
- GeoTIFF export uses landmask tiles for georeferencing
- hash verification is enabled by default

## Workflow

### 1. Check coverage first

```bash
geotessera coverage --output coverage_map.png
geotessera coverage --year 2024 --output coverage_2024.png
geotessera coverage --country uk
```

### 2. Download for a region

Use either a bbox or a vector region file.

```bash
geotessera download \
  --bbox "-0.2,51.4,0.1,51.6" \
  --year 2024 \
  --output ./london_tiffs
```

```bash
geotessera download \
  --region-file cambridge.geojson \
  --year 2024 \
  --output ./cambridge_tiffs
```

### 3. Pick output format

```bash
geotessera download --bbox "-0.2,51.4,0.1,51.6" --format tiff --year 2024 --output ./tiffs
geotessera download --bbox "-0.2,51.4,0.1,51.6" --format npy --year 2024 --output ./arrays
```

### 4. Select bands if needed

```bash
geotessera download \
  --bbox "-0.2,51.4,0.1,51.6" \
  --bands "0,1,2" \
  --year 2024 \
  --output ./rgb_like
```

### 5. Visualize or serve

```bash
geotessera visualize ./tiffs --type web --output ./web
geotessera serve ./web --open
```

## Quick Reference

```bash
geotessera coverage --output coverage_map.png
geotessera coverage --country uk
geotessera coverage --year 2024 --output coverage_2024.png
geotessera download --bbox "-0.2,51.4,0.1,51.6" --year 2024 --output ./out
geotessera download --region-file region.geojson --year 2024 --output ./out
geotessera download --bbox "-0.2,51.4,0.1,51.6" --format npy --year 2024 --output ./arrays
geotessera download --bbox "-0.2,51.4,0.1,51.6" --bands "0,1,2" --year 2024 --output ./subset
geotessera download --cache-dir /path/to/cache --bbox "-0.2,51.4,0.1,51.6" --output ./out
geotessera download --registry-path /path/to/registry.parquet --bbox "-0.2,51.4,0.1,51.6" --output ./out
geotessera visualize ./tiffs --type web --output ./web
geotessera serve ./web --port 8000 --open
```

## Tips

- prefer `coverage` before large downloads
- use `--format tiff` for GIS-ready outputs
- use `--format npy` for array-first ML workflows
- use `--bands` to reduce output size
- keep `--year` explicit
- use a fixed registry path or URL for reproducibility

## References

- `references/geotessera-cli.md`
