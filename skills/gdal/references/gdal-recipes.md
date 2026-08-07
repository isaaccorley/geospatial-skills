# GDAL Recipes

General GDAL command patterns for raster and vector processing.

## Vector recipes

```bash
# Create polygon of raster extent
gdaltindex -t_srs epsg:4326 -f GeoJSON OUTPUT_EXTENT.geojson INPUT_RASTER.tif

# Clip shapefile to raster extent
gdaltindex -t_srs epsg:4326 -f GeoJSON OUTPUT_EXTENT.geojson INPUT_RASTER.tif
ogr2ogr -f GeoJSON -clipsrc OUTPUT_EXTENT.geojson OUTPUT_CLIPPED.geojson INPUT.shp

# Convert shapefile to GeoJSON
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp

# Reproject vector file
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp

# Filter + computed fields need -dialect SQLite (OGR's default dialect
# has no GROUP BY, window functions, or spatial functions)
ogr2ogr -f GPKG OUT.gpkg IN.shp -dialect SQLite \
  -sql "SELECT *, ST_Area(ST_Transform(geometry, EPSG)) AS area_m2 FROM layer WHERE field IN ('a','b')" \
  -t_srs EPSG:XXXX -nln layername
```

## Raster recipes

```bash
# Reproject raster (set resolution and resampling explicitly:
# bilinear/cubic for continuous data, near for categorical)
gdalwarp -t_srs EPSG:XXXX -tr XRES YRES -r bilinear -co TILED=YES -co COMPRESS=DEFLATE -co PREDICTOR=2 INPUT.tif OUTPUT.tif

# Clip by pixel window (exact, no resampling)
gdal_translate -srcwin XOFF YOFF XSIZE YSIZE INPUT.tif OUTPUT.tif

# Clip by georeferenced bounds
gdal_translate -projwin ULX ULY LRX LRY INPUT.tif OUTPUT.tif

# Crop raster based on a shapefile
gdalwarp -cutline INPUT.shp -crop_to_cutline -dstalpha INPUT.tif OUTPUT.tif

# Extract subset of bands
gdal_translate -b 1 -b 2 -b 3 INPUT.tif OUTPUT.tif

# Make thumbnail
gdal_translate -b 1 -b 2 -b 3 -of JPEG -outsize 400 0 INPUT.tif OUTPUT.jpg

# Quantize float raster to byte
gdal_translate -of GTiff -ot Byte -scale 0 4000 0 255 -co COMPRESS=LZW -co BIGTIFF=YES INPUT.tif OUTPUT.tif
```

## Mosaics and band stacks

```bash
# Merge many rasters into a VRT
gdalbuildvrt OUTPUT.vrt path/to/tiffs/*.tif

# Build VRT from list of files
gdalbuildvrt OUTPUT.vrt -input_file_list INPUT_FILES.txt

# Convert VRT to compressed GeoTIFF
gdal_translate -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 OUTPUT.vrt OUTPUT.tif

# Stack aligned bands
gdalbuildvrt -separate OUTPUT.vrt BAND_1.tif BAND_2.tif BAND_3.tif
gdal_translate OUTPUT.vrt OUTPUT.tif

# Internal overviews (-r near for categorical; -ro would write an external .ovr)
gdaladdo -r average OUTPUT.tif 2 4 8

# Verify a mosaic quadrant is bit-identical to its source tile (repeat per tile;
# explicit offsets — avoid shell arrays, the login shell may be zsh)
gdal_translate -q -of VRT -srcwin 0 0 256 256 MOSAIC.tif /tmp/quad.vrt
gdalinfo -checksum /tmp/quad.vrt | grep Checksum   # compare vs TILE_0.tif
```

## Rasterization and tiles

```bash
# Rasterize vector file
gdal_rasterize -burn 1.0 -ot Byte -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES INPUT.shp OUTPUT.tif

# Rasterize using an attribute field
gdal_rasterize -a label -a_nodata 0 -ot Byte -tr 0.000269494585236 0.000269494585236 -co COMPRESS=LZW INPUT.shp OUTPUT.tif

# Convert raster to XYZ tiles
gdal2tiles.py -z 10-16 INPUT_BYTE.tif OUTPUT/
```

## COG

```bash
# Format-only conversion — smallest tool that fits
gdal_translate -of COG -co COMPRESS=LZW -co PREDICTOR=2 -co NUM_THREADS=ALL_CPUS INPUT.tif OUTPUT.tif

# Only when also reprojecting in the same step
gdalwarp -t_srs EPSG:XXXX -of COG -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 INPUT.tif OUTPUT.tif

# Validate
rio cogeo validate OUTPUT.tif   # via `uv run --with rio-cogeo` if not installed
```
