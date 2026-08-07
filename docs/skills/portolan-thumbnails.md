---
template: skill.html
title: Portolan Thumbnails
slug: portolan-thumbnails
tag: RENDER
install_skill: portolan-thumbnails
upstream:
  - label: Kanahiro/chiitiler
    href: https://github.com/Kanahiro/chiitiler
  - label: portolan-sdi/portolan-skills
    href: https://github.com/portolan-sdi/portolan-skills
license: 'Apache-2.0 (upstream: portolan-sdi/portolan-skills)'
requires: Node.js 18+, npm, git, Python 3, <code>curl</code>; a collection with .pmtiles and <code>styles/default.json</code>
summary: >-
  Server-side rendering recipe for hero-quality collection thumbnails. Clones
  chiitiler (MapLibre GL Native tile server), rewrites each collection's
  shipped <code>styles/default.json</code> to point at local PMTiles,
  optionally layers a raster basemap underneath, and renders a PNG/JPEG/WebP
  per collection &mdash; preserving the portal's actual cartography instead of
  default matplotlib previews.
features:
  - Batch script iterates collection dirs, extracts each bbox from <code>collection.json</code>, renders every collection
  - Preserves the portal's real cartography &mdash; the original MapLibre style layers are used unchanged
  - Optional basemaps (Carto, OSM, Stadia) or plain background with <code>USE_BASEMAP=false</code>
  - <code>CHIITILER_PROCESSES=0</code> multi-process mode to survive large batches; in-memory tile cache
  - Configurable output format, size, and quality with an output sanity check
  - Post-render <code>portolan push</code> syncs thumbnails with auto-updated checksums
example_html: |
  <span class="com"># install and start the render server</span>
  <span class="dim">$</span> git clone --depth 1 <span class="arg">https://github.com/Kanahiro/chiitiler</span> &amp;&amp; cd chiitiler &amp;&amp; npm install
  <span class="dim">$</span> CHIITILER_PROCESSES=0 npx tsx src/main.ts tile-server --port 13579 --cache memory

  <span class="com"># render one collection thumbnail from its style</span>
  <span class="dim">$</span> curl -s -X POST <span class="arg">"http://localhost:13579/clip.png?bbox=${BBOX}&amp;size=1024"</span> -d @style.json -o thumb.png
prev:
  slug: reading-portolan
  name: Reading Portolan
next:
  slug: register-catalog
  name: Register Catalog
---
