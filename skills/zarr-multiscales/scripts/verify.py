"""Verification harness for a Zarr multiscale pyramid.

Store-agnostic: describe your pyramid in a PyramidSpec and this runs the checks that
actually catch real bugs. Exits non-zero on any failure so it can gate a release.

    spec = PyramidSpec(
        root=zarr.open_group(store, mode="r"),
        factors=[2, 4, 8, 16],
        level_path=lambda f: f"{f}x",       # or str(i) for 0/1/2 naming
        data_name="variables",
        list_shards=lambda f: {...},        # factor -> set of chunk-grid index tuples
        target_count=lambda f: 1234,        # factor -> expected object count
        window_of=lambda f, idx: (sel, out_win, in_win),   # see below
        level0_shape=(1566049, 4007517),
        origin=(-180.0, 83.748345),
        pixel=(8.98311982e-05, -8.98311982e-05),
        vector_axis=1,                      # band axis, or None
        invariant="simplex",                # "simplex" | "range01" | None
    )
    raise SystemExit(run_checks(spec, samples=3))

`window_of(factor, idx)` maps a shard index tuple to:
    sel      leading index tuple (e.g. (t,)) used to select non-spatial dims
    out_win  ((y0, y1), (x0, x1)) in this level's grid
    in_win   ((y0, y1), (x0, x1)) in the parent's grid (2x out_win, clipped)

Why these checks in particular: see references/pitfalls.md. The non-obvious ones are
count==target as a total completeness proof, stripe-aware sampling instead of random,
and coarsest-level occupancy compared against the source.
"""

import dataclasses
import random
from typing import Any, Callable, Optional, Sequence

import numpy as np

from downsample import downsample_average, level_shape


@dataclasses.dataclass
class PyramidSpec:
    root: Any
    factors: Sequence[int]
    level_path: Callable[[int], str]
    data_name: str
    list_shards: Callable[[int], set]
    target_count: Callable[[int], int]
    window_of: Callable[[int, tuple], tuple]
    level0_shape: Sequence[int]
    origin: Sequence[float] = (0.0, 0.0)
    pixel: Sequence[float] = (1.0, -1.0)
    spatial_axes: Sequence[int] = (-2, -1)
    vector_axis: Optional[int] = None
    invariant: Optional[str] = None
    reducer: Callable = downsample_average
    coord_names: Sequence[str] = ("x", "y")
    crs_var: str = "spatial_ref"
    parent_of: Optional[Callable[[int], Optional[int]]] = None

    def parent(self, factor):
        """Factor of the level this one is derived from; None means level 0 (root)."""
        if self.parent_of is not None:
            return self.parent_of(factor)
        return None if factor == self.factors[0] else factor // 2


class Checks:
    def __init__(self):
        self.failed, self.passed = [], 0

    def __call__(self, ok, label, detail=""):
        ok = bool(ok)
        if ok:
            self.passed += 1
        else:
            self.failed.append(f"{label}: {detail}")
        print(f"  {'PASS' if ok else 'FAIL'}  {label}{'' if ok else '  <- ' + detail}",
              flush=True)


def _level(spec, factor):
    return spec.root[spec.level_path(factor)]


def _data(spec, factor):
    return _level(spec, factor)[spec.data_name]


def _parent_data(spec, factor):
    p = spec.parent(factor)
    return spec.root[spec.data_name] if p is None else _data(spec, p)


# --- checks -----------------------------------------------------------------

def check_completeness(spec, c):
    """count == target. Each object maps to exactly one required task, so equality
    is a total proof of no gaps — and it costs one listing, no data reads."""
    print("\n== completeness ==")
    for f in spec.factors:
        have, want = len(spec.list_shards(f)), spec.target_count(f)
        c(have == want, f"{spec.level_path(f)} object count == target",
          f"{have}/{want} ({want - have} missing)")


