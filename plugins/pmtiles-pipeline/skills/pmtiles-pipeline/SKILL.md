---
name: pmtiles-pipeline
description: Build a global PMTiles archive from raster predictions or any large vector dataset on a single fat node. Covers raster→polygon→geoparquet→FlatGeobuf→sharded tippecanoe→tile-join, with profiling, error recovery, and I/O-aware staging. Use when the user asks to vectorize raster predictions, polygonize change layers, build PMTiles at over 100M-feature scale, profile tippecanoe, decide tippecanoe flags, choose between tippecanoe / planetiler / pmtiles merge, or speed up a slow pmtiles build.
---

# PMTiles Pipeline

Reference for building a single global PMTiles archive on one fat node, distilled from a real global change-layer build (~6T-px raster input, 176M polygons, 28 GB PMTiles output). The pipeline is:

```
raster.zarr  →  geoparquet shards  →  FlatGeobuf batches  →  sharded tippecanoe  →  tile-join  →  pmtiles
   (1)              (2)                    (3)                     (4)                  (5)
```

Each stage's "why" matters more than the syntax. **Use this skill whenever a step in this pipeline is being built, debugged, or optimized.**

## Stage 1 — Raster → polygons (as parquet shards)

- Use `contourrs.shapes_arrow` to vectorize a classified uint8 raster directly to Arrow (skip GeoJSON in/out).
- Pre-filter with `scipy.ndimage.binary_opening(struct=NxN)` per class to wipe salt-and-pepper noise. **N=3 is a sane default at 10m resolution.**
- Write GeoParquet via geopandas with `compression="zstd"`. One parquet per super-tile (e.g., 8192² px) → tens of thousands of small shards. That granularity matters for downstream resume + parallelism.
- Track fields: `class` (uint8), `area_deg2` (float64 — useful for downstream filtering), `geometry`.
- Connectivity 8 (diagonals count) and `min-pixels=25` are fine starting defaults; higher min-pixels = aggressive smoothing.

## Stage 2 — Field-size analysis before any pmtiles work

**Always do this once.** It informs the area filter at stage 3 and the simplification tolerance.

Sample ~100 random parquet shards, read `class` + `area_deg2` only (no geometry — `pq.read_table(p, columns=[...]).to_pandas()`, geopandas refuses to read parquet without geom). Convert to m² via `area_deg2 * 111320**2` (equator approximation, slight overestimate at high latitudes).

Look at percentiles + cumulative-below thresholds at: 0.25, 0.5, 1, 2.5, 5, 10 ha. The min observed area = polygonize floor + small expansion from simplify. Anything in the bottom decile is artifact noise; smallholder ag fields are typically 0.5–2 ha (median ~0.7 ha real-world).

## Stage 3 — GeoParquet → FlatGeobuf (parallel, with filter + simplify)

**Why FlatGeobuf:** tippecanoe parallelizes natively on FGB input via the spatial index. No `--read-parallel` flag needed. GeoJSON-seq input forces single-thread JSON parsing — kills 96-core scaling. **Tippecanoe does NOT read GeoParquet directly** — FGB is the only fast format.

Implementation pattern:

- Round-robin shards into N batches (default N = physical core count) so every batch covers global geography.
- ProcessPool worker per batch. Each worker:
  1. Concat its parquet shards into one GeoDataFrame
  2. Filter by `area_deg2 >= MIN` (default 3.2e-7 deg² ≈ 0.4 ha drops ~15%)
  3. `shapely.simplify(geoms, tolerance, preserve_topology=True)` (default 2e-4 deg ≈ 22m at equator → smooths contour-step edges)
  4. **Drop NULL/empty/invalid:** `geom.notna() & ~geom.is_empty & geom.is_valid`. **This is mandatory** — pyogrio's FGB writer with spatial index errors out on NULL geometry mid-write. Without this filter you'll get `FeatureError: NULL geometry not supported with spatial index`.
  5. `pyogrio.write_dataframe(gdf, path, driver="FlatGeobuf")` — Arrow path, fast.
