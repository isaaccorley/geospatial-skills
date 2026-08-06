---
template: skill.html
title: Detect Objects
slug: detect-objects
tag: ML
install_skill: detect-objects
upstream:
  - label: opengeos/geoai
    href: https://github.com/opengeos/geoai
  - label: GeoAI docs
    href: https://opengeoai.org
license: "MIT (upstream: opengeos/geoai-skills)"
requires: "<code>geoai-py</code>, PyTorch + torchvision (CUDA GPU recommended); models pulled from Hugging Face on first use"
summary: >-
  Runs geoai's pre-trained detectors over a GeoTIFF and writes detections out
  as a GeoPackage. Maps a short model argument &mdash; buildings, cars, ships,
  solar panels, parking lots, agriculture &mdash; to the matching geoai class,
  or routes free-text prompts through GroundedSAM for open-vocabulary
  segmentation.
features:
  - "Six pre-trained detectors mapped to geoai classes, e.g. <code>geoai.BuildingFootprintExtractor</code>"
  - "Text-prompted segmentation via <code>geoai.GroundedSAM</code>"
  - "GPU/CUDA preflight with device name and VRAM, plus a CPU-mode warning"
  - "Vector output to GeoPackage via each detector's <code>predict(..., output_path=...)</code>"
  - "Error playbook for CUDA OOM (reduce tile size), failed model downloads, and non-raster input"
example_html: |
  <span class="com"># building footprints from aerial imagery</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; gdf = geoai.BuildingFootprintExtractor().predict('naip.tif', output_path='buildings.gpkg'); print(len(gdf))"</span>

  <span class="com"># text-prompted segmentation</span>
  <span class="dim">$</span> python3 -c <span class="arg">"import geoai; geoai.GroundedSAM().predict('scene.tif', text_prompt='swimming pools', output_path='pools.gpkg')"</span>
prev:
  slug: overture-data
  name: Overture Data
---
