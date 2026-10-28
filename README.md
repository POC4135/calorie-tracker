# macro-tracker

A Claude skill that calculates calories and macros in chat for a predominantly Indian diet eaten in the US. Describe a meal or send a photo with `#ct`, and Claude returns a per-item macro table, today's running totals, % of target, what's remaining, and 1-3 specific food suggestions to close the gap.

No database, no sync, no dashboard. Everything lives in the chat.

## Install (claude.ai)

Requires a Pro, Max, Team or Enterprise plan.

1. Download `macro-tracker.skill` from this repo. It is a zip file; if the upload dialog will not accept it, rename it to `macro-tracker.zip`.
2. In Claude, go to Settings > Capabilities and turn on **Code execution and file creation**.
3. In the Skills section, click **Upload skill** and choose the zip.
4. Toggle the skill on.

## First use

Start a chat with something like:

```
#ct setup: 28, male, 5'9", 172 lb, BMR 1720 from my smart scale,
moderately active, goal recomposition, vegetarian
```

Claude will check your BMR against the Mifflin-St Jeor formula, compute targets, and show them. Missing details get asked for in one message.

## Daily use

```
#ct 2 rotis, 1 katori dal, bhindi sabzi
#ct [photo of your plate]
#ct takeout: half a paneer tikka masala and 1 garlic naan
#ct today
#ct that was 1 roti not 2
#ct remove last
#ct weight 170 lb
#ct what should I eat for dinner?
```

## How targets are set

- BMR: yours if lab-measured or within 10% of Mifflin-St Jeor; otherwise Mifflin-St Jeor (you can override)
- TDEE = BMR x activity (1.2 / 1.375 / 1.55 / 1.725)
- Calories = TDEE x goal (fat loss 0.80, recomp 0.90, maintain 1.00, lean gain 1.10), never below BMR
- Protein = 1.8 g/kg (fat loss, recomp) or 1.6 g/kg, using weight at BMI 25 if you are above it
- Fat = 28% of calories; carbs = the remainder, so macros always add up to the calorie target
- Fiber 14 g per 1,000 kcal, added sugar under 10% of calories, sodium under 2,300 mg
- BMI shown with the WHO Asian action points (23 and 27.5)

## Limits you should know

- **Running totals only exist within one chat.** Use one chat per day. To skip setup each time, put your targets table in a Claude Project's instructions and log inside that project.
- **Estimates, not measurements.** Photo estimates can be off by 20-30%, mostly from hidden oil and ghee. Weighing food or giving label values tightens this a lot.
- **Not medical advice.** If you have diabetes, kidney disease, are pregnant, or take medication that affects appetite or blood sugar, set targets with a doctor or dietitian.

## Repo layout

```
macro-tracker.skill          # packaged skill (zip) to upload
macro-tracker/
  SKILL.md                   # instructions Claude follows
  references/indian_food_db.md
  scripts/targets.py         # target calculator
```
