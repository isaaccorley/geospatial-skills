---
template: skill.html
title: Register Catalog
slug: register-catalog
tag: REGISTRY
install_skill: register-catalog
upstream:
  - label: portolan-sdi/portolan-registry
    href: https://github.com/portolan-sdi/portolan-registry
  - label: portolan-sdi.org
    href: https://www.portolan-sdi.org
license: "Apache-2.0 (upstream: portolan-sdi/portolan-skills)"
requires: "<code>gh</code> CLI (authenticated), git, <code>curl</code>, Python 3"
summary: >-
  A short procedural skill for listing a published catalog in the Portolan
  registry. The registry entry is a single YAML file containing only a
  <code>url:</code> field &mdash; CI crawls the catalog and extracts
  everything else. The skill validates the catalog.json URL, derives the slug,
  then forks the registry, commits the entry, and opens the pull request.
features:
  - "One-field entry format &mdash; <code>url:</code> only; the schema forbids inventing any other metadata"
  - "URL validation via curl + Python assert that the target is a STAC-typed Catalog root"
  - "Slug derivation from the directory containing <code>catalog.json</code>"
  - "Full <code>gh repo fork</code> / branch / commit / <code>gh pr create</code> sequence"
  - "Post-merge behavior explained: CI crawls, validates, and exports metadata"
example_html: |
  <span class="com"># confirm the URL is a reachable catalog root</span>
  <span class="dim">$</span> curl -fsSL <span class="arg">"$CATALOG_URL"</span> | python3 -c <span class="arg">"import sys, json; assert json.load(sys.stdin).get('type') == 'Catalog'"</span>

  <span class="com"># derive the registry slug and open the registration PR</span>
  <span class="dim">$</span> SLUG=$(basename <span class="arg">"$(dirname "$CATALOG_URL")"</span>)
  <span class="dim">$</span> gh pr create --repo portolan-sdi/portolan-registry --title <span class="arg">"Add $SLUG catalog"</span>
prev:
  slug: portolan-thumbnails
  name: Portolan Thumbnails
next:
  slug: sourcecoop
  name: Source Cooperative
---
