<section class="hero-shell">
  <p class="eyebrow">Geospatial Skills</p>
  <h1>Installable geospatial skills for coding agents.</h1>
  <p class="hero-lead">
    Minimal docs. Shared source. Claude packaging when needed.
  </p>
  <div class="hero-actions">
    <a class="hero-button" href="#catalog">Browse Skills</a>
    <a class="hero-link" href="#install">Install</a>
  </div>
</section>

## Install

### Universal

```bash
cp -R skills/<skill-name> ~/.agent/skills/<skill-name>
```

If your setup uses a different shared skill folder, copy the matching
`skills/<skill-name>` directory there instead.

### Claude

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install <skill-name>@geospatial-skills
```

CLI:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install <skill-name>@geospatial-skills
```

## Catalog { #catalog }

- [`geoparquet-validation`](skills/geoparquet-validation.md): `gpio`-focused GeoParquet validation, optimization, and distribution workflows. Referenced from `geoparquet-io/geoparquet-skill`.
- [`gdal`](skills/gdal.md): GDAL command line workflows for raster and vector data. Referenced from Microsoft AI for Earth geospatial recipes.
- [`geospatial-viewers`](skills/geospatial-viewers.md): Interactive raster, vector, and terminal geospatial viewers. Referenced from `nkeikon/viewtif`, `nkeikon/viewgeom`, and `nkeikon/viewinline`.
- [`tessera`](skills/tessera.md): Download Tessera embeddings with the `geotessera` CLI. Referenced from `ucam-eo/geotessera`.
