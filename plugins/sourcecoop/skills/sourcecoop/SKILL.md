---
name: sourcecoop
description: Upload geospatial data to Source Cooperative with proper metadata and READMEs using Portolan CLI.
---


<!-- freshness: last-verified: 2026-04-08, maps-to: portolan_cli/cli.py -->

# Source Cooperative Upload Skill

You are helping a user publish geospatial data to [Source Cooperative](https://source.coop), an open data commons for geospatial data. This skill orchestrates the full Portolan pipeline to ensure data is properly formatted, documented, and uploaded.

## Prerequisites

**Source Cooperative requires automated access for programmatic uploads.**

Before proceeding, verify the user has automated access:

```bash
# Check for Source Co-op AWS profile
grep -l "source" ~/.aws/credentials 2>/dev/null || echo "No source profile found"

# Check Portolan config
portolan config get profile 2>/dev/null
portolan config get remote 2>/dev/null
```

**If no credentials are configured:**
- Users WITH automated access: Guide them through credential setup (see Credential Setup section)
- Users WITHOUT automated access: Direct them to request access at **hello@source.coop**

---

## Workflow Overview

The Source Co-op upload workflow follows these steps:

1. **Initialize** — Create Portolan catalog structure
2. **Configure** — Set remote destination and AWS profile
3. **Add** — Track files in the catalog
4. **Metadata** — Create/validate metadata.yaml (recursive)
5. **README** — Generate READMEs from metadata (recursive)
6. **Push** — Upload to Source Co-op with parallel workers

---

## Step 1: Gather Information

Ask the user for:

1. **Organization name** (required): Their Source Co-op organization slug
   - Example: `nlebovits`, `radiant-mlhub`, `vida`

2. **Product name** (optional): Defaults to current directory name
   - Example: `phl-aerial-imagery`, `global-building-footprints`

Build the remote URL:
```
s3://us-west-2.opendata.source.coop/{org}/{product}/
```

---

## Step 2: Credential Setup

If credentials aren't configured, guide the user:

```bash
# 1. Create/edit AWS credentials file
# Add a profile named "source-coop" with their Source Co-op credentials:
#
# ~/.aws/credentials:
# [source-coop]
# aws_access_key_id = <from Source Co-op dashboard>
# aws_secret_access_key = <from Source Co-op dashboard>

# 2. Create .env file in catalog root (never pushed to remote)
cat > .env << 'EOF'
PORTOLAN_REMOTE=s3://us-west-2.opendata.source.coop/{org}/{product}/
PORTOLAN_PROFILE=source-coop
EOF

# Verify configuration
portolan config list
```

**Security note:** Credentials (remote, profile, region) are stored in `.env` files or environment variables — never in `.portolan/config.yaml`. This prevents accidentally pushing credentials to public buckets.

**Important:** Source Co-op uses temporary credentials. If uploads fail with auth errors, the user may need to refresh their credentials from the Source Co-op dashboard.

---

## Step 3: Initialize Catalog

```bash
# Initialize if not already a catalog
portolan init --title "{product_title}" --auto

# Or if catalog exists, verify structure
portolan info
```

---

## Step 4: Configure Remote

Credentials are stored in `.env` file (created in Step 2), not in config.yaml:

```bash
# Verify .env file exists with correct values
cat .env
# Should show:
# PORTOLAN_REMOTE=s3://us-west-2.opendata.source.coop/{org}/{product}/
# PORTOLAN_PROFILE=source-coop

# Verify Portolan reads the config
portolan config list
```

---

## Step 5: Add Files

**Important:** Files must be organized in collection subdirectories. Files at the catalog root are skipped.

```
my-catalog/
├── catalog.json
├── buildings/          # <-- Collection subdirectory
│   └── data.parquet    # <-- Files go here
└── imagery/            # <-- Another collection
    └── ortho.tif
```

```bash
# Organize files into collection subdirectories first if needed
mkdir -p buildings
mv *.parquet buildings/

# Add all collections
portolan add .

# Or add specific collections
portolan add buildings/
portolan add imagery/
```

---

## Step 6: Create Metadata

Source Cooperative emphasizes good metadata. Create metadata.yaml files recursively:

```bash
# Initialize metadata templates for catalog and all collections
portolan metadata init --recursive
```

**Required fields** (validate these exist):
- `title` — Human-readable title
- `description` — What the data contains, its purpose
- `license` — SPDX license identifier (e.g., `CC-BY-4.0`, `CC0-1.0`, `ODbL-1.0`)
- `contact.email` — Contact email for questions

**Recommended fields** (prompt user for these):
- `keywords` — List of tags for discoverability
- `citation` — How to cite this collection
- `temporal_extent` — Time range the data covers
- `providers` — Organizations that created/host the data

```bash
# Validate metadata after editing
portolan metadata validate --recursive
```

---

## Step 7: Generate READMEs

```bash
# Generate READMEs for catalog and all collections
portolan readme --recursive

# Verify READMEs look correct
cat README.md
```

---

## Step 8: Push to Source Co-op

```bash
# Determine optimal worker count (max 8)
# workers = min(cpu_count, 8)

# Dry run first to preview
portolan push --dry-run

# Push with parallel uploads
portolan push --workers {workers} --verbose
```

**Worker recommendation:**
- 1-2 cores: `--workers 1`
- 4 cores: `--workers 4`
- 8+ cores: `--workers 8`

---

<!-- BEGIN GENERATED: cli-reference -->
## CLI Command Reference

### `portolan init`
Initialize a new Portolan catalog.

```bash
portolan init                       # Initialize in current directory
portolan init --auto                # Skip prompts, use defaults
portolan init --title "My Catalog"  # Set title
```

### `portolan config set`
Set a configuration value.

```bash
portolan config set remote s3://bucket/path/   # Set remote destination
portolan config set profile source-coop        # Set AWS profile
```

### `portolan config get`
Get a configuration value.

```bash
portolan config get remote                     # Get current remote
```

### `portolan config list`
List all configuration settings.

```bash
portolan config list                           # List all settings
```

### `portolan add`
Track files in the catalog.

```bash
portolan add .                    # Add all files
portolan add demographics/        # Add collection
portolan add file1.parquet        # Add specific file
```

### `portolan metadata init`
Generate a metadata.yaml template.

```bash
portolan metadata init                # Create template at catalog root
portolan metadata init --recursive    # Create for catalog and all collections
```

### `portolan metadata validate`
Validate metadata.yaml against schema.

```bash
portolan metadata validate            # Validate metadata.yaml
```

### `portolan readme`
Generate README.md from STAC metadata and metadata.yaml.

```bash
portolan readme                    # Generate at catalog root
portolan readme --recursive        # Generate for catalog and all collections
portolan readme --check            # CI mode: exit 1 if stale
```

### `portolan push`
Push local catalog changes to cloud object storage.

```bash
portolan push                              # Push to configured remote
portolan push --dry-run                    # Preview without uploading
portolan push --workers 8                  # Parallel uploads (max 8 recommended)
portolan push --verbose                    # Show per-file progress
portolan push --profile source-coop        # Override AWS profile
```

<!-- END GENERATED: cli-reference -->

---

## Troubleshooting

### "Access Denied" or "403 Forbidden"

**Cause:** AWS credentials are invalid, expired, or don't have permission for this bucket prefix.

**Solution:**
1. Verify credentials in `~/.aws/credentials` under `[source-coop]`
2. Check that the remote URL matches your assigned prefix exactly
3. Refresh credentials from Source Co-op dashboard if they've expired
4. Contact hello@source.coop if you need access to a different prefix

### "No such bucket" or "Bucket not found"

**Cause:** The bucket name is wrong.

**Solution:** Source Co-op bucket is always `us-west-2.opendata.source.coop`. Check your remote:
```bash
portolan config get remote
# Should be: s3://us-west-2.opendata.source.coop/{org}/{product}/
```

### "Push conflict: remote has newer version"

**Cause:** Someone else pushed changes since your last pull.

**Solution:**
```bash
portolan pull   # Get remote changes first
# Resolve any conflicts
portolan push   # Try again
```

### Slow uploads

**Cause:** Single-threaded upload or large files.

**Solution:**
```bash
# Use parallel workers (max 8)
portolan push --workers 8 --verbose
```

### Missing metadata validation

**Cause:** metadata.yaml is missing required fields.

**Solution:**
```bash
portolan metadata validate --recursive
# Edit metadata.yaml files to add missing fields
# Required: title, description, license, contact.email
```

---

## Complete Example

```bash
# 1. Navigate to your data directory
cd ~/data/phl-aerial-imagery

# 2. Initialize catalog
portolan init --title "Philadelphia Aerial Imagery" --auto

# 3. Configure Source Co-op credentials via .env file
cat > .env << 'EOF'
PORTOLAN_REMOTE=s3://us-west-2.opendata.source.coop/nlebovits/phl-aerial-imagery/
PORTOLAN_PROFILE=source-coop
EOF

# 4. Add files
portolan add .

# 5. Create and edit metadata
portolan metadata init --recursive
# Edit .portolan/metadata.yaml with title, description, license, contact

# 6. Generate READMEs
portolan readme --recursive

# 7. Push to Source Co-op
portolan push --workers 8 --verbose
```

---

## Styles

Portolan supports multiple named visualization styles per collection. Each style is a complete Mapbox GL v8 JSON file stored in `{collection}/styles/`.

### Creating Styles

Style files are complete Mapbox GL v8 specs with relative PMTiles source paths:

```json
{
  "version": 8,
  "name": "Buildings by Construction Year",
  "sources": {
    "data": {
      "type": "vector",
      "url": "../data.pmtiles"
    }
  },
  "layers": [
    {
      "id": "buildings-by-age",
      "type": "fill",
      "source": "data",
      "source-layer": "layer_name",
      "paint": {
        "fill-color": ["interpolate", ["linear"], ["get", "bouwjaar"],
          1400, "#1a0a00", 1900, "#8B4513", 1960, "#DAA520", 2020, "#FFFF00"
        ],
        "fill-opacity": 0.7
      }
    }
  ]
}
```

A default style is auto-generated during PMTiles creation. Drop additional style files into `styles/` and they'll be discovered automatically.

### Style Best Practices

1. **Create multiple styles for rich collections.** If a collection has interesting categorical or numeric attributes, create data-driven styles for each. Example: buildings by construction year, by usage type, by height. Don't stop at a single default.

2. **Vary default styles across a catalog.** Each collection should have a visually distinct default color/palette. Use subject matter to inform color choices — water features in blues, vegetation in greens, built environment in warm tones, infrastructure in grays.

3. **Use data-driven styling.** Leverage Mapbox GL expressions (`interpolate`, `match`, `case`, `step`) to reveal patterns in data. For categorical data use `match`; for continuous data use `interpolate` or `step`.

4. **Include a description field on the STAC asset** explaining what the colors/sizes represent. This appears in style pickers and tooltips.

5. **Consider label layers.** For collections with names (monuments, administrative areas, roads), add a label style layer or a dedicated "with labels" style variant.

6. **Look at the collection's table:columns** to understand what attributes are available for data-driven styling. Interesting fields for visualization include: categories/enums, dates/years, numeric measurements, status fields.

### STAC Registration

Styles are registered as collection-level assets with the `portolan:styles` manifest:

```json
{
  "portolan:styles": ["styles/default", "styles/by-age", "styles/by-use"],
  "assets": {
    "styles/default": {
      "href": "./styles/default.json",
      "type": "application/json",
      "title": "Default",
      "description": "Blue building footprints.",
      "roles": ["style"]
    }
  }
}
```

First entry in `portolan:styles` is the default. `portolan scan` discovers styles and registers them automatically.

---

## Source Cooperative Best Practices

1. **Use descriptive titles** — "Philadelphia 2023 Aerial Orthoimagery" not "imagery"
2. **Include spatial coverage** — Mention the geographic area in the description
3. **Specify temporal extent** — When was the data collected?
4. **Choose appropriate license** — CC-BY-4.0 or CC0-1.0 are common for open data
5. **Add keywords** — Help users discover your data (e.g., "aerial", "orthoimagery", "philadelphia", "pennsylvania")
6. **Provide contact info** — So users can ask questions about the data
<!-- /freshness -->
