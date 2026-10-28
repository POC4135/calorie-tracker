# Restaurant guide

## Contents

1. Menu decoder
2. Ranking method
3. Ordering scripts
4. Building an order inside a budget
5. Cuisine notes
6. Chains and non-Indian menus

## 1. Menu decoder

What the words on an Indian menu usually mean for calories:

| Word on the menu | What it means | Effect |
|---|---|---|
| Makhani, makhanwala, butter | butter and cream tomato gravy | very high fat |
| Malai, shahi, korma, Navratan, Mughlai, pasanda, lababdar | cream, cashew or almond paste | very high fat |
| Tikka masala | grilled meat or paneer in a cream tomato sauce | high fat |
| Kadai, karahi, jalfrezi, do pyaza | sauteed with onions and peppers, less cream | moderate |
| Vindaloo, Chettinad, Madras | spicy, oil-based, usually no cream | moderate to high fat |
| Saag, palak | spinach, often finished with cream | moderate to high |
| Tandoori, tikka (dry), kebab, seekh, hariyali, reshmi | grilled or tandoor-baked | lowest fat; reshmi and malai tikka are marinated in cream |
| 65, manchurian, pakora, bhaji, cutlet, fry, crispy | deep fried | high fat |
| Dal tadka, dal fry | lentils with a ghee tempering | moderate; the best value side for fiber |
| Dal makhani | whole urad simmered with butter and cream | high |
| Biryani | rice cooked with ghee and meat or vegetables | high calories mostly from rice and ghee; generous portions |
| Thali | a set plate of 4-8 bowls | estimate each bowl separately |

Breads, lightest to heaviest: tandoori roti, plain naan, garlic or butter naan, laccha paratha, onion kulcha, cheese naan, Peshawari naan, bhatura.

## 2. Ranking method

Rank only the dishes that fit the user's diet type. For each, use the restaurant estimate for the share they will eat.

1. **Fit:** the dish plus a reasonable side (one roti or half the rice) stays within the remaining calories. Dishes that do not fit even alone go to "Save for another day".
2. **Protein per 100 kcal:** higher is better when protein is short. Tandoori chicken is about 15 g per 100 kcal; chicken tikka masala about 7; paneer tikka masala about 4; chana masala about 3.5.
3. **Tiebreakers:** fiber (dal, chana, vegetables) and sodium (lower is better).

Groups:
- **Best picks:** fit comfortably and score well on protein
- **Fine with tweaks:** fit only with an ordering change (gravy on the side, shared, smaller bread)
- **Save for another day:** do not fit today's budget; say so without judgment

## 3. Ordering scripts

Phrases that work at most US Indian restaurants:

- "Can I get the tandoori chicken (or tikka) as a dry dish, with the sauce on the side?"
- "Tandoori roti instead of butter naan, please." Saves 150-250 kcal.
- "No butter on top of the naan."
- "Half rice, or rice on the side." A restaurant side of rice is about 1.5 cups (300 kcal).
- "Extra onion salad or raita on the side."
- "Can you make it with less oil or butter?" Some kitchens can; many cannot.
- "We'll share one curry and add a tandoori dish." Splits a rich entree between two people.
- For South Indian: "plain or onion dosa, chutney and sambar on the side"; sambar is low calorie and adds fiber; coconut chutney is mostly fat.

## 4. Building an order inside a budget

1. Start with one protein anchor (tandoori or tikka, a grilled kebab, dal, chana, or paneer for vegetarians who accept the fat).
2. Add one carb: tandoori roti or plain naan, or half a rice side.
3. Add one vegetable or a raita.
4. If calories remain, add a second curry to share or a small dessert.
5. Run `log` with `prior` and check that the day stays within target. Adjust the bread or rice first; they are the easiest lever.

Typical results (computed from the `r-` rows):
- Tandoori chicken (half) + tandoori roti + raita: about 750 kcal, 74 g protein
- Chicken tikka masala (half an entree) + half a plain naan + side salad: about 625 kcal, 36 g protein
- Chana masala (half) + dal tadka (half) + tandoori roti + raita: about 855 kcal, 34 g protein
- Restaurant masala dosa + sambar + tomato chutney: about 625 kcal, 16 g protein

## 5. Cuisine notes

- **South Indian:** idli and plain dosa are the lightest bases; the potato filling, ghee roast dosas, and coconut chutney add the calories. Pesarattu (moong dosa) and uttapam with vegetables add protein or fiber.
- **Indo-Chinese:** gobi manchurian, chilli paneer, and chilli chicken are battered and fried in a sugary sauce. Hakka noodles and fried rice run 330-450 kcal a cup. A dry chilli chicken shared, plus a soup, is the least costly path.
- **Chaat and street food:** pani puri is the lightest; papdi chaat, sev puri, and dahi puri run 280-400 kcal a plate with 6-10 g added sugar from the chutneys.
- **Buffets:** take one plate. Fill half with tandoori items, dal, and salad before any gravy dish.
- **Sweets:** gulab jamun 175-190 kcal each with syrup; rasmalai about 165 each; one shared dessert is the usual compromise.

## 6. Chains and non-Indian menus

For chains (Chipotle, Cava, Sweetgreen, Panera, Starbucks, Subway, Taco Bell, McDonald's, Chick-fil-A, Domino's), search for the official nutrition page or calculator and use those numbers as explicit items. Label them as official in the confidence line.

Quick heuristics when no official numbers exist:
- **Mexican:** a burrito is 900-1,300 kcal; a bowl without the tortilla saves about 300; chips are 500+ per basket
- **Mediterranean:** grilled chicken or falafel plates are 700-1,000 kcal; ask for extra salad instead of rice
- **Thai:** curries with coconut milk 600-900 kcal per bowl without rice; stir fries 500-800
- **Pizza:** a large-pizza slice is 280-320 kcal (cheese) to 350+ (meat)
- **Burgers:** 500-900 kcal before fries; fries add 320-500
- **Sushi:** 8-piece roll 250-500 kcal; tempura and spicy mayo rolls at the top
