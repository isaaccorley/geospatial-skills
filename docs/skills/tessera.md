<div class="skill-hero" markdown>
  <span class="skill-hero-icon">🛰️</span>

# Tessera
</div>

Work with TESSERA satellite embeddings via the CLI, Python library, or R library.

<div class="skill-callout">
  <p class="skill-callout-label">Tool</p>
  <p><code>geotessera</code> — CLI, Python library, and R library for coverage checks, point sampling, mosaic building, downloads, and visualization.</p>
</div>

## Install

=== "Universal"

    ```bash
    cp -R skills/tessera ~/.agent/skills/tessera
    ```

=== "Claude"

    ```bash
    /plugin marketplace add isaaccorley/geospatial-skills
    /plugin install tessera@geospatial-skills
    ```

    CLI:

    ```bash
    claude plugin marketplace add isaaccorley/geospatial-skills
    claude plugin install tessera@geospatial-skills
    ```

## Quick start

### Python library (preferred for most tasks)

```python
from geotessera import GeoTessera

gt = GeoTessera()

# Point sampling — preferred over mosaics for sparse locations
points = [(0.15, 52.05), (0.25, 52.15)]
embeddings = gt.sample_embeddings_at_points(points, year=2024)

# Mosaic — only for dense per-pixel analysis
bbox = (-0.2, 51.4, 0.1, 51.6)
mosaic, transform, crs = gt.fetch_mosaic_for_region(bbox, year=2024)
```

### R library

```r
remotes::install_github("lassa-sentinel/GeoTessera")
library(GeoTessera)

gt <- geotessera()
tiles <- gt$get_tiles(bbox = c(-0.2, 51.4, 0.1, 51.6), year = 2024)
gt$export_embedding_geotiffs(tiles = tiles, output_dir = "london_tiles")
```

### CLI

```bash
geotessera coverage --year 2024 --output coverage_2024.png
geotessera download --bbox "-0.2,51.4,0.1,51.6" --year 2024 --output ./out
geotessera download --region-file region.geojson --format npy --year 2024 --output ./arrays
geotessera visualize ./out --type web --output ./web
geotessera serve ./web --open
```

uv and uvx works, so you can `uvx geotessera` for zero-installation invocation.

## Source

<div class="source-panel" markdown>

- Skill: [skills/tessera/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/tessera/SKILL.md)
- CLI reference: [skills/tessera/references/geotessera-cli.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/tessera/references/geotessera-cli.md)
- Library reference: [skills/tessera/references/geotessera-library.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/tessera/references/geotessera-library.md)
- R library docs: [lassa-sentinel.github.io/GeoTessera](https://lassa-sentinel.github.io/GeoTessera)
- Upstream: [ucam-eo/geotessera](https://github.com/ucam-eo/geotessera)

</div>
