# Estimation guide

How to turn a description or a photo into quantities the calculator can use. Read the section you need.

## Contents

1. Portion sizes and serveware
2. Hidden oil and ghee
3. Home vs US restaurant
4. Photos
5. Nutrition labels
6. Common mistakes
7. Alcohol
8. Confidence

## 1. Portion sizes and serveware

| Reference | Typical size |
|---|---|
| Steel katori | 150 ml (small 100 ml, large 200 ml) |
| US measuring cup | 240 ml |
| US dinner plate | 26-27 cm across |
| Steel thali | 30 cm across |
| Quarter plate / salad plate | 18-20 cm |
| Takeout container, small / large | 16 oz (about 2 cups) / 32 oz (about 4 cups) |
| Roti | 6-7 in, 30 g atta, 40 g cooked; a large one is 40 g atta |
| Restaurant naan | 100-140 g |
| Cooked rice | a fist or a baseball is about 1 cup; a tennis ball is about 2/3 cup |
| Cooked meat or paneer | a palm (no fingers) is about 85-100 g |
| Fats | a fingertip is about 1 tsp; a thumb is about 1 tbsp |

When a user says "a bowl", ask once whether it was a katori or a cereal bowl only if the dish is calorie-dense (curry, rice, kheer). For dal or sabzi, assume a katori.

## 2. Hidden oil and ghee

Cooking fat is the biggest source of error in Indian food. The database rows assume typical home cooking. Adjust with `oil_tsp` or `ghee_tsp` when you have a reason to.

| Situation | Extra fat to add |
|---|---|
| Visible oil layer or "tari" on curry | +1 to 2 tsp per cup |
| Ghee smeared on roti | +1 tsp per roti (use `roti-ghee`) |
| Ghee drizzled on dal or rice | +1 tsp per drizzle |
| Butter on pav or paratha | +1 tsp per piece |
| Shallow-fried (tawa) snacks | already in the row; add +1 tsp if they look glossy |
| "Light" home cooking, nonstick pan | consider `multiplier` 0.85 on sabzi rows |

1 tsp oil is 4.5 g, 40 kcal, 4.5 g fat. 1 tsp ghee is 4.3 g, 38 kcal.

Ask about ghee or oil only when the answer would change the meal by more than about 80 kcal. Otherwise assume typical and say so in the confidence line.

## 3. Home vs US restaurant

US Indian restaurant food is richer and bigger than home food:

- Curries: use the `r-` restaurant rows (an entree is about 2 cups). If you only have a home row, a restaurant cup runs 1.25x the home value, and 1.5x for makhani, malai, korma, shahi, butter, and cream dishes
- Rice: a restaurant side is about 1.5 cups
- Bread: restaurant naan is 340-450 kcal; tandoori roti is the lightest bread on most menus
- Dosa: US restaurant dosas run 1.5-2x the home size
- Shared dishes: ask how many people shared, then divide
- Buffets: estimate each item separately with restaurant rows

For US chains (Chipotle, Starbucks, Subway, Panera, Taco Bell, McDonald's, Cava, Sweetgreen), the chain's own nutrition calculator beats any estimate. Search for it when web search is available and use the official numbers as an explicit item.

## 4. Photos

1. List every item you can see, including sides (chutney, raita, pickle, papad, salad).
2. Find a scale reference: plate (26-27 cm US, 30 cm thali), katori, spoon (15 cm), fork (18 cm), phone (15 cm), hand (18-20 cm long).
3. Estimate volume for each item from height and area, and count pieces (rotis, idlis, pieces of chicken).
4. Look for oil sheen, pooled oil, butter, cream swirls and fried textures, and adjust fat.
5. State your assumptions in one line under the table ("2 rotis about 6 in, 1 katori dal, 3/4 cup rice, no ghee visible").
6. If a key item is hidden or ambiguous (a stuffed paratha, a curry that could be paneer or chicken), give the table anyway and ask one question.

Do not store or describe the image beyond what the estimate needs.

## 5. Nutrition labels

- US labels are per serving; check "servings per container" and scale to what was eaten
- Many imported Indian packets list per 100 g; scale to the grams eaten
- Use the label's calories and macros as an explicit item. Label "Added sugars" goes in `added_sugar`; "Total sugars" does not
- Frozen parathas, rotis and snacks vary twofold between brands, so a label beats the database every time

## 6. Common mistakes

- Dal protein: a katori of home dal has about 5 g protein, not 15-20 g. Dal adds fiber and some protein, but it is not a protein anchor
- Paneer: about as much fat as protein by weight. When calories are tight, suggest tofu, Greek yogurt, egg whites, soya chunks, chicken, fish, or whey instead
- Chai: 2 tsp sugar is 8 g added sugar per cup; three cups a day is 24 g
- Coconut chutney: 3 tbsp is about 95 kcal, mostly fat
- Fried snacks: samosa, pakora, vada, puri, bhatura are 40-60% fat by calories
- "Healthy" restaurant picks: palak paneer and dal makhani run 700-750 kcal per entree because of cream and butter
- Rice volume: people underestimate restaurant rice by half
- Fruit is not free: a cup of mango is 100 kcal; a glass of juice is 110 kcal

## 7. Alcohol

Alcohol is 7 kcal per gram and is not protein, carbs or fat. The calculator reports it separately.

| Drink | Calories |
|---|---|
| Beer, 12 oz regular / light | 150 / 100 |
| Wine, 5 oz | 125 |
| Spirits, US shot 1.5 oz (44 ml) | 97 |
| Indian small peg 30 ml / large peg 60 ml | 70 / 140 |
| Mixer: 8 oz soda / tonic | 100 / 85 |
| Margarita or sweet cocktail | 250-350 |

## 8. Confidence

- **High:** named dish and a clear portion (weighed, counted, or a standard katori or cup)
- **Medium:** named dish, portion estimated; most photo estimates
- **Low:** vague description, unclear photo, or an unfamiliar dish with no close database match

For low confidence, still give the table, list the assumptions, and ask one question whose answer would change the total the most.
