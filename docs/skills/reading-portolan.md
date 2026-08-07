---
template: skill.html
title: Reading Portolan
slug: reading-portolan
tag: STAC
install_skill: reading-portolan
upstream:
  - label: portolan-sdi/portolan-skills
    href: https://github.com/portolan-sdi/portolan-skills
  - label: portolan-sdi/portolan-spec
    href: https://github.com/portolan-sdi/portolan-spec
license: 'Apache-2.0 (upstream: portolan-sdi/portolan-skills)'
requires: DuckDB 1.2+ with spatial + httpfs; <code>gpio</code> recommended; GDAL/OGR for conversions
summary: >-
  The comprehensive consumer's guide to Portolan catalogs, organized as a
  five-step workflow: navigate the STAC tree into a collection inventory,
  query GeoParquet with DuckDB locally or over HTTP range requests, inspect
  with gpio, convert to legacy formats with GDAL/OGR, and visualize. The
  visualization section is opinionated &mdash; always PMTiles + MapLibre,
  never exported GeoJSON.
features:
  - Crawl <code>catalog.json</code> child links, including nested sub-catalogs, into a full dataset inventory
  - 'DuckDB spatial analysis: <code>ST_Intersects</code>/<code>ST_Within</code> filters, buffers, cross-collection joins, partition globs'
  - Remote reads via HTTP range requests and s3:// with credential setup; export to GeoParquet/GeoJSON/CSV
  - <code>gpio inspect</code>/<code>check</code>/<code>extract</code> for validation and subsetting without SQL
  - GDAL/OGR conversion for legacy consumers, with <code>/vsicurl/</code> and <code>/vsis3/</code> remote access
  - MapLibre + PMTiles templates, shipped-style discovery via <code>portolan:styles</code>, deck.gl, TiTiler, and Potree
example_html: |
  <span class="com"># discover collections from the root STAC catalog</span>
  <span class="dim">$</span> curl -s <span class="arg">https://data.source.coop/user/catalog-name/catalog.json</span> | python3 -m json.tool

  <span class="com"># query remote GeoParquet via HTTP range requests</span>
  <span class="dim">$</span> duckdb -c <span class="arg">"LOAD spatial; SELECT count(*) FROM read_parquet('https://data.source.coop/.../data.parquet')"</span>

  <span class="com"># row count, bbox, geometry types, CRS &mdash; no SQL</span>
  <span class="dim">$</span> gpio inspect stats data.parquet
prev:
  slug: portolan-bootstrap
  name: Portolan Bootstrap
next:
  slug: portolan-thumbnails
  name: Portolan Thumbnails
---
