<div class="skill-hero" markdown>
  <span class="skill-hero-icon">🧊</span>

# GeoZarr

</div>

Author, patch, and validate georeferenced Zarr stores for xarray, rioxarray, GDAL, and QGIS.

<div class="skill-callout">
  <p class="skill-callout-label">Tools</p>
  <p><code>xarray</code>, <code>rioxarray</code>, <code>zarr</code>, and <code>gdalinfo</code>.</p>
</div>

## Install

=== "Universal"

    ```bash
    cp -R skills/geozarr ~/.agent/skills/geozarr
    ```

=== "Claude"

    ```bash
    /plugin marketplace add isaaccorley/geospatial-skills
    /plugin install geozarr@geospatial-skills
    ```

    CLI:

    ```bash
    claude plugin marketplace add isaaccorley/geospatial-skills
    claude plugin install geozarr@geospatial-skills
    ```

## Common tasks

1. Author a Zarr store that round-trips as a georeferenced raster.
1. Audit stores that open without CRS or transform metadata.
1. Patch CF grid mapping metadata without rewriting data chunks.
1. Choose between Zarr v2 and v3 dimension declarations.
1. Add optional `proj:`, `spatial:`, or multiscale metadata for target readers.

## Essential checks

```bash
# Tool versions
python -c "import zarr, xarray; print('zarr', zarr.__version__, 'xarray', xarray.__version__)"
gdalinfo --version

# Round-trip CRS through rioxarray
python -c "import xarray as xr, rioxarray; print(xr.open_zarr('store.zarr').data_var.rio.crs)"

# GDAL view
gdalinfo 'ZARR:"store.zarr":/data_var'
```

## Minimum metadata

- root `Conventions`
- scalar `spatial_ref` or `crs` grid mapping variable
- `grid_mapping` attribute on each georeferenced data array
- spatial coordinate arrays for rectilinear grids
- dimension declarations on every array
- consolidated metadata when supported by the target Zarr format and library

## Source

<div class="source-panel" markdown>

- Skill: [skills/geozarr/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geozarr/SKILL.md)
- GeoZarr draft: [zarr-developers/geozarr-spec](https://github.com/zarr-developers/geozarr-spec)
- Rendered draft: [zarr.dev/geozarr-spec](https://zarr.dev/geozarr-spec/documents/standard/template/geozarr-spec.html)
- GDAL Zarr driver: [gdal.org Zarr driver docs](https://gdal.org/en/latest/drivers/raster/zarr.html)

</div>
