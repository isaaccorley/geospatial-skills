---
template: skill.html
title: Portolan Bootstrap
slug: portolan-bootstrap
tag: CATALOG
install_skill: portolan-bootstrap
upstream:
  - label: portolan-sdi/portolan-skills
    href: https://github.com/portolan-sdi/portolan-skills
  - label: Source Cooperative
    href: https://source.coop
license: "Apache-2.0 (upstream: portolan-sdi/portolan-skills)"
requires: "<code>portolan-cli</code>; <code>tippecanoe</code> optional for PMTiles; Python 3 for metadata edits"
summary: >-
  A nine-phase, checkpoint-driven playbook for bootstrapping a complete
  Portolan catalog from a raw source &mdash; WFS, ArcGIS
  Feature/Map/ImageServer endpoints, or a directory of local files. Walks
  discovery, extraction, remote setup, asset generation, metadata enrichment,
  README generation, STAC-GeoParquet, and push, pausing at explicit
  checkpoints for confirmation. Its core rule: never hallucinate metadata.
features:
  - "Detect source type and dry-run extraction with <code>portolan extract &lt;type&gt; &lt;URL&gt; --dry-run</code> before committing"
  - "Local-file path via <code>init --auto</code> / <code>scan</code> / <code>check --fix</code> (GPKG and Shapefile to GeoParquet, rasters to COG)"
  - "Explicit user checkpoints for destination, license, contact info, PMTiles generation, and push confirmation"
  - "Strict metadata-enrichment rules &mdash; fill only from source metadata, fix encoding, never invent titles"
  - "Recursive <code>portolan metadata init</code> and <code>portolan readme</code> for catalog- and collection-level docs"
  - "STAC-GeoParquet <code>items.parquet</code> generation for catalogs with 1000+ assets, then dry-run and verbose push"
example_html: |
  <span class="com"># preview a remote-service extraction before running it</span>
  <span class="dim">$</span> portolan extract arcgis <span class="arg">"https://services.example.com/arcgis/rest/services/Parcels/FeatureServer"</span> --dry-run

  <span class="com"># convert non-cloud-native files in place</span>
  <span class="dim">$</span> portolan check --fix

  <span class="com"># validate credentials and preview the upload</span>
  <span class="dim">$</span> portolan push --dry-run
prev:
  slug: portolan-cli
  name: Portolan CLI
next:
  slug: reading-portolan
  name: Reading Portolan
---
