---
name: geozarr
description: GeoZarr conventions for geospatial Zarr stores: CF grid_mapping, coordinate arrays, Zarr v2/v3 dimension declarations, multiscales, proj:/spatial: namespaces, and xarray/rioxarray/GDAL interop. Use when authoring, patching, validating, or ingesting Zarr stores intended to round-trip as georeferenced rasters.
---

# GeoZarr

GeoZarr is a set of modular Zarr conventions for multidimensional georeferenced grids. It bridges the Zarr format with the Climate-and-Forecast (CF) data model, GDAL, and STAC so common tools such as xarray, rioxarray, GDAL, and QGIS can open a Zarr store as a properly georeferenced raster without per-tool metadata patches.

This skill covers what a compliant store looks like, how to author one from scratch, and how to patch existing non-compliant stores in place.

## How to use this skill

Work from the user's actual files, environment, and target reader. Do not assume local paths, private buckets, one cloud provider, or one Python package manager. Prefer examples with placeholders such as `store.zarr`, `data_var`, `s3://bucket/path/`, or `https://example.com/store.zarr`; replace them only when the user provides concrete values.

When advice depends on a moving draft spec or a specific reader version, say so explicitly and verify the installed tool when possible:

```bash
python -c "import zarr, xarray; print('zarr', zarr.__version__, 'xarray', xarray.__version__)"
gdalinfo --version
```

## Status and version guidance

