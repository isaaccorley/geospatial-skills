---
template: skill.html
title: Geospatial Frontend
slug: geospatial-frontend
tag: FRONTEND
install_skill: geospatial-frontend
license: Apache-2.0
requires: Node + a modern browser with WASM
summary: >-
  Build premium map-centric demo webapps with MapLibre globe, DuckDB-WASM, and
  a warm dark HUD aesthetic. Stack is Vite + vanilla TypeScript + pure CSS
  &mdash; deliberately no React, Vue, or Tailwind &mdash; with a single global
  state object, fingerprint-diffed re-renders, and glassmorphed floating
  panels over a fullscreen globe.
features:
  - 'MapLibre GL JS globe (<code>projection: "globe"</code>) with layered AOI / draft / result GeoJSON sources'
  - 'Drawing tools: rectangle (shift+drag) and click-to-add polygons'
  - DuckDB-WASM data pipeline with a Web Worker for compute-heavy scoring
  - Glassmorphed floating HUD panels over a fullscreen map; CSS-token-driven dark theme
  - Vanilla TypeScript &mdash; explicitly no React, Vue, or Tailwind
  - Interactive spotlight tutorial system that simulates real user actions
example_html: |
  <span class="com"># scaffold the Vite + vanilla-TS app the skill describes</span>
  <span class="dim">$</span> npm create vite@latest <span class="arg">my-geo-app</span> -- --template <span class="arg">vanilla-ts</span>
  <span class="dim">$</span> cd <span class="arg">my-geo-app</span>
  <span class="dim">$</span> npm i <span class="arg">maplibre-gl</span> <span class="arg">@duckdb/duckdb-wasm</span>
  <span class="dim">$</span> npm run dev
prev:
  slug: geospatial-viewers
  name: Geospatial Viewers
next:
  slug: parallel-geospatial
  name: Parallel Geospatial
---
