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
```

## Raster recipes

```bash
# Reproject raster
gdalwarp -t_srs epsg:4326 INPUT.tif OUTPUT.tif

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
gdalwarp -co BIGTIFF=YES -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -co PREDICTOR=2 -of COG INPUT.tif OUTPUT.tif
```
