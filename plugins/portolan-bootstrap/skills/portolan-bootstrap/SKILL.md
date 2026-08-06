---
name: portolan-bootstrap
description: End-to-end catalog creation from a data source - extract, enrich metadata, generate assets, push to remote
---


# Portolan Bootstrap Skill

Bootstrap a complete geospatial data catalog from any source portolan supports.

## Critical Principles

1. **NEVER hallucinate metadata.** Only use information that exists in the source.
2. **When uncertain, checkpoint and ask.** Prefer asking too much over assuming.
3. **Always dry-run first.** Warn about large outputs, slow operations, anything concerning.
4. **Failures: warn inline, summarize at end.** Don't stop for every failure, but don't hide them.

---

## Phase 1: Discovery

### Detect source type

Portolan supports two workflows:

**Remote services** (use `portolan extract`):
- **WFS**: `/wfs`, `/geoserver/`, `service=WFS`
- **ArcGIS FeatureServer**: `/FeatureServer`, `/MapServer`
- **ArcGIS ImageServer**: `/ImageServer`

**Local files** (use `portolan init` → `scan` → `check` → `add`):
- Directory with Shapefiles, GeoJSON, GeoPackage, GeoTIFF, etc.

### For remote services: Dry-run extraction

```bash
portolan extract <type> "<URL>" --dry-run
```

### For local files: Initialize and scan

```bash
portolan init --auto
portolan scan
```

### ⏸️ CHECKPOINT: Discovery Results

Present to user:
- Layer/file count
- Estimated total features (if available)
- Any warnings (large counts, mixed formats, non-cloud-native files)

Ask: "Found X layers/files. This may take Y minutes and produce ~Z MB. Proceed?"

**Warn if:**
- Layer count > 50 (will take time)
- Any layer has > 100k features (memory concerns)
- Mixed geometry types detected
- Missing CRS information
- Non-cloud-native files that need conversion (GPKG, Shapefile, etc.)
- Files at root level (must be in subdirectories for collections)

---

## Phase 2: Extraction / Conversion

### For remote services: Run extraction

```bash
portolan extract <type> "<URL>" --output <path>
```

Monitor progress. **Warn inline** on any failures but continue.

### For local files: Check and convert

```bash
# Preview what needs conversion
portolan check --dry-run

# Convert non-cloud-native files (GPKG → GeoParquet, etc.)
portolan check --fix
```

**IMPORTANT**: Files must be in subdirectories. Each subdirectory becomes a STAC collection.
If files are at root level, move them into appropriately named subdirectories first.

### ⏸️ CHECKPOINT: Extraction/Conversion Complete

Present:
- Success count vs total
- List any failures with reasons
- Total data size
- Files converted (for local workflow)

Ask: "Extracted/converted X/Y layers. Z failures: [list]. Continue?"

---

## Phase 3: Remote Setup

### ⏸️ CHECKPOINT: Destination

