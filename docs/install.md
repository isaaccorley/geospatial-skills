# Install

## Manual

Copy a skill directory into your agent's local skills folder.

```bash
cp -R skills/geoparquet ~/.claude/skills/geoparquet
```

If your tool uses a different skill directory, copy the same folder there.

## OpenSkills

`geoparquet` already supports OpenSkills-style installation:

```bash
npx openskills install geoparquet-io/geoparquet-skill
```

## Claude Code / Cowork

The upstream `geoparquet` skill also ships marketplace/plugin metadata. See the
skill page for the exact commands and UI flow.

## Local docs

```bash
uv sync
uv run mkdocs serve
```
