# calorie-tracker

Claude skills for tracking calories and macros in chat, built for a mostly Indian diet in the US.

- **macro-tracker**: log meals from text or photos with daily targets, running totals, and suggestions. `#ct 2 rotis, 1 katori dal, bhindi sabzi`
- **recipe-macros**: per-serving macros for a batch recipe. `#ct recipe ...`
- **menu-macros**: what to order at a restaurant to fit the rest of your day. `#ct menu ...`
- **meal-planner**: one- or seven-day plans checked against your targets. `#ct plan ...`

## Install

Needs a paid Claude plan with code execution on (Settings > Capabilities).

- **claude.ai or the desktop app:** Customize > Plugins > Add > Add marketplace, enter `POC4135/calorie-tracker`, then add the plugin.
- **One skill only:** zip a folder from `skills/` (the folder itself, not its contents) and upload it under Customize > Skills.
- **Claude Code:** `/plugin install calorie-tracker --marketplace POC4135/calorie-tracker`

## Use

Start a chat with your details, then log as you eat:

```text
#ct setup: 28, male, 5'9", 172 lb, BMR 1720, moderately active, goal recomp, vegetarian
#ct 2 rotis, 1 katori dal, bhindi sabzi
#ct today
```

Totals live in the chat; nothing is stored anywhere else. Numbers are estimates, not medical advice.

## License

MIT
