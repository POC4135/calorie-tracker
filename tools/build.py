#!/usr/bin/env python3
"""Build tooling for the Katori skills.

    python tools/build.py sync      copy shared files into every skill and fill shared SKILL.md blocks
    python tools/build.py check     validate everything; fail if any synced file is stale (used by CI)
    python tools/build.py package   check, then write zips to dist/ (one per skill, plus the whole plugin)
    python tools/build.py notes X   print the CHANGELOG section for version X (used by the release workflow)

Edit shared sources only (data/, shared/). `sync` writes the copies inside skills/.
Standard library plus PyYAML (pip install pyyaml).
"""

import hashlib
import json
import os
import re
import shutil
import sys
import zipfile

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")
PLUGIN_JSON = os.path.join(ROOT, ".claude-plugin", "plugin.json")
MARKETPLACE_JSON = os.path.join(ROOT, ".claude-plugin", "marketplace.json")

ALL = ["macro-tracker", "recipe-macros", "menu-macros", "meal-planner"]

# shared source -> (destination inside each skill, which skills get it)
SYNC = [
    ("shared/scripts/macros.py", "scripts/macros.py", ALL),
    ("data/foods.csv", "references/foods.csv", ALL),
    ("data/measures.csv", "references/measures.csv", ALL),
    ("shared/references/calculator.md", "references/calculator.md", ALL),
    ("shared/references/estimation-guide.md", "references/estimation-guide.md", ["macro-tracker", "menu-macros"]),
]
BLOCKS = {"guardrails": "shared/blocks/guardrails.md", "style": "shared/blocks/style.md"}
BLOCK_RE = re.compile(r"(<!-- BEGIN SHARED: (\w+) -->\n)(.*?)(<!-- END SHARED: \2 -->)", re.S)

# claude.ai documents a 200-character limit for uploaded skill descriptions; the Agent Skills
# spec allows 1,024. Staying under 200 keeps every upload path working.
DESCRIPTION_MAX = 200
NAME_MAX = 64
SKILL_BODY_MAX_LINES = 500
REFERENCE_TOC_MIN_LINES = 100     # longer reference files need a table of contents
DIRECTORY_FILE_MAX_BYTES = 256 * 1024  # Anthropic directory review limit for non-image files
DIRECTORY_MAX_FILES = 512
ZIP_DATE = (2026, 1, 1, 0, 0, 0)  # fixed timestamp so zips are reproducible
JUNK = {".DS_Store", "Thumbs.db", "desktop.ini"}
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", "evals", "node_modules"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".woff", ".woff2", ".ttf", ".otf"}
TEXT_EXT = {".md", ".py", ".csv", ".json", ".yml", ".yaml", ".txt", ".toml", ".cfg", ".sh", ".html", ".svg"}
EM_DASH = chr(0x2014)  # the em dash character


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------

def expected_files():
    """Map of destination path -> expected content for every synced file."""
    out = {}
    for src, dest, skills in SYNC:
        content = read(os.path.join(ROOT, src))
        for skill in skills:
            out[os.path.join(SKILLS_DIR, skill, dest)] = content
    blocks = {name: read(os.path.join(ROOT, path)).rstrip("\n") + "\n" for name, path in BLOCKS.items()}
    for skill in ALL:
        path = os.path.join(SKILLS_DIR, skill, "SKILL.md")
        text = read(path)

        def fill(match):
            name = match.group(2)
            if name not in blocks:
                raise SystemExit(f"{rel(path)}: unknown shared block '{name}'")
            return match.group(1) + blocks[name] + match.group(4)

        out[path] = BLOCK_RE.sub(fill, text)
    return out


def sync():
    changed = 0
    for path, content in expected_files().items():
        if not os.path.exists(path) or read(path) != content:
            write(path, content)
            changed += 1
            print(f"synced {rel(path)}")
    print(f"sync: {changed} file(s) updated")


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

def parse_skill(path):
    text = read(path)
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return None, None, "missing or malformed YAML frontmatter"
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, None, f"invalid YAML: {exc}"
    return meta, match.group(2), None


