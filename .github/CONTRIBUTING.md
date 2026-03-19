# Contributing

## Repo goals

- keep each skill self-contained under `skills/<name>/`
- publish calm, earth-forward docs
- keep install paths obvious for Codex, Claude, Cursor, Aider, and similar tooling

## Docs

- canonical URL: `https://isaac.earth/geospatial-skills/`
- local dev:

```bash
uv sync --group dev
uv run mkdocs serve
```

- strict build:

```bash
uv run mkdocs build --strict
```

## Quality gate

Run before handoff:

```bash
uv sync --group dev
uv run pre-commit run --all-files
uv run mkdocs build --strict
```

## CI

- `.github/workflows/ci.yaml`: pre-commit + strict docs build on pushes to `main` and PRs
- `.github/workflows/docs-pages.yaml`: GitHub Pages build/deploy on pushes to `main`

## Pages

Set repository Pages source to GitHub Actions. Published site should resolve at:

- `https://isaac.earth/geospatial-skills/`
