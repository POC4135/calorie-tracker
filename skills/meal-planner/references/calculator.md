# Calculator reference (scripts/macros.py)

Python 3.8+, standard library only. Run from any folder:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command> [options]
```

`${CLAUDE_SKILL_DIR}` is the folder that holds this skill's SKILL.md. If your environment does not fill it in, use that folder's path. The script finds `references/foods.csv` next to itself.

Exit code 0 means success. Exit code 2 means an input problem; the message on stderr says what to fix (unknown food id with suggestions, missing unit, bad JSON). Fix and rerun; do not guess around it.

## Contents

- targets
- lookup
- units
- log
- summary
- recipe
- plan
- Item format (shared by log, recipe and plan)

## targets

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py targets --age 28 --sex male \
  --height-ft 5 --height-in 9 --weight-lb 172 --bmr 1720 --bmr-source scale \
  --activity moderate --goal recomp
```

- `--sex`: male, female, or unspecified (uses the midpoint of the two formulas)
- Height: `--height-cm` or `--height-ft` with `--height-in`. Weight: `--weight-kg` or `--weight-lb`
- `--bmr` is optional. `--bmr-source`: lab, scale, app, formula, unknown. Only lab values are trusted when they disagree with Mifflin-St Jeor by more than 10%
- `--activity`: sedentary, light, moderate, very_active
- `--goal`: fat_loss, recomp, maintenance, lean_gain
- `--protein-per-kg` overrides the protein factor (default 1.8 for fat loss and recomp, 1.6 otherwise)

Prints a targets table, a one-line "Math" explanation, BMI with the WHO Asian action points, notes, and a last line `TARGETS_JSON {...}`. Keep that JSON for `log` and `plan`. Refuses (exit 2) for anyone under 18.

## lookup

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py lookup "roti, dal, bhindi"
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py lookup "greek yogurt" --grams 200
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py lookup paneer --kind ingredient
```

Fuzzy search over ids, names, and aliases (Hindi, Tamil, Telugu, Kannada, Marathi, Gujarati, Bengali names and common spellings). Separate several foods with commas. `--grams` or `--servings` scales the rows. `--kind`: ingredient, dish, grocery, restaurant, drink. The `basis` column says where a value comes from: usda, label, recipe (reproducible from a documented recipe), or estimate.

## units

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py units toor-dal-raw
```

Lists household measures for one food (cup, tbsp, tsp, medium, piece, katori). Every food also accepts g, kg, oz, lb.

## log

Reads one JSON object on stdin. Use a quoted heredoc so apostrophes in names are safe:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py log <<'EOF'
{"targets": {"kcal":2400,"protein":138,"carbs":294,"fat":75,"fiber":34,"added_sugar":30,"sodium":2300},
 "prior":   {"kcal":450,"protein":22,"carbs":60,"fat":14,"fiber":5,"added_sugar":8,"sodium":700,"alcohol":0},
 "items": [
   {"query": "chapati", "servings": 2, "label": "2 rotis"},
   {"food": "dal-home", "qty": 1, "unit": "katori", "label": "1 katori dal"},
   {"food": "bhindi-masala", "oil_tsp": 1, "label": "Bhindi sabzi (oily)"},
   {"name": "Haldiram's bhujia", "label": "Bhujia, 20 g (label)", "kcal": 110, "protein": 3, "carbs": 9, "fat": 7}
 ]}
EOF
```

- `targets`: the TARGETS_JSON object. Omit it before setup; the table then has no % or remaining rows
- `prior`: today's totals before this meal (the TODAY_JSON from the last log in this chat). Omit for the first meal of the day
- Output: the entry table, the secondary table, then two machine lines. `CHECKS` lists fuzzy matches to verify, estimate-based items, and nutrients that were not counted. `TODAY_JSON` is the new running total to pass as `prior` next time. Do not paste the machine lines into the reply

## summary

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py summary <<'EOF'
{"targets": {...TARGETS_JSON...}, "today": {...TODAY_JSON...}}
EOF
```

Prints Table 1 with only the totals rows and Table 2, for `#ct today`.

## recipe

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py recipe <<'EOF'
{"name": "Mom's rajma", "servings": 6, "cooked_weight_g": 1800,
 "ingredients": [
   {"food": "rajma-raw", "qty": 1.5, "unit": "cup"},
   {"food": "onion", "qty": 2, "unit": "medium"},
   {"food": "tomato", "qty": 3, "unit": "medium"},
   {"food": "oil", "qty": 3, "unit": "tbsp"},
   {"food": "ghee", "qty": 1, "unit": "tsp"},
   {"food": "salt", "qty": 2, "unit": "tsp"},
   {"food": "spices"}, {"food": "water"}
 ]}
EOF
```

- Needs `servings`, `cooked_weight_g`, or both. With a cooked weight it also prints per 100 g, per katori (150 g) and per cup (240 g)
- `water` and `spices` count as zero. Ground spices add under 10 kcal per tsp, so skip them
- Prints `LOG_ITEM_JSON` (one serving as a ready-to-log item) and, with a cooked weight, `PER_100G_JSON`

## plan

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py plan <<'EOF'
{"targets": {...TARGETS_JSON...},
 "meals": [
   {"meal": "Breakfast", "items": [{"food": "poha", "label": "1 cup poha"}, {"food": "greek-yogurt-cup"}]},
   {"meal": "Lunch", "items": [...]}
 ]}
EOF
```

Prints a per-meal table, day totals against targets, and one line per check. Core checks print PASS or ADJUST: calories within 5%, protein at least 95%, fat 20-35% of calories. Advisory checks print PASS or NOTE: fiber at or above target, added sugar and sodium under limits. The last line is `PLAN_OK` when every core check passes, otherwise `PLAN_NEEDS_ADJUSTMENT`. Report NOTE lines to the user (sodium is the usual one for Indian home cooking) with a practical fix.

## Item format (shared by log, recipe and plan)

One of three shapes:

1. A database food by id: `{"food": "<id>", ...amount}`
2. A database food by fuzzy name: `{"query": "bhindi sabzi", ...amount}`. The match appears in `CHECKS.matched_queries`; if it picked the wrong food, rerun with the right id
3. Your own numbers: `{"name": "...", "kcal": n, "protein": n, "carbs": n, "fat": n}` plus optional `fiber`, `added_sugar`, `sodium`, `alcohol`. Use this for label values and anything not in the database

Amount, for shapes 1 and 2 (pick one; default is 1 serving):
- `"servings": 2` (multiples of the database serving)
- `"grams": 150`
- `"qty": 1.5, "unit": "cup"` (units from `units`; dishes served by the cup also take `katori`)

Optional on any item:
- `"label"`: what the row should say ("2 rotis (80 g)"). Always set it; it reads better than the default
- `"oil_tsp"` or `"ghee_tsp"`: extra fat beyond the database value (40 or 38 kcal per tsp)
- `"multiplier"`: scale everything, for example 1.3 for a large portion
