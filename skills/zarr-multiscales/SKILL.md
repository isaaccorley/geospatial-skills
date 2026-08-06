---
name: zarr-multiscales
description: "Build GeoZarr multiscale pyramids (overviews) into existing Zarr stores for tile/web streaming — choosing a resampling operator that respects the data's semantics (probability simplex, categorical, continuous), cascading levels, striping work across batch workers or dask without losing shards, and verifying completeness. Use when adding overviews/pyramids/multiscales to a Zarr or GeoZarr store, downsampling ML prediction rasters, or debugging a pyramid with missing or wrong shards."
---

# Zarr Multiscales

Adding a multiscale pyramid to a Zarr store sounds mechanical — halve, repeat. In
practice the failure modes are semantic (wrong resampling operator silently changes
what the data means) and distributed (a partitioning bug loses shards while every
job reports success). This skill covers both.

For the CRS / CF / `grid_mapping` side of a georeferenced store, use the `geozarr`
skill — this one assumes that layer is handled and focuses on the pyramid.

## Pick the resampling operator from the data's semantics

This is the decision that matters most, and it is not a style preference. Ask what
invariant the data carries, then pick the operator that preserves it.

| Data | Operator | Why |
|---|---|---|
| **Class probabilities / softmax** (sums to 1) | `average` | Mean of vectors each summing to 1 also sums to 1, by linearity. **No renormalization needed.** |
| **Single probability / continuous** (reflectance, NDVI, elevation) | `average` | Minimizes aliasing; the physically meaningful reduction. |
| **Categorical / class labels** (land cover, argmax output) | `mode` | Averaging label *integers* is meaningless (class 1 + class 3 ≠ class 2). |
| **Binary mask** | `average` → keeps fraction, or `mode` → keeps a mask | Decide whether the overview means "fraction covered" or "majority class". |
| **Counts / population** | `sum` | Preserves the total; averaging changes units per cell. |
| **Anything you will threshold later** | `average`, threshold at read time | Thresholding before averaging destroys sub-pixel information. |

**Never use `nearest` for overviews** of continuous or probabilistic data. It
preserves per-pixel validity but aliases badly — thin features flicker in and out
across zoom levels.

**Prefer probabilities over argmax for pyramids.** If you have both, build the
pyramid from probabilities and argmax at read time. Averaging probabilities then
taking argmax is well-defined; taking the mode of argmax labels throws away
confidence and produces different, worse answers at coarse zooms.

### Two details that make average pooling actually correct

Both of these are easy to get wrong and hard to notice:

1. **Joint validity mask across the "vector" dimension.** For multi-band data with a
   cross-band invariant (like sum-to-1), a pixel must contribute only if it is valid
   in *all* bands. Averaging each band over its own nodata mask makes bands average
   over different pixel sets, and the coarse vector drifts off the simplex.

2. **Nodata-aware reduction.** A block averages only its valid cells; an all-nodata
   block stays nodata. Otherwise ocean/fill bleeds into real data at every level.

Implement the masked mean as explicit `sum/count`, not `np.nanmean`:

```python
valid = np.isfinite(block)
block = np.where(valid, block, 0.0)
sums   = block.reshape(b, H // 2, 2, W // 2, 2).sum(axis=(2, 4))
counts = valid.reshape(b, H // 2, 2, W // 2, 2).sum(axis=(2, 4))
out = np.divide(sums, counts, out=np.full_like(sums, np.nan), where=counts > 0)
```

`np.nanmean` warns on all-nodata blocks, and silencing that needs
`warnings.catch_warnings()`, which mutates global state and is **not thread-safe** —
a real bug when downsampling in a thread pool. `sum/count` is also faster and makes
the all-nodata case an intentional NaN rather than a suppressed warning.

See `scripts/downsample.py` for a ready implementation plus a `mode` variant.

## Cascade, don't re-read the source

Build level 2 from the original, level 4 from level 2, level 8 from level 4. Each
pass reads a quarter of the previous, so the entire tail costs ~33% more than the one
unavoidable full-resolution read. Building every level directly from level 0 costs
~Nx that.

