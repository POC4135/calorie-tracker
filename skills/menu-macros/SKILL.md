---
name: menu-macros
description: Ranks restaurant and takeout menu items by fit with remaining calories and protein, tuned for US Indian restaurants and chains. Use for menu photos, menu text, 'what should I order', or '#ct menu'.
---

# Menu Macros

Reads a menu and recommends what to order, and how to order it, so the meal fits what is left of the user's day. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Get every number from `scripts/macros.py` (Python 3, standard library). Run it as `python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command>`; `${CLAUDE_SKILL_DIR}` is this skill's folder (use its path if it is not filled in). Foods are in `references/foods.csv`; US restaurant portions start with `r-` (an entree is about 2 cups).

- `lookup "butter chicken, tandoori roti" --kind restaurant` finds restaurant rows; drop `--kind` to search home dishes too.
- `log` reads JSON on stdin and prints the order's table with today's totals:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py log <<'EOF'
{"targets": {"kcal":2400,"protein":138,"carbs":294,"fat":75,"fiber":34,"added_sugar":30,"sodium":2300},
 "prior": {"kcal":1400,"protein":90,"carbs":170,"fat":45,"fiber":20,"added_sugar":10,"sodium":1700},
 "items": [
   {"food": "r-tandoori-chicken", "label": "Tandoori chicken, half"},
   {"food": "r-tandoori-roti", "label": "Tandoori roti"},
   {"food": "r-chana-masala", "servings": 0.5, "label": "Chana masala, half (shared)"}
 ]}
EOF
```

  - Items: a database id (`food`), a fuzzy name (`query`), or your own numbers (`name`, `kcal`, `protein`, `carbs`, `fat`, optional `sodium`). Amount: `servings` or `grams`. Always set `label`.
  - Do not paste the `CHECKS` and `TODAY_JSON` lines that follow the tables.

## Workflow

1. **Menu and budget.** Take a photo, text, link, or restaurant name (with web access, search for the menu; for a chain, use its official nutrition page). Use the remaining calories and protein from macro-tracker in this chat if available; otherwise ask for them. Ask about diet type and sharing if unknown.
2. **Estimate** each plausible dish from the `r-` rows, or from the closest home dish scaled to a restaurant portion. Menu words: makhani, malai, korma, shahi, and butter mean cream and butter (highest fat); tikka masala is grilled meat or paneer in a cream sauce; kadai and jalfrezi are lighter; tandoori, tikka (dry), and kebab are grilled (lowest fat); 65, manchurian, and pakora are fried.
3. **Rank** by fit within the remaining calories, then protein per 100 kcal, then sodium.
4. **Build one order** that fits, including bread or rice, and check it with `log`.
5. **Reply:**
   1. The recommended order's tables, copied as printed.
   2. A short ranked list (Dish | Est. cal | Protein | Why), five to eight rows.
   3. Two to four ordering tips: tandoori roti instead of butter naan (saves about 180 kcal), half the rice, gravy on the side, share one rich curry.
   4. A confidence line naming the biggest unknown (usually portion or cream).

## Rules

- Only chain nutrition pages count as official; everything else is an estimate and should say so.
- One restaurant meal often reaches 2,000 mg sodium; mention it, do not lecture.
- If nothing fits, say so and give the least costly option.

## Safety

If the user shows signs of disordered eating (fear of eating, purging, distress over small amounts), stop giving numbers, respond with care, and mention the National Alliance for Eating Disorders helpline, 1-866-662-1235 (US).

## Style

Tables first. Plain sentences, no emoji, no em dashes. Use the user's units.
