---
name: parallel-geospatial
description: Parallelize large-scale geospatial operations on a single fat node — tile-edge dissolve, polygon elimination, polygonize, spatial joins, reprojection, simplification — at national/continental scale (10–100M polygons). Use when speeding up or designing a geospatial batch process, or as a pre-flight checklist for known failure modes (DuckDB GEOS segfaults, topology exceptions, int64 overflow, NFS thrashing).
---

# Parallel Geospatial

Reference for designing and debugging large-scale parallel geospatial processing on a single fat node. **You do not write geospatial code at this scale single-threaded.** The defaults below come from real continental-scale (15M polygons, 6T-pixel rasters) failures.

The shape of every problem here is the same: **partition along an axis where work is naturally independent, then run an embarrassingly parallel pool over the partitions**. The skill is identifying that axis cheaply and avoiding the operation-specific footguns that crash GEOS or DuckDB at scale.

## The decision tree (start here)

For a new geospatial operation at >1M-feature or >1B-pixel scale, ask in this order:

1. **Is there a natural disjoint partition?** state, county, tile, hilbert-curve cell, raster window, time slice. If yes → ProcessPool over partitions. Stop, you're done thinking.
2. **Is the work output-disjoint but input-overlapping?** (e.g. spatial join: each output row needs a small bbox query against an input). Build an STRtree once on inputs, partition over outputs. Workers share a read-only tree via fork-inherited memory or rebuild small per worker.
3. **Is it a global aggregation that can't be partitioned?** Decompose into a tree-reduce: partition → reduce-per-partition → small final merge. Almost every real "global" op decomposes this way (union, dissolve, count-distinct, hilbert sort).
4. **Is it truly serial?** Rare. Consider whether you actually need the operation, or whether a different formulation (e.g. raster mask AND vs. polygon difference) sidesteps it.

If you find yourself running anything covering a continent in a single thread, **stop and reconsider** — single-threaded for >1M features is almost always a design bug, not a "we'll optimize later" one.

## Footguns that cost whole batch jobs (real failures)

These are operations whose textbook one-liner segfaults or silently corrupts at continental scale. **Bake the workaround in from the start; do not "try the simple version first."**

| Operation | Looks like | Fails how | Fix |
| --- | --- | --- | --- |
| DuckDB self-join with `ST_Touches` over 15M rows | `SELECT a.id, b.id FROM t a JOIN t b ON ST_Touches(a.geom, b.geom)` | Segfault during execution (exit 139), no error message | Materialise to Arrow, build `shapely.STRtree`, call `tree.query(geoms, predicate="touches")`. Vectorised, ~1000× faster, no GEOS-from-DuckDB crash. |
| DuckDB `ST_Union_Agg` GROUP BY over millions of rows | `SELECT root_id, ST_Union_Agg(geom) FROM ... GROUP BY root_id` | Segfault deep inside GEOS | Group rows in Python, ProcessPool dissolves each group with `shapely.union_all`. Use `parallel_map`. |
| DuckDB `ST_Buffer` on `ST_Transform(geom, ...)` lines (spatial 1.5.0) | `ST_Buffer(ST_Transform(geom, 'EPSG:4326', 'EPSG:5070'), 15)` | Segfault on first row (exit 139) | Do reprojection in DuckDB, fetch WKB, buffer in `shapely.buffer(geoms, m)`. |
| DuckDB `ST_Transform` 4326 → projected without `always_xy` | `ST_Transform(geom, 'EPSG:4326', 'EPSG:5070')` | All output coords are `Infinity` (no error) | Always pass `always_xy => true`. EPSG:4326's authoritative axis order is lat,lon — DuckDB respects that, PROJ tries to swap, output becomes garbage. |
| DuckDB `GROUP BY a, ALL` (mixing named key + ALL) | `GROUP BY root_oid, ALL` | Parser error: "syntax error at or near ALL" | DuckDB's `GROUP BY ALL` doesn't compose with explicit keys. Restructure as a dissolve-then-join: aggregate geometry by root, then join one representative row's attributes back. |
| `shapely.union_all` on degenerate geoms | `shapely.union_all([g1, g2, ...])` | `GEOSException: TopologyException: side location conflict` | Always `geoms = shapely.make_valid(geoms)` before `union_all` / `intersection_all` / etc. Cheap insurance. |
| Polygon-elimination on int32 label ids when count × tile_count > 2³¹ | union-find over `int32` ids | Silent collisions; output polygon count drops by ~50% with no error | Use `int64` everywhere for labels and remaps. One real national-scale "polygon count gap" was a one-line int32→int64 fix that recovered ~7M polygons. |
| Reading a 5GB GeoParquet from a network filesystem with 96 concurrent workers | `pq.read_table(...)` per worker | NFS saturates at ~70 MB/s aggregate; whole job stalls | Stage to local NVMe scratch (1–2 GB/s) before fanning out. Bash one-liner. |
| `pyogrio.write_dataframe(..., driver="FlatGeobuf")` with NULL geoms | `gdf.to_file(...)` | `FeatureError: NULL geometry not supported with spatial index` | Filter `geom.notna() & ~geom.is_empty & geom.is_valid` before write. Mandatory at FGB write. |
| Tippecanoe single-process at 100M+ features | `tippecanoe -o out.pmtiles in.fgb` | Times out at 8h+ even on 96-core node | Sharded path: round-robin into N FGBs, N × `tippecanoe TIPPECANOE_MAX_THREADS=1`, then `tile-join`. See `pmtiles-pipeline` skill. |