- The OGC GeoZarr Standards Working Group draft lives at [zarr-developers/geozarr-spec](https://github.com/zarr-developers/geozarr-spec); rendered draft at [zarr.dev/geozarr-spec](https://zarr.dev/geozarr-spec/documents/standard/template/geozarr-spec.html).
- The draft is **modular**. You can adopt CF + grid_mapping alone, or layer on `proj:` / `spatial:` / multiscales conventions independently. Treat these layers as compatibility choices, not a single mandatory profile.
- Zarr v2 and v3 are both relevant in real systems. In v2, dimension names live in `_ARRAY_DIMENSIONS`; in v3, they live in `dimension_names`.
- GDAL support varies by version and convention. GDAL 3.11 added Kerchunk reference support; GDAL 3.12 added remote stores without reliable directory listing; GDAL 3.13 added Zarr v3 sharding, multiscales reading, and `SPATIAL_PROJ` georeferencing read/write support.

## When to use this skill

- Writing a new Zarr from xarray/rioxarray and want it to be readable by GDAL/QGIS as a raster.
- Auditing an existing Zarr that "opens but has no CRS" or where `rio.crs` is `None`.
- Patching a published store in place to add CF + grid_mapping without rewriting chunks.
- Building virtual references (kerchunk / virtualizarr / icechunk) and need the resulting store to be GeoZarr-compliant.
- Adding multiscale overviews (pyramids) for tile-server / web-map consumption.

## The compliance checklist

A minimum-viable georeferenced Zarr store has:

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
4. **1D coordinate arrays** along the spatial axes (`x`/`y` or `lon`/`lat`) when the grid is rectilinear:
   - dtype `float64`, monotonic, **cell-center** values (`x0 + (i + 0.5) * dx`)
   - `dimension_names: ["x"]` (Zarr v3) or `_ARRAY_DIMENSIONS: ["x"]` (v2)
   - For projected: `standard_name: "projection_x_coordinate"`, `units: "m"`, `axis: "X"`
   - For geographic: `standard_name: "longitude"`, `units: "degrees_east"`, `axis: "X"` (analogous for `y`/latitude)
5. **Dimension names declared on every array** (not just coord arrays) so readers know which axis is which.
6. **Consolidated metadata** at the root for fast remote opens when supported by the chosen Zarr format and library.

That's enough for `xarray.open_zarr(...)` + `rioxarray` to recover the CRS and transform in common Python workflows, and for GDAL to expose a populated coordinate system when the installed GDAL version supports the chosen convention.

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

Recent xarray handles both. Check the installed GDAL version before promising a specific v3, Kerchunk, multiscale, or `SPATIAL_PROJ` behavior.

## Optional layered conventions

These are independent. Adopt only the layers needed by the target readers. They may be identified in root attrs by a `zarr_conventions` array of `{uuid, name, spec_url, schema_url}` entries.

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

When you cannot or should not rewrite chunks, patch metadata only. The pattern:

1. Open the root group `r+`.
2. Create 1D `x`/`y` coord arrays sized `(NX,)` / `(NY,)`, single-chunk, float64. Fill from the GeoTransform with the cell-center +0.5 offset. Set `standard_name` / `units` / `axis` on each.
3. On data arrays, set `grid_mapping = "spatial_ref"` and `coordinates = "spatial_ref"` (so plain `xr.open_zarr` without `decode_coords="all"` promotes it to a scalar coord). If GDAL is a target reader, also set the array-level `_CRS` attr (see gotchas below).
4. Ensure every array declares its dimensions. **Zarr v3: zarr-python has no API to set `dimension_names` on an existing array** — edit each array's `zarr.json` document directly:

   ```python
   for name, dims in {"data_var": ["y", "x"], "x": ["x"], "y": ["y"]}.items():
       doc = store_path / name / "zarr.json"
       meta = json.loads(doc.read_text())
       meta["dimension_names"] = dims
       doc.write_text(json.dumps(meta))
   ```

   (Zarr v2: just set `_ARRAY_DIMENSIONS` in `.zattrs` via `arr.attrs`.)
5. On root, set `Conventions = "CF-1.8"`.
6. Re-run `zarr.consolidate_metadata(store_path)` **as the last step, after any direct `zarr.json` edits** — consolidated metadata shadows per-array documents on read, so stale consolidation silently undoes the patch. On Zarr v3 this emits `ZarrUserWarning: Consolidated metadata is currently not part in the Zarr format 3 specification` — expected, not an error.

Total bytes written are usually small compared with the data chunks; the coordinate arrays dominate. Dry-run/apply separation matters for published or shared stores; for a scratch copy, an assert-guarded single-pass patch script is fine.

A re-runnable additive patch is safe; the predicate to skip is "child arrays already exist with the right shape and attrs."

## Common gotchas

- **`rio.crs` is None on read.** Almost always one of: missing `grid_mapping` on the data var, missing `crs_wkt` on `spatial_ref`, or `dimension_names` not set so xarray can't find the spatial axes.
- **Coords half a pixel off.** Cell-center vs pixel-edge confusion. See above.
- **GDAL sees the array but no CRS.** The classic GDAL Zarr driver does **not** read CF `grid_mapping` — it reads a `_CRS` attribute on the data array itself: `"_CRS": {"wkt": "<WKT2>", "projjson": {...}}`. Add it alongside `grid_mapping` whenever GDAL must open the store (GDAL ≥ 3.13 can alternatively read root `spatial:`/`proj:` attrs). rioxarray reads CF `grid_mapping`/`crs_wkt`. Patch all readers you target; know which key serves which reader.
- **GDAL reports NoData you never set.** The Zarr array's codec-level `fill_value` (in `zarr.json`/`.zarray`) surfaces as GDAL's NoData. If 0.0 is a valid data value, author with a distinct fill (e.g. NaN for float) — this is baked in at creation and is not a metadata-only fix.
- **xarray promotes `spatial_ref` to a data var instead of a scalar coord.** Add `coordinates: "spatial_ref"` to the data var's attrs, OR set `decode_coords="all"` on open. Pick one — both is fine in CF but doubly-listing can confuse readers.
- **virtualizarr-built reference store has no `Conventions`.** virtualizarr emits geometry but not CF metadata. You must add it post-hoc.
- **Negative `dy` flipped to positive.** North-up data has `dy < 0`. If you sort coords ascending you reverse the array. Keep `y` descending for north-up.
- **Cloud/object-store paths differ by library.** S3, GCS, Azure, HTTPS, fsspec, obstore, and GDAL VSI paths use different URL forms. Verify the reader's expected path syntax instead of rewriting paths blindly.

## Validation

Which reader needs which keys — patch only the rows for your target readers:

| Target reader | Reads |
|---|---|
| rioxarray / xarray | `grid_mapping` + `crs_wkt` on `spatial_ref`, `dimension_names`/`_ARRAY_DIMENSIONS`, `coordinates` attr or `decode_coords="all"` |
| GDAL Zarr driver (classic, all versions) | array-level `_CRS` attr; geotransform inferred from regular 1D dim arrays (requires `dimension_names`) |
| GDAL ≥ 3.13 spatial layer | root `spatial:` / `proj:` attrs |

When the Python env is spun up per-invocation (uv/pipx/conda run), heavy geo imports dominate wall time — fold patch and verification into **one** script: patch, then in the same process `xr.open_zarr(...)`, assert `da.rio.crs` is not None, and print crs/transform/bounds; follow with `gdalinfo` (no Python needed) as the second, independent check. Pre-checks (e.g. the cell-center assertion) belong inside the same patch script as a guard, not a separate run.

```bash
# Round-trip CRS through rioxarray
python -c "import xarray as xr, rioxarray; print(xr.open_zarr('store.zarr').data_var.rio.crs)"

# GDAL view
gdalinfo 'ZARR:"store.zarr":/data_var'

# Inspect a remote or local Zarr root
python -c "
import zarr
g = zarr.open_group('store.zarr', mode='r')
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
| Read GeoZarr as raster | `rioxarray`, QGIS via GDAL, and GDAL versions that support the chosen Zarr/convention layer |
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
