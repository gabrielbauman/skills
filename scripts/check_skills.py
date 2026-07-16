#!/usr/bin/env python3
"""Repo lint: skill frontmatter, marketplace sync, README index, scripts.

Every failure mode this checks for is silent in normal use: a skill with
invalid strict YAML still loads in Claude Code but is dropped by the
skills.sh CLI, and a missing marketplace entry or README row just never
appears anywhere. Run from the repo root; exits nonzero with one line per
problem. Requires PyYAML.
"""

import json
import py_compile
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
problems = []


def check(cond, message):
    if not cond:
        problems.append(message)
    return cond


def frontmatter(skill_dir):
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not check(match, f"{skill_dir.name}: SKILL.md has no frontmatter block"):
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        problems.append(
            f"{skill_dir.name}: frontmatter is not strict YAML "
            f"(quote the description?): {str(exc).splitlines()[0]}"
        )
        return None
    check(isinstance(data, dict), f"{skill_dir.name}: frontmatter is not a mapping")
    return data if isinstance(data, dict) else None


skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
check(skill_dirs, "no skill directories found under skills/")

for d in skill_dirs:
    if not check((d / "SKILL.md").is_file(), f"{d.name}: missing SKILL.md"):
        continue
    data = frontmatter(d)
    if data is None:
        continue
    check(data.get("name") == d.name,
          f"{d.name}: frontmatter name {data.get('name')!r} != directory name")
    desc = data.get("description")
    check(isinstance(desc, str) and desc.strip(),
          f"{d.name}: missing or empty description")

manifest_path = ROOT / ".claude-plugin" / "marketplace.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
plugin_skills = set()
for plugin in manifest.get("plugins", []):
    name = plugin.get("name", "<unnamed>")
    for rel in plugin.get("skills", []):
        check((ROOT / rel).is_dir(),
              f"marketplace plugin {name}: skills path {rel} does not exist")
        plugin_skills.add(Path(rel).name)

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for d in skill_dirs:
    check(d.name in plugin_skills,
          f"{d.name}: no marketplace.json plugin entry references it")
    check(f"](skills/{d.name}/)" in readme,
          f"{d.name}: no row in the README skills table")
check(plugin_skills <= {d.name for d in skill_dirs},
      f"marketplace references unknown skills: "
      f"{sorted(plugin_skills - {d.name for d in skill_dirs})}")

for script in SKILLS_DIR.glob("*/scripts/*.py"):
    try:
        py_compile.compile(str(script), doraise=True)
    except py_compile.PyCompileError as exc:
        problems.append(f"{script.relative_to(ROOT)}: does not compile: {exc.msg}")

if problems:
    print(f"{len(problems)} problem(s):")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print(f"OK: {len(skill_dirs)} skills checked")
