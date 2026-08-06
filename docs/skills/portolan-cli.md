---
template: skill.html
title: Portolan CLI
slug: portolan-cli
tag: CATALOG
install_skill: portolan-cli
upstream:
  - label: portolan-sdi/portolan-skills
    href: https://github.com/portolan-sdi/portolan-skills
  - label: portolan-sdi/portolan-spec
    href: https://github.com/portolan-sdi/portolan-spec
license: "Apache-2.0 (upstream: portolan-sdi/portolan-skills)"
requires: "<code>portolan-cli</code> (<code>pipx install portolan-cli</code>); cloud credentials for push/pull"
summary: >-
  Full command reference for the Portolan CLI, which publishes and manages
  cloud-native geospatial catalogs as static files &mdash; GeoParquet, COG,
  COPC, PMTiles under STAC metadata &mdash; synced to S3/GCS/Azure with no
  server. Documents all ~20 subcommands, the catalog directory layout, per-
  collection SemVer versioning, and a consistent <code>--json</code> output
  envelope for agents.
features:
  - "Initialize and scan catalogs: <code>portolan init --auto</code>, <code>portolan scan --json</code>"
  - "Validate and auto-convert to cloud-native formats with <code>portolan check --fix</code> (vectors &rarr; GeoParquet, rasters &rarr; COG)"
  - "Git-like remote workflow &mdash; <code>push</code>, <code>pull</code>, <code>sync</code>, <code>clone</code>, <code>status</code> against s3://, gs://, Azure"
  - "Partition large GeoParquet and extract from ArcGIS/WFS services"
  - "Generate metadata templates, READMEs, and STAC-GeoParquet <code>items.parquet</code> per collection"
  - "Per-collection semantic versioning with SHA-256 checksums in <code>versions.json</code>"
example_html: |
  <span class="com"># initialize a new catalog in the current directory</span>
  <span class="dim">$</span> portolan init --title <span class="arg">"My Geospatial Data"</span>

  <span class="com"># convert files to cloud-native formats before publishing</span>
  <span class="dim">$</span> portolan check --geo-assets --fix

  <span class="com"># upload one collection to object storage</span>
  <span class="dim">$</span> portolan push <span class="arg">s3://mybucket/my-catalog</span> --collection demographics
prev:
  slug: planet-bulk-download
  name: Planet Bulk Download
next:
  slug: portolan-bootstrap
  name: Portolan Bootstrap
---
