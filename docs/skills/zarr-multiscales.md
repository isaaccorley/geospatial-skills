---
template: skill.html
title: Zarr Multiscales
slug: zarr-multiscales
tag: ARRAYS
install_skill: zarr-multiscales
upstream:
  - label: zarr-developers/geozarr-spec
    href: https://github.com/zarr-developers/geozarr-spec
  - label: zarr-developers/zarr-python
    href: https://github.com/zarr-developers/zarr-python
license: "Apache-2.0"
requires: "<code>zarr</code> v3, <code>xarray</code>, <code>numpy</code>; pairs with the <code>geozarr</code> skill for the CRS layer"
summary: >-
  Add multiscale pyramids (overviews) to existing Zarr stores for tile and web
  streaming. The hard parts are semantic and distributed: choosing a
  resampling operator that preserves what the data means (probability simplex,
  categorical, counts), cascading levels without building on incomplete
  parents, and striping work across batch workers without silently losing
  shards.
features:
  - "Operator-selection table keyed on the data's invariant: <code>average</code> for probabilities, <code>mode</code> for labels, <code>sum</code> for counts"
  - "Thread-safe nodata-aware masked mean (explicit <code>sum/count</code>, not <code>np.nanmean</code>) with joint validity across bands"
  - "Shard-aligned work units &mdash; one input shard maps to one output object: no write races, trivial retry and resume"
  - "The stripe-then-filter partitioning rule, and the silent shard-loss bug the reverse order causes, with regression tests"
  - "Completeness gates between cascade levels: real object counts vs manifest targets, never job exit codes"
  - "Ready scripts: downsamplers, manifest pruning, and a stripe-aware verification harness; a 12-entry failure catalogue"
example_html: |
  <span class="com"># each pyramid level opens standalone</span>
  <span class="dim">$</span> python -c <span class="arg">"import xarray as xr; print(xr.open_zarr('store.zarr', group='8x'))"</span>

  <span class="com"># stripe the stable task list first, then filter for resume &mdash; never the reverse</span>
  <span class="dim">$</span> python -c <span class="arg">"mine = tasks[stripe::nstripes]; mine = [t for t in mine if t not in done]"</span>
prev:
  slug: pmtiles-pipeline
  name: PMTiles Pipeline
next:
  slug: planet-bulk-download
  name: Planet Bulk Download
---
