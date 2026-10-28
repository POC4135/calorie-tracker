# Methodology

How Katori sets targets, where its food values come from, and how they are checked. Every constant below lives in `shared/scripts/macros.py` with a comment.

## Contents

1. Daily targets
2. Food database
3. Calculator rules
4. Quality checks
5. Known limitations
6. Sources

## 1. Daily targets

| Step | Rule | Why |
|---|---|---|
| BMR | Your BMR if it was lab-measured, or if it is within 10% of Mifflin-St Jeor. Otherwise Mifflin-St Jeor, with a note you can override. | Mifflin-St Jeor is the most accurate common equation in reviews, yet it still misses by more than 10% for roughly a third of people. Smart-scale and app BMRs are themselves estimates, so a large disagreement usually means the device is off. |
| Mifflin-St Jeor | Men 10 x kg + 6.25 x cm - 5 x age + 5; women the same with -161; "unspecified" uses the midpoint (-78). | |
| TDEE | BMR x 1.2 sedentary, 1.375 light, 1.55 moderate, 1.725 very active | Standard activity factors. People overestimate activity, so the skill picks the lower level when unsure. |
| Calories | TDEE x 0.80 fat loss, 0.90 recomposition, 1.00 maintenance, 1.10 lean gain; never below BMR | Moderate changes that are sustainable; the BMR floor prevents crash targets. |
| Protein | 1.8 g/kg for fat loss and recomposition, 1.6 g/kg otherwise | Inside the ISSN's 1.4-2.0 g/kg for people who exercise; the 2025-2030 US Dietary Guidelines suggest 1.2-1.6 g/kg for adults. |
| Reference weight | Actual weight, or the weight at BMI 25 if BMI is above 25 | Sizing protein from total weight overshoots for heavier people. |
| Fat | 28% of calories, at least 0.6 g/kg | Inside the 20-35% Acceptable Macronutrient Distribution Range. |
| Carbs | The remainder: (calories - 4 x protein - 9 x fat) / 4 | The three macros always add up to the calorie target. |
| Fiber | 14 g per 1,000 kcal | National Academies Adequate Intake. |
| Added sugar | Under 5% of calories | The WHO's conditional recommendation for free sugars, close to the American Heart Association's 25-36 g a day. The 2025-2030 US Dietary Guidelines recommend no amount of added sugar, so this is a ceiling, not an allowance. |
| Sodium | Under 2,300 mg | 2025-2030 US Dietary Guidelines. |
| BMI | Standard BMI plus the WHO action points for Asian populations (23 increased risk, 27.5 high risk) | South Asians carry higher cardiometabolic risk at lower BMI. |
| Age | No targets under 18 | Adult equations and deficits do not apply to teenagers. |

Targets are a starting point. After two to three weeks of consistent logging, the weight trend shows whether calories should move.

## 2. Food database

`data/foods.csv` holds 354 foods. Each row gives one serving with its grams, calories, protein, carbs (total, including fiber), fat, fiber, added sugar, sodium, and alcohol where relevant. `data/measures.csv` maps household units (cup, tbsp, katori, "1 medium onion") to grams for 100+ ingredients.

| Kind | Count | What it covers |
|---|---|---|
| ingredient | 102 | Raw ingredients per 100 g, for recipes |
| dish | 143 | Home-style Indian dishes and everyday US foods, per typical serving |
| grocery | 48 | Packaged and grocery items: protein staples, breads, snacks, fruit |
| restaurant | 40 | US Indian restaurant portions (an entree is about 2 cups) |
| drink | 21 | Chai, coffee, lassi, juices, soda, beer, wine, spirits |

Every row has a `basis`:

- **usda** (120 rows): values from USDA FoodData Central reference foods, rounded.
- **label** (31 rows): typical US label values for packaged foods. Brands vary, so the skills prefer the user's own label.
- **recipe** (7 rows): computed by the calculator from documented recipes in `data/recipes/` (roti, roti with ghee, jowar bhakri, home dal, curd rice, soya chunks curry, poha). Tests recompute them on every change.
- **estimate** (196 rows): typical home or restaurant versions, built from standard recipes and portion sizes and checked against the macro math below. The skills tell the user when a meal leans on estimates.

Aliases cover Hindi, Tamil, Telugu, Kannada, Marathi, Gujarati, and Bengali names and common spellings, so "vendakkai poriyal", "bhindi fry", and "okra fry" find the same dish.

Restaurant rows assume US portions and cooking: entrees about 2 cups with more butter, cream, and oil than home versions, naan of 100-140 g, and a rice side of about 1.5 cups.

Sodium for home dishes assumes typical salting (about 0.5-1% salt by weight), which is why a normal day of home Indian food reaches 3,000-4,000 mg. Values are marked with `~` in replies because salt varies most between kitchens.