- Expected: 36 GB FGB from 26 GB parquet at this scale (5× expansion: spatial index + no row-level compression).
- Wall time: ~7 min on 96 cores for 124M filtered polygons.

Min-area threshold rule of thumb: at maxzoom=14 (9.6 m/px), a 50m feature = 5×5 px = the practical "easily visible" floor. Anything <2500 m² (25 px²) renders as 1–2 px even at maxzoom = noise. Default 0.4 ha is conservative; bump to 1 ha for cleaner output at the cost of dropping ~64% of polys (mostly smallholder fields).

## Stage 4 — Build pmtiles via sharded tippecanoe

**Single-process tippecanoe does NOT scale to 96 cores at 100M+ feature scale.** Even with FGB native parallelism, tippecanoe's sort + final-write phases serialize to ~10–20 effective cores. A single-process build of a 124M-poly dataset **timed out at 8h** on a 96-core node. The sharded path finished in ~50 min.

### Architecture

```
1. Stage N FGBs from network storage (NFS) to local NVMe scratch   ← critical for I/O
2. Run N tippecanoes in parallel, TIPPECANOE_MAX_THREADS=1, one per FGB
   → N sub-pmtiles on local scratch
3. tile-join all N sub-pmtiles into one final pmtiles on local scratch
4. cp final pmtiles back to network storage
```

Step 1 is the biggest non-obvious win. N concurrent readers hit NFS hard when reading network storage directly (measured ~70 MB/s aggregate ceiling). NVMe local scratch gives 1–2 GB/s aggregate read. **Always stage at this scale.**

### tippecanoe flags (zoom decisions are dataset-specific, not universal)

These flags are tuned for a 10 m agricultural change layer (polygons). Adjust for your dataset.

```bash
-l <layer>                     # layer name in MVT
--minimum-zoom=3               # global view from this pmtiles. If you serve a separate raster overview for low zooms (a common split: pmtiles for z>=11 + COG for z<11), set higher.
--maximum-zoom=14              # 9.6 m/px ≈ 10m source native. Don't go past native unless you want client-side overzoom only.
--base-zoom=14                 # full detail held until maxzoom — no premature simplify. Use lower (e.g. 12) if you want smaller tiles at intermediate zooms.
--full-detail=14               # max vertex precision per tile (default 12). Bumping helps small-feature visibility at maxzoom.
--simplification=1             # near-zero DP simplify. Polygonize already simplified at stage 3; let high-zoom be detailed.
--buffer=8                     # pixel buffer on tile edges to prevent feature clipping mid-render. Default 5 sometimes shows seams.
--drop-rate=1                  # ~no rate-based dropping (default 2.5). Bigger pmtiles, more features at low zooms — set to 2–3 if you want a smaller archive.
--maximum-tile-bytes=2000000   # 2MB cap (default 500K). Web renderers handle 2MB fine; lower if mobile-perf matters.
--maximum-tile-features=1000000# 1M cap (default 200K). Same trade-off.
-y class                       # carry only the `class` attribute; drop other parquet columns to save bytes.
--coalesce-smallest-as-needed  # merge sub-pixel adjacent same-class polys at low zoom (preserves info vs dropping)
--drop-densest-as-needed       # safety net: tippecanoe ERRORS without this if a tile blows past the byte cap. Always include.
--detect-shared-borders        # geometry compression for adjacent same-class polys (5-10% size win, slight CPU cost). Drop in sharded mode — round-robin splits adjacent features across shards so the flag does little.
```

**DO NOT use `--no-feature-limit` or `--no-tile-size-limit`.** Both are present in many starter scripts; they produce tiles browsers can't render. Tippecanoe's defaults are correct.

**Sharded caveat:** tile-join (Felt v2.79) doesn't support `--maximum-tile-bytes` / `--drop-densest-as-needed` at merge time. Per-shard caps are the only enforcement. Round-robin sharding makes this OK — merged tile sizes recover to ~natural global density.

### What didn't work + why (don't repeat these mistakes)