The cascade's cost is that levels become *dependent*: a level built on an incomplete
parent is silently wrong. That is what the completeness gate below is for.

## Align output shards to input shards

Choose the output shard size so that **one input shard maps to a whole number of
output shards** (ideally exactly one). If source shards are 8192² and you write 4096²
output shards, each task reads exactly one source shard and writes exactly one output
object. Consequences:

- No two workers ever write the same object → **no write races**, no read-modify-write
- Any task can be retried independently
- Work unit = one output shard, which makes striping and resume trivial

Chunk *inside* the shard for tile serving: small inner chunks (256–512 px) inside
larger shards (2048–4096 px) so a map tile fetches a small byte range instead of a
whole shard. Sharding keeps object counts sane; inner chunks keep tile reads cheap.

## Prune empty regions by listing, not reading

Sparse stores (ocean, tiles outside an AOI) omit chunks entirely. **List the shard
keys first** and derive the work list from what exists:

```python
# zarr v3 shard keys: <array_path>/c/<t>/<...>/<yi>/<xi>
present = {(t, yi, xi) for path in list_objects(prefix=f"{array}/c/")
           if (m := KEY_RE.search(path)) for t, _, yi, xi in [map(int, m.groups())]}
```

An output task is worth running only if some input shard overlaps its window. On a
global 10 m store this pruned 188,160 naive tasks to 84,870 real ones — 55% of the
grid was all-nodata ocean and was never fetched. See `scripts/manifest.py`.

## Striping across workers — the subtle bug

**Partition the stable task list first, then filter for resume. Never the reverse.**

```python
# CORRECT
mine = tasks[stripe::nstripes]                 # deterministic, timing-independent
mine = [t for t in mine if t not in already_done]

# WRONG — silently loses work
kept = [t for t in tasks if t not in already_done]   # each worker sees a different
mine = kept[stripe::nstripes]                       # `already_done` → different length
```

Why the wrong order breaks: concurrent workers list "already done" at slightly
different moments, so each gets a differently-*sized* filtered list. `tasks[i::N]`
over different-length lists is no longer a partition — subsets overlap, and some
tasks are claimed by nobody.

This is a genuinely nasty bug because **nothing fails**. In one real run, a level
reported `wrote 22353, skipped 0` across six batch array tasks that all reported
success while only **14,974 of 22,482** objects existed. The next level then built nodata
holes on top of it. It surfaced only because a progress table showed the parent at
`66.6% partial` while the child was already `RUNNING`.

Test it (see `scripts/test_striping.py`): assert the stripes partition exactly even
when each worker observes a *different* done-set, and keep a test asserting the wrong
order does lose tasks so the guard cannot rot silently.

## Completeness gate between levels

**Job success is not data completeness.** Scheduler dependency chains (`afterok`-style),
dask futures resolving, and exit code 0 all prove the *processes* finished — not that
they wrote every shard.
Gate on real object counts:

```python
if factor > 2:
    have = len(list_shards(store, factor // 2))
    want = len(tasks_from_manifest(factor // 2, list_shards(store, factor // 4)))
    if have != want:
        raise RuntimeError(f"parent {factor // 2}x incomplete: {have}/{want}; "
                           "finish it before building this level")
```

Because each object maps to exactly one required task, `count == target` is a
sufficient proof of no gaps — cheap and total, no data reads.

Run this as a gate in the builder, not only as a post-hoc report, so a
misconfigured resume cannot start on a partial parent.

## Long-running jobs: credentials and resume

- **Token expiry.** Temporary S3/STS credentials often last far less than the job
  (source.coop defaults to ~40 min). Request the maximum, and **re-open the store
  periodically** (every N tasks) so a fresh token is picked up. Otherwise a
  multi-hour job dies partway with 403s.