Added sugar counts only sugar added in cooking or processing (sugar, jaggery, honey, syrups), not the natural sugar in milk or fruit.

## 3. Calculator rules

- **Deterministic arithmetic.** Every total, percentage, remaining value, recipe division, and plan check is computed by `scripts/macros.py` rather than by the language model.
- **Rounding.** Items round to 5 kcal and whole grams; totals are the sum of the rounded rows, so the table always adds up on screen.
- **Katori.** 150 ml. Dishes served by the cup accept `katori` and `cup` directly.
- **Extra fat.** `oil_tsp` adds 4.5 g oil (about 40 kcal); `ghee_tsp` adds 4.3 g ghee (about 38 kcal).
- **Alcohol.** 7 kcal per gram, counted in calories and reported separately because it is not protein, carbs, or fat.
- **Plan checks.** Core checks decide whether a plan passes: calories within 5% of target, protein at least 95%, fat 20-35% of calories. Fiber, added sugar, and sodium are advisory notes, because almost every home-cooked Indian day exceeds 2,300 mg sodium and a plan that can never pass hides the checks that matter for the targets.
- **Errors, not guesses.** Unknown foods, unknown units, and bad input stop with a message that says what to fix, including likely matches.

## 4. Quality checks

Run with `pytest`:

- Every food's calories agree with its macros: within 20 kcal or 10% of 4 x protein + 4 x carbs + 9 x fat + 7 x alcohol, allowing fiber at 2 to 4 kcal per gram.
- Fiber and added sugar never exceed carbs; ids are unique; ingredient rows are per 100 g; measures point at real foods.
- Every recipe-basis row reproduces from its recipe within 5% of calories.
- Target math: Mifflin-St Jeor reference values, macros summing to calories, the BMR floor, BMI 25 reference weight, and refusal for minors.
- Logging, recipes, plans, unit conversion, fuzzy search, and error messages.

`tools/build.py check` also validates every SKILL.md against the Agent Skills specification and claude.ai's limits, confirms the copies inside each skill match the shared sources, and enforces the Anthropic plugin directory's file rules.

## 5. Known limitations

- Estimated rows are typical versions; any one kitchen can differ by 20% or more, mostly through oil and ghee.
- Photo portion estimates are the weakest link. A weighed portion or a count beats any photo.
- Even US nutrition labels may legally run up to 20% above their stated calories.
- Equations predict averages. Individuals vary, and medical conditions and medications change energy needs.
- No history across chats, by design: Katori stores nothing.

## 6. Sources

- Mifflin MD, St Jeor ST, et al. A new predictive equation for resting energy expenditure in healthy individuals. *Am J Clin Nutr.* 1990;51(2):241-247. [PubMed](https://pubmed.ncbi.nlm.nih.gov/2305711/)
- Frankenfield D, Roth-Yousey L, Compher C. Comparison of predictive equations for resting metabolic rate in healthy nonobese and obese adults: a systematic review. *J Am Diet Assoc.* 2005;105(5):775-789. [Journal page](https://www.jandonline.org/article/S0002-8223(05)00149-5/abstract)
- Validity of predictive equations to estimate RMR in females with varying BMI. *Journal of Nutritional Science* (Mifflin-St Jeor within 10% for 71% of participants). [Cambridge](https://www.cambridge.org/core/journals/journal-of-nutritional-science/article/validity-of-predictive-equations-to-estimate-rmr-in-females-with-varying-bmi/9EB5881462F01C1082D52F5E78FAF691)
- Jäger R, et al. International Society of Sports Nutrition Position Stand: protein and exercise. *J Int Soc Sports Nutr.* 2017;14:20. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/)
- WHO Expert Consultation. Appropriate body-mass index for Asian populations and its implications for policy and intervention strategies. *Lancet.* 2004;363:157-163. [The Lancet](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(03)15268-3/abstract)
- National Academies. Dietary Reference Intakes for Energy, Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino Acids. 2005. [National Academies Press](https://nap.nationalacademies.org/catalog/10490)
- World Health Organization. Guideline: sugars intake for adults and children. 2015. [WHO](https://www.who.int/publications/i/item/9789241549028)
- American Heart Association. Added sugars. [heart.org](https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/sugar/added-sugars)
- US Departments of Agriculture and Health and Human Services. Dietary Guidelines for Americans, 2025-2030. [dietaryguidelines.gov](https://www.dietaryguidelines.gov/)
- USDA Agricultural Research Service. FoodData Central. [fdc.nal.usda.gov](https://fdc.nal.usda.gov/)
- US Food and Drug Administration. Nutrition labeling of food, 21 CFR 101.9(g)(5) (label compliance). [eCFR](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101/subpart-A/section-101.9)
