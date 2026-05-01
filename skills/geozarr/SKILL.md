---
name: geozarr
description: GeoZarr conventions for geospatial Zarr stores — CF-1.8 grid_mapping, 1D coord arrays, Zarr v3 dimension_names, multiscales, proj:/spatial: namespaces, and rioxarray/GDAL interop. Use when authoring, patching, validating, or ingesting Zarr stores intended to round-trip as georeferenced rasters.
---

# GeoZarr

GeoZarr is a set of modular Zarr conventions for multidimensional georeferenced grids. It bridges the Zarr format with the Climate-and-Forecast (CF) data model, GDAL, and STAC — letting xarray, rioxarray, GDAL, and QGIS open a Zarr store as a properly georeferenced raster without per-tool hacks.

This skill covers what a compliant store looks like, how to author one from scratch, and how to patch existing non-compliant stores in place.

## Status (2026)

- The OGC GeoZarr Standards Working Group is targeting Architecture Board review summer 2026. Spec lives at [zarr-developers/geozarr-spec](https://github.com/zarr-developers/geozarr-spec); rendered draft at [zarr.dev/geozarr-spec](https://zarr.dev/geozarr-spec/documents/standard/template/geozarr-spec.html).
- The spec is **modular**. You can adopt CF + grid_mapping alone, or layer on the experimental `proj:` / `spatial:` / multiscales conventions independently. Each is identified by UUID + JSON Schema in the [Zarr Conventions Framework](https://github.com/zarr-conventions).
- Latest reference release aligns with Zarr v3, CF-1.8+, and GDAL ≥ 3.12 (which reads GeoZarr natively).

## When to use this skill

- Writing a new Zarr from xarray/rioxarray and want it to be readable by GDAL/QGIS as a raster.
- Auditing an existing Zarr that "opens but has no CRS" or where `rio.crs` is `None`.
- Patching a published store in place to add CF + grid_mapping without rewriting chunks.
- Building virtual references (kerchunk / virtualizarr / icechunk) and need the resulting store to be GeoZarr-compliant.
- Adding multiscale overviews (pyramids) for tile-server / web-map consumption.

## The compliance checklist

A minimum-viable GeoZarr-compliant Zarr v3 store has:

1. **Root group attrs**
   - `Conventions: "CF-1.8"` (or later)
   - Optional but recommended: `title`, `institution`, `history`, `source`, `references`.
2. **A spatial_ref / crs scalar variable** (CF "grid mapping variable"). Common names: `spatial_ref`, `crs`. Attrs:
   - `grid_mapping_name` (e.g. `latitude_longitude`, `transverse_mercator`)
   - `crs_wkt` (WKT2 string — what GDAL/rioxarray actually reads)
   - `spatial_ref` (legacy GDAL key, same WKT) — optional but improves compat
   - `GeoTransform: "x0 dx 0 y0 0 dy"` — six-number affine, pixel-edge origin
   - For lat/lon: `semi_major_axis`, `inverse_flattening`, `longitude_of_prime_meridian`
3. **Each data array** carries:
   - `grid_mapping: "spatial_ref"` (the name of the grid mapping variable)
   - `_FillValue` (or `missing_value`) if applicable
   - `units`, `standard_name`, `long_name` when meaningful
4. **1D coordinate arrays** along the spatial axes (`x`/`y` or `lon`/`lat`):
   - dtype `float64`, monotonic, **cell-center** values (`x0 + (i + 0.5) * dx`)
   - `dimension_names: ["x"]` (Zarr v3) or `_ARRAY_DIMENSIONS: ["x"]` (v2)
   - For projected: `standard_name: "projection_x_coordinate"`, `units: "m"`, `axis: "X"`
   - For geographic: `standard_name: "longitude"`, `units: "degrees_east"`, `axis: "X"` (analogous for `y`/latitude)
5. **Dimension names declared on every array** (not just coord arrays) so xarray knows which axis is which.
6. **Consolidated metadata** at the root for fast remote opens (`zarr.consolidate_metadata(store)`).

That's enough for `xarray.open_zarr(...)` + `rioxarray` to recover the CRS and transform, and for `gdalinfo ZARR:...` to print a populated `Coordinate System is:` block.

## Cell-center vs pixel-edge

CF coordinate variables are **cell centers**. The GeoTransform string is **pixel edge** (matches GDAL). Don't mix them up.

```python
# Coordinate arrays — cell centers
x = x0 + (np.arange(NX) + 0.5) * dx
y = y0 + (np.arange(NY) + 0.5) * dy   # dy is negative for north-up

# GeoTransform attribute on spatial_ref — pixel edge
"GeoTransform": f"{x0} {dx} 0 {y0} 0 {dy}"

# bbox (pixel edge): [x0, y0 + NY*dy, x0 + NX*dx, y0]   # for north-up dy<0
```

If your coords are off by half a pixel after a round-trip, this is almost always the bug.

## Zarr v2 vs v3 dimension declaration

| What | v2 | v3 |
|---|---|---|
| Dimension names | `_ARRAY_DIMENSIONS` in `.zattrs` | `dimension_names` field in `zarr.json` |
| Consolidated metadata | `.zmetadata` | `zarr.json` blocks merged into root |
| Sharding | n/a | first-class |

GDAL ≥ 3.12 and recent xarray handle both. virtualizarr ≥ 2.5 emits v3 by default.

## Optional layered conventions

These are independent — adopt as needed. Identified in root attrs by a `zarr_conventions` array of `{uuid, name, spec_url, schema_url}` entries.

### `proj:` (geo-proj v1)

CRS info as root attrs alongside CF grid_mapping:

```json
{
  "proj:code": "EPSG:4326",
  "proj:wkt2": "...",
  "proj:projjson": { ... }
}
```

### `spatial:` (zarr-conventions/spatial v1)

Compact affine + bbox at the root, redundant with grid_mapping but easier to read:

```json
{
  "spatial:dimensions": ["y", "x"],
  "spatial:transform": [dx, 0, x0, 0, dy, y0],
  "spatial:transform_type": "affine",
  "spatial:bbox": [xmin, ymin, xmax, ymax],
  "spatial:shape": [NY, NX],
  "spatial:registration": "pixel"
}
```

### Multiscales / pyramids

For multi-resolution overviews, a parent group holds child groups (`0`, `1`, `2`, …) at successive halvings. Root attrs:

```json
{
  "multiscales": [{
    "tile_matrix_set": "WebMercatorQuad",
    "resampling_method": "average",
    "datasets": [
      {"path": "0"},
      {"path": "1"},
      {"path": "2"}
    ]
  }]
}
```

`tile_matrix_set` may be an OGC TMS identifier, a URI, or inline JSON. Resampling: `nearest`, `average`, `bilinear`, `cubic`, `lanczos`, `mode`.

## Authoring from xarray/rioxarray

```python
import rioxarray  # noqa: F401  — registers .rio
import xarray as xr

da = xr.open_dataset("input.tif").band_data  # already has CRS via rio
ds = da.to_dataset(name="reflectance")
ds.attrs["Conventions"] = "CF-1.8"
ds.rio.write_crs("EPSG:4326", inplace=True)         # writes spatial_ref
ds.rio.write_coordinate_system(inplace=True)        # writes axis/standard_name
ds.rio.write_transform(inplace=True)                # writes GeoTransform on spatial_ref
ds.to_zarr("out.zarr", mode="w", zarr_format=3, consolidated=True)
```

Verify: `xr.open_zarr("out.zarr").reflectance.rio.crs` should be non-None.

## Patching an existing store in place

When you can't rewrite chunks (huge published store), patch metadata only. The pattern:

1. Open the root group `r+`.
2. Create 1D `x`/`y` coord arrays sized `(NX,)` / `(NY,)`, single-chunk, float64. Fill from the GeoTransform with the cell-center +0.5 offset. Set `standard_name` / `units` / `axis` on each.
3. On data arrays, set `grid_mapping = "spatial_ref"`. Drop any stale `coordinates: spatial_ref` that conflicts (CF allows both, but some readers get confused — pick one).
4. On root, set `Conventions = "CF-1.8"`.
5. Re-run `zarr.consolidate_metadata(root.store)`.

Total bytes written for a continental-scale store: usually under 100 MB (the two coord arrays dominate). Always dry-run first — print the plan, then `--apply`.

A re-runnable additive patch is safe; the predicate to skip is "child arrays already exist with the right shape and attrs."

## Common gotchas

- **`rio.crs` is None on read.** Almost always one of: missing `grid_mapping` on the data var, missing `crs_wkt` on `spatial_ref`, or `dimension_names` not set so xarray can't find the spatial axes.
- **Coords half a pixel off.** Cell-center vs pixel-edge confusion. See above.
- **GDAL sees the array but no CRS.** Try `gdalinfo "ZARR:\"path/to/store.zarr\":/data_var_name"`. Inspect `spatial_ref.attrs`. WKT2 missing or malformed is the usual cause.
- **xarray promotes `spatial_ref` to a data var instead of a scalar coord.** Add `coordinates: "spatial_ref"` to the data var's attrs, OR set `decode_coords="all"` on open. Pick one — both is fine in CF but doubly-listing can confuse readers.
- **virtualizarr-built reference store has no `Conventions`.** virtualizarr emits geometry but not CF metadata. You must add it post-hoc.
- **Negative `dy` flipped to positive.** North-up data has `dy < 0`. If you sort coords ascending you reverse the array. Keep `y` descending for north-up.
- **Trailing slash on container prefix.** S3 obstore with prefix needs no trailing slash; Zarr keys are joined with `/` internally.

## Validation

```bash
# Round-trip CRS through rioxarray
python -c "import xarray as xr, rioxarray; print(xr.open_zarr('store.zarr').data_var.rio.crs)"

# GDAL view
gdalinfo 'ZARR:"store.zarr":/data_var'

# Inspect a remote Zarr v3 root
python -c "
import zarr
g = zarr.open_group('s3://bucket/path/store.zarr', mode='r')
print(dict(g.attrs)); print(list(g))
"
```

A draft validator is tracked under [zarr-developers/geozarr-spec issues](https://github.com/zarr-developers/geozarr-spec/issues). Until it lands, the GDAL + rioxarray round-trip is the de facto conformance check.

## Tooling matrix

| Need | Tool |
|---|---|
| Author from raster | `rioxarray` + `xr.to_zarr` |
| Virtual reference store over COGs/NetCDFs | `virtualizarr` ≥ 2.5, `icechunk` |
| Remote object IO | `obstore`, `obspec-utils` |
| Read GeoZarr as raster | GDAL ≥ 3.12, `rioxarray`, QGIS (via GDAL) |
| Tile / pyramid generation | `ndpyramid`, `xarray-multiscale` |
| Visual inspect | [Earthmover Arraylake](https://earthmover.io), `xarray` repr in Jupyter |

## References

- [GeoZarr spec repo](https://github.com/zarr-developers/geozarr-spec)
- [GeoZarr.org](https://geozarr.org)
- [OGC GeoZarr SWG announcement](https://www.ogc.org/announcement/ogc-forms-new-geozarr-standards-working-group-to-establish-a-zarr-encoding-for-geospatial-data/)
- [zarr-conventions framework](https://github.com/zarr-conventions)
- [zarr-experimental/geo-proj](https://github.com/zarr-experimental/geo-proj)
- [CF-1.8 conventions](https://cfconventions.org/cf-conventions/cf-conventions.html)
- [EOPF Sentinel Zarr Explorer](https://explorer.eopf.copernicus.eu/software-services/datamodel/) — large-scale GeoZarr deployment example
