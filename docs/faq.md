# FAQ

**Is it free?**
Yes. Katori is open source under the MIT license. You need a Claude plan that supports skills (Pro, Max, Team, or Enterprise) with code execution turned on.

**Why not just ask Claude for calories without a skill?**
You can, but answers drift from chat to chat, totals get added up in prose, and Indian dishes get treated like their restaurant versions. Katori gives Claude a food database built for Indian home and restaurant food, fixed targets, a calculator for every number, and one reply format every time.

**Where is my data stored?**
Nowhere new. Katori has no server or database. Your meals live in your Claude conversation, under your account's privacy settings. See [PRIVACY.md](../PRIVACY.md).

**Can it remember yesterday?**
Not by itself; each chat holds one day. Use `#ct export` to copy the day into a spreadsheet, keep your targets in a Claude Project's instructions, and if your account has Claude's memory turned on, Claude may remember your targets between chats.

**How accurate is it?**
As accurate as the portion information you give it. Weighed or counted portions and label values are close; typical home cooking lands within the normal variation between kitchens; photos and restaurant meals carry the most uncertainty, mostly from oil, ghee, and cream. Every reply ends with a confidence line that says what was assumed. Details: [methodology.md](methodology.md).

**Why does it ask about ghee and oil?**
Because one tablespoon of oil is 120 kcal, and the difference between a dry sabzi and an oily one is bigger than the difference between most dishes. It only asks when the answer would change the meal by roughly 80 kcal or more.

**Why are my protein targets hard to hit as a vegetarian?**
Dal, paneer, and chickpeas bring a lot of calories per gram of protein. Greek yogurt, skyr, tofu, soya chunks, ultra-filtered milk, edamame, and whey are what make 1.6-1.8 g/kg possible inside a calorie target. Katori says so plainly and suggests them by name.

**Why is sodium always high?**
Typical Indian home cooking lands at 3,000-4,000 mg of sodium a day, well above the 2,300 mg guideline. Katori reports it so you can decide; the easiest cuts are pickle, papad, namkeen, packaged sauces, and lighter salting of dal and sabzi.

**Why is the added sugar target so low?**
The 2025-2030 US Dietary Guidelines recommend no amount of added sugar. Katori uses 5% of calories (the WHO's stricter recommendation) as a ceiling. Two cups of chai with 2 tsp sugar each are about half of it.

**My BMR from my scale was replaced. Why?**
If your BMR differs from the Mifflin-St Jeor formula by more than 10% and was not measured in a lab, Katori uses the formula and tells you. Smart scales estimate BMR from bioimpedance and formulas of their own. Say "use my BMR" and it will.

**Does it work for non-Indian food?**
Yes. The database includes US groceries, chains, pizza, burgers, burritos, fruit, and drinks, and Claude estimates anything else from the closest foods. For chain restaurants it prefers official nutrition pages.

**Can I use it for my child?**
No. Katori sets no targets for anyone under 18. A pediatrician or registered dietitian should set targets for children and teens.

**I have diabetes, kidney disease, or take a GLP-1 medication. Can I use it?**
You can use it to count what you eat, but set targets with your doctor or dietitian. Katori will say so and will not push a calorie deficit.

**How do I add my family's dishes?**
For yourself, run the recipe through `#ct recipe` and save the per-100 g line in a Claude Project. For everyone, open a [food request](https://github.com/POC4135/calorie-tracker/issues/new?template=food_request.yml) or send a pull request; see [CONTRIBUTING.md](../CONTRIBUTING.md).

**Is this affiliated with Anthropic?**
No. Katori is an independent open-source project built on Claude's skills and plugin formats.
