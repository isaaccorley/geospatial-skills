---
hide:
  - toc
  - navigation
---

<section class="hero-shell">
  <div class="hero-contour">
    <svg viewBox="0 0 260 200" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 180 Q60 140 100 150 T180 120 T250 90" stroke="#a8c5a0" stroke-width="1" fill="none" opacity="0.6"/>
      <path d="M10 160 Q70 110 130 130 T200 100 T260 60" stroke="#c4b57a" stroke-width="0.8" fill="none" opacity="0.5"/>
      <path d="M30 140 Q80 90 140 110 T210 80 T260 40" stroke="#a8c5a0" stroke-width="0.6" fill="none" opacity="0.4"/>
      <path d="M40 120 Q90 70 150 90 T220 60 T260 20" stroke="#d4a853" stroke-width="0.5" fill="none" opacity="0.3"/>
      <path d="M50 100 Q100 50 160 70 T230 40 T260 5" stroke="#a8c5a0" stroke-width="0.4" fill="none" opacity="0.25"/>
    </svg>
  </div>
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

=== "Universal"

    ```bash
    cp -R skills/<skill-name> ~/.agent/skills/<skill-name>
    ```

    If your setup uses a different shared skill folder, copy the matching
    `skills/<skill-name>` directory there instead.

=== "Claude"

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

<div class="catalog-grid"><a class="catalog-card" href="skills/gdal/" style="--i:0"><span class="catalog-card-icon">🗺️</span><span class="catalog-card-name">GDAL</span><span class="catalog-card-desc">Command line workflows for raster and vector geospatial processing.</span><span class="catalog-card-tag">raster + vector</span></a><a class="catalog-card" href="skills/geoparquet-validation/" style="--i:1"><span class="catalog-card-icon">📐</span><span class="catalog-card-name">GeoParquet Validation</span><span class="catalog-card-desc">Inspect, validate, optimize, and distribute GeoParquet data with gpio.</span><span class="catalog-card-tag">cloud-native</span></a><a class="catalog-card" href="skills/tessera/" style="--i:2"><span class="catalog-card-icon">🛰️</span><span class="catalog-card-name">Tessera</span><span class="catalog-card-desc">Download TESSERA satellite embeddings via CLI, Python, or R.</span><span class="catalog-card-tag">embeddings</span></a><a class="catalog-card" href="skills/geospatial-viewers/" style="--i:3"><span class="catalog-card-icon">👁️</span><span class="catalog-card-name">Geospatial Viewers</span><span class="catalog-card-desc">Interactive raster, vector, and terminal-inline geospatial viewers.</span><span class="catalog-card-tag">visualization</span></a><a class="catalog-card" href="skills/geospatial-frontend/" style="--i:4"><span class="catalog-card-icon">🌍</span><span class="catalog-card-name">Geospatial Frontend</span><span class="catalog-card-desc">Map-centric demo webapps with MapLibre globe, DuckDB-WASM, and warm dark HUD.</span><span class="catalog-card-tag">frontend</span></a></div>
