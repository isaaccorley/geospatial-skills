# Tessera

Download Tessera embeddings with the `geotessera` CLI.

<div class="skill-callout">
  <p class="skill-callout-label">Tool</p>
  <p><code>geotessera</code> for coverage checks, downloads, visualization, and local serving.</p>
</div>

## Install

### Universal

```bash
cp -R skills/tessera ~/.agent/skills/tessera
```

### Claude

```bash
/plugin marketplace add isaaccorley/geospatial-skills
/plugin install tessera@geospatial-skills
```

CLI:

```bash
claude plugin marketplace add isaaccorley/geospatial-skills
claude plugin install tessera@geospatial-skills
```

## Essential commands

```bash
geotessera coverage --year 2024 --output coverage_2024.png
geotessera download --bbox "-0.2,51.4,0.1,51.6" --year 2024 --output ./out
geotessera download --region-file region.geojson --format npy --year 2024 --output ./arrays
geotessera download --bbox "-0.2,51.4,0.1,51.6" --bands "0,1,2" --year 2024 --output ./subset
geotessera visualize ./out --type web --output ./web
geotessera serve ./web --open
```

## Source

- Skill: [skills/tessera/SKILL.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/tessera/SKILL.md)
- CLI reference: [skills/tessera/references/geotessera-cli.md](https://github.com/isaaccorley/geospatial-skills/blob/main/skills/tessera/references/geotessera-cli.md)
- Upstream reference: [ucam-eo/geotessera](https://github.com/ucam-eo/geotessera)
