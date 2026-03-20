# Geospatial Viewers

Preview and inspect geospatial files from the command line using `viewtif`, `viewgeom`, and `viewinline`.

<div class="skill-callout">
  <p class="skill-callout-label">Tools</p>
  <p><code>viewtif</code> (interactive raster), <code>viewgeom</code> (interactive vector), <code>viewinline</code> (terminal-inline).</p>
</div>

## Install

### Universal

```bash
cp -R skills/geospatial-viewers ~/.agent/skills/geospatial-viewers
```

### Claude

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install geospatial-viewers@geospatial-skills
```

CLI:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install geospatial-viewers@geospatial-skills
```

## Common tasks

1. Quick-look inspect a raster (GeoTIFF, HDF, NetCDF) with interactive zoom and pan.
1. Preview vector datasets with attribute-based coloring and filtering.
1. Render rasters, vectors, or CSV inline in the terminal (no GUI).
1. Analyze CSV files with summary statistics, histograms, scatter plots, and SQL.

## Essential commands

```bash
uvx viewtif image.tif
uvx viewtif sentinel2.tif --rgb 4 3 2
uvx viewgeom boundaries.geojson --column area_sqkm
uvx viewgeom earthquake.geojson --duckdb "SELECT * FROM data WHERE mag > 5"
uvx viewinline file.tif --colormap
uvx viewinline boundaries.geojson --color-by population
uvx viewinline data.csv --describe
uvx viewinline data.csv --scatter longitude latitude
```

## Source

- Skill: [skills/geospatial-viewers/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-viewers/SKILL.md)
- viewtif reference: [skills/geospatial-viewers/references/viewtif.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-viewers/references/viewtif.md)
- viewgeom reference: [skills/geospatial-viewers/references/viewgeom.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-viewers/references/viewgeom.md)
- viewinline reference: [skills/geospatial-viewers/references/viewinline.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-viewers/references/viewinline.md)
- Upstream: [nkeikon/tifviewer](https://github.com/nkeikon/tifviewer), [nkeikon/geomviewer](https://github.com/nkeikon/geomviewer), [nkeikon/inlineviewer](https://github.com/nkeikon/inlineviewer)
