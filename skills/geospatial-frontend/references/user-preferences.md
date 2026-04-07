# UI Preferences & Design Rules

Battle-tested patterns from building a production geospatial retrieval demo.

## Layout & Sizing

- **Panels must be compact.** Default to smaller controls. Common correction: "make the side panel smaller", "draw button is way too large".
- **Map is king.** Globe should be large on load. Panels never crowd it.
- **Exemplar panel shorter, retrieval panel taller.** Results > inputs in visual hierarchy.
- **Brand subtitle letterspacing must match title width.**

## Remove Clutter

Aggressively strip unnecessary text. All explicitly removed in testing:
- "Region of Interest" label, "Draw an AOI to fetch candidate tiles", "Ranked candidates" heading, "Awaiting Region" placeholder
- Chip IDs (just show coords), section numbering (01/02/03), "Clear points" text when icon suffices
- Stats panels (shards/roi/patches count), "Cutoff" label (just show "1/300"), "data-driven" badges

**Rule**: If the UI element doesn't directly help the user DO something, remove it.

## Button & Control Design

- Draw mode: literal "Draw Box" and "Draw Poly" buttons. No separate trigger.
- Button stays "Draw Region" after drawing -- NOT "Redraw Region".
- "Export GeoParquet" -> just "Export". Same row as other actions.
- Slider fill syncs with thumb position (CSS `--v` var).
- Buttons styled with accent gradient (orange/rust), not outline.

## Click Behavior

- **Click list item = zoom to it.** NOT remove it.
- **X button = remove.** Always explicit delete affordance.
- Exemplar points appear INSTANTLY on click (draw dot immediately, load embedding async).
- Clicking before drawing a region is allowed -- queue points.
- Negative exemplars work ANYWHERE on map, not just inside region.
- Deduplicate: same patch clicked twice must NOT add duplicate.
- Drawing a region must NOT zoom out to fit. Keep current viewport.
- Result click should zoom in slightly MORE than default fly-to.

## Hover & Tooltips

- Tooltip delay: FAST (cut default in half).
- Every icon button needs tooltip: name + 1-line description.
- Help popovers (?) must not clip at viewport edges.
- Popover z-index above everything (9999+).

## Scrollability

- Scrollable lists MUST have bottom fade-out mask.
- Both exemplar and result lists need this treatment.

## Tutorial

- Must simulate real actions, not just point at panels.
- Simulate: zoom in -> draw region -> click exemplar (inside AND outside region) -> show top-k vs heatmap.
- Auto-place exemplars if user skips ahead. Enter key advances.
- ~1.1s per view mode cycle during demo.
- Card styling matches glass-panel theme.
- Show on first load (localStorage gate).
- Demonstrate multi-region and external exemplars.

## Confirmed Good Features

- Heatmap view ("the nicest feature")
- External exemplars (click OUTSIDE region)
- Multi-AOI support
- Polygon draw with DuckDB ST_Intersects
- Outlier detection ("most unique" patches)
- Threshold histogram with slider
- Embedding arithmetic (mean/AND/OR/XOR)
- Invert toggle (bit flip for "opposite" search)
- Similarity gradient field
- Pre-computed scores cached for instant view switching

## Features Removed After Testing

- Contour view mode, find similar regions / region fingerprint, basemap attribution

## Data & Performance

- Two-phase fetch: metadata first, full embedding on demand.
- Default top-k: 50, max slider: 100
- Numbers > 1000: compact format (1.8k)
- Shard loading must NOT block exemplar placement
- Stale loading messages must always clear

## Branding

- Attribution: "Created by [Name]" (hyperlinked, underlined)
- Brand panel: translucent backdrop, not opaque. Needs margin to avoid overlapping query panel.

## Build & Deploy

- Static build can break MapLibre overlays that work in dev. Need MapLibre dev bundle + z-index fix on map canvas for production.
- Always test static build, not just dev server.
