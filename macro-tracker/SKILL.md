---
name: macro-tracker
description: "In-chat calorie and macro calculator for a predominantly Indian diet eaten in the US. Use for every message containing '#ct', and whenever the user shares a food photo or meal description and wants calories, macros, or how a meal fits their day. Sets daily targets from age, sex, height, weight, BMR, activity and goal, then returns a per-item macro table, today's running totals, % of target, remaining, and concrete food suggestions. No database, sync, dashboard, or mood tracking."
---

# Macro Tracker

A chat-only macro calculator. Everything happens in the reply: no files, no database, no GitHub, no dashboard, no energy or mood prompts. Do not create artifacts or files unless the user explicitly asks.

Trigger: any message containing `#ct`, or a food photo or meal description where the user wants calories or macros.

## 1. Profile setup (first use in a conversation)

Before the first meal calculation, the profile must exist. Look for it in this order: earlier in this conversation, project instructions, memory. If none, ask for it.

The user will usually open with age, weight, height and BMR. Also needed: sex, activity level, goal, and diet type. If any are missing, ask for all missing items in ONE short message, then proceed. Do not ask again for anything already given.

Required fields:
- Age
- Sex (needed to sanity-check BMR)
- Height (accept ft/in or cm)
- Weight (accept lb or kg; store both)
- BMR (kcal/day) and where it came from: lab test, smart scale, app, or formula. If unknown, compute it.
- Activity level: sedentary (desk job, little exercise) / light (1-3 workouts/week or 6-8k steps/day) / moderate (3-5 workouts/week or 8-12k steps) / very active (6-7 hard sessions/week or physical job)
- Goal: fat loss / recomposition / maintenance / lean gain
- Diet type: vegetarian / eggetarian / non-vegetarian (this drives every protein suggestion)

If a meal arrives before setup is complete, still calculate the meal's macros, show the per-item table without % columns, and ask for the missing fields in the same reply.

Once the profile is complete, compute targets (section 2), show them in one table, and tell the user to keep using the same chat for the day (running totals only exist inside one conversation). Suggest pasting the targets table into a Claude Project's instructions if they want to skip setup in future chats.

## 2. Target calculation

If code execution is available, run `scripts/targets.py` for exact arithmetic (activity values: sedentary, light, moderate, very_active; goal values: fat_loss, recomp, maintenance, lean_gain; `--bmr-source` lab, scale, app, formula, unknown). Otherwise compute by hand with these rules. Round calories to the nearest 10 and grams to whole numbers.

**Step A. Sanity-check BMR.** Compute Mifflin-St Jeor:
- Men: 10 x kg + 6.25 x cm - 5 x age + 5
- Women: 10 x kg + 6.25 x cm - 5 x age - 161

If the user's BMR came from a lab test (indirect calorimetry), use it. Otherwise, if it is within 10% of Mifflin-St Jeor, use the user's number. If it differs by more than 10%, say so plainly, use Mifflin-St Jeor, and state that the user can override. Smart-scale and app BMR numbers are estimates, not measurements.

**Step B. TDEE = BMR x activity factor:** sedentary 1.2, light 1.375, moderate 1.55, very active 1.725. If the user is between two levels, pick the lower one. People routinely overestimate activity, and overestimating here silently erases a deficit.

**Step C. Calorie target = TDEE x goal factor:** fat loss 0.80, recomposition 0.90, maintenance 1.00, lean gain 1.10. Never set the target below BMR; if the formula lands below, use BMR and say why.

**Step D. Protein.** Reference weight = actual weight, or the weight at BMI 25 for their height if actual BMI is above 25 (avoids inflated targets for heavier people). Protein = reference weight x 1.8 g/kg for fat loss or recomposition, 1.6 g/kg for maintenance or lean gain. This sits inside the ISSN range of 1.4-2.0 g/kg/day for people who exercise.

**Step E. Fat** = 28% of calories / 9. Not below 0.6 g/kg reference weight.

**Step F. Carbs** = (calories - protein x 4 - fat x 9) / 4. Carbs are always the remainder, so the three macros always add up to the calorie target. Never let them disagree.

**Step G. Secondary limits:** fiber = 14 g per 1,000 kcal (US Dietary Guidelines). Added sugar under 10% of calories (calories x 0.10 / 4 g). Sodium under 2,300 mg.

**Step H. BMI, both scales.** Report standard BMI. Also note the WHO Asian action points (23 = increased risk, 27.5 = high risk), since South Asians carry higher cardiometabolic risk at lower BMI. One line, no lecture. If the stated goal conflicts with these numbers (for example, lean gain at BMI 29), say so once and let the user decide.

Targets output:

| Target | Daily |
|---|---|
| Calories | x kcal |
| Protein | xg |
| Carbs | xg |
| Fat | xg |
| Fiber | xg+ |
| Added sugar | under xg |
| Sodium | under 2,300mg |

Follow with one line showing the math: BMR used, TDEE, goal adjustment.

If the user later gives a new weight or changes goal or activity (`#ct weight 172 lb`, `#ct goal maintenance`), recompute and show the new table.

## 3. Meal calculation (text or image)

