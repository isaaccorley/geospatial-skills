---
template: skill.html
title: Planet Bulk Download
slug: planet-bulk-download
tag: IMAGERY
install_skill: planet-bulk-download
upstream:
  - label: planetlabs/planet-client-python
    href: https://github.com/planetlabs/planet-client-python
  - label: Planet Data API
    href: https://docs.planet.com/develop/apis/data/
license: "Apache-2.0"
requires: "<code>planet</code> SDK v2, <code>rasterio</code> / GDAL, <code>httpx</code>; a Planet account with Data API access"
summary: >-
  Pull PlanetScope imagery at scale &mdash; hundreds to 100k+ AOIs &mdash;
  with the Planet SDK v2, which ships no retries, no batching, and no cold-
  storage awareness. A three-phase search &rarr; activate &rarr; extract
  architecture with resumable JSONL caches, measured concurrency budgets, and
  the Planet-side reliability gotchas you otherwise learn from a burned
  17-hour job.
features:
  - "COG range reads via <code>/vsicurl/</code> beat the Orders API by ~100&times; for windowed access"
  - "Scene grouping before activation cuts activation calls 10&ndash;20&times;"
  - "A GDAL config dict for signed URLs, including the <code>CPL_VSIL_CURL_ALLOWED_EXTENSIONS</code> trap"
  - "Retry wrapper covering 429s, string-matched 5xx <code>APIError</code>s, and httpx transients"
  - "Measured per-phase concurrency budgets and the undocumented ~10 cold scenes/min/account thaw cap"
  - "Re-activation pass for the ~24% of activations that return broken URLs; budget 3&ndash;5% permanently dead assets"
example_html: |
  <span class="com"># windowed read from an activated scene &mdash; no full-strip download</span>
  <span class="dim">$</span> python -c <span class="arg">"import rasterio; src = rasterio.open('/vsicurl/' + url); print(src.profile)"</span>

  <span class="com"># signed URLs end in ?token=..., so never allowlist extensions</span>
  <span class="dim">$</span> unset CPL_VSIL_CURL_ALLOWED_EXTENSIONS
prev:
  slug: zarr-multiscales
  name: Zarr Multiscales
next:
  slug: portolan-cli
  name: Portolan CLI
---
