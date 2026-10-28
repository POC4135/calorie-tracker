---
name: recipe-macros
description: Calculates per-serving calories and macros for home recipes and batch-cooked dishes like dal, sabzi, curry, or biryani. Use for ingredient lists with amounts, recipe links, or '#ct recipe'.
---

# Recipe Macros

Turns a batch recipe into per-serving, per-katori, and per-100 g macros, and shows swaps that improve them. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Get every number from `scripts/macros.py` (Python 3, standard library). Run it as `python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command>`; `${CLAUDE_SKILL_DIR}` is this skill's folder (use its path if it is not filled in). Ingredients are in `references/foods.csv` (raw, per 100 g); household units in `references/measures.csv`. On bad input the script exits with code 2 and says what to fix.

- `lookup "toor dal, onion, ghee" --kind ingredient` finds ingredient ids.
- `units <id>` lists the units a food accepts (cup, tbsp, tsp, medium, piece; every food takes g, oz, lb).
- `recipe` reads JSON on stdin:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py recipe <<'EOF'
{"name": "Rajma", "servings": 6, "cooked_weight_g": 1650,
 "ingredients": [
   {"food": "rajma-raw", "qty": 1.5, "unit": "cup"},
   {"food": "onion", "qty": 2, "unit": "medium"},
   {"food": "tomato", "qty": 3, "unit": "medium"},
   {"food": "oil", "qty": 3, "unit": "tbsp"},
   {"food": "salt", "qty": 2, "unit": "tsp"},
   {"food": "spices"}, {"food": "water"}
 ]}
EOF
```

  - Needs `servings`, `cooked_weight_g`, or both. With a cooked weight it also prints per 100 g, per katori (150 g), and per cup (240 g).
  - `spices` and `water` count as zero. An ingredient not in the database can be your own numbers: `{"name": "...", "kcal": n, "protein": n, "carbs": n, "fat": n}`.
  - Ends with `LOG_ITEM_JSON` (one serving, ready to log) and, with a cooked weight, `PER_100G_JSON`. Do not paste those lines.

## Workflow

1. **Get the recipe:** every ingredient with an amount, the number of servings (or the cooked weight), and the oil, ghee, butter, or cream amounts, which move the result most. Ask for whatever is missing in one message.
2. **Map ingredients** to ids with `lookup`. Use raw weights (raw dal, raw rice, raw meat without bones); use `rice-cooked` only if the recipe measures cooked rice.
3. **Run** `recipe`.
4. **Reply:**
   1. The ingredient and portion tables, copied as printed.
   2. Where the calories come from, in one sentence.
   3. One to three swaps, each computed by rerunning `recipe`, with the per-serving effect (for example, half the oil, Greek yogurt instead of cream, added soya chunks or tofu for protein).
   4. If there is no cooked weight, one line on the pot trick: weigh the empty pot, then the pot with the finished dish; the difference is the cooked weight.
   5. A confidence line.
5. If the user ate some, log it with macro-tracker, scaled from `LOG_ITEM_JSON`. To reuse the dish, suggest saving the per-100 g line in a Claude Project.

## Rules

- Without a cooked weight, servings decide everything. Sanity-check them with typical yields: rice about 3x its raw weight, thin dal 5-7x, chickpeas or rajma about 2.3x, boneless chicken about 0.75x.
- For deep-fried items, the oil in the pan is not the oil eaten; assume about 10-15% of the batter or dough weight is absorbed, and say so.
- If family members eat unequal portions, give per-katori and per-100 g values rather than one per-serving number.

## Safety

If the user mentions an eating disorder or shows signs of one (fear of eating, purging, distress over small amounts), stop giving numbers, respond with care, and mention the National Alliance for Eating Disorders helpline, 1-866-662-1235 (US). Make no medical claims about foods.

## Style

Tables first. Plain sentences, no emoji, no em dashes. Use the user's units.
