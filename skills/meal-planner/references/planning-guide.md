# Planning guide

## Contents

1. Protein anchors by diet type
2. How to build a day
3. Meal templates by region
4. Batch cooking
5. Grocery lists
6. Iterating with the checker

## 1. Protein anchors by diet type

Values from `references/foods.csv`. "P per 100 kcal" is protein density: the higher it is, the easier a protein target fits inside a calorie target.

| Food and portion | Cal | Protein | P per 100 kcal | Diet |
|---|---|---|---|---|
| Whey, 1 scoop (30 g) | 120 | 24 g | 20 | veg (check label for vegan pea protein) |
| Egg whites, 1/2 cup | 63 | 13 g | 21 | egg |
| Nonfat Greek yogurt, 170 g cup | 100 | 17 g | 17 | veg |
| Skyr, 150 g | 90 | 16 g | 18 | veg |
| Soya chunks, 30 g dry | 104 | 16 g | 15 | veg, vegan, Jain (most households) |
| Cottage cheese 2%, 1/2 cup | 92 | 12 g | 13 | veg |
| Firm tofu, 150 g | 216 | 26 g | 12 | veg, vegan |
| Ultra-filtered 2% milk, 1 cup | 120 | 13 g | 11 | veg |
| Edamame, 1 cup shelled | 188 | 18 g | 10 | veg, vegan |
| Eggs, 2 large | 144 | 13 g | 9 | egg |
| Lentils, 1 cup boiled | 230 | 18 g | 8 | veg, vegan |
| Paneer (store), 100 g | 320 | 21 g | 7 | veg |
| 2% milk, 1 cup | 122 | 8 g | 7 | veg |
| Chickpeas, 1 cup canned | 222 | 11 g | 5 | veg, vegan |
| Home dal, 1 katori | 98 | 5 g | 5 | veg, vegan, Jain |
| Shrimp, 150 g raw | 128 | 30 g | 24 | non-veg |
| Canned tuna, 1 can drained | 110 | 25 g | 23 | non-veg |
| White fish (tilapia, rohu), 150 g raw | 144 | 30 g | 21 | non-veg |
| Chicken breast, 120 g cooked | 198 | 37 g | 19 | non-veg |
| Goat, 150 g raw boneless | 164 | 31 g | 19 | non-veg |
| Chicken thigh, 150 g raw boneless | 182 | 30 g | 16 | non-veg |
| Salmon, 150 g raw | 312 | 31 g | 10 | non-veg |

What this means in practice:
- **Vegetarian at 130-150 g protein:** needs two or three of Greek yogurt or skyr, tofu, soya chunks, ultra-filtered milk, and whey most days. Dal, paneer, and chickpeas help, but cannot carry the target alone inside a calorie budget.
- **Eggetarian:** egg whites are the cheapest lean add-on; whole eggs bring fat with the protein.
- **Non-vegetarian:** one portion of chicken, fish, or goat per main meal usually covers it.
- **Vegan:** tofu, soya chunks, edamame, lentils, chickpea pasta, and a pea or soy protein powder from its label.
- **Jain:** no onion, garlic, potato, carrot, or other root vegetables. Build masalas from tomato, hing, and spices; some families use dry ginger (sonth), so ask. Lean on dairy, soya chunks, moong, and dal.

Spread protein across the day: about 25-40 g per meal (the ISSN suggests about 0.25 g/kg per meal), rather than one large serving at dinner.

## 2. How to build a day

1. Split calories roughly 25% breakfast, 35% lunch, 10-15% snack, 25-30% dinner, unless the user eats differently.
2. Put a protein anchor in every meal, then the user's usual carb (roti, rice, idli, poha), then vegetables.
3. Use the user's own dishes first. A plan they already know how to cook beats a perfect one they will not.
4. Keep fats honest: count the tadka, the ghee on rotis, and the oil in sabzi. The database rows assume typical home cooking.
5. Put more carbs before and after training if the user trains.
6. Leave room for chai, fruit, and the small things people actually eat.

## 3. Meal templates by region

Starting points; portions get tuned by the checker.

**Breakfast**
- Poha with peanuts + 170 g Greek yogurt
- 2 besan or moong chillas + 1 katori dahi
- 3 idli + sambar + 1/2 cup egg whites as a masala scramble
- Paneer or tofu bhurji + 1 roti
- Masala omelette (2 eggs) + 1 slice whole wheat toast + fruit
- Upma with vegetables + 1 cup ultra-filtered milk
- Overnight oats with 1 scoop whey and banana

