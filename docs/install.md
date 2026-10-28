# Install

## Contents

1. Requirements
2. claude.ai and the Claude desktop app
3. Claude Code
4. Other agents
5. Claude API
6. Updating
7. Troubleshooting

## 1. Requirements

- **claude.ai or the desktop app:** a Pro, Max, Team, or Enterprise plan, with **Code execution and file creation** turned on in Settings > Capabilities. On Enterprise, an Owner may need to enable skills and plugins for the organization first.
- **Claude Code:** any recent version. The one-step install command needs 2.1.275 or later.
- **Everywhere:** the calculator needs Python 3.8 or later, which claude.ai's sandbox and most machines already have. No packages to install.

## 2. claude.ai and the Claude desktop app

### Option A: add the marketplace (recommended)

You get all four skills in one step, and updates when you want them.

1. Go to **Customize > Plugins** ([claude.ai/customize/plugins](https://claude.ai/customize/plugins)).
2. Select **Add > Add marketplace**.
3. Enter `POC4135/calorie-tracker` (or the full URL `https://github.com/POC4135/calorie-tracker`).
4. Open **Katori** and select **Add**.
5. Optional: turn on **Sync automatically** to receive updates.

The skills then work in chat on the web, desktop and mobile, in Cowork, and in Claude Code sessions signed in to the same account.

### Option B: upload the plugin zip

1. Download [`katori-plugin.zip`](https://github.com/POC4135/calorie-tracker/releases/latest/download/katori-plugin.zip) from the latest release.
2. Go to **Customize > Plugins > Add > Upload plugin** and choose the zip.

### Option C: upload individual skills

1. Download the skill you want from the [latest release](https://github.com/POC4135/calorie-tracker/releases/latest): `macro-tracker.zip`, `recipe-macros.zip`, `menu-macros.zip`, or `meal-planner.zip`. Start with `macro-tracker.zip`; the others add to it.
2. Go to **Customize > Skills** ([claude.ai/customize/skills](https://claude.ai/customize/skills)) and upload the zip. On older accounts the uploader is under **Settings > Capabilities > Skills**.
3. Turn the skill on.

Each zip holds one folder with the skill's name at its top level, which is the layout claude.ai expects. Do not unzip and re-zip the contents.

### Check that it works

Start a new chat and send:

```text
#ct setup: 30, female, 5'4", 140 lb, lightly active, maintenance, eggetarian
```

Claude should load the macro-tracker skill (you can see it in Claude's thinking or tool use) and reply with a targets table.

## 3. Claude Code

One step (Claude Code 2.1.275 or later):

```text
/plugin install katori --marketplace POC4135/calorie-tracker
```

Two steps, for earlier versions or from your shell:

```bash
claude plugin marketplace add POC4135/calorie-tracker
claude plugin install katori@katori
```

The skills appear as `/katori:macro-tracker`, `/katori:recipe-macros`, `/katori:menu-macros`, and `/katori:meal-planner`, and also load on their own when you type `#ct ...`.

To use a single skill without the plugin, copy its folder from `skills/` into `~/.claude/skills/` (for all projects) or `.claude/skills/` (for one project).

## 4. Other agents

The skills follow the open [Agent Skills](https://agentskills.io/specification) format, so agents that support it (OpenAI Codex, Cursor, OpenCode, and others) can use them:

```bash
npx skills add POC4135/calorie-tracker
npx skills add POC4135/calorie-tracker --skill macro-tracker
```

Or copy a folder from `skills/` into the agent's skills directory. The agent needs to be able to run `python3`.

## 5. Claude API

1. Create a custom skill from each folder under `skills/` with the Skills API (`POST /v1/skills`, uploading the folder's files with `SKILL.md` at its root), or with the `ant` CLI.
2. In a Messages request, attach the skills in `container.skills` with `"type": "custom"` and enable the code execution tool, which skills require.

```python
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    container={"skills": [{"type": "custom", "skill_id": "skill_...", "version": "latest"}]},
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[{"role": "user", "content": "#ct 2 idli, 1 cup sambar, coconut chutney"}],
)
```

The skills need no network access and no extra packages, which suits the API's sandbox. Check the [Agent Skills guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide) for current parameter names and model support. Keep the conversation history between turns so running totals carry over.

## 6. Updating

- **Marketplace on claude.ai:** with **Sync automatically** on, updates arrive by themselves; otherwise open Katori and select **Check for updates**.
- **Claude Code:** `claude plugin update katori@katori`, or turn on auto-update for the `katori` marketplace in `/plugin` > Marketplaces (third-party marketplaces start with auto-update off).
- **Uploaded zips:** download the new zip from the latest release and upload it again.

[CHANGELOG.md](../CHANGELOG.md) lists what changed.

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| Upload says `plugin.json must be at .claude-plugin/plugin.json` | You uploaded a skill zip as a plugin, or re-zipped the folder. Use `katori-plugin.zip` for **Upload plugin** and the skill zips for **Customize > Skills**. |
| The skill does not load | Start the message with `#ct`. Check that the skill or plugin is turned on and that code execution is on. |
| Two trackers answer `#ct` | You have another calorie skill installed. Turn one off. |
| "Input problem: ..." in Claude's tool output | The calculator rejected something (an unknown food or unit). Claude should fix it and rerun; if it does not, tell it to. |
| Totals reset | Totals live in one chat. Keep a day in one conversation, or paste `#ct today` output into the next chat as your starting point. |
| Numbers look off for your cooking | Tell Claude ("we use a lot more oil", "our rotis are big"), or run your family recipe through `#ct recipe` once and save the per-100 g line in a Project. |
