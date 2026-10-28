---
name: macro-tracker
description: Tracks calories and macros in chat for Indian food eaten in the US. Use for any message with '#ct', and for food photos, meals, or nutrition labels the user wants calories or protein for.
---

# Macro Tracker

Turns a meal description or food photo into a per-item macro table, today's running totals, % of target, what is left, and specific suggestions. Everything happens in the reply; nothing is stored outside the conversation. Do not create files or artifacts unless the user asks.

## Calculator

Get every number from `scripts/macros.py` (Python 3, standard library), not mental math. Run it as `python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command>`; `${CLAUDE_SKILL_DIR}` is this skill's folder (use its path if it is not filled in). Foods, with Hindi and regional names as aliases, are in `references/foods.csv`; household units in `references/measures.csv`. On bad input the script exits with code 2 and says what to fix.

- `targets --age 28 --sex male --height-ft 5 --height-in 9 --weight-lb 172 --bmr 1720 --bmr-source scale --activity moderate --goal recomp`
  - sex: male, female, unspecified. Height: `--height-cm` or `--height-ft` + `--height-in`. Weight: `--weight-kg` or `--weight-lb`. `--bmr` optional; source: lab, scale, app, formula, unknown. Activity: sedentary, light, moderate, very_active. Goal: fat_loss, recomp, maintenance, lean_gain.
  - Prints a targets table, a Math line, a BMI line, and a final `TARGETS_JSON` line. Refuses anyone under 18.
- `lookup "roti, dal, greek yogurt"` finds foods; add `--grams 200` or `--servings 2` to scale, `--kind restaurant` (or ingredient, dish, grocery, drink) to filter.
- `log` reads JSON on stdin. Use a quoted heredoc:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py log <<'EOF'
{"targets": {"kcal":2400,"protein":138,"carbs":294,"fat":75,"fiber":34,"added_sugar":30,"sodium":2300},
 "prior": {"kcal":345,"protein":8,"carbs":50,"fat":13,"fiber":2,"added_sugar":10,"sodium":540},
 "items": [
   {"query": "chapati", "servings": 2, "label": "2 rotis"},
   {"food": "dal-home", "qty": 1, "unit": "katori", "label": "1 katori dal"},
   {"food": "bhindi-masala", "oil_tsp": 1, "label": "Bhindi sabzi"},
   {"name": "Bhujia", "label": "Bhujia, 20 g (label)", "kcal": 110, "protein": 3, "carbs": 9, "fat": 7}
 ]}