When in doubt about whether a given DuckDB-spatial or GEOS operation will scale, **assume it will segfault**. Cost of bake-in workaround: 30 min. Cost of discovering the segfault on a real run: a 4h job, wasted allocation, plus the time to find the bug after the empty stderr.

## Embarrassingly-parallel patterns

### Pattern A — Per-tile / per-state ProcessPool (the default)

The 80% case. Used for: raster polygonize, postprocess spatial joins, tile-edge pair finding, multi-year raster combines.

```python
import os
from concurrent.futures import ProcessPoolExecutor

def worker_count(frac=0.95):
    return max(1, int((os.cpu_count() or 1) * frac))

def parallel_map(fn, items, max_workers):
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(fn, items))

partitions = partition_by_state(national)  # or by tile, region, etc.
results = parallel_map(
    _worker_fn,
    partitions,
    max_workers=worker_count(0.95),  # leave headroom for the OS / monitoring
)
merged = combine(results)
```

The `_worker_fn` should:

- Take ONLY picklable args (Arrow buffers, numpy arrays, paths, primitives — not DuckDB connections, not open file handles).
- Open its own DuckDB connection / Rasterio handle / etc. inside the worker. Workers share *forked* memory but you cannot share an open driver state.
- Return small results. If the result is large (e.g. 1GB of polygons), write to disk in the worker and return only the path.

### Pattern B — Tree-reduce (when "global" aggregation is needed)

Example — a national tile-edge dissolve:

```
15M polygons globally
   │
   ├── partition by tile_id      # (a) cheap: just a column already on the row
   │
   ├── per-tile envelope         # (b) trivial groupby in DuckDB
   │
   ├── on_edge filter            # (c) keep only polygons whose bbox touches its tile envelope
   │       ↓
   │   ~500k polygons remain     # ~3% of original — STRtree now actually fits
   │
   ├── partition by state        # (d) tile-edge dissolves never cross state lines
   │
   ├── ProcessPool: STRtree+touches per state    # (e) pair finding
   │
   ├── union-find on combined pairs              # (f) connected components, fast in pure Python
   │
   └── ProcessPool: shapely.union_all per group  # (g) most groups have 2-3 members
```

Lesson: **filter aggressively before the expensive step**. The on_edge filter (c) drops 97% of work. Without it, even the parallel STRtree is too slow.

### Pattern C — Output-disjoint, input-overlapping spatial join

Example — assigning each polygon its largest-overlap administrative boundary. STRtree of boundaries (small, ~3000 counties), partition over polygons:

```python
boundary_tree = STRtree(boundary_geoms)
# In each worker:
def assign_county(polygon_chunk):
    out = []
    for poly in polygon_chunk:
        candidates = boundary_tree.query(poly, predicate="intersects")
        # Pick largest-overlap candidate by ST_Intersection area.
        ...
    return out
```

Workers share `boundary_tree` via fork (Linux). On Windows / macOS spawn, rebuild per worker (cheap if input is small).

## Always-applicable defaults

These are the "no thinking required" choices for a new geospatial pipeline. Deviate only with a reason.

