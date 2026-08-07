---
template: skill.html
title: PMTiles Pipeline
slug: pmtiles-pipeline
tag: TILES
install_skill: pmtiles-pipeline
upstream:
  - label: felt/tippecanoe
    href: https://github.com/felt/tippecanoe
  - label: protomaps/go-pmtiles
    href: https://github.com/protomaps/go-pmtiles
  - label: isaaccorley/contourrs
    href: https://github.com/isaaccorley/contourrs
license: Apache-2.0
requires: <code>tippecanoe</code> (Felt fork), <code>pyogrio</code>, <code>geopandas</code>, <code>contourrs</code>; <code>go-pmtiles</code> optional
summary: >-
  Build one global PMTiles archive from raster predictions or any
  100M+-feature vector dataset on a single fat node. Covers the full raster
  &rarr; GeoParquet &rarr; FlatGeobuf &rarr; sharded tippecanoe &rarr; tile-
  join pipeline with the measured reasoning behind every stage, distilled from
  a real ~6T-pixel, 176M-polygon build.
features:
  - Vectorize classified rasters straight to Arrow with <code>contourrs</code>, denoised via <code>binary_opening</code>
  - Field-size analysis to pick area filters and simplification tolerances before any tile work
  - 'Why FlatGeobuf: native tippecanoe parallelism &mdash; GeoParquet and GeoJSON-seq inputs kill 96-core scaling'
  - Sharded tippecanoe + tile-join architecture that turned an 8h timeout into a ~50-min build
  - A tuned tippecanoe flag set with per-flag reasoning, plus the two flags to never use
  - Geographic sharding + <code>pmtiles merge</code> design for repeated builds; a table of what didn't work and why
example_html: |
  <span class="com"># one tippecanoe per FGB shard, single-threaded each</span>
  <span class="dim">$</span> TIPPECANOE_MAX_THREADS=1 tippecanoe -o sub_042.pmtiles <span class="arg">--maximum-zoom=14 --drop-densest-as-needed</span> batch_042.fgb

  <span class="com"># merge overlapping sub-archives into the final pmtiles</span>
  <span class="dim">$</span> tile-join -o final.pmtiles sub_*.pmtiles
prev:
  slug: parallel-geospatial
  name: Parallel Geospatial
next:
  slug: zarr-multiscales
  name: Zarr Multiscales
---
