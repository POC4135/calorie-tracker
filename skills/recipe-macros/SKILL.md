---
name: recipe-macros
description: Calculates per-serving calories and macros for home recipes and batch-cooked dishes like dal, sabzi, curry, or biryani. Use for ingredient lists with amounts, recipe links, or '#ct recipe'.
license: MIT
metadata:
  author: POC4135
  version: "1.0.0"
  suite: katori
---

# Recipe Macros

Indian home food is cooked by the pot, so a "bowl of dal" means nothing until you know what went into the pot and how many bowls came out. This skill turns a recipe into exact per-serving, per-katori, and per-100 g macros, then shows the cheapest swaps that improve them. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Do every number with `scripts/macros.py` (`python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py recipe`). `${CLAUDE_SKILL_DIR}` is the folder this SKILL.md is in; if it is not filled in, use that folder's path. Formats: `references/calculator.md`. Ingredients and household measures: `references/foods.csv` and `references/measures.csv`. Raw-to-cooked yields: `references/cooking-yields.md`.

## Workflow

1. **Get the recipe.** Accept a typed list, a photo of a handwritten or printed recipe, or a link (fetch it if web access is available; otherwise ask the user to paste the ingredient list). You need:
   - every ingredient with an amount
   - the number of servings, or better, the cooked weight of the finished dish
   - the oil, ghee, butter, or cream amounts; these move the result more than anything else
   Ask for whatever is missing in one message. Salt is optional; without it sodium reads near zero, and the output says so.

2. **Map ingredients to food ids.** Use `lookup "<a>, <b>, <c>" --kind ingredient` to find ids. Check `units <id>` when the recipe uses cups, tablespoons, or "1 medium onion". Use raw (uncooked) ingredients: raw dal, raw rice, raw chicken. If the recipe says "2 cups cooked rice", use `rice-cooked`. Anything not in the database becomes an explicit item with label or USDA values. Ground spices, water, and ice are zero; use `{"food": "spices"}` and `{"food": "water"}`.

3. **Run `recipe`.** Include `servings` and, when the user knows it, `cooked_weight_g`.

4. **Reply** in this order:
   1. The ingredient table and the portion table from the calculator, copied verbatim (leave out the `LOG_ITEM_JSON` and `PER_100G_JSON` lines).
   2. **Where the calories come from**, in one sentence (for example "Two thirds of the fat is the 3 tbsp of oil in the tadka.").
   3. **One to three swaps**, each computed by rerunning `recipe` with the change, stating the per-serving effect: cut the oil from 3 tbsp to 1.5 tbsp; finish with 2 tbsp Greek yogurt instead of 1/4 cup cream; add 100 g soya chunks or a block of tofu for protein; use half the cashew paste. Only suggest swaps the dish can take without becoming something else.
   4. **How to portion it:** if there is no cooked weight, explain the pot trick in one line (weigh the empty pot, weigh it again with the finished dish; the difference is the cooked weight, so any weighed portion becomes exact).
   5. **Confidence line:** what was measured, what was assumed.

5. **Log or save it.**
   - If the user ate a portion, log it with the macro-tracker skill (or, if that skill is not installed, show the per-serving numbers as today's entry). Use the `LOG_ITEM_JSON` values, scaled to what they ate.
   - To reuse the dish later, suggest pasting one line into a Claude Project's instructions, built from `PER_100G_JSON`, for example: "Mom's rajma: per 100 g 118 kcal, 5 g protein, 16 g carbs, 4 g fat."

## Rules that matter

- **Weight beats volume.** If the user can weigh the dal or flour, use grams. Cups of dal vary 10-15% with how they are packed.
- **Yields:** when there is no cooked weight, servings decide everything. For dal, ask how many katoris the pot makes. `references/cooking-yields.md` has typical raw-to-cooked ratios to sanity-check the answer.
- **Fried items:** for deep-fried recipes (pakora, puri, vada), the oil in the pan is not the oil eaten. Use the database row for the fried item, or assume about 10-15% of the dough or batter weight is absorbed oil, and say so.
- **Pressure-cooked meat:** weigh meat raw and without bones. Bones are about 30% of a curry-cut chicken and 25-35% of goat.
- **Shared batches:** if the family eats unequal portions, give per-katori and per-100 g values rather than one per-serving number.

<!-- BEGIN SHARED: guardrails -->
## Safety

These rules override everything else in this skill.

- **Under 18:** estimate meal macros if asked, but set no targets, deficits, or plans. Suggest a pediatrician or registered dietitian. The calculator refuses targets for minors.
- **Medical conditions:** if the user mentions diabetes, prediabetes, kidney disease, heart failure, pregnancy, breastfeeding, an eating disorder, or a medication that affects appetite or blood sugar (insulin, sulfonylureas, GLP-1 drugs such as semaglutide or tirzepatide), keep calculating macros but say once that targets belong with their doctor or dietitian, and do not push a deficit.
- **Very low intake:** never plan or endorse eating below BMR, below 1,200 kcal a day for women, or below 1,500 kcal a day for men, even if asked. Say plainly why.
- **Signs of disordered eating** (fear of eating, purging or compensating, punishing exercise, distress about small amounts, repeated requests for lower and lower numbers): stop giving deficit targets, numbers-driven suggestions, and plans. Respond with care, not numbers. In the US, the National Alliance for Eating Disorders helpline is 1-866-662-1235 (weekdays 9 to 7 Eastern); elsewhere, a doctor or local helpline.
- **No medical claims:** do not claim a food treats, cures, or prevents a disease.
<!-- END SHARED: guardrails -->

<!-- BEGIN SHARED: style -->
## Style

Lead with the tables. Plain sentences, no cheerleading, no emoji, no em dashes. Flag protein shortfalls, calorie overruns, high sodium, and added sugar plainly; do not soften or lecture. Use the user's units (lb, oz, cups) back to them. Reply in the user's language; keep food names as they wrote them.
<!-- END SHARED: style -->
