# Copilot Review Instructions

Prioritize skill packaging correctness over generic style feedback.

## Review for

- each public skill lives under `skills/<name>/`
- each Claude plugin lives under `plugins/<name>/`
- each portable skill includes `skills/<name>/SKILL.md`
- each Claude plugin includes `plugins/<name>/.claude-plugin/plugin.json`
- each Claude plugin includes `plugins/<name>/skills/<name>/SKILL.md`
- `.claude-plugin/marketplace.json` entries point `source` to `./plugins/<name>`
- plugin `name` fields match the public skill slug
- docs skill page paths and nav entries match actual skill slugs
- homepage catalog lists every public skill
- homepage catalog includes attribution like `Referenced from ...`
- `SKILL.md` files preserve valid YAML frontmatter
- if a source skill has `references/`, the Claude plugin copy has matching references
- universal install examples use `.agent/skills/<name>`

## Flag as bugs

- stale old skill names after a rename
- marketplace entries pointing at repo root instead of plugin folders
- install commands pointing to the wrong skill slug
- missing docs pages for public skills
- broken or mangled `SKILL.md` frontmatter
- CI scripts validating the wrong directory layout
