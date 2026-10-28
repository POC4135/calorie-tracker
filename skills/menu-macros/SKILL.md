---
name: menu-macros
description: Ranks restaurant and takeout menu items by fit with remaining calories and protein, tuned for US Indian restaurants and chains. Use for menu photos, menu text, 'what should I order', or '#ct menu'.
license: MIT
metadata:
  author: POC4135
  version: "1.0.0"
  suite: katori
---

# Menu Macros

Eating out is where a good tracking day usually falls apart: a US Indian restaurant entree runs 700-1,000 kcal before rice and naan. This skill reads a menu and tells the user what to order, and how to order it, so the meal fits what is left of their day. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Do every number with `scripts/macros.py` (`python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py ...`). `${CLAUDE_SKILL_DIR}` is the folder this SKILL.md is in; if it is not filled in, use that folder's path. Formats: `references/calculator.md`. US restaurant rows in `references/foods.csv` start with `r-` (`lookup "<dish>" --kind restaurant`). Menu vocabulary, ranking method, and ordering scripts: `references/restaurant-guide.md`. Portions and hidden fat: `references/estimation-guide.md`. Household measures: `references/measures.csv`.

## Workflow

1. **Get the menu and the budget.**
   - Menu: a photo, pasted text, a link, or just the restaurant name. With only a name and web access, search for the menu; for a chain, search for its official nutrition page, which beats any estimate.
   - Budget: the remaining calories and protein. If the macro-tracker skill has run in this chat, use its `TARGETS_JSON` and latest `TODAY_JSON`. Otherwise ask for the numbers, or for a rough budget ("about 800 kcal left, need protein").
   - Context worth one question if unknown: diet type, and whether dishes are shared and by how many.

2. **Estimate each plausible dish.** Use the `r-` row when there is one. Otherwise build the estimate from the closest home dish row scaled to a restaurant portion, using the menu decoder in `references/restaurant-guide.md` (makhani, malai, korma, shahi mean cream and butter; tandoori and tikka mean grilled; 65 and manchurian mean fried). Skip items that clearly do not fit the user's diet type.

3. **Rank** with the method in `references/restaurant-guide.md`: fit within the calorie budget first, then protein per 100 kcal, then sodium and fiber.

4. **Build one recommended order** that fits the budget, including bread or rice choices and sides, and check it with `log` (pass `prior` so the result shows where the day lands). If the budget is tight, show a strict option and a relaxed one.

5. **Reply** in this order:
   1. **Recommended order** with the `log` tables, copied verbatim (no machine lines).
   2. **Ranked shortlist** table: Dish | Est. cal | Protein | Why (one short reason). Five to eight rows across "Best picks", "Fine with tweaks", and "Save for another day".
   3. **How to order it:** two to four specific requests from the ordering scripts (gravy on the side, tandoori roti instead of butter naan, half the rice, extra raita or salad, share one rich entree).
   4. **Confidence line:** restaurant estimates are usually medium confidence; say so, and name the largest unknown (portion size, cream).

6. **After the meal,** if the user says what they actually ate, log it with the macro-tracker skill, or with `log` directly if that skill is not installed.

## Rules that matter

- Never present an estimate as a restaurant's official number. Only chain nutrition pages count as official.
- Portion is the biggest variable. If the user can see the food, ask what share of the container they ate.
- Do not moralize about eating out. Give the best option inside the budget, or say plainly that nothing on the menu fits and what the least-bad choice costs.
- Sodium from one restaurant meal often reaches 2,000 mg. Mention it when it does; do not lecture.

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