def check(errors, warnings):
    plugin = json.loads(read(PLUGIN_JSON))
    market = json.loads(read(MARKETPLACE_JSON))
    version = plugin["version"]

    # Synced copies are current
    for path, content in expected_files().items():
        if not os.path.exists(path):
            errors.append(f"{rel(path)} is missing; run python tools/build.py sync")
        elif read(path) != content:
            errors.append(f"{rel(path)} is stale; edit the shared source and run python tools/build.py sync")

    # Plugin and marketplace agree
    entries = {p["name"]: p for p in market.get("plugins", [])}
    if plugin["name"] not in entries:
        errors.append("marketplace.json has no entry named like plugin.json")
    else:
        entry = entries[plugin["name"]]
        if entry.get("version") != version:
            errors.append(f"marketplace.json version {entry.get('version')} != plugin.json version {version}")
        if entry.get("source") != "./":
            errors.append("marketplace entry source should be './' (the repo root is the plugin)")

    found = sorted(d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d)))
    if found != sorted(ALL):
        errors.append(f"skills/ holds {found}; tools/build.py lists {ALL}")

    for skill in ALL:
        skill_dir = os.path.join(SKILLS_DIR, skill)
        path = os.path.join(skill_dir, "SKILL.md")
        meta, body, problem = parse_skill(path)
        if problem:
            errors.append(f"{rel(path)}: {problem}")
            continue
        name = str(meta.get("name", ""))
        desc = str(meta.get("description", "")).strip()
        if name != skill:
            errors.append(f"{rel(path)}: name '{name}' must match folder '{skill}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > NAME_MAX:
            errors.append(f"{rel(path)}: name must be kebab-case and at most {NAME_MAX} characters")
        if re.search(r"claude|anthropic", name):
            errors.append(f"{rel(path)}: name may not contain 'claude' or 'anthropic'")
        if not desc:
            errors.append(f"{rel(path)}: empty description")
        if len(desc) > DESCRIPTION_MAX:
            errors.append(f"{rel(path)}: description is {len(desc)} characters (max {DESCRIPTION_MAX})")
        if "<" in desc or ">" in desc:
            errors.append(f"{rel(path)}: description may not contain angle brackets")
        allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
        extra = set(meta) - allowed
        if extra:
            errors.append(f"{rel(path)}: unexpected frontmatter keys {sorted(extra)}")
        md = meta.get("metadata") or {}
        if not all(isinstance(v, str) for v in md.values()):
            errors.append(f"{rel(path)}: metadata values must be strings (quote the version)")
        if md.get("version") != version:
            errors.append(f"{rel(path)}: metadata.version {md.get('version')} != plugin version {version}")
        if len(body.splitlines()) > SKILL_BODY_MAX_LINES:
            errors.append(f"{rel(path)}: body is over {SKILL_BODY_MAX_LINES} lines")
        for ref in sorted(set(re.findall(r"`((?:references|scripts)/[A-Za-z0-9_./-]+)`", body))):
            if not os.path.exists(os.path.join(skill_dir, ref)):
                errors.append(f"{rel(path)}: mentions {ref}, which does not exist")
        for match in BLOCK_RE.finditer(read(path)):
            if not match.group(3).strip():
                errors.append(f"{rel(path)}: shared block '{match.group(2)}' is empty; run sync")
        # Every reference file is mentioned somewhere in SKILL.md, and long ones have contents
        ref_dir = os.path.join(skill_dir, "references")
        for ref in sorted(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else []:
            ref_path = os.path.join(ref_dir, ref)
            if f"references/{ref}" not in body:
                warnings.append(f"{rel(ref_path)} is never mentioned in SKILL.md")
            if ref.endswith(".md") and len(read(ref_path).splitlines()) > REFERENCE_TOC_MIN_LINES:
                if "## Contents" not in read(ref_path):
                    errors.append(f"{rel(ref_path)}: over {REFERENCE_TOC_MIN_LINES} lines without a '## Contents' section")

    # Repository hygiene and Anthropic directory limits
    count = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "dist", "__pycache__", ".pytest_cache"}]
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            count += 1
            ext = os.path.splitext(filename)[1].lower()
            if filename in JUNK or "__MACOSX" in path:
                errors.append(f"{rel(path)}: remove OS junk files")
            if ext not in IMAGE_EXT and os.path.getsize(path) > DIRECTORY_FILE_MAX_BYTES:
                errors.append(f"{rel(path)}: over 256 KiB, which the plugin directory holds for review")
            if ext in {".zip", ".skill", ".plugin", ".pdf", ".ico"}:
                errors.append(f"{rel(path)}: binary archives belong in GitHub Releases, not the repo")
            if ext in TEXT_EXT and EM_DASH in read(path):
                target = errors if rel(path).startswith("skills/") else warnings
                target.append(f"{rel(path)}: contains an em dash")
    if count > DIRECTORY_MAX_FILES:
        errors.append(f"repository has {count} files; the plugin directory reviews plugins over {DIRECTORY_MAX_FILES}")