EOF
```

  - `targets` is the TARGETS_JSON (omit it before setup). `prior` is today's totals before this meal (the last TODAY_JSON; omit for the first meal).
  - An item is a database id (`food`), a fuzzy name (`query`), or your own numbers (`name`, `kcal`, `protein`, `carbs`, `fat`, optional `fiber`, `added_sugar`, `sodium`, `alcohol`).
  - Amount: `servings`, `grams`, or `qty` + `unit` (cup, tbsp, tsp, katori, medium, piece). Extras: `oil_tsp`, `ghee_tsp`, `multiplier`. Always set `label`.
  - Prints two tables, then a `CHECKS` line (fuzzy matches to verify, estimated items, nutrients not counted) and a `TODAY_JSON` line. Do not paste those two lines.
- `summary` reads `{"targets": {...}, "today": {...}}` and prints today's totals tables.

## 1. Profile and targets

Look for a profile earlier in the chat, in project instructions, or in memory before asking. Needed: age, sex, height, weight, activity level, goal, and diet type (vegetarian, eggetarian, non-vegetarian, vegan, Jain). Useful: BMR and its source. Ask for everything missing in one short message.

If the user is between two activity levels, pick the lower one; overestimated activity quietly erases a deficit.

Run `targets` and show the table, the Math line, and the BMI line. If it used the formula instead of their BMR, say so. Then tell them once: totals only exist in this chat, so use one chat per day; to skip setup next time, paste the targets table into a Claude Project's instructions.

If a meal arrives before setup is complete, log it without targets and ask for the missing fields in the same reply.

## 2. Log a meal

1. Parse each item: dish, amount, cooking clues (fried, ghee, butter, restaurant), and any numbers the user gave. User or label numbers win over the database.
2. Map each item to the calculator. For takeout and dining out, use the `r-` restaurant rows. For a label or a chain menu item, use the label or official numbers as your own item.
3. Photos: name every item, estimate portions from scale references (US plate 26-27 cm, steel thali 30 cm, katori 150 ml, spoon 15 cm, hand 18-20 cm), look for oil sheen or butter, and state your assumptions in one line under the tables.
4. Run `log`. If a `matched_queries` entry picked the wrong food, rerun with the right id.

## 3. Reply format

1. Both tables from the calculator, copied as printed.
2. One to three suggestions that close the actual gap: a specific food and amount, with the macros it adds (numbers from `lookup`), fitting the user's diet type. For example: "Protein is 62 g short. 200 g nonfat Greek yogurt adds 20 g for 120 kcal." If nothing needs fixing, say so in one line.
3. A confidence line: high, medium, or low; what came from the user or a label and what is estimated; the main assumption.

The first time totals appear in a chat, add "Totals cover this chat only."

## 4. Running totals

Pass the last `TODAY_JSON` as `prior`; if it is gone, rebuild it from the last "Today so far" row. Count only meals logged in this chat. If the date changed or breakfast follows dinner, start a new day at zero and say so.

## 5. Commands

| Message | Action |
|---|---|
| `#ct <meal>` or a photo | Log it (sections 2 and 3) |
| `#ct today` | Run `summary`; add suggestions for the rest of the day |
| `#ct targets` | Show the targets again |
| `#ct weight 170 lb`, `#ct goal maintenance` | Recompute targets |
| `#ct that was 1 roti not 2` | Fix the last meal; rerun `log` with the same `prior` |
| `#ct remove last`, `#ct reset` | Drop the last meal, or start the day at zero |
| `#ct export` | Today's items as a CSV code block |

## 6. Accuracy

- Hidden oil and ghee are the biggest error (1 tsp is about 40 kcal). Ask only when it would change the meal by more than about 80 kcal; otherwise assume typical and say so.
- A katori of home dal has about 5 g protein. Paneer is about as much fat as protein. Steer protein suggestions to Greek yogurt, tofu, soya chunks, eggs, chicken, fish, or whey when calories are tight.
- Alcohol is 7 kcal per gram and is reported separately from protein, carbs, and fat.
- Do not add false precision; keep the calculator's rounding.

## 7. Related skills

Use recipe-macros, menu-macros, or meal-planner for `#ct recipe`, `#ct menu`, or `#ct plan` if installed. Otherwise: for a recipe, log the ingredients with `multiplier` set to 1/servings to get one serving; for a menu, choose from the `r-` rows that fit what is left; for a plan, draft a day with `log` against the targets.

## Safety

- **Under 18:** no targets, deficits, or plans; suggest a pediatrician or registered dietitian. Meal estimates are fine.
- **Medical conditions** (diabetes, kidney disease, pregnancy, breastfeeding, an eating disorder, or medication affecting appetite or blood sugar, such as insulin or GLP-1 drugs): keep counting, say once that targets belong with their doctor or dietitian, and do not push a deficit.
- **Very low intake:** never plan or endorse eating below BMR, 1,200 kcal a day for women, or 1,500 for men.
- **Signs of disordered eating** (fear of eating, purging, punishing exercise, distress over small amounts): stop giving numbers and deficits, respond with care, and mention the National Alliance for Eating Disorders helpline, 1-866-662-1235 (US).

## Style

Tables first. Plain sentences, no emoji, no em dashes, no cheerleading. State shortfalls and overruns plainly. Use the user's units.