- **CRS**: pick one and lock it (`EPSG:5070` for CONUS, `EPSG:6933` for global equal-area). Never reproject silently mid-pipeline.
- **GeoParquet**: 1.1 with full-PROJJSON CRS. The short `{id: {authority, code}}` form breaks pyproj 3.x, geopandas, pyogrio, and GDAL readers.
- **Bbox columns**: explicit `xmin`/`ymin`/`xmax`/`ymax` in addition to geometry. Lets DuckDB row-group statistics prune queries before any GEOS work runs.
- **Hilbert sort** before write for any parquet that will be range-queried by bbox: `ORDER BY ST_Hilbert(geom, BOX_2D)`. Co-locates spatially-near features in the same row group.
- **Row group size**: 50k–100k features. Smaller groups = better pruning, larger groups = better compression. 50k is a good default for ~30M-feature national datasets.
- **Compression**: `zstd` always. Never default `snappy` for vector — zstd is 30-50% smaller for similar speed.
- **Workers**: `worker_count(0.95)` of physical cores. The 5% headroom matters on shared nodes.
- **dtype**: `int64` for IDs and labels. Cost of int64 vs int32: nothing. Cost of int32 overflow: silent data loss.
- **Validation gate at every boundary**: `geom.notna() & ~geom.is_empty & geom.is_valid` before any write that builds a spatial index (FGB, STRtree, DuckDB spatial parquet).

## DuckDB-spatial-specific guidance

DuckDB-spatial is the right tool for a lot of this work but it has sharp edges. Treat these as load-bearing.

- **Heavy GEOS ops segfault on big tables.** ST_Union_Agg, ST_Touches self-joins, ST_Buffer over transformed lines. Materialise to Arrow + use shapely / numpy when you have >1M rows.
- **Bbox stats are how you get pruning.** Read parquet with explicit xmin/xmax/ymin/ymax; queries with `WHERE xmax >= ? AND xmin <= ? ...` will skip whole row groups before decoding any geometry.
- **`always_xy => true` on every `ST_Transform` from `EPSG:4326`.** Otherwise lat/lon swap → Infinity coords.
- **Don't trust DuckDB's binder on wide self-joins with spatial predicates.** Even when it doesn't crash, it produces "Failed to bind column reference" errors. Workaround: split into geometry-only spatial join CTE then attribute-join.
- **`GROUP BY ALL` is great alone, broken with explicit keys.** Use `GROUP BY ALL` by itself, or list every key explicitly. Do not mix.
- **Use `BIND` over the parquet file, not over a TABLE you SELECTed into.** `read_parquet('path')` lets DuckDB use file statistics; an in-memory `CREATE TABLE ... AS SELECT ...` discards them.

## Shapely-specific guidance

- **Vectorise everything.** `shapely.from_wkb(list)` and `shapely.buffer(geoms, m)` are 50–100× faster than per-geometry loops. Never write `[g.buffer(m) for g in geoms]` over more than 1000 geoms.
- **Always `make_valid` before union/intersect.** Cheap, prevents 100% of TopologyException crashes.
- **`shapely.coverage_union_all` for non-overlapping polygons; `union_all` for arbitrary.** Coverage is ~10× faster but only correct on coverages (no overlaps, no gaps).
- **STRtree is the only correct way to do bbox prefiltering at scale.** Don't write your own grid index — `shapely.strtree.STRtree` is GEOS-backed and bulk-vectorized.
- **STRtree.query returns a (2, N) array of (input_idx, tree_idx) pairs.** When self-querying, filter `a < b` to dedupe. Predicate values: `'intersects'`, `'touches'`, `'contains'`, `'within'`.

## Shared clusters and batch schedulers

- **Stage network-filesystem data to local NVMe scratch before parallel reads.** NFS commonly ceilings around ~70 MB/s aggregate; local NVMe scratch gives 1–2 GB/s. 96 workers reading NFS concurrently = job stall. One bash `cp` to scratch first = problem solved.
- **Use your scheduler's job-dependency support for multi-stage pipelines** (`afterok`-style chains). Don't run stages interactively back-to-back; you waste time waiting for the previous step to finish before queuing the next.
- **One batch job per natural pipeline stage, but collapse small stages.** Don't fragment a 4-stage pipeline into 4 jobs if 3 of the stages are <5 min each — that's just dependency-chain latency.
- **Request most-but-not-all of a shared node.** For example, half the cores and most of the RAM of a fat node — enough for `parallel_map` to scale while leaving room for other users.
- **Always have a resume pattern.** Per-tile parquet output that the next run skips if present. Wasting compute because phase 5 of 6 crashed is unforgivable on shared infrastructure.
- **Never pass `--force` from a wrapper script.** A re-run that auto-passed `--force` once wiped a near-complete zarr store. Add a preflight that refuses to start if expected outputs are missing in unexpected ways, rather than auto-overwriting.

