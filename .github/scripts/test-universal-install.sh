#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

target_root="$tmpdir/.agent/skills"
mkdir -p "$target_root"

shopt -s nullglob
skills=("$repo_root"/skills/*)

if [[ ${#skills[@]} -eq 0 ]]; then
  echo "No skills found under skills/"
  exit 1
fi

for skill_dir in "${skills[@]}"; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue

  skill_name="$(basename "$skill_dir")"
  install_dir="$target_root/$skill_name"

  cp -R "$skill_dir" "$install_dir"

  skill_file="$install_dir/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "Missing SKILL.md after install: $skill_name"
    exit 1
  fi

  first_line="$(sed -n '1p' "$skill_file")"
  if [[ "$first_line" != "---" ]]; then
    echo "Invalid frontmatter start in $skill_file"
    exit 1
  fi

  if ! grep -Eq '^name:[[:space:]]+[a-z0-9-]+$' "$skill_file"; then
    echo "Missing or invalid name field in $skill_file"
    exit 1
  fi

  if ! grep -Eq '^description:[[:space:]]+.+' "$skill_file"; then
    echo "Missing description field in $skill_file"
    exit 1
  fi

  if [[ -d "$skill_dir/references" ]] && [[ ! -d "$install_dir/references" ]]; then
    echo "Missing references directory after install: $skill_name"
    exit 1
  fi

  echo "installed: $skill_name"
done

echo "Universal install smoke test passed"
