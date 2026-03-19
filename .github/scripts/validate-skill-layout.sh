#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

skills_ok=0

for skill_dir in skills/*; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue

  skill_name="$(basename "$skill_dir")"
  plugin_dir="plugins/$skill_name"
  plugin_skill="$plugin_dir/skills/$skill_name/SKILL.md"
  plugin_json="$plugin_dir/.claude-plugin/plugin.json"
  docs_page="docs/skills/$skill_name.md"

  [[ -f "$plugin_json" ]] || { echo "missing plugin.json for $skill_name"; exit 1; }
  [[ -f "$plugin_skill" ]] || { echo "missing plugin skill for $skill_name"; exit 1; }
  [[ -f "$docs_page" ]] || { echo "missing docs page for $skill_name"; exit 1; }

  grep -Eq "^name:[[:space:]]+$skill_name$" "$skill_dir/SKILL.md" || {
    echo "portable SKILL name mismatch for $skill_name"
    exit 1
  }

  grep -Eq "^name:[[:space:]]+$skill_name$" "$plugin_skill" || {
    echo "plugin SKILL name mismatch for $skill_name"
    exit 1
  }

  jq -e --arg name "$skill_name" '.name == $name' "$plugin_json" >/dev/null || {
    echo "plugin.json name mismatch for $skill_name"
    exit 1
  }

  jq -e --arg name "$skill_name" '.plugins[] | select(.name == $name and .source == ("./plugins/" + $name))' .claude-plugin/marketplace.json >/dev/null || {
    echo "marketplace entry mismatch for $skill_name"
    exit 1
  }

  if [[ -d "$skill_dir/references" && ! -d "$plugin_dir/skills/$skill_name/references" ]]; then
    echo "missing plugin references for $skill_name"
    exit 1
  fi

  skills_ok=1
  echo "validated: $skill_name"
done

[[ "$skills_ok" -eq 1 ]] || { echo "no skills validated"; exit 1; }
echo "Skill layout validation passed"
