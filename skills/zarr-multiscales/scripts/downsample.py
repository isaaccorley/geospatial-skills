"""Nodata-aware 2x block reducers for building Zarr multiscale pyramids.

Generic over layout: pass the axes to reduce. All reducers are thread-safe (no
global warning-filter state), which matters because pyramid builds are network
bound and run in thread pools.

Choose the reducer from the data's semantics, not by taste:

    average  probabilities (incl. softmax vectors), reflectance, elevation, NDVI
    mode     categorical labels / class maps / argmax output
    sum      counts, population

`average` preserves a sum-to-1 constraint across a vector axis automatically: the
mean of vectors each summing to 1 also sums to 1. No renormalization needed.
"""

import numpy as np


def _pair_reshape(a, ys, xs):
    """Reshape so the trailing spatial axes become (n//2, 2) pairs."""
    shape = list(a.shape)
    new = []
    for i, s in enumerate(shape):
        if i == ys or i == xs:
            new += [s // 2, 2]
        else:
            new.append(s)
    return a.reshape(new)


def _pad_odd(a, ys, xs, fill):
    pad = [(0, 0)] * a.ndim
    pad[ys] = (0, a.shape[ys] % 2)
    pad[xs] = (0, a.shape[xs] % 2)
    if pad[ys][1] or pad[xs][1]:
        a = np.pad(a, pad, mode="constant", constant_values=fill)
    return a


def _reduce_axes(ndim, ys, xs):
    """Axis indices of the inserted pair-dims after _pair_reshape."""
    off_y = ys + 1
    off_x = xs + 1 + (1 if xs > ys else 0)
    return (off_y, off_x)


def downsample_average(block, ys=-2, xs=-1, vector_axis=None, nodata=np.nan):
    """Average-pool by 2x over axes (ys, xs), ignoring nodata.

    vector_axis: if given, a pixel contributes only where it is valid across
        *every* element of that axis. Use this for probability vectors — averaging
        each band over its own mask makes bands average over different pixel sets
        and the coarsened vector drifts off the simplex.

    An all-nodata block yields nodata. Odd dimensions are padded with nodata so the
    coarse grid keeps the top-left origin (GDAL overview semantics).
    """
    a = np.asarray(block, dtype=np.float64)
    ys, xs = ys % a.ndim, xs % a.ndim
    valid = np.isfinite(a) if _is_nan(nodata) else (a != nodata)

    if vector_axis is not None:
        va = vector_axis % a.ndim
        joint = valid.all(axis=va, keepdims=True)
        valid = np.broadcast_to(joint, a.shape)

    a = np.where(valid, a, 0.0)
    a = _pad_odd(a, ys, xs, 0.0)
    v = _pad_odd(valid.astype(np.int64), ys, xs, 0)

    ax = _reduce_axes(a.ndim, ys, xs)
    sums = _pair_reshape(a, ys, xs).sum(axis=ax)
    counts = _pair_reshape(v, ys, xs).sum(axis=ax)

    # Explicit sum/count rather than np.nanmean: nanmean warns on all-nodata
    # windows, and suppressing that needs warnings.catch_warnings(), which mutates
    # global state and is not thread-safe. This is also faster, and makes the
    # all-nodata result an intentional nodata rather than a silenced warning.
    out = np.divide(sums, counts,
                    out=np.full(sums.shape, np.nan if _is_nan(nodata) else nodata,
                                dtype=np.float64),
                    where=counts > 0)
    return out.astype(np.asarray(block).dtype, copy=False)


def downsample_sum(block, ys=-2, xs=-1, nodata=np.nan):
    """Sum-pool by 2x. For counts, where averaging would change the units."""
    a = np.asarray(block, dtype=np.float64)
    ys, xs = ys % a.ndim, xs % a.ndim
    valid = np.isfinite(a) if _is_nan(nodata) else (a != nodata)
    a = _pad_odd(np.where(valid, a, 0.0), ys, xs, 0.0)
    v = _pad_odd(valid.astype(np.int64), ys, xs, 0)
    ax = _reduce_axes(a.ndim, ys, xs)
    sums = _pair_reshape(a, ys, xs).sum(axis=ax)
    counts = _pair_reshape(v, ys, xs).sum(axis=ax)
    fill = np.nan if _is_nan(nodata) else nodata
    out = np.where(counts > 0, sums, fill)
    return out.astype(np.asarray(block).dtype, copy=False)


def downsample_mode(block, ys=-2, xs=-1, nodata=None):
    """Majority-vote pool by 2x, for categorical labels.

    Averaging class integers is meaningless (class 1 and 3 do not average to 2), so
    label rasters must use mode. Ties go to the smallest label, which is arbitrary
    but deterministic. All-nodata blocks yield nodata.
    """
    a = np.asarray(block)
    ys, xs = ys % a.ndim, xs % a.ndim
    fill = nodata if nodata is not None else 0
    a2 = _pad_odd(a, ys, xs, fill)
    ax = _reduce_axes(a2.ndim, ys, xs)
    grouped = _pair_reshape(a2, ys, xs)
    # Move the two pair-axes to the end and flatten them into one "votes" axis.
    grouped = np.moveaxis(grouped, ax, (-2, -1))
    votes = grouped.reshape(*grouped.shape[:-2], 4)

    labels = np.unique(a2)
    if nodata is not None:
        labels = labels[labels != nodata]
    if labels.size == 0:
        return np.full(votes.shape[:-1], fill, dtype=a.dtype)

    best_count = np.zeros(votes.shape[:-1], dtype=np.int64)
    best = np.full(votes.shape[:-1], fill, dtype=a.dtype)
    for lab in labels:
        cnt = (votes == lab).sum(axis=-1)
        take = cnt > best_count
        best = np.where(take, lab, best)
        best_count = np.where(take, cnt, best_count)
    return best.astype(a.dtype, copy=False)


def _is_nan(v):
    try:
        return bool(np.isnan(v))
    except TypeError:
        return False


def level_shape(shape, factor, axes=(-2, -1)):
    """Ceil-halved shape after `factor` (power of two) downsampling."""
    out = list(shape)
    steps = int(np.log2(factor))
    if 2**steps != factor:
        raise ValueError(f"factor must be a power of 2, got {factor}")
    for ax in axes:
        ax %= len(out)
        for _ in range(steps):
            out[ax] = (out[ax] + 1) // 2
    return tuple(out)


def cell_centers(origin, pixel, n):
    """1D cell-center coordinates (CF convention). GeoTransform is pixel-edge."""
    return origin + (np.arange(n, dtype=np.float64) + 0.5) * pixel
