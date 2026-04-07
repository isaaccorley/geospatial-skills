---
name: geospatial-frontend
description: Build visually stunning geospatial demo webapps with MapLibre globe, DuckDB-WASM, and a warm dark HUD aesthetic. Use when building satellite imagery retrieval demos, embedding visualization tools, geospatial search UIs, or any map-centric data exploration frontend. Triggers on requests to scaffold a new geo demo, build a map-based UI, or create a retrieval/search visualization over satellite data.
---

# Geospatial Frontend Demo Builder

Build premium map-centric demo webapps. Derived from a production geospatial retrieval demo with battle-tested design patterns.

## Architecture

- **Stack**: Vite + vanilla TypeScript + MapLibre GL JS (globe) + DuckDB-WASM + pure CSS
- **No frameworks**: No React, Vue, Tailwind, CSS-in-JS. Pure semantic HTML + CSS custom properties + vanilla TS.
- **Map-first**: The globe IS the app. Everything else floats on top as a transparent HUD.
- **Single source of truth**: Global `state` object; `updateView()` re-renders; fingerprint diffing prevents redundant DOM rebuilds.

## Design System

See [references/design-system.md](references/design-system.md) for full token spec (colors, fonts, shadows, spacing, radii, animations, components).

**Core identity**: Warm espresso + ivory + rust. Dark mode only. Glassmorphed floating panels. Inspired by Anthropic Salon aesthetic.

## UI Rules

See [references/user-preferences.md](references/user-preferences.md) for battle-tested patterns, confirmed features, and design rules.

## Layout

```
viewport (100vw x 100vh, fixed)
  ::before  starfield
  ::after   vignette
  #map      MapLibre globe canvas
  brand     top-left (spinning rings + logotype)
  search    top-center (glassmorphed geocoder)
  status    top-center-below (pulsing LED + message)
  panel-L   left (query: draw controls, exemplars, results)
  panel-R   right (explore/discoveries, optional)
  tutorial  overlay + spotlight + card (z:1000+)
```

Panels are `position: fixed`, glassmorphed, with generous padding. Map fills entire viewport underneath.

## Map Integration

- **MapLibre GL JS** with `projection: "globe"` (3D globe, not flat)
- **Sentinel-2 cloudless tiles** (or similar satellite basemap)
- **Layer stack**: AOI fill/stroke -> draft layers -> result fill/stroke -> point circles with halos -> hover preview
- **Drawing**: rectangle (shift+drag with DOM overlay) + polygon (click-to-add, double-click-to-close)
- **Fly-to animations**: `globe.flyTo()` with curve 1.4, speed 1.2
- **GeoJSON sources**: all data as GeoJSON, expression-based paint properties for dynamic styling

## Data Pipeline Pattern

- DuckDB-WASM loads Parquet manifest + shards
- Spatial filtering via `ST_Intersects` or bbox containment
- Web Worker for heavy compute (embedding distances, scoring)
- Concurrency-limited parallel shard fetches
- Two-phase data loading: metadata first, embeddings on demand

## Tutorial System

Interactive 5-7 step spotlight walkthrough that SIMULATES real actions:
- Box-shadow spotlight (`0 0 0 9999px rgba(...)`) cuts a hole over target element
- Card auto-positioned via `getBoundingClientRect()`, glass-panel styled
- Simulated clicks with animated ripple effect
- Enter key advances; auto-place exemplars if user skips ahead
- Store completion in localStorage
- Must be a LIVE demo -- simulate zoom, draw, exemplar placement, view modes

## Responsive

Two breakpoints only:
- **1100px**: shrink panels, hide secondary nav
- **900px**: panels collapse to bottom-center stack, max-height 40-45vh

## File Organization

Keep files under ~500 LOC. Split by concern:
- `main.ts` -- app state, DOM, event handlers, tutorial
- `map.ts` -- MapLibre setup, layers, drawing, camera
- `types.ts` -- interfaces
- `util.ts` -- geometry, color interpolation, formatting
- `scoring-worker.ts` -- Web Worker for compute
- `styles.css` -- all CSS (pure, no preprocessor)
- `index.html` -- entry with font preloads + meta tags
