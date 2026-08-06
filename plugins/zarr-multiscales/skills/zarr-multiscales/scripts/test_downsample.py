"""Tests for the generic reducers. Run: pytest test_downsample.py"""

import numpy as np
import pytest

from downsample import (
    cell_centers,
    downsample_average,
    downsample_mode,
    downsample_sum,
    level_shape,
)


def simplex(b, h, w, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.random((b, h, w))
    return (x / x.sum(axis=0, keepdims=True)).astype(np.float32)


def test_average_preserves_simplex():
    p = simplex(3, 8, 8)
    out = downsample_average(p, vector_axis=0)
    assert out.shape == (3, 4, 4)
    np.testing.assert_allclose(out.sum(axis=0), 1.0, atol=1e-5)


def test_joint_mask_keeps_simplex_when_one_band_is_nodata():
    """A pixel invalid in one band must be dropped for all bands, else the
    coarsened vector drifts off the simplex."""
    p = simplex(3, 2, 2)
    p[1, 0, 0] = np.nan
    out = downsample_average(p, vector_axis=0)
    np.testing.assert_allclose(out.sum(axis=0), 1.0, atol=1e-5)


def test_without_joint_mask_simplex_breaks():
    """Guard the guard: per-band masking really does break the invariant."""
    p = simplex(3, 2, 2)
    p[1, 0, 0] = np.nan
    out = downsample_average(p, vector_axis=None)
    assert not np.allclose(out.sum(axis=0), 1.0, atol=1e-5)


def test_all_nodata_block_stays_nodata():
    p = np.full((3, 2, 2), np.nan, dtype=np.float32)
    out = downsample_average(p, vector_axis=0)
    assert out.shape == (3, 1, 1) and np.isnan(out).all()


def test_no_runtime_warning_on_all_nodata(recwarn):
    """np.nanmean warns "Mean of empty slice" here. Suppressing that needs
    warnings.catch_warnings(), which mutates global state and is not thread-safe —
    so the reducer must not warn at all."""
    out = downsample_average(np.full((1, 2, 2), np.nan))
    assert np.isnan(out).all()
    assert [w for w in recwarn if issubclass(w.category, RuntimeWarning)] == []


def test_average_value_is_the_mean():
    a = np.array([[[1.0, 3.0], [5.0, 7.0]]])
    assert downsample_average(a)[0, 0, 0] == pytest.approx(4.0)


def test_average_ignores_nodata_cells():
    a = np.array([[[1.0, 3.0], [np.nan, np.nan]]])
    assert downsample_average(a)[0, 0, 0] == pytest.approx(2.0)


def test_sum_preserves_total():
    a = np.arange(16, dtype=np.float64).reshape(1, 4, 4)
    assert downsample_sum(a).sum() == pytest.approx(a.sum())


def test_mode_picks_majority_not_mean():
    a = np.array([[[1, 1], [1, 3]]])
    out = downsample_mode(a)
    assert out[0, 0, 0] == 1, "mode must not average labels into a class that isn't there"


def test_mode_ignores_nodata_label():
    a = np.array([[[0, 5], [5, 0]]])
    assert downsample_mode(a, nodata=0)[0, 0, 0] == 5


def test_odd_dims_ceil_halved_and_padded_at_trailing_edge():
    p = simplex(3, 5, 7)
    out = downsample_average(p, vector_axis=0)
    assert out.shape == (3, 3, 4)
    # top-left cell is a true average of real data, i.e. origin preserved
    assert np.isfinite(out[:, 0, 0]).all()


def test_level_shape_matches_repeated_ceil_halving():
    assert level_shape((1566049, 4007517), 2) == (783025, 2003759)
    assert level_shape((1566049, 4007517), 8) == (195757, 500940)


def test_level_shape_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        level_shape((10, 10), 3)


def test_cell_centers_offset_half_pixel():
    np.testing.assert_allclose(cell_centers(-180.0, 1.0, 3), [-179.5, -178.5, -177.5])


def test_leading_dims_are_untouched():
    a = simplex(3, 4, 4)[None].repeat(2, axis=0)  # (t=2, band=3, y, x)
    out = downsample_average(a, ys=-2, xs=-1, vector_axis=1)
    assert out.shape == (2, 3, 2, 2)
    np.testing.assert_allclose(out.sum(axis=1), 1.0, atol=1e-5)
