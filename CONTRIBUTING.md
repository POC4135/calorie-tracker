# Contributing

Thanks for helping. The most useful contributions are dishes the database is missing, values that look wrong (with a source), regional names, and real conversations where a skill went wrong.

## How the repository fits together

```text
data/foods.csv            the food database (edit this)
data/measures.csv         household units to grams (edit this)
data/recipes/*.json       recipes behind every food with basis=recipe
shared/scripts/macros.py  the calculator (edit this)
shared/references/        reference docs shared by several skills (edit these)
shared/blocks/            safety and style text injected into every SKILL.md
skills/<name>/            the four skills; copies of shared files live here
tools/build.py            sync, check, and package
tests/                    pytest suite
evals/                    behavior test cases for claude plugin eval
```

Edit the shared sources, never the copies inside `skills/`. Then run:

```bash
pip install -r requirements-dev.txt
python tools/build.py sync     # copy shared files into the skills
python -m pytest -q            # run the tests
python tools/build.py check    # validate skills, manifests, and file rules
```

CI runs the same commands on every pull request.

## Adding or fixing a food

Each row in `data/foods.csv` is one serving:

| Column | Notes |
|---|---|
| `id` | lowercase-with-hyphens, unique; restaurant rows start with `r-` |
| `name` | what people call it, with the key assumption in parentheses |
| `aliases` | pipe-separated, lowercase: Hindi and regional names, spellings |
| `kind` | `ingredient` (raw, per 100 g), `dish`, `grocery`, `restaurant`, or `drink` |
| `serving`, `serving_g` | the serving in words and in grams (ml for drinks) |
| `kcal` ... `sodium_mg` | per serving; carbs include fiber; added sugar excludes milk and fruit sugars |
| `alcohol_g` | drinks only |
| `basis` | `usda`, `label`, `recipe`, or `estimate` |
| `notes` | short; use semicolons, not commas |

Rules that keep the data honest:

- Give a source in the pull request: a USDA FoodData Central entry, a photo of a label, or a recipe with amounts.
- Calories must agree with the macros (4 x protein + 4 x carbs + 9 x fat + 7 x alcohol, allowing for fiber). The tests check this.
- If you mark a row `recipe`, add the recipe to `data/recipes/` with `db_id` set; the tests recompute it.
- Use typical home amounts of oil and salt for home dishes and US portions for restaurant rows.
- No brand names in `id` or `name` unless the row is a specific branded product.

Not sure about the numbers? Open a [food request](https://github.com/POC4135/calorie-tracker/issues/new?template=food_request.yml) instead.

## Changing a skill

- Keep each SKILL.md under 500 lines and its description under 200 characters (claude.ai's upload limit).
- Explain the reason behind an instruction rather than adding rules in capitals.
- Never move arithmetic out of the calculator and into prose.
- Keep the safety block intact. Changes to `shared/blocks/guardrails.md` need a clear rationale in the pull request.
- Add or update a case in `evals/` for behavior you change.

## Behavior tests

`evals/` holds test cases in the format `claude plugin eval` reads. With Claude Code installed:

```bash
claude plugin eval . --allow-tools Bash
```

These are real model runs billed to your account, so CI does not run them.

## Releases

1. Update `version` in `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and each SKILL.md's `metadata.version` (the build check enforces that they match).
2. Add an entry to `CHANGELOG.md`.
3. Merge to `main`, then tag: `git tag v1.1.0 && git push origin v1.1.0`. The release workflow builds the zips and publishes the GitHub release.

## Style

Plain language, no em dashes, no emoji in skill text. Write for someone in a hurry.