- **Resume must be object-level.** `--skip-existing` that checks "does this object
  exist" makes any timeout or preemption cheap. But it treats *exists* as *correct* —
  only true if the parent was complete when that shard was written. If a level ever
  ran against a partial parent, **delete that level's chunk prefix and rebuild**
  rather than resuming onto it.
- **Let task exceptions propagate.** A failed shard should fail the worker so the
  scheduler retries it. Catching and logging leaves a permanent hole in the pyramid.

## Concurrency is usually the bottleneck

Pyramid builds against object storage are network-bound, not CPU-bound. Measure
before sizing: in one case a single stream sustained 19 MB/s while 48 concurrent
streams reached 1.8 GB/s — a ~90x difference that decides between a week and a few
hours. Scale the worker/thread count, not the core count, and re-measure aggregate
throughput to check for server-side throttling.

## Metadata: additive, and don't break level 0

To add a pyramid to a *published* store without disturbing it:

1. Write each level as a **sibling group** (`2x`, `4x`, … or `0`, `1`, `2`, …), each a
   self-contained dataset with its own coord arrays and CRS variable, so it opens
   standalone: `xr.open_zarr(store, group="8x")`.
2. Add only the `multiscales` attribute to the root. Level 0 stays the root arrays.
3. Re-consolidate metadata so one request serves the whole pyramid.
4. **Back up the root metadata first** — adding an attribute rewrites `zarr.json`.
5. **Prove level 0 is untouched**: diff every level-0 node's metadata against the
   backup, byte for byte, and confirm the only root change is the added attribute.

```json
{"multiscales": [{
  "tile_matrix_set": "WGS84Quad",
  "resampling_method": "average",
  "datasets": [{"path": "."}, {"path": "2x"}, {"path": "4x"}]
}]}
```

Per-level geometry: pixel size scales by the factor, **origin is unchanged**, shape
is ceil-halved each step. Coordinates are cell centers (`x0 + (i + 0.5) * dx`) while
`GeoTransform` is pixel-edge — see the `geozarr` skill.

### How deep?

Stop when the coarsest level is roughly one tile (a few hundred px on the long side),
so a viewer can zoom out to the whole dataset. Tail levels are nearly free — each is
a quarter of the last, so the entire tail beyond level 2 is ~1/3 of one level-2 pass.
A 4M-px-wide global 10 m grid reaches ~490x192 at factor 8192, i.e. 13 levels.

## Verification checklist

Do not declare a pyramid done on job exit codes. Check, in increasing cost:

1. **Counts** — every level's object count equals its manifest target (proves no gaps).
2. **Metadata** — per level: shape, dtype, `dimension_names`, shard/chunk shape,
   `grid_mapping`, CRS attrs, coord length/spacing, cell-center offset, `GeoTransform`
   pixel size scaled and origin unchanged, y descending for north-up.
3. **Invariants on real data** — sampled shards: value range, nodata mask consistent
   across bands, and the semantic invariant (e.g. sums to 1).
4. **Re-derive** — recompute sampled shards from the parent level and compare; expect
   bitwise-equal (`maxdiff == 0`) for a deterministic reduction.
5. **Stripe-aware sampling** — check first/middle/last of every stripe, not random
   shards. Random sampling can miss an entire starved stripe, which is exactly what a
   partitioning bug produces.
6. **Coverage sanity** — the coarsest level's valid-data fraction should match the
   source's occupancy. If a global store is 45.1% land, the top of the pyramid should
   be too; drift means nodata bled or data was lost.
7. **Client round-trip** — open the published URL *anonymously* (no credentials) the
   way a browser will, and confirm CRS/resolution/bounds per level.

`scripts/verify.py` implements 1–6 as a gate that exits non-zero.

## Reference files

- `scripts/downsample.py` — thread-safe nodata-aware `average` and `mode` reducers
- `scripts/manifest.py` — shard-key listing and manifest-pruned task generation
- `scripts/verify.py` — completeness/metadata/data/stripe verification harness
- `scripts/test_striping.py` — partition regression tests (including the anti-rot test)
- `references/pitfalls.md` — the failure catalogue with symptoms and fixes