Ask: "Where should this catalog be published?"
- Source Cooperative (s3://us-west-2.opendata.source.coop/...)
- Other S3 bucket
- GCS bucket
- Azure blob storage

### ⏸️ CHECKPOINT: License

Ask: "What license applies to this data?"
- Show what's in source metadata (if anything)
- Common options: CC-BY-4.0, CC0, ODbL

### ⏸️ CHECKPOINT: Contact Info

Ask: "Contact info for this catalog?"
- Name
- Email

### Validate credentials

```bash
# Set up .env
echo "PORTOLAN_REMOTE=<destination>" > .env

# Dry-run push to validate
portolan push --dry-run
```

---

## Phase 4: Asset Generation

### Check tippecanoe availability

```bash
which tippecanoe
```

### ⏸️ CHECKPOINT: PMTiles Generation

Ask: "Generate PMTiles for web visualization?"
- Note if tippecanoe is/isn't available
- Warn about time for large datasets

### Register files and generate assets

```bash
# For remote extractions (files already in collection subdirs):
portolan add . --recursive [--pmtiles]

# For local files (after check --fix):
portolan add <collection-dir>/ [--pmtiles]
```

### ⏸️ CHECKPOINT: Assets Generated

Present:
- Collections processed
- Thumbnails generated
- Any failures

---

## Phase 5: Metadata Enrichment

**CRITICAL: Only use information from the source. Do NOT invent content.**

### What enrichment means

✅ **DO:**
- Fill fields that exist in source but weren't auto-extracted
- Re-read source service metadata (GetCapabilities, service info) to find missed fields
- Fix encoding issues (mojibake, garbled characters)
- Clean up formatting (extra whitespace, inconsistent capitalization)
- Standardize inconsistencies within the source (if source uses "Pergamino" and "Perg." → use whichever is more common in source)

❌ **DO NOT:**
- Invent titles that aren't in the source
- Translate unless source provides both languages
- Add descriptive context that isn't in the original
- Expand abbreviations using external knowledge
- "Improve" wording beyond what the source says

### Infer language

Check layer names and descriptions:
- If consistently one language → use that
- If mixed → checkpoint and ask user

### ⏸️ CHECKPOINT (if mixed language)

Ask: "Source has mixed languages (Spanish titles, English descriptions). Which should be primary?"

### Check source metadata completeness

Compare what portolan extracted vs what's in the source:

1. Re-read source service metadata (GetCapabilities, ArcGIS service info, etc.)
2. For each collection, check:
   - Does source have a title that wasn't extracted? → Use it
   - Does source have a description that wasn't extracted? → Use it
   - Does source have attribution/contact info? → Use it

### ⏸️ CHECKPOINT: Metadata Gaps

If you find fields in the source that weren't extracted:

Present: "I found these fields in the source metadata that weren't auto-extracted:"
- [Show exact text from source for each field]

Ask: "Should I add these to the catalog? (Showing source text exactly as-is)"

### ⏸️ CHECKPOINT: Remaining Gaps

For fields that MUST be filled but aren't in source:

Present: "These required fields aren't in the source metadata:"
- Catalog title: [missing]
- Catalog description: [missing]

Ask: "Please provide values for these, or I can leave them as the auto-generated defaults."

### Update catalog.json

Only with confirmed/approved content:
```python
catalog["title"] = "<from source or user-provided>"
catalog["description"] = "<from source or user-provided>"
```

### Update collection metadata

For fields from source:
```python
collection["title"] = "<from source>"  # Only if source has it
```

For .portolan/metadata.yaml (per ADR-0038):
```yaml
contact:
  name: "<from checkpoint>"
  email: "<from checkpoint>"
license: "<from checkpoint>"
attribution: "<from source if available>"
source_url: "<original service URL>"
keywords: "<from source if available>"
processing_notes: "Extracted from <service type> on <date>"
```

---

## Phase 6: Metadata Templates & README Generation

### Create metadata templates (always recursive)

```bash
portolan metadata init --recursive
```

This creates `.portolan/metadata.yaml` at catalog and all collection levels.

### Generate READMEs (always recursive)

```bash
portolan readme --recursive
```

### ⏸️ CHECKPOINT: README Review

Show catalog-level README summary.

Ask: "READMEs generated. Here's the catalog README. Look correct?"

---

## Phase 7: STAC-GeoParquet (if >1000 assets)

If the catalog has more than 1000 assets, generate items.parquet for efficient queries:

```bash
portolan stac-geoparquet
```

This creates an `items.parquet` file in each collection for fast spatial/temporal queries.

Skip this step for smaller catalogs.

---

## Phase 8: Push

### Dry-run first

```bash
portolan push --dry-run
```

### ⏸️ CHECKPOINT: Push Confirmation

Present:
- File count
- Total size
- Destination URL

Ask: "Ready to push X files (Y MB) to Z. Proceed?"

### Execute push

```bash
portolan push --verbose
```

---

## Phase 9: Final Summary

Present:
- Total collections published
- Live URL
- Any failures/warnings from entire session
- Suggested next steps (verify in browser, check a sample collection)

---

## Failure Handling

| Situation | Action |
|-----------|--------|
| Layer fails extraction | Warn inline, continue, summarize at end |
| Missing CRS | Flag it, ask user if critical |
| Large dataset (>100k features) | Warn about time/memory before proceeding |
| Credentials invalid | Stop and help user fix |
| Mixed languages | Checkpoint and ask |
| Field exists in source but not extracted | Checkpoint with exact source text |
| Required field missing from source | Checkpoint and ask user to provide |
