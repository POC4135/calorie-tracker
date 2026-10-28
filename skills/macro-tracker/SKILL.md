---
name: macro-tracker
description: Tracks calories and macros in chat for Indian food eaten in the US. Use for any message with '#ct', and for food photos, meals, or nutrition labels the user wants calories or protein for.
license: MIT
metadata:
  author: POC4135
  version: "1.0.0"
  suite: katori
---

# Macro Tracker

Turns a meal description or food photo into a per-item macro table, today's running totals, % of target, what is left, and specific suggestions. Everything happens in the reply. Nothing is stored outside the conversation: no files, database, dashboard, or mood tracking. Do not create artifacts or files unless the user asks.

Built for a predominantly Indian diet in the US (home food, Indian groceries, US restaurants and chains), and works for any food.

## Calculator

Do every number with `scripts/macros.py`, not mental math; long tables are where arithmetic slips happen. Run it as `python3 ${CLAUDE_SKILL_DIR}/scripts/macros.py <command>`. `${CLAUDE_SKILL_DIR}` is the folder this SKILL.md is in; if it is not filled in, use that folder's path. Command and JSON formats: `references/calculator.md`. The food database is `references/foods.csv` (about 350 Indian, US grocery, US restaurant and drink items, with Hindi and regional names as aliases); household measures such as cups, katoris, and "1 medium onion" are in `references/measures.csv`.

If you truly cannot run code, read `references/foods.csv` directly, compute carefully, and add "computed without the calculator" to the confidence line.

## 1. Set up the profile

Targets need a profile. Look for one earlier in this chat, in project instructions, or in memory before asking.

Needed: age, sex, height, weight, activity level, goal, and diet type. Useful: BMR and where it came from (lab test, smart scale, app), foods they avoid, and their regional cuisine. People often open with age, weight, height, and BMR; ask for everything else that is missing in one short message, then proceed.

- Activity: sedentary (desk job, little exercise), light (1-3 workouts a week or 6-8k steps), moderate (3-5 workouts or 8-12k steps), very active (6-7 hard sessions or a physical job). If the user is between two levels, pick the lower one, because overestimated activity quietly erases a deficit.
- Goal: fat loss, recomposition, maintenance, or lean gain.
- Diet type: vegetarian, eggetarian, non-vegetarian, vegan, or Jain. This drives every protein suggestion.
- Sex: male or female for the formula. If they prefer not to say, use `unspecified`.

Run `targets` (see `references/calculator.md`). Show the targets table, the "Math" line, and the BMI line from the output. Keep `TARGETS_JSON` for later calls; do not paste it. If the calculator says it used Mifflin-St Jeor instead of their BMR, relay that note.

Then tell the user, once: totals only exist inside this chat, so use one chat per day; to skip setup next time, paste the targets table into a Claude Project's instructions and log inside that project.

If a meal arrives before setup is complete, log it without targets (omit `targets` in the payload) and ask for the missing fields in the same reply.

## 2. Log a meal

1. **Parse** each item: dish, quantity and unit, cooking clues (fried, tadka, ghee, butter, restaurant, takeout), and any numbers the user gave. User-given calories or label values win over the database.
2. **Map** each item to the calculator:
   - A common food: `{"query": "bhindi sabzi", ...}` or the exact `food` id if you know it.
   - A label, a chain menu item, or a dish not in the database: an explicit item with your best estimate of kcal, protein, carbs, and fat, built from the closest database rows (`lookup`) and `references/estimation-guide.md`.
   - Extra fat you can see or the user mentions: `oil_tsp` or `ghee_tsp` on that item.
   - Always set `label` to what the user would call it, with the portion ("2 rotis (80 g)", "1 katori dal").
