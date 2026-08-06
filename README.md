# geospatial-skills

A collection of separately installable geospatial `SKILL.md` packages for AI coding agents.

Site: <https://isaac.earth/geospatial-skills/>

## Install

The recommended path is [`skills.sh`](https://skills.sh) — a single-line install that works across most agents:

```bash
# install everything
npx skills add isaaccorley/geospatial-skills

# or install one skill at a time
npx skills add isaaccorley/geospatial-skills/<skill>   # e.g. gdal, geozarr, pmtiles-pipeline
```

Other paths:

```bash
# Claude Code plugin
/plugin install <skill>@geospatial-skills

# Or copy a skill directly into your shared skills folder
cp -R skills/<skill> ~/.agent/skills/<skill>
```

## Skills

| Skill                   | What it does                                                                |
| ----------------------- | --------------------------------------------------------------------------- |
| `gdal`                  | GDAL command-line workflows for raster and vector data                      |
| `geoparquet-validation` | `gpio`-focused GeoParquet inspection, validation, and distribution          |
| `geozarr`               | GeoZarr metadata conventions for georeferenced Zarr stores                  |
| `tessera`               | TESSERA embedding downloads via the `geotessera` CLI / Python / R libraries |
| `geospatial-viewers`    | `viewtif` / `viewgeom` / `viewinline` quick-look CLIs (run via `uvx`)       |
| `geospatial-frontend`   | Map-centric demo webapps with MapLibre globe + DuckDB-WASM                  |
| `parallel-geospatial`   | Parallelize continental-scale vector/raster ops on one fat node             |
| `pmtiles-pipeline`      | Raster predictions to a global PMTiles archive via sharded tippecanoe       |
| `zarr-multiscales`      | Build multiscale pyramids into existing Zarr stores without losing shards   |
| `planet-bulk-download`  | Bulk PlanetScope downloads via COG range reads, retries, and resume         |
| `portolan-cli`          | Publish and manage cloud-native STAC catalogs with the Portolan CLI         |
| `portolan-bootstrap`    | Bootstrap a full Portolan catalog from WFS, ArcGIS, or local files          |
| `reading-portolan`      | Explore, query, and visualize Portolan STAC catalogs end to end             |
| `portolan-thumbnails`   | Server-side collection thumbnails with chiitiler + MapLibre GL Native       |
| `register-catalog`      | List a published catalog in the Portolan registry via pull request          |
| `sourcecoop`            | Publish geospatial data to Source Cooperative with Portolan                 |
| `search-stac`           | Search and download Planetary Computer imagery via STAC                     |
| `overture-data`         | Download Overture Maps buildings, places, roads, and more                   |
| `detect-objects`        | Run pre-trained detection models on satellite and aerial imagery            |

## Provenance and licenses

Skills come from three sources; imported skills carry their upstream license file in
their own directory and keep upstream content verbatim:

- authored here (Apache-2.0): `gdal`, `geoparquet-validation`, `geozarr`, `tessera`,
    `geospatial-viewers`, `geospatial-frontend`, `parallel-geospatial`,
    `pmtiles-pipeline`, `zarr-multiscales`, `planet-bulk-download`
- imported from [portolan-sdi/portolan-skills](https://github.com/portolan-sdi/portolan-skills)
    (Apache-2.0, Portolan SDI): `portolan-cli`, `portolan-bootstrap`, `reading-portolan`,
    `portolan-thumbnails`, `register-catalog`, `sourcecoop`
- imported from [opengeos/geoai-skills](https://github.com/opengeos/geoai-skills)
    (MIT, Qiusheng Wu): `search-stac`, `overture-data`, `detect-objects` —
    cross-references were repointed from the upstream plugin namespace to this
    catalog's skills, and error paths now give inline `pip install` instructions

## Layout

```text
skills/
  <skill>/                 SKILL.md  [references/]  [scripts/]  [LICENSE]
plugins/
  <skill>/                 .claude-plugin/plugin.json  skills/<skill>/  (mirror)
docs/
  skills/<skill>.md        one docs page per skill
overrides/
  home.html  skill.html
```

## Docs

```bash
uv sync --group dev
uv run mkdocs serve   # local preview
uv run mkdocs build   # build to ./site
```

Contributor workflow, CI, and docs deploy notes live in `.github/CONTRIBUTING.md`.
