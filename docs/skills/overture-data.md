---
template: skill.html
title: Overture Data
slug: overture-data
tag: VECTOR
install_skill: overture-data
upstream:
  - label: opengeos/geoai
    href: https://github.com/opengeos/geoai
  - label: Overture Maps
    href: https://overturemaps.org
license: 'MIT (upstream: opengeos/geoai-skills)'
requires: <code>geoai-py</code> with the overturemaps extra (<code>pip install "geoai-py[extra]"</code>)
summary: >-
  Pulls Overture Maps features for a bounding box through geoai's Overture
  helpers and saves them as GeoPackage or GeoJSON. Knows the full Overture
  type taxonomy &mdash; buildings, places, roads, divisions, land use, water,
  and friends &mdash; and reports feature counts, columns, CRS, and bounds.
features:
  - All 14 Overture data types enumerated, from <code>address</code> to <code>water</code>
  - Dedicated buildings path via <code>geoai.download_overture_buildings</code>
  - Generic path via <code>geoai.get_overture_data(overture_type=..., bbox=...)</code>
  - Natural-language requests resolved to type + bbox
  - 'GeoDataFrame report: feature count, columns, CRS, bounds, head sample'
example_html: |
  <span class="com"># Overture buildings for a bbox</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; gdf = geoai.download_overture_buildings(bbox=(-83.5, 35.5, -83.4, 35.6), output='buildings.gpkg'); print(len(gdf))"</span>

  <span class="com"># any other Overture layer</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; geoai.get_overture_data(overture_type='land_use', bbox=(-122.5, 37.7, -122.3, 37.8), output='land_use.gpkg')"</span>
prev:
  slug: search-stac
  name: Search STAC
next:
  slug: detect-objects
  name: Detect Objects
---