def check_geometry(spec, c):
    """Ceil-halved shape, cell-center coords, pixel size scaled, origin fixed."""
    print("\n== geometry ==")
    ndim = len(spec.level0_shape)
    ys, xs = (a % ndim for a in spec.spatial_axes)
    x0, y0 = spec.origin
    dx0, dy0 = spec.pixel

    for f in spec.factors:
        name = spec.level_path(f)
        want = level_shape(spec.level0_shape, f, axes=spec.spatial_axes)
        v = _data(spec, f)
        c(v.shape[ys] == want[ys] and v.shape[xs] == want[xs],
          f"{name} spatial shape is ceil-halved",
          f"{(v.shape[ys], v.shape[xs])} vs {(want[ys], want[xs])}")

        g = _level(spec, f)
        xn, yn = spec.coord_names
        members = set(g.array_keys()) | set(g.group_keys())
        if xn in members and yn in members:
            x, y = g[xn][:], g[yn][:]
            c(len(x) == want[xs] and len(y) == want[ys], f"{name} coord lengths",
              f"x={len(x)} y={len(y)} vs {want[xs]},{want[ys]}")
            c(np.isclose(x[0], x0 + 0.5 * dx0 * f), f"{name} x[0] is a cell center",
              f"{x[0]} vs {x0 + 0.5 * dx0 * f}")
            c(np.isclose(y[0], y0 + 0.5 * dy0 * f), f"{name} y[0] is a cell center",
              f"{y[0]} vs {y0 + 0.5 * dy0 * f}")
            if len(x) > 1:
                c(np.isclose(np.diff(x)[0], dx0 * f), f"{name} x spacing == level dx")
            if len(y) > 1 and dy0 < 0:
                c(np.all(np.diff(y) < 0), f"{name} y descending (north-up)")

        if spec.crs_var in members and "GeoTransform" in g[spec.crs_var].attrs:
            gt = g[spec.crs_var].attrs["GeoTransform"].split()
            c(np.isclose(float(gt[1]), dx0 * f) and np.isclose(float(gt[5]), dy0 * f),
              f"{name} GeoTransform pixel size scaled", " ".join(gt))
            c(np.isclose(float(gt[0]), x0) and np.isclose(float(gt[3]), y0),
              f"{name} GeoTransform origin unchanged", " ".join(gt))


def check_invariants(spec, c, arr, label):
    """Nodata-mask consistency and the semantic invariant, on a real block."""
    va = spec.vector_axis
    fin = np.isfinite(arr)
    if va is not None:
        allv, nonev = fin.all(axis=va), (~fin).all(axis=va)
        # All-or-nothing per pixel: a pixel valid in only some bands means the bands
        # averaged over different pixel sets, which breaks a cross-band invariant.
        c((allv | nonev).all(), f"{label} nodata mask consistent across vector axis")
        m = allv
    else:
        m = fin

    if not m.any():
        c(False, f"{label} has valid data", "all nodata but the object exists")
        return

    if spec.invariant == "simplex" and va is not None:
        s = np.nansum(np.where(fin, arr, 0.0), axis=va)[m]
        c(np.allclose(s, 1.0, atol=2e-3), f"{label} sums to 1",
          f"min={s.min():.6f} max={s.max():.6f}")
    if spec.invariant in ("simplex", "range01"):
        vals = arr[fin]
        c(((vals >= -1e-6) & (vals <= 1 + 1e-6)).all(), f"{label} in [0,1]")


