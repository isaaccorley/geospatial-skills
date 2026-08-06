---
template: skill.html
title: Source Cooperative
slug: sourcecoop
tag: PUBLISH
install_skill: sourcecoop
upstream:
  - label: Source Cooperative
    href: https://source.coop
  - label: portolan-sdi/portolan-skills
    href: https://github.com/portolan-sdi/portolan-skills
license: "Apache-2.0 (upstream: portolan-sdi/portolan-skills)"
requires: "<code>portolan-cli</code>; Source Cooperative automated-access credentials (AWS profile)"
summary: >-
  End-to-end recipe for publishing to Source Cooperative, the open geospatial
  data commons, via the Portolan CLI. Covers automated-access credentials,
  configuring the remote through a .env file so credentials never land in
  catalog config, required metadata fields, README generation, and parallel-
  worker pushes &mdash; plus an appendix on Portolan's multi-style MapLibre
  system.
features:
  - "Credential model: an AWS profile plus <code>PORTOLAN_REMOTE</code>/<code>PORTOLAN_PROFILE</code> in .env, never in catalog config"
  - "Remote URL convention for Source Cooperative product buckets"
  - "Required metadata gate &mdash; title, description, SPDX license, contact &mdash; via <code>portolan metadata validate --recursive</code>"
  - "Recursive README generation and a CI staleness check (<code>portolan readme --check</code>)"
  - "Parallel uploads sized to cores (<code>portolan push --workers 8</code>) with dry-run preview"
  - "Style authoring best practices: data-driven MapLibre expressions registered as <code>portolan:styles</code> STAC assets"
example_html: |
  <span class="com"># initialize the catalog in the data directory</span>
  <span class="dim">$</span> portolan init --title <span class="arg">"City Aerial Imagery"</span> --auto

  <span class="com"># scaffold and validate required metadata</span>
  <span class="dim">$</span> portolan metadata init --recursive &amp;&amp; portolan metadata validate --recursive

  <span class="com"># parallel upload to Source Cooperative</span>
  <span class="dim">$</span> portolan push --workers 8 --verbose
prev:
  slug: register-catalog
  name: Register Catalog
next:
  slug: search-stac
  name: Search STAC
---
