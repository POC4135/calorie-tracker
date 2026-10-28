# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-28

First public release as the Katori suite.

### Added
- Four skills: `macro-tracker`, `recipe-macros`, `menu-macros`, `meal-planner`.
- Shared calculator (`scripts/macros.py`): targets, food lookup, meal logging, day summary, recipe macros, and plan checks, using only the Python standard library.
- Food database of 354 foods (Indian home dishes, raw ingredients, US groceries, US Indian restaurant portions, drinks) with regional aliases, provenance for every row, and 147 household measures.
- Documented recipes behind the seven recipe-based foods.
- Plugin and marketplace manifests for claude.ai, the Claude desktop app, and Claude Code; per-skill and full-plugin zips in each release.
- Safety rules shared by every skill: no targets under 18, no plans below BMR or 1,200/1,500 kcal, clinician referral for medical conditions, and a stop on numbers when disordered eating shows up.
- Automated tests, build validation, CI, and tag-based releases.

### Changed
- `macro-tracker` rewritten from the first draft: description under 200 characters for claude.ai uploads, every number from the calculator, added-sugar ceiling of 5% of calories in line with current guidance, `#ct today`, `#ct export`, and correction commands.

[1.0.0]: https://github.com/POC4135/calorie-tracker/releases/tag/v1.0.0
