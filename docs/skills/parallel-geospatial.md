---
template: skill.html
title: Parallel Geospatial
slug: parallel-geospatial
tag: SCALE
install_skill: parallel-geospatial
upstream:
  - label: duckdb/duckdb-spatial
    href: https://github.com/duckdb/duckdb-spatial
  - label: shapely
    href: https://github.com/shapely/shapely
license: "Apache-2.0"
requires: "<code>duckdb</code> + spatial, <code>shapely</code> 2.x, <code>pyarrow</code>, <code>pyogrio</code>; a many-core node"
summary: >-
  Design and debug embarrassingly-parallel geospatial processing on a single
  fat node &mdash; partition axes, tree-reduce patterns, and the operation-
  specific footguns that segfault GEOS or DuckDB at 10&ndash;100M-polygon
  scale. Distilled from real continental-scale failures: silent int32
  overflow, NFS thrashing, topology exceptions, and DuckDB spatial
  aggregations that exit 139.
features:
  - "A decision tree for finding the natural partition axis: disjoint partitions, output-disjoint joins, tree-reduce aggregations"
  - "Footgun table of textbook one-liners that segfault or silently corrupt at scale, each with a bake-in workaround"
  - "ProcessPool, tree-reduce, and STRtree spatial-join patterns with worker rules (picklable args, per-worker connections, small returns)"
  - "No-thinking-required defaults: locked CRS, GeoParquet 1.1 + full PROJJSON, bbox columns, hilbert sort, <code>zstd</code>, int64 ids"
  - "Diagnostic checklist for slow parallel jobs: worker CPU%, fork-inherited memory, pickle overhead, NFS saturation"
  - "When to graduate to Dask / Sedona / multi-node arrays &mdash; and why you usually shouldn't"
example_html: |
  <span class="com"># never self-join ST_Touches in DuckDB at scale &mdash; STRtree instead</span>
  <span class="dim">$</span> python -c <span class="arg">"import shapely; pairs = shapely.STRtree(geoms).query(geoms, predicate='touches')"</span>

  <span class="com"># always make_valid before union_all</span>
  <span class="dim">$</span> python -c <span class="arg">"import shapely; merged = shapely.union_all(shapely.make_valid(geoms))"</span>

  <span class="com"># stage network-filesystem inputs to local NVMe scratch before fanning out</span>
  <span class="dim">$</span> cp /nfs/data/*.parquet /tmp/work/
prev:
  slug: geospatial-frontend
  name: Geospatial Frontend
next:
  slug: pmtiles-pipeline
  name: PMTiles Pipeline
---