## Diagnostic checklist when "the parallel version is slow"

Symptom: you wrote the parallel version, it's still slow / OOMing / hanging.

1. **CPU% on workers.** `ssh node "ps -u user -o pid,pcpu,etime,rss,cmd"`. If workers are at 100% each, you're CPU-bound — count the cores you're getting. If they're at 5–20%, you're I/O- or GIL-bound.
2. **Memory per worker.** ProcessPool fork-inherits the parent's memory. If the parent has 50GB resident, every worker starts at 50GB. Materialise the inputs you need, drop the parent's references, then fork. Or use `spawn` with explicit data passing.
3. **Pickle size.** Each task argument gets pickled. A 5MB Arrow chunk × 5000 tasks = 25GB of pickling overhead. Group small tasks; pass paths/offsets, not data.
4. **GEOS errors silently swallowed.** Workers crashing on TopologyException don't always propagate. Wrap workers in try/except that logs + re-raises.
5. **NFS / filesystem.** `iostat -x 5` on the node. Saturation = stage to local scratch first.
6. **Single-thread inner loop.** Profile a single worker (`py-spy record`). If 80% of time is in one Python loop, vectorise it (numpy/shapely bulk ops).

## When to leave the single-node paradigm

Single fat node + ProcessPool + DuckDB scales to surprisingly large workloads (one real national-scale build: 6T pixels, 15M polygons, 25 minutes wall on one 96-core node). You only need to graduate to:

- **Dask** when working set won't fit one node's RAM (~512GB), or when the operation must distribute across heterogeneous storage backends. The complexity tax is real — start single-node.
- **Sedona / Spark** for very-wide spatial joins where one side is 100M+ and the other 100M+ and you can't STRtree-prefilter. Rare.
- **Multi-node array jobs** when an embarrassingly parallel job has >node-RAM total memory and per-task is small enough to send. Use array indexing, not MPI.

If you reach for distributed compute on a continental-scale problem, check first whether you're falling into one of the footguns above. Most "I need Dask" instincts on this size of data turn out to be "I'm using DuckDB's GEOS aggregations on millions of rows."

## Common errors + fixes

- **`exit code 139` with no traceback** — segfault, almost always GEOS-from-DuckDB on large input. See footguns table. Drop to shapely.
- **`exit code 137`** — OOM kill. Workers fork-inherited too much, or too many workers per node. Cut `worker_count` or materialise less in parent.
- **`TopologyException: side location conflict at <coord>`** — invalid geometry through union/intersection. `make_valid` before the op.
- **`Failed to bind column reference` in DuckDB** — wide self-join with spatial predicate. Split into CTE: spatial predicate alone, then attribute join.
- **Silent zero-row output from DuckDB query** — almost certainly bbox prefilter excluded everything. Check axis order on `ST_Transform`, check `always_xy`.
- **Parquet read 1000× slower than expected** — bbox columns missing, no row-group stats, full-table scan. Hilbert-sort + add bbox columns.

## Quick reference: when each tool is right

| tool | use when | avoid when |
| --- | --- | --- |
| **DuckDB-spatial** | bbox-pruned reads of GeoParquet, simple per-row spatial ops, joins to small auxiliary tables | aggregations across >1M rows, self-joins, ST_Buffer over millions of geoms — segfaults |
| **shapely + numpy** | bulk vector ops (buffer, simplify, bounds, valid checks); STRtree spatial prefilter; per-group dissolve | row-by-row Python loops; one-off scripts where DuckDB SQL is more readable |
| **rasterio + scipy.ndimage** | raster combine, label, binary_opening, polygonize via `rasterio.features.rasterize` | huge rasters needing chunking — switch to xarray/dask or windowed reads |
| **pyogrio** | fast FGB / GPKG read+write; Arrow-path GeoDataFrame I/O | parquet — use pyarrow and a full-PROJJSON GeoParquet writer |
| **ProcessPool (`parallel_map`)** | the default for any partitioned workload | when results are huge (write to disk, return paths); when args are huge (pass paths, not data) |
| **Dask / Spark** | working set > one node's RAM; multi-node required | single fat node still has headroom — start there |

## Memory aids

- "Single-threaded over a continent" = 30 min refactor.
- "DuckDB ST_X on millions of rows" = will segfault.
- "I'll add `make_valid` later" = TopologyException at 80% of the run.
- "I'll figure out the partition axis later" = re-architect later.
