"""MkDocs hook: package each skills/<name>/ directory as site/downloads/<name>.skill.

A .skill file is a zip archive whose top-level entry is the skill directory
(<name>/SKILL.md, ...), the format Claude Cowork and claude.ai accept as an
uploadable skill.
"""

import zipfile
from pathlib import Path
from typing import Any


def on_post_build(config: dict[str, Any], **kwargs: Any) -> None:
    repo_root = Path(config["config_file_path"]).parent
    skills_dir = repo_root / "skills"
    downloads = Path(config["site_dir"]) / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)

    for skill_dir in sorted(skills_dir.iterdir()):
        if not (skill_dir / "SKILL.md").is_file():
            continue
        out = downloads / f"{skill_dir.name}.skill"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(skill_dir.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(skills_dir))