3. **Photos:** follow section 4 of `references/estimation-guide.md`.
4. **Run** `log` with `targets` and `prior` (today's totals before this meal).
5. **Check** the `CHECKS` line before replying. If a `matched_queries` entry picked the wrong food, rerun with the right id. Items listed in `estimated_items` and `nutrients_not_counted` feed the confidence line.

## 3. Reply format

Every meal log uses exactly this order:

1. **Table 1 and Table 2** from the calculator output, copied verbatim (targets are in the column headers so every number reads against its target). Leave out the `CHECKS` and `TODAY_JSON` lines.
2. **One to three suggestions** that close the actual gap. Each names a specific food and amount, with the macros it adds, sized to what is remaining and fitting the user's diet type. Pull the numbers from `lookup`, not from memory. Prefer foods an Indian household in the US can buy easily (Greek yogurt, ultra-filtered milk, paneer, tofu, soya chunks, eggs, chicken, fish, whey, sprouts, edamame, chickpeas). The right shape:
   - "Protein is 62 g short. 200 g nonfat Greek yogurt with dinner adds 20 g protein for 120 kcal, which still fits."
   - "You have 350 kcal and 40 g protein left. Swap the second roti for 100 g grilled chicken breast: +27 g protein for about 60 kcal more."
   - "Sodium is already near 2,100 mg from takeout. Skip the achar and papad tonight."
   If nothing needs fixing, say so in one line and skip suggestions.
3. **Confidence line:** high, medium, or low; which values came from the user or a label and which are estimates; the main assumption (for example "assumed no ghee on rotis").

The first time totals appear in a chat, add: "Totals cover this chat only."

## 4. Running totals

- Pass the `TODAY_JSON` from the previous log in this chat as `prior`. If you cannot find it, rebuild it from the last reply's "Today so far" row and secondary table.
- Count only meals logged in this conversation. Never invent meals from other chats.
- New day: if the date changed since the last log, or the user logs breakfast after dinner, start from zero and say "Starting a new day." If it is genuinely unclear, ask in the same reply.

## 5. Commands

| Message | What to do |
|---|---|
| `#ct <meal>` or `#ct` + photo | Sections 2 and 3 |
| `#ct today` | Run `summary` with `TODAY_JSON`; show both tables and suggestions for the rest of the day |
| `#ct targets` | Show the targets table again |
| `#ct weight 170 lb`, `#ct goal maintenance`, `#ct activity light` | Recompute targets and show the new table and what changed |
| `#ct that was 1 roti not 2`, `#ct actually 400 cal` | Fix the last meal, rerun `log` with the same `prior` it used, show the full tables |
| `#ct remove last` | Drop the last meal; today's totals go back to that meal's `prior` |
| `#ct reset` | Start today's totals at zero |
| `#ct export` | Today's logged items as a CSV code block (date, meal, item, kcal, protein, carbs, fat, fiber, added sugar, sodium) for pasting into a spreadsheet |
| `#ct what should I eat for dinner?` | Use today's remaining macros; give 2-3 specific Indian or US-available options with their macros from `lookup` |

## 6. Accuracy rules

- Hidden oil and ghee are the biggest error. Ask about ghee on rotis or rice only when it changes the meal by more than about 80 kcal; otherwise assume typical and say so.
- A katori of home dal is about 5 g protein. Do not let dal carry a protein target.
- Paneer is roughly as much fat as protein by weight; when calories are tight, steer protein suggestions to leaner sources.
- US restaurant portions are large: use the `r-` restaurant rows for takeout and dining out.
- For US chains, the official nutrition calculator beats any estimate; search for it when web search is available.
- Do not show false precision. The calculator rounds items to 5 kcal and whole grams; keep that.

## 7. Other Katori skills

If the matching skill is installed, hand off to it; otherwise handle a basic version here:

- A batch recipe with ingredient amounts (`#ct recipe`): **recipe-macros**. Basic version: run `recipe`, then log one serving with `LOG_ITEM_JSON`.
- A restaurant menu or "what should I order" (`#ct menu`): **menu-macros**. Basic version: pick 3 options from the `r-` rows that fit the remaining macros.
- A meal plan or diet plan (`#ct plan`): **meal-planner**. Basic version: draft one day and check it with `plan`.

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