| approach | result | reason |
| -------- | ------ | ------ |
| Single-process tippecanoe at 96-c, 124M polys, full-detail=14, --detect-shared-borders | TIMEOUT at 8h | Sort + write phases single-thread; --detect-shared-borders builds an O(N²)-ish edge graph |
| Hierarchical tile-join (96 → 8 → 1) | **slower** than 96 → 1 | The final 8-input merge still serializes the full output write; the parallel 8-way phase saved ~30 min but the final merge added ~35 min |
| GeoJSON-seq streaming via Python `shapely → mapping → json.dumps` | bottlenecked at single thread | the stream is single-producer; tippecanoe's --read-parallel only helps with multiple input *files*, not one stream |
| planetiler with custom YAML schema | infeasible | planetiler-custommap doesn't support GeoParquet input; would need a custom Java Profile + Maven build (~2h setup just to start) |
| `tile-join --maximum-tile-bytes` | flag rejected | this version's tile-join doesn't expose it |

## Stage 5 — Faster path for repeated runs: geographic-sharding + `pmtiles merge`

If you'll iterate on this pipeline regularly, the real speedup is here. The architecture worth investing in:

```
1. Geographic shard at z=3 tile boundaries → 64 cells
2. Build z=0..2 once from all FGBs combined (small, ~1-2 min)
3. Build z=3..14 in 64 parallel tippecanoes, each over its own cell's FGB
   → 64 sub-pmtiles with DISJOINT (non-overlapping) tile coverage
4. go-pmtiles `pmtiles merge low.pmtiles cell_*.pmtiles → final.pmtiles`
   → byte-level concatenation, no MVT decode/encode, ~2-5 min
```

Why dramatically faster: `pmtiles merge` is O(bytes copied), tile-join is O(features × overlapping_inputs). For 124M features the difference is 5-10× on the merge step alone.

Caveats:

- Polygon clipping at cell boundaries needed (or accept seam artifacts at high zoom)
- z<3 must use feature-level merging (separate small build)
- All inputs must be `clustered` per pmtiles spec (tippecanoe writes clustered by default)

Decision rule: one-shot build → tile-join is fine. Annual / repeated builds → invest in geographic sharding.

## Cluster and I/O notes

- At this scale, request a full fat node (96+ cores) and stage inputs to local NVMe scratch — never read 96-way concurrent from a network filesystem.
- The single-process path needs an 8h+ walltime budget (and timed out anyway); the sharded path fits comfortably in 1.5h.
- Make every stage resumable: polygonize skips existing parquet shards, the FGB step skips existing batch outputs, and wrapper scripts trap on EXIT and print the resume command.
- **Never pass `--force` from a wrapper script.** A wrapper that auto-passed `--force` once wiped a near-complete zarr store when re-run to fill in errored shards. Add a preflight that refuses to start if the existing store is missing expected arrays.

## Quick reference: when each tool is right

| tool | use when | avoid when |
| ---- | -------- | ---------- |
| **tippecanoe (FGB input, sharded + tile-join)** | one-shot or occasional rebuilds, <500M features | repeated rebuilds where the merge step dominates |
| **planetiler** | annual rebuilds, willing to write a Java Profile | one-shot or non-Java teams |
| **pmtiles merge** (go-pmtiles) | combining geographically-disjoint pmtiles | inputs have any tile-coordinate overlap |
| **tile-join** (Felt) | combining round-robin or other overlapping pmtiles | inputs are disjoint (use pmtiles merge — much faster) |

## Common errors + fixes

- **`FeatureError: NULL geometry not supported with spatial index`** during FGB write — drop `geom.notna() & ~geom.is_empty & geom.is_valid` rows before write.
- **`tile-join: unrecognized option '--maximum-tile-bytes'`** — Felt tile-join doesn't expose this; per-shard caps from sub-builds are the only enforcement.
- **Tippecanoe progress hangs at "99.9% 14/x/y"** — stuck on the very densest z=14 tiles in agricultural regions (Iowa/Punjab/Po Valley). Either wait, or drop `--detect-shared-borders` and rebuild.
- **pmtiles file size grows then stops, but job is still running** — single-threaded final-seal phase. Can take 30+ min on a multi-GB output written to network storage. Stage output to local scratch first to mitigate.
