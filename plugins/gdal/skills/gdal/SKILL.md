---
name: gdal
description: This skill should be used when working with GDAL command line tools for raster and vector geospatial processing. Covers inspection, reprojection, clipping, raster conversion, mosaics, tiling, rasterization, and COG creation.
---

# GDAL Skill

Use GDAL command line tools for common raster and vector geospatial workflows.

## Tools

Prefer the smallest tool that fits the task:

- `gdalinfo`
- `ogrinfo`
- `gdalwarp`
- `gdal_translate`
- `gdalbuildvrt`
- `gdaltindex`
- `gdal_rasterize`
- `gdal2tiles.py`
- `ogr2ogr`

If GDAL is not installed, ask the user to install it before continuing.

## Workflow

### 1. Inspect first

```bash
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so
```

### 2. Pick raster vs vector path

- Raster tasks: `gdalwarp`, `gdal_translate`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2tiles.py`
- Vector tasks: `ogr2ogr`, `ogrinfo`, `gdaltindex`

### 3. Write a new output

- prefer new output files
- preserve CRS and nodata intentionally
- use compression for large rasters

### 4. Validate output

```bash
gdalinfo OUTPUT.tif
ogrinfo OUTPUT.geojson -so
```

## Quick Reference

```bash
# Inspect
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so

# Vector conversion and clipping
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp
gdaltindex -t_srs epsg:4326 -f GeoJSON OUTPUT_EXTENT.geojson INPUT_RASTER.tif
ogr2ogr -f GeoJSON -clipsrc OUTPUT_EXTENT.geojson OUTPUT_CLIPPED.geojson INPUT.shp

# Raster reprojection and clipping
gdalwarp -t_srs epsg:4326 INPUT.tif OUTPUT.tif
gdalwarp -cutline INPUT.shp -crop_to_cutline -dstalpha INPUT.tif OUTPUT.tif

# Raster conversion
gdal_translate -b 1 -b 2 -b 3 INPUT.tif OUTPUT.tif
gdal_translate -b 1 -b 2 -b 3 -of JPEG -outsize 400 0 INPUT.tif OUTPUT.jpg

# Mosaic and stack
gdalbuildvrt OUTPUT.vrt path/to/tiffs/*.tif
gdal_translate -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 OUTPUT.vrt OUTPUT.tif

# Rasterize and tile
gdal_rasterize -burn 1.0 -ot Byte -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES INPUT.shp OUTPUT.tif
gdal2tiles.py -z 10-16 INPUT_BYTE.tif OUTPUT/

# COG
gdalwarp -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 -of COG INPUT.tif OUTPUT.tif
```

## References

- `references/gdal-recipes.md`
