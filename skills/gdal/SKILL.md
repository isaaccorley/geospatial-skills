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
- `gdaladdo`
- `gdaltindex`
- `gdal_rasterize`
- `gdal2tiles.py`
- `ogr2ogr`

If GDAL is not installed, ask the user to install it before continuing.

## Workflow

### 1. Inspect first

```bash
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so -al
```

One full `gdalinfo` dump on unknown data is worth it; after that, grep for the lines you need (`Size is|Origin|Pixel Size|Band|Overviews|ID\[`) — full WKT dumps are large. For vectors, `-so -al` prints the layer summary; bare `-so` without `-al` or a layer name prints nothing useful.

### 2. Pick raster vs vector path

- Raster tasks: `gdalwarp`, `gdal_translate`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2tiles.py`
- Vector tasks: `ogr2ogr`, `ogrinfo`, `gdaltindex`

### 3. Write a new output

- prefer new output files
- preserve CRS and nodata intentionally
- use compression for large rasters

### 4. Validate output

Use the check that matches the operation — improvising verification is where runs go wrong:

```bash
# Any lossless conversion or mosaic: band checksums must match the input
gdalinfo -checksum INPUT.tif | grep Checksum
gdalinfo -checksum OUTPUT.tif | grep Checksum

# COG: quick layout check, then real validation
gdalinfo OUTPUT.tif | grep -E "LAYOUT|Block=|Overviews"
rio cogeo validate OUTPUT.tif   # via `uv run --with rio-cogeo` if not installed

# Warp/clip: CRS, resolution, per-band min/max in one call
gdalinfo -mm OUTPUT.tif

# Mosaic seamlessness: each quadrant bit-identical to its source tile
# (explicit offsets per tile — avoid shell arrays, the login shell may be zsh)
gdal_translate -q -of VRT -srcwin 0 0 256 256 MOSAIC.tif /tmp/quad.vrt
gdalinfo -checksum /tmp/quad.vrt | grep Checksum   # compare vs TILE_0.tif

# Vector: layer summary + SQLite-dialect counts
ogrinfo OUTPUT.gpkg LAYER -so
ogrinfo OUTPUT.gpkg -dialect SQLite -sql "SELECT COUNT(*) FROM layer"
```

`gdaladdo` on a writable GeoTIFF builds internal overviews; `-ro` forces an external `.ovr` sidecar — so the absence of a `.ovr` file next to the output proves the overviews are internal.

## Quick Reference

```bash
# Inspect
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so

# Vector conversion and clipping
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp
gdaltindex -t_srs epsg:4326 -f GeoJSON OUTPUT_EXTENT.geojson INPUT_RASTER.tif
ogr2ogr -f GeoJSON -clipsrc OUTPUT_EXTENT.geojson OUTPUT_CLIPPED.geojson INPUT.shp

# Raster reprojection (choose -r intentionally: bilinear/cubic for continuous, near for categorical)
gdalwarp -t_srs EPSG:XXXX -tr XRES YRES -r bilinear -co TILED=YES -co COMPRESS=DEFLATE -co PREDICTOR=2 INPUT.tif OUTPUT.tif

# Raster clipping
gdal_translate -srcwin XOFF YOFF XSIZE YSIZE INPUT.tif OUTPUT.tif   # by pixel window (exact, no resampling)
gdal_translate -projwin ULX ULY LRX LRY INPUT.tif OUTPUT.tif        # by georeferenced bounds
gdalwarp -cutline INPUT.shp -crop_to_cutline -dstalpha INPUT.tif OUTPUT.tif   # by polygon

# Raster conversion
gdal_translate -b 1 -b 2 -b 3 INPUT.tif OUTPUT.tif
gdal_translate -b 1 -b 2 -b 3 -of JPEG -outsize 400 0 INPUT.tif OUTPUT.jpg

# Mosaic and stack
gdalbuildvrt OUTPUT.vrt path/to/tiffs/*.tif
gdal_translate -co TILED=YES -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 OUTPUT.vrt OUTPUT.tif

# Internal overviews on an existing GeoTIFF (-r near for categorical; -ro writes external .ovr instead)
gdaladdo -r average OUTPUT.tif 2 4 8

# Rasterize and tile
gdal_rasterize -burn 1.0 -ot Byte -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES INPUT.shp OUTPUT.tif
gdal2tiles.py -z 10-16 INPUT_BYTE.tif OUTPUT/

# COG (format-only conversion — smallest tool that fits)
gdal_translate -of COG -co COMPRESS=LZW -co PREDICTOR=2 -co NUM_THREADS=ALL_CPUS INPUT.tif OUTPUT.tif
# use gdalwarp -of COG only when also reprojecting in the same step

# Vector SQL: OGR's default dialect has no GROUP BY, window, or spatial functions —
# pass -dialect SQLite for anything beyond simple SELECT/WHERE
ogr2ogr -f GPKG OUT.gpkg IN.shp -dialect SQLite \
  -sql "SELECT *, ST_Area(ST_Transform(geometry, EPSG)) AS area_m2 FROM layer WHERE landuse IN ('ag')" \
  -t_srs EPSG:XXXX -nln layername
```

## References

- `references/gdal-recipes.md` (the only reference file)
