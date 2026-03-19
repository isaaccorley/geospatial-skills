# GDAL

General GDAL command line workflows for raster and vector geospatial processing.

<div class="skill-callout">
  <p class="skill-callout-label">Tools</p>
  <p><code>gdalwarp</code>, <code>gdal_translate</code>, <code>gdalbuildvrt</code>, <code>gdal_rasterize</code>, <code>ogr2ogr</code>.</p>
</div>

## Install

### Universal

```bash
cp -R skills/gdal ~/.agent/skills/gdal
```

### Claude

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install gdal@geospatial-skills
```

CLI:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install gdal@geospatial-skills
```

## Common tasks

1. Inspect raster or vector metadata.
1. Reproject rasters and vectors.
1. Clip rasters to shapes or vectors to raster extents.
1. Build mosaics, band stacks, thumbnails, or XYZ tiles.
1. Convert GeoTIFF outputs to compressed GeoTIFF or COG.

## Essential commands

```bash
gdalinfo INPUT.tif
ogrinfo INPUT.shp -so
gdalwarp -t_srs epsg:4326 INPUT.tif OUTPUT.tif
ogr2ogr -f GeoJSON -t_srs epsg:4326 OUTPUT.geojson INPUT.shp
gdalbuildvrt OUTPUT.vrt path/to/tiffs/*.tif
gdal_translate -co COMPRESS=LZW -co BIGTIFF=YES OUTPUT.vrt OUTPUT.tif
gdal_rasterize -burn 1.0 -ot Byte -of GTiff INPUT.shp OUTPUT.tif
gdal2tiles.py -z 10-16 INPUT_BYTE.tif OUTPUT/
```

## Source

- Skill: [skills/gdal/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/gdal/SKILL.md)
- Recipes: [skills/gdal/references/gdal-recipes.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/gdal/references/gdal-recipes.md)
- Upstream reference: [microsoft/ai4eutils geospatial recipes](https://github.com/microsoft/ai4eutils/blob/master/geospatial/recipes_and_guides/geospatial_recipes.md)
