<div class="skill-hero" markdown>
  <span class="skill-hero-icon">🌍</span>

# Geospatial Frontend
</div>

Build premium map-centric demo webapps with MapLibre globe, DuckDB-WASM, and a warm dark HUD aesthetic.

<div class="skill-callout">
  <p class="skill-callout-label">Stack</p>
  <p>Vite + vanilla TypeScript + MapLibre GL JS (globe) + DuckDB-WASM + pure CSS. No frameworks.</p>
</div>

## Install

=== "Universal"

    ```bash
    cp -R skills/geospatial-frontend ~/.agent/skills/geospatial-frontend
    ```

=== "Claude"

    ```bash
    /plugin marketplace add isaaccorley/geospatial-skills
    /plugin install geospatial-frontend@geospatial-skills
    ```

    CLI:

    ```bash
    claude plugin marketplace add isaaccorley/geospatial-skills
    claude plugin install geospatial-frontend@geospatial-skills
    ```

## Common tasks

1. Scaffold a satellite imagery retrieval demo with globe view and floating HUD panels.
1. Build an embedding visualization tool with heatmap, top-k, and similarity gradient views.
1. Create a geospatial search UI with draw-to-query (box/polygon) and exemplar-based retrieval.
1. Add an interactive spotlight tutorial that simulates real user actions.

## Design highlights

- **Warm espresso + ivory + rust** palette with glassmorphed floating panels
- **Globe projection** (not flat Web Mercator) with Sentinel-2 cloudless tiles
- **Typography triad**: Fraunces (display), Inter Tight (body), JetBrains Mono (data)
- **Plasma colormap** for heatmap visualization
- **Staggered list animations**, scroll fade masks, orbital brand mark

## Source

<div class="source-panel" markdown>

- Skill: [skills/geospatial-frontend/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-frontend/SKILL.md)
- Design system: [skills/geospatial-frontend/references/design-system.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-frontend/references/design-system.md)
- UI preferences: [skills/geospatial-frontend/references/user-preferences.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/geospatial-frontend/references/user-preferences.md)

</div>
