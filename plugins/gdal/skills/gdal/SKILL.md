______________________________________________________________________

## name: gdal description: This skill should be used when working with GDAL command line tools for raster and vector geospatial processing. Covers inspection, reprojection, clipping, raster conversion, mosaics, tiling, rasterization, and COG creation.

# GDAL Skill

Use GDAL command line tools for common raster and vector geospatial workflows.

## Tools

Prefer the smallest tool that fits the task:

- `gdalinfo`: inspect raster metadata
- `ogrinfo`: inspect vector metadata
- `gdalwarp`: reproject, clip, resample, and crop rasters
- `gdal_translate`: convert raster formats, select bands, compress, scale
- `gdalbuildvrt`: build mosaics and band stacks without copying pixels
- `gdaltindex`: create extent polygons for rasters
- `gdal_rasterize`: burn vector data into rasters
- `gdal2tiles.py`: build XYZ tile pyramids
- `ogr2ogr`: convert, reproject, and clip vector files

If GDAL is not installed, ask the user to install it before continuing.

## Workflow

When a user asks for GDAL help:

### 1. Inspect first

```bash
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so
```

Report CRS, bounds, resolution, band count, data type, and geometry type before editing data.

### 2. Pick raster vs vector path

- Raster tasks: `gdalwarp`, `gdal_translate`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2tiles.py`
- Vector tasks: `ogr2ogr`, `ogrinfo`, `gdaltindex`

### 3. Avoid destructive rewrites

- Prefer writing to a new output file
- Preserve CRS and nodata intentionally
- For large rasters, prefer compression and `BIGTIFF=YES`

### 4. Validate output

```bash
gdalinfo OUTPUT.tif
ogrinfo OUTPUT.geojson -so
```

Confirm CRS, extent, dimensions, and band/field structure match the intended result.

## Quick Reference

### Inspection

```bash
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so
```

### Vector conversion and clipping

```bash
# Convert shapefile to GeoJSON and reproject
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp

# Clip vector file to raster extent
gdaltindex -t_srs epsg:4326 -f GeoJSON OUTPUT_EXTENT.geojson INPUT_RASTER.tif
ogr2ogr -f GeoJSON -clipsrc OUTPUT_EXTENT.geojson OUTPUT_CLIPPED.geojson INPUT.shp
```

### Raster reprojection and clipping

```bash
# Reproject raster
gdalwarp -t_srs epsg:4326 INPUT.tif OUTPUT.tif

# Crop raster by vector cutline
gdalwarp -cutline INPUT.shp -crop_to_cutline -dstalpha INPUT.tif OUTPUT.tif
```

### Raster conversion and band selection

```bash
# Extract RGB bands
gdal_translate -b 1 -b 2 -b 3 INPUT.tif OUTPUT.tif

# Make thumbnail
gdal_translate -b 1 -b 2 -b 3 -of JPEG -outsize 400 0 INPUT.tif OUTPUT.jpg

# Quantize float raster to byte
gdal_translate -of GTiff -ot Byte -scale 0 4000 0 255 -co COMPRESS=LZW -co BIGTIFF=YES INPUT.tif OUTPUT.tif
```

### Mosaics and band stacks

```bash
# Mosaic many rasters virtually
gdalbuildvrt OUTPUT.vrt path/to/tiffs/*.tif

# Convert VRT to compressed GeoTIFF
gdal_translate -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 OUTPUT.vrt OUTPUT.tif

# Merge aligned bands into a virtual multiband raster
gdalbuildvrt -separate OUTPUT.vrt BAND_1.tif BAND_2.tif BAND_3.tif
gdal_translate OUTPUT.vrt OUTPUT.tif
```

### Rasterization and tiling

```bash
# Rasterize vector file
gdal_rasterize -burn 1.0 -ot Byte -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES INPUT.shp OUTPUT.tif

# Build XYZ tiles
gdal2tiles.py -z 10-16 INPUT_BYTE.tif OUTPUT/
```

### COG output

```bash
gdalwarp -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 -of COG INPUT.tif OUTPUT.tif
```

Requires GDAL >= 3.1.

## Tips

- Prefer `gdalbuildvrt` before expensive mosaics
- For large GeoTIFFs, use `-co COMPRESS=LZW -co BIGTIFF=YES`
- Confirm pixel size and bounds before rasterizing or resampling
- Use explicit output files instead of in-place edits
- If the user gives a target raster, match its CRS, bounds, width, and height exactly

## Source Note

This skill was adapted from Microsoft AI for Earth geospatial GDAL recipes and generalized into an agent-facing workflow and command reference.
