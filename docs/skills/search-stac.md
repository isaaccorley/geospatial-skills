---
template: skill.html
title: Search STAC
slug: search-stac
tag: STAC
install_skill: search-stac
upstream:
  - label: opengeos/geoai
    href: https://github.com/opengeos/geoai
  - label: Microsoft Planetary Computer
    href: https://planetarycomputer.microsoft.com
license: "MIT (upstream: opengeos/geoai-skills)"
requires: "<code>geoai-py</code>; network access to Microsoft Planetary Computer"
summary: >-
  Drives Microsoft Planetary Computer's STAC catalog through geoai's
  <code>pc_*</code> helpers. Lists and keyword-filters collections, searches a
  collection by bbox and time range with an item limit, enumerates per-item
  assets and bands, and downloads matched items to a local directory with size
  reporting.
features:
  - "Collection browsing via <code>geoai.pc_collection_list(filter_by=...)</code>"
  - "Item search via <code>geoai.pc_stac_search</code> with bbox, <code>YYYY-MM-DD/YYYY-MM-DD</code> ranges, and limits"
  - "Per-item asset and band listing via <code>geoai.pc_item_asset_list</code>"
  - "Bulk download via <code>geoai.pc_stac_download</code> with per-file sizes"
  - "Error playbook for bad collection names (closest-match suggestion) and empty result sets"
example_html: |
  <span class="com"># what collections exist</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; print(geoai.pc_collection_list(filter_by='sentinel'))"</span>

  <span class="com"># search by bbox and date range</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; print(len(geoai.pc_stac_search(collection='sentinel-2-l2a', bbox=[-83.5, 35.5, -83.4, 35.6], time_range='2023-01-01/2023-06-30')))"</span>
prev:
  slug: sourcecoop
  name: Source Cooperative
next:
  slug: overture-data
  name: Overture Data
---
