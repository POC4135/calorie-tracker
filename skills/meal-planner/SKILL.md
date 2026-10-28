---
name: meal-planner
description: Builds one-day or seven-day Indian meal plans that hit calorie and protein targets with US grocery staples, plus a grocery list. Use for meal plans, diet plans, weekly prep, or '#ct plan'.
---

# Meal Planner

Builds meal plans from food the user already cooks, plus the US grocery staples that make protein targets reachable. Every day is checked by the calculator before it is shown. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Get every number from `scripts/macros.py` (Python 3, standard library). Run it as `python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command>`; `${CLAUDE_SKILL_DIR}` is this skill's folder (use its path if it is not filled in). Foods are in `references/foods.csv`; household units in `references/measures.csv`.

- `targets --age 34 --sex female --height-cm 165 --weight-kg 70 --activity light --goal fat_loss` (optional `--bmr` and `--bmr-source`) prints targets and a final `TARGETS_JSON` line. Refuses anyone under 18.
- `lookup "tofu, soya chunks, greek yogurt"` finds ids and portions.
- `plan` reads JSON on stdin:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py plan <<'EOF'
{"targets": {"kcal":2400,"protein":138,"carbs":294,"fat":75,"fiber":34,"added_sugar":30,"sodium":2300},
 "meals": [
   {"meal": "Breakfast", "items": [{"food": "poha", "servings": 1.25, "label": "Poha, 1 1/4 cups"}, {"food": "greek-yogurt-cup", "label": "Greek yogurt, 170 g"}]},
   {"meal": "Lunch", "items": [{"food": "roti", "servings": 2, "label": "2 rotis"}, {"food": "rajma-curry", "label": "Rajma, 1 cup"}, {"food": "tofu-firm", "grams": 150, "oil_tsp": 1, "label": "Tofu, 150 g"}]}
 ]}
EOF
```

  - Items: a database id (`food`), a fuzzy name (`query`), or your own numbers. Amount: `servings`, `grams`, or `qty` + `unit`. Extras: `oil_tsp`, `ghee_tsp`. Always set `label`.
  - Prints a meal table, day totals against targets, and PASS or ADJUST for calories (within 5%), protein (at least 95%), and fat (20-35% of calories); fiber, added sugar, and sodium print PASS or NOTE. The last line is `PLAN_OK` or `PLAN_NEEDS_ADJUSTMENT`.

## Workflow

1. **Targets:** use targets from earlier in the chat or from the user; otherwise collect age, sex, height, weight, activity, goal, and diet type, and run `targets`.
2. **Constraints:** ask once for anything unknown, with defaults if they skip it: diet type and foods to avoid; regional style [mixed]; one or seven days [one]; meals per day [3 plus a snack]; weekday cooking time [30 minutes].
3. **Draft** each day: a protein source in every meal (25-40 g), the user's usual carbs (roti, rice, idli, poha), and at least two vegetable servings, with portions in household units.
4. **Check** each day with `plan`. On `PLAN_NEEDS_ADJUSTMENT`, fix the biggest miss and rerun, up to three times; then show the closest version and state the gap. Never show an unchecked day. NOTE lines do not block a plan; sodium is the usual one (home cooking often lands at 3,000-4,000 mg), so suggest lighter salt and fewer pickles, papads, and namkeen.
5. **Reply:**
   1. One day: the `plan` table and its check lines. Seven days: a weekly grid (Day | Breakfast | Lunch | Snack | Dinner | Cal | Protein), then the full table for one day.
   2. Short prep notes (what to batch-cook: dal, rajma or chole, soaked soya chunks, chopped onion-tomato masala).
   3. A grocery list for the whole plan, grouped by Indian grocery, regular grocery, and warehouse club, in package sizes.

## Rules

- Vegetarians rarely reach 1.6-1.8 g/kg protein on dal and paneer within a calorie target. Use Greek yogurt, skyr, ultra-filtered milk, tofu, soya chunks, edamame, or whey, and say so. If the user refuses all of them, show the best achievable protein and the gap.
- Reuse batch-cooked dishes across days; seven-day plans should repeat dishes.
- If the user cooks for family, change portions, not menus.

## Safety

- **Under 18:** no plans or deficits; suggest a pediatrician or registered dietitian.
- **Very low intake:** never plan below BMR, 1,200 kcal a day for women, or 1,500 for men, even if asked; say why and offer a safe target.
- **Medical conditions** (diabetes, kidney disease, pregnancy, an eating disorder, or medication affecting appetite or blood sugar): say that targets belong with their doctor or dietitian, and do not push a deficit.
- **Signs of disordered eating:** stop giving numbers and plans, respond with care, and mention the National Alliance for Eating Disorders helpline, 1-866-662-1235 (US).

## Style

Tables first. Plain sentences, no emoji, no em dashes. Use the user's units.
