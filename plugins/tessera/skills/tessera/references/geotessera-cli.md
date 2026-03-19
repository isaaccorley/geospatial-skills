# GeoTessera CLI Reference

Core command patterns for downloading Tessera embeddings with `geotessera`.

## Install

```bash
pip install geotessera
```

## Coverage

```bash
geotessera coverage --output coverage_map.png
geotessera coverage --country uk
geotessera coverage --year 2024 --output coverage_2024.png
geotessera coverage --tile-color blue --tile-alpha 0.3
```

## Download

```bash
geotessera download \
  --bbox "-0.2,51.4,0.1,51.6" \
  --year 2024 \
  --output ./london_tiffs

geotessera download \
  --bbox "-0.2,51.4,0.1,51.6" \
  --format npy \
  --year 2024 \
  --output ./london_arrays

geotessera download \
  --region-file cambridge.geojson \
  --format tiff \
  --year 2024 \
  --output ./cambridge_tiles

geotessera download \
  --bbox "-0.2,51.4,0.1,51.6" \
  --bands "0,1,2" \
  --year 2024 \
  --output ./london_rgb
```

## Visualize

```bash
geotessera visualize ./london_tiffs --type web --output ./london_web
geotessera visualize ./london_tiffs --type rgb --bands "30,60,90" --output ./london_rgb
geotessera serve ./london_web --open
```

## Registry and cache

```bash
geotessera download --cache-dir /path/to/cache --bbox "-0.2,51.4,0.1,51.6" --output ./out
geotessera download --registry-path /path/to/registry.parquet --bbox "-0.2,51.4,0.1,51.6" --output ./out
geotessera download --registry-dir /path/to/registry-dir --bbox "-0.2,51.4,0.1,51.6" --output ./out
```

## Notes

- registry is cached locally
- embedding and landmask files are downloaded to temporary files
- hash verification is enabled by default
- `--skip-hash` disables verification when necessary