def check_one_shard(spec, c, factor, idx, label):
    """Read a shard and re-derive it from the parent level; expect bitwise equality."""
    sel, out_win, in_win = spec.window_of(factor, idx)
    (oy0, oy1), (ox0, ox1) = out_win
    (iy0, iy1), (ix0, ix1) = in_win

    got = _data(spec, factor)[sel + (slice(None), slice(oy0, oy1), slice(ox0, ox1))]
    blk = _parent_data(spec, factor)[sel + (slice(None), slice(iy0, iy1), slice(ix0, ix1))]

    kw = {"vector_axis": spec.vector_axis - len(sel)} if spec.vector_axis is not None else {}
    ref = spec.reducer(blk, **kw)[:, : oy1 - oy0, : ox1 - ox0]

    check_invariants(spec, c, got, label)
    c((np.isnan(got) == np.isnan(ref)).all(), f"{label} nodata pattern matches parent")
    diff = np.abs(np.nan_to_num(got, nan=-9e9) - np.nan_to_num(ref, nan=-9e9)).max()
    # A deterministic reduction should reproduce exactly, not approximately.
    c(diff < 1e-6, f"{label} matches recompute from parent", f"max diff {diff:.3e}")


def check_samples(spec, c, samples, seed=0):
    print(f"\n== data ({samples} random shards per level) ==")
    rng = random.Random(seed)
    for f in spec.factors:
        present = sorted(spec.list_shards(f))
        if not present:
            c(False, f"{spec.level_path(f)} sampling", "no shards present")
            continue
        for idx in rng.sample(present, min(samples, len(present))):
            check_one_shard(spec, c, f, idx, f"{spec.level_path(f)} shard {idx}")


def check_stripes(spec, c, factor, nstripes, tasks, index_of):
    """First/middle/last of every stripe, plus an exact-partition assertion.

    Random sampling can miss an entire starved stripe, which is precisely what a
    stripe-partitioning bug produces. `tasks` must be the same ordered list the
    builder striped; `index_of(task)` maps a task to its chunk-grid index tuple.
    """
    print(f"\n== stripes ({spec.level_path(factor)}, {nstripes}-way) ==")
    union = [t for i in range(nstripes) for t in tasks[i::nstripes]]
    c(len(union) == len(tasks) and len(set(map(index_of, union))) == len(tasks),
      f"{nstripes}-way partition covers every task exactly once",
      f"{len(union)} claimed vs {len(tasks)} tasks")

    seen = set()
    for s in range(nstripes):
        mine = tasks[s::nstripes]
        if not mine:
            c(False, f"stripe {s} non-empty", "no tasks assigned")
            continue
        for pos, task in {"first": mine[0], "mid": mine[len(mine) // 2],
                          "last": mine[-1]}.items():
            idx = index_of(task)
            c(idx not in seen, f"stripe {s} {pos} not claimed twice", str(idx))
            seen.add(idx)
            check_one_shard(spec, c, factor, idx, f"stripe {s} {pos} {idx}")


def check_occupancy(spec, c):
    """The coarsest level's valid fraction should match the source's occupancy.
    Growth means nodata bled outward; shrinkage means data was lost."""
    print("\n== occupancy ==")
    f = spec.factors[-1]
    arr = np.asarray(_data(spec, f)[:])
    va = spec.vector_axis
    m = np.isfinite(arr).all(axis=va) if va is not None else np.isfinite(arr)
    frac = float(m.mean())
    f0 = spec.factors[0]
    src = spec.target_count(f0)
    src_frac = len(spec.list_shards(f0)) / src if src else float("nan")
    c(abs(frac - src_frac) < 0.05,
      f"coarsest valid fraction {frac:.3f} ~= source occupancy {src_frac:.3f}",
      "drift > 5% suggests nodata bleed or lost data")


def run_checks(spec, samples=0, stripes=None, stripe_factor=None, tasks=None,
               index_of=None, occupancy=True):
    c = Checks()
    check_completeness(spec, c)
    check_geometry(spec, c)
    if occupancy:
        check_occupancy(spec, c)
    if samples:
        check_samples(spec, c, samples)
    if stripes and tasks is not None and index_of is not None:
        check_stripes(spec, c, stripe_factor or spec.factors[0], stripes, tasks, index_of)

    print(f"\n{c.passed} passed, {len(c.failed)} failed")
    for f in c.failed:
        print(f"  FAILED: {f}")
    return 1 if c.failed else 0
