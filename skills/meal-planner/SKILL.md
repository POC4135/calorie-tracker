---
name: meal-planner
description: Builds one-day or seven-day Indian meal plans that hit calorie and protein targets with US grocery staples, plus a grocery list. Use for meal plans, diet plans, weekly prep, or '#ct plan'.
license: MIT
metadata:
  author: POC4135
  version: "1.0.0"
  suite: katori
---

# Meal Planner

Builds meal plans from food the user already cooks: rotis, dal, sabzi, rice, idli, poha, curries, plus the US grocery staples that make protein targets reachable. Every day in a plan is checked against the targets by the calculator before it is shown. Everything happens in the reply; nothing is stored. Do not create files unless the user asks.

## Calculator

Do every number with `scripts/macros.py` (`python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py ...`). `${CLAUDE_SKILL_DIR}` is the folder this SKILL.md is in; if it is not filled in, use that folder's path. Formats: `references/calculator.md`. Foods and measures: `references/foods.csv`, `references/measures.csv`. Protein anchors, meal templates, batch cooking, and grocery lists: `references/planning-guide.md`.

## Workflow

1. **Targets.** Use `TARGETS_JSON` if the macro-tracker skill set targets earlier in this chat, or targets the user gives you. Otherwise collect the profile (age, sex, height, weight, activity, goal, diet type, and BMR if they have one) and run `targets`.

2. **Constraints.** Ask once, in one short message, for whatever you do not know; use the defaults in brackets if they skip it:
   - diet type [from the profile] and foods they avoid or cannot eat
   - regional style: North, South, Gujarati, Bengali, Maharashtrian, mixed [mixed]
   - one day or seven days [one day]; meals per day [3 meals and 1 snack]
   - cooking time on weekdays [30 minutes]; batch cooking on weekends [yes]
   - whether they cook for family, and workout timing [no, evening]

3. **Draft** each day from `references/planning-guide.md`: a protein anchor in every meal (25-40 g), the user's usual staples for carbs, at least two vegetable servings, and portions in household units with grams ("2 rotis (60 g atta)", "1 katori dal", "150 g tofu").

4. **Check** each day with `plan`. If the result is `PLAN_NEEDS_ADJUSTMENT`, fix the biggest miss first (usually protein or calories), adjust portions or swap one item, and run it again. Stop after three passes and report the closest version with the remaining gap stated plainly. Never show a day that was not checked. NOTE lines (sodium, fiber, added sugar) do not block a plan; mention them with a practical fix. Sodium is the usual one: typical home cooking lands at 3,000-4,000 mg, so suggest salting dal and sabzi lightly and skipping pickle, papad, and namkeen on most days.

5. **Reply** in this order:
   1. **One-day plan:** the `plan` table and its PASS or ADJUST lines, copied verbatim (omit the `PLAN_OK` line).
      **Seven-day plan:** a weekly grid (Day | Breakfast | Lunch | Snack | Dinner | Cal | Protein) built from the checked days, then the full `plan` table for one representative day.
   2. **Prep notes:** what to batch-cook and when, with storage times.
   3. **Grocery list** for the whole plan, grouped by store (Indian grocery, regular grocery, warehouse club), in US package sizes.
   4. **Swaps:** two or three like-for-like swaps that keep the macros (for example tofu bhurji instead of paneer bhurji saves about 50 kcal and adds about 6 g protein).
   5. One line on how to use it: log meals with `#ct` as they eat, and repeat the week as is or ask for a new one.

## Rules that matter

- **Realistic protein for vegetarians.** Dal and paneer alone rarely reach 1.6-1.8 g/kg inside a calorie target. Say so, and use Greek yogurt, ultra-filtered milk, tofu, soya chunks, edamame, or whey to close the gap. If the user refuses all of them, show the best achievable protein and the gap.
- **Keep it cookable.** Reuse batch-cooked dal, beans, and sabzi across days. No more than one new recipe per weekday. A seven-day plan should repeat dishes; real kitchens do.
- **Respect the household.** If the user cooks for family, plan dishes everyone eats and change portions, not menus.
- **Restaurant days.** If the user eats out on certain days, leave a calorie budget for that meal and point them to the menu-macros skill for ordering.
- **Plans are starting points.** Hunger, training, and the scale over two to three weeks decide whether calories should move. Suggest a review after two weeks of consistent logging.

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
