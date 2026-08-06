"""Manifest-driven work lists for Zarr pyramid builds.

Sparse stores omit chunks for all-nodata regions. Listing what exists first means
workers never issue a read for a region that cannot contain data, and gives exact
progress accounting and a cheap completeness proof.

Zarr v3 shard/chunk keys look like:  <array_path>/c/<i0>/<i1>/.../<iN>
with one index per array dimension (the chunk_key_encoding default separator "/").
"""

import re


def shard_key_re(ndim):
    """Regex capturing the ndim trailing chunk-grid indices of a zarr v3 key."""
    return re.compile(r"/c/" + r"/".join([r"(\d+)"] * ndim) + r"$")


def list_shard_indices(list_objects, array_path, ndim):
    """Set of chunk-grid index tuples present for an array.

    list_objects: callable(prefix) -> iterable of key strings. Wrap whatever client
        you have (obstore, boto3 paginator, fsspec.find, local walk).
    """
    rx = shard_key_re(ndim)
    found = set()
    for key in list_objects(f"{array_path}/c/"):
        m = rx.search(key)
        if m:
            found.add(tuple(int(g) for g in m.groups()))
    return found


def grid_blocks(shape, shard, axes):
    """Yield per-axis block ranges over `axes`, as (start, stop) along each axis."""
    ranges = []
    for ax in axes:
        step = shard[ax]
        ranges.append([(s, min(s + step, shape[ax])) for s in range(0, shape[ax], step)])
    return ranges


def tasks_from_parent(
    out_shape, out_shard, parent_shape, parent_shard, parent_present,
    spatial_axes=(-2, -1), leading_sizes=(), factor_step=2,
):
    """Output-shard tasks whose input region actually contains data.

    Returns a list of (leading_index_tuple, [(y0, y1), (x0, x1), ...]) windows in the
    *output* grid. A task is emitted only if some parent shard overlaps its input
    window, which is what prunes empty ocean/AOI-exterior without any reads.

    parent_present: set of parent chunk-grid index tuples, from list_shard_indices.
    leading_sizes: sizes of non-spatial leading dims (e.g. (time, band)) that the
        shard spans one-per-object; iterate whichever of those index the shard grid.
    """
    ndim = len(out_shape)
    axes = [a % ndim for a in spatial_axes]
    blocks = grid_blocks(out_shape, out_shard, axes)

    lead_iter = [()]
    for n in leading_sizes:
        lead_iter = [prev + (i,) for prev in lead_iter for i in range(n)]

    tasks = []
    for lead in lead_iter:
        for combo in _product(blocks):
            in_win = [(s * factor_step, min(e * factor_step, parent_shape[ax]))
                      for (s, e), ax in zip(combo, axes)]
            if _parent_overlaps(lead, in_win, axes, parent_shard, parent_present):
                tasks.append((lead, combo))
    return tasks


def _product(lists):
    out = [()]
    for lst in lists:
        out = [prev + (item,) for prev in out for item in lst]
    return out


def _parent_overlaps(lead, in_win, axes, parent_shard, parent_present):
    idx_ranges = []
    for (s, e), ax in zip(in_win, axes):
        step = parent_shard[ax]
        idx_ranges.append(range(s // step, (e - 1) // step + 1))
    for combo in _product([list(r) for r in idx_ranges]):
        if lead + combo in parent_present:
            return True
    return False


def is_complete(present_count, target_count):
    """Completeness proof: each object maps to exactly one required task, so
    count == target rules out gaps without reading any data."""
    return present_count == target_count


def stripe(tasks, index, nstripes):
    """Deterministic partition of a STABLE task list.

    Always stripe before filtering for resume. Filtering first lets concurrent
    workers see different done-sets, producing different-length lists, and
    tasks[i::N] over those is no longer a partition — work is both duplicated and
    silently dropped. See references/pitfalls.md.
    """
    if nstripes <= 0:
        raise ValueError("nstripes must be >= 1")
    return tasks[index::nstripes]


def drop_existing(tasks, present, key_of):
    """Filter a stripe's own tasks against existing objects (resume).

    Apply AFTER stripe(). `key_of(task)` must map a task to its output chunk-grid
    index tuple.

    Caveat: this treats "object exists" as "object is correct", which holds only if
    the parent level was complete when that object was written. If a level ever ran
    against a partial parent, delete its chunk prefix and rebuild instead.
    """
    return [t for t in tasks if key_of(t) not in present]