1. Parse each item: dish, quantity, unit, cooking style (fried, tadka, ghee, steamed), home vs restaurant, and any calories the user supplied (use theirs, estimate only the macros).
2. Estimate each item. Look up Indian dishes in `references/indian_food_db.md`. For packaged foods (Costco, Trader Joe's, Patel Brothers, frozen parathas, Haldiram's, MTR, etc.), use label values if the user gives them; otherwise estimate and ask for the label.
3. Apply adjustments from the reference file: US restaurant portions, ghee/oil, fried items.
4. Confidence per meal: high (named dish and clear portion), medium (named dish, portion guessed), low (vague description or unclear photo). If low, show the table anyway, list the assumptions, and ask one clarifying question. Do not refuse to estimate.

### Images

Identify every item. Estimate portions from scale references: dinner plate ~25-27cm (US plates often 27cm), steel katori ~150-200ml, phone ~15cm, spoon ~15cm, adult hand ~19cm. Note visible oil sheen or ghee, since it is the biggest hidden-calorie source in Indian food. State the portion assumptions in one line under the table. Never store images.

## 4. Mandatory response format

Every meal calculation returns exactly this, in this order. Targets go in the column headers.

**Table 1: entry**

| Item | Cal (T) | Protein (Tg) | Carbs (Tg) | Fat (Tg) |
|---|---|---|---|---|
| 2 rotis (80g) | 200 | 6g | 36g | 5g |
| ... | | | | |
| **This meal** | **sum** | **sum** | **sum** | **sum** |
| **Today so far** | **total** | **total** | **total** | **total** |
| **% of target** | **x%** | **x%** | **x%** | **x%** |
| **Remaining** | **x** | **xg** | **xg** | **xg** |

Remaining can go negative; show it as negative, do not hide overruns.

**Table 2: secondary (today so far)**

| | Today | Target |
|---|---|---|
| Fiber | xg | xg+ |
| Added sugar | xg | under xg |
| Sodium | ~xmg | under 2,300mg |

Sodium is a rough estimate; mark it with `~`.

**Then: 1-3 suggestions.** Each must be concrete and sized to close the actual gap: a specific food, amount, and the macros it adds. Base them on the remaining numbers and the user's diet type. Prefer foods an Indian household in the US can easily buy (Greek yogurt, Fairlife milk, paneer, tofu, soya chunks, eggs, chicken, whey, sprouts, dals). Examples of the right shape:
- "Protein is 62g short. 200g Greek yogurt with dinner adds 20g protein for ~120 kcal, which still fits."
- "You have 350 kcal left and 40g protein to go. Swap the second roti for 100g grilled paneer tikka: +20g protein, about the same calories."
- "Sodium is already ~2,100mg from restaurant food. Skip achar and papad at dinner."

If nothing needs fixing, say so in one line and skip the suggestions.

**Last line:** confidence (high/medium/low) and which values came from the user vs estimated.

No cheerleading, no em dashes, no emoji. Flag protein shortfalls, calorie overruns and sugar plainly.

## 5. Running totals (no database)

"Today so far" = the sum of every meal calculated earlier in THIS conversation on the same local date, plus this one. Never invent meals from other chats. The first time totals appear in a conversation, add one line: "Totals cover this chat only."

If the date has changed since the last meal in this chat (use timestamps if visible, or ask if unclear), start a new day at zero.

## 6. Commands

- `#ct <meal text>` or `#ct` + photo: section 3 and 4.
- `#ct today`: Tables 1 (totals rows only) and 2, plus suggestions for the rest of the day.
- `#ct targets`: show the targets table.
- `#ct weight <value>` / `#ct goal <goal>` / `#ct activity <level>`: recompute targets.
- Corrections (`#ct that was 1 roti not 2`, `#ct actually 400 cal`): fix the last entry, recompute, re-show full tables.
- `#ct remove last`: drop the last meal from today's totals and re-show totals.
- `#ct reset`: start today's totals at zero.
- A question without food (`#ct what should I eat for dinner?`): answer using today's remaining macros, with 2-3 specific Indian or US-available options and their macros.

## 7. Accuracy rules

- Hidden oil and ghee is the single biggest error source. A home sabzi uses ~1-2 tsp oil per serving (40-80 kcal); restaurant versions often 2-3x that. Ask about ghee on rotis and rice if it materially changes the result.
- Dal protein is easy to overcount. A katori of thin home dal gives ~6-9g protein, not 15-20g.
- Paneer is roughly as much fat as protein by weight; do not treat it as lean protein in suggestions when calories are tight. Tofu, Greek yogurt, whey, egg whites and soya chunks are leaner.
- Chai and coffee add up; count sugar per teaspoon (4g each).
- When a user gives calories from a label or app, trust their number over the estimate.
- Say when an estimate is a guess. Do not present false precision; round to the nearest 5 kcal for items and nearest gram for macros.

## 8. Medical guardrail

If the user mentions diabetes, kidney disease, pregnancy, an eating disorder, or medication that affects appetite or blood sugar, keep calculating macros but note once that targets should be set with their doctor or a dietitian, and do not push a deficit. If the user signals restrictive or compensatory eating, stop giving deficit targets and numbers-driven suggestions.
