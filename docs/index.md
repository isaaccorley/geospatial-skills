<section class="hero-shell">
  <p class="eyebrow">Geospatial Skills</p>
  <h1>Installable geospatial skills for coding agents.</h1>
  <p class="hero-lead">
    Minimal docs. Shared source. Claude packaging when needed.
  </p>
  <div class="hero-actions">
    <a class="hero-button" href="skills/geoparquet/">Open GeoParquet</a>
    <a class="hero-link" href="#install">Install</a>
  </div>
</section>

## Install

### Universal

```bash
git clone https://github.com/isaaccorley/geospatial-skills.git
cp -R geospatial-skills/skills/<skill-name> ~/.claude/skills/<skill-name>
```

If your tool uses a different local skill folder, copy the matching
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

## Catalog

- [`geoparquet`](skills/geoparquet.md): GeoParquet workflows with `gpio` and DuckDB
- [`gdal`](skills/gdal.md): GDAL command line workflows for raster and vector data