def run_check():
    errors, warnings = [], []
    check(errors, warnings)
    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}")
    if errors:
        print(f"check failed: {len(errors)} error(s)")
        return 1
    print(f"check passed ({len(warnings)} warning(s))")
    return 0


# ---------------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------------

def _add_tree(archive, source_dir, arc_prefix):
    for dirpath, dirnames, filenames in os.walk(source_dir):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for filename in sorted(filenames):
            if filename in JUNK or filename.endswith(".pyc"):
                continue
            full = os.path.join(dirpath, filename)
            arcname = os.path.join(arc_prefix, os.path.relpath(full, source_dir)).replace(os.sep, "/")
            _add_file(archive, full, arcname)


def _add_file(archive, full, arcname):
    info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if full.endswith(".py") else 0o644) << 16
    with open(full, "rb") as handle:
        archive.writestr(info, handle.read())


def package():
    if run_check():
        return 1
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    built = []
    for skill in ALL:
        out = os.path.join(DIST, f"{skill}.zip")
        with zipfile.ZipFile(out, "w") as archive:
            _add_tree(archive, os.path.join(SKILLS_DIR, skill), skill)
        built.append(out)
    plugin_zip = os.path.join(DIST, "katori-plugin.zip")
    with zipfile.ZipFile(plugin_zip, "w") as archive:
        _add_file(archive, PLUGIN_JSON, ".claude-plugin/plugin.json")
        for name in ("README.md", "LICENSE"):
            _add_file(archive, os.path.join(ROOT, name), name)
        _add_tree(archive, SKILLS_DIR, "skills")
    built.append(plugin_zip)
    sums = []
    for path in built:
        with open(path, "rb") as handle:
            sums.append(f"{hashlib.sha256(handle.read()).hexdigest()}  {os.path.basename(path)}")
    write(os.path.join(DIST, "SHA256SUMS.txt"), "\n".join(sums) + "\n")
    for path in built:
        print(f"built {rel(path)} ({os.path.getsize(path) // 1024} KiB)")
    return 0


INSTALL_NOTES = """
## Install

- **claude.ai or the desktop app:** Customize > Plugins > Add > Add marketplace, enter `POC4135/calorie-tracker`, then add Katori. Or upload `katori-plugin.zip` with Add > Upload plugin.
- **One skill:** upload `macro-tracker.zip` (or another skill zip) under Customize > Skills.
- **Claude Code:** `/plugin install katori --marketplace POC4135/calorie-tracker`

`SHA256SUMS.txt` lists checksums for every zip.
"""


def release_notes(version):
    text = read(os.path.join(ROOT, "CHANGELOG.md"))
    match = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[)", text, re.S | re.M)
    if not match:
        raise SystemExit(f"No CHANGELOG.md section for {version}")
    return match.group(1).strip() + "\n" + INSTALL_NOTES


def main(argv):
    command = argv[1] if len(argv) > 1 else "check"
    if command == "notes" and len(argv) > 2:
        print(release_notes(argv[2]))
        return 0
    if command == "sync":
        sync()
        return run_check()
    if command == "check":
        return run_check()
    if command == "package":
        return package()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