**Lunch**
- North: 2 rotis + 1 katori dal + 1 cup sabzi + salad + raita; or rajma or chole with 3/4 cup rice and salad
- South: 1 cup rice + sambar + poriyal + 1 katori curd; or curd rice + kootu, with chicken or egg on the side for non-veg
- Gujarati: 2 rotli + dal + shaak + kadhi (small) + salad
- Bengali: 3/4 cup rice + dal + fish curry + shukto or a vegetable
- Maharashtrian: 2 bhakri or chapati + varan or usal + bhaji + salad
- Any: soya chunks curry + 2 rotis + salad

**Snacks**
- Roasted chana, 30 g; or makhana, 30 g
- Greek yogurt or skyr with fruit
- Sprouts chaat
- Whey in milk or water
- 2 boiled eggs, or 1 cup edamame
- Fruit with 15-20 g peanuts

**Dinner** (often lighter on carbs)
- Home palak paneer or tofu palak + 1 roti + salad
- Tofu or paneer bhurji + 2 rotis
- Fish curry + 1/2 cup rice + vegetable
- Dal + sabzi + 1 roti + raita
- Home tandoori chicken + salad + raita + 1 roti
- Khichdi + 1 katori curd + papad (roasted)

## 4. Batch cooking

A weekend session of 90 minutes covers most weekdays:

| Batch | Keeps in the fridge | Notes |
|---|---|---|
| Dal (1 cup raw, about 6 cups) | 3-4 days | add the tadka fresh each day if possible |
| Rajma or chole (1.5 cups dry) | 4 days; freezes well | soak overnight |
| Boiled chickpeas or kala chana | 4 days | for chaat, salads, quick curries |
| Soya chunks, soaked and squeezed | 3 days | add to any gravy for protein |
| Marinated chicken or paneer tikka | 2 days raw; cook as needed | |
| Chopped onion, tomato, ginger-garlic | 3-4 days | the masala base for weekday sabzis |
| Roti dough | 2 days | |
| Boiled eggs | 7 days in the shell | |

Pressure cooker or Instant Pot, typical times at high pressure (follow your cooker's guide): toor or moong dal 8-10 min; soaked chickpeas 15-20 min; soaked rajma 20-25 min; rice 5-6 min.

## 5. Grocery lists

Group by store and give quantities in the sizes people actually buy:

- **Indian grocery (Patel Brothers, Apna Bazar, India Bazaar, local stores):** atta (10 or 20 lb bag), dals (2 or 4 lb), rajma and chana (2 lb), soya chunks (200 g packs), poha, sooji, spices, curry leaves, paneer (14 oz block), frozen rotis or parathas (check labels), pickle and papad.
- **Regular grocery (Kroger, Publix, Safeway, Trader Joe's, Whole Foods, H-E-B):** vegetables, fruit, Greek yogurt (32 oz tubs or 6 oz cups), skyr, tofu (14 oz), eggs (12 or 18), milk or ultra-filtered milk (52 oz), chicken, fish, frozen vegetables, edamame.
- **Warehouse club (Costco, Sam's Club):** chicken breast or thighs (bulk), eggs (two dozen), Greek yogurt tubs, frozen vegetables, whey, nuts, ultra-filtered milk multipacks.

Add up quantities across the whole plan first, then round up to package sizes. Mark pantry items the user probably has ("check pantry: rice, spices, oil").

Cheapest protein per dollar is usually dal, chana, rajma, soya chunks, eggs, and whey; paneer and ready-made protein drinks cost the most.

## 6. Iterating with the checker

1. Run `plan` on the draft day.
2. Fix the largest miss first:
   - Protein short: swap a carb portion for a protein anchor, or add a high-density anchor (whey, Greek yogurt, egg whites, soya chunks, tofu, chicken, fish).
   - Calories high: trim oil or ghee, then rice or roti, then sweets or fried items.
   - Calories low: add rice, roti, fruit, nuts, or milk.
   - Fat high: replace paneer with tofu or Greek yogurt; trim tadka oil.
   - Sodium high: drop pickle, papad, namkeen, packaged sauces; restaurant meals dominate sodium.
3. Run `plan` again. Stop at three passes and report the remaining gap plainly.
