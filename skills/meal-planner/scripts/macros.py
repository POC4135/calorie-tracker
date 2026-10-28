#!/usr/bin/env python3
"""Katori macro calculator: targets, food lookup, meal logging, recipes and plan checks.

Standard library only (Python 3.8+). Every number Katori shows the user should come
from this script, because language models make arithmetic slips on long tables.

Commands
  targets   Daily calorie and macro targets from age, sex, height, weight, BMR, activity, goal.
  lookup    Search the food database by name, alias or id; optionally scale to grams or servings.
  units     List the household units (cup, tbsp, medium, ...) known for one food id.
  log       Build the meal table and today's running totals. Reads JSON on stdin.
  summary   Today's totals against targets, with no new meal. Reads JSON on stdin.
  recipe    Per-serving macros for a batch recipe. Reads JSON on stdin.
  plan      Check a day plan against targets. Reads JSON on stdin.

Run any command with -h for its options. The JSON formats are documented in
references/calculator.md inside each skill.
"""

import argparse
import csv
import difflib
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Constants (each one is sourced or explained; see references/methodology.md)
# ---------------------------------------------------------------------------

# Standard activity multipliers applied to BMR to estimate TDEE.
ACTIVITY_FACTORS = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "very_active": 1.725}

# Calorie target as a fraction of TDEE. 20% below maintenance is a moderate deficit;
# 10% suits recomposition; 10% above suits a slow lean gain.
GOAL_FACTORS = {"fat_loss": 0.80, "recomp": 0.90, "maintenance": 1.00, "lean_gain": 1.10}

# Protein in g per kg of reference weight. Both sit inside the ISSN range of
# 1.4-2.0 g/kg/day for people who exercise; the higher value protects lean mass in a deficit.
PROTEIN_PER_KG = {"fat_loss": 1.8, "recomp": 1.8, "maintenance": 1.6, "lean_gain": 1.6}

FAT_SHARE = 0.28            # fat as a share of calories, inside the 20-35% AMDR (National Academies)
FAT_FLOOR_G_PER_KG = 0.6    # do not let fat fall below this
FIBER_G_PER_1000_KCAL = 14  # National Academies Adequate Intake for fiber
# Added sugar ceiling: 5% of calories, the WHO's conditional recommendation for free sugars and
# close to the American Heart Association's 25-36 g a day. The 2025-2030 Dietary Guidelines for
# Americans recommend no amount of added sugar, so this is a ceiling, not an allowance.
ADDED_SUGAR_SHARE = 0.05
SODIUM_LIMIT_MG = 2300      # Dietary Guidelines for Americans 2025-2030: under 2,300 mg a day
REFERENCE_BMI = 25.0        # above this, size protein from the weight at BMI 25
ASIAN_BMI_POINTS = (23.0, 27.5)  # WHO expert consultation action points for Asian populations
BMR_AGREEMENT = 0.10        # accept a non-lab BMR within 10% of Mifflin-St Jeor

KCAL_PER_G = {"protein": 4, "carbs": 4, "fat": 9, "alcohol": 7}
KATORI_ML = 150  # a typical steel katori holds about 150 ml of dal or curry
CUP_ML = 240
OIL_G_PER_TSP = 4.5
GHEE_G_PER_TSP = 4.3

# Plan check tolerances
PLAN_KCAL_TOLERANCE = 0.05    # day total within 5% of the calorie target
PLAN_PROTEIN_MIN_SHARE = 0.95 # at least 95% of the protein target
PLAN_FAT_SHARE_RANGE = (0.20, 0.35)

NUTRIENTS = ["kcal", "protein", "carbs", "fat", "fiber", "added_sugar", "sodium", "alcohol"]
CSV_COLUMNS = {
    "kcal": "kcal", "protein": "protein_g", "carbs": "carbs_g", "fat": "fat_g",
    "fiber": "fiber_g", "added_sugar": "added_sugar_g", "sodium": "sodium_mg",
    "alcohol": "alcohol_g",
}
TARGET_KEYS = ["kcal", "protein", "carbs", "fat", "fiber", "added_sugar", "sodium"]

UNIT_ALIASES = {
    "g": "g", "gm": "g", "gms": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "ml": "ml", "milliliter": "ml", "milliliters": "ml", "l": "l", "liter": "l", "litre": "l",
    "cup": "cup", "cups": "cup", "c": "cup",
    "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp", "tbs": "tbsp", "tbl": "tbsp",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "katori": "katori", "bowl": "katori",
    "piece": "piece", "pieces": "piece", "pc": "piece", "pcs": "piece",
    "each": "each", "whole": "each", "nos": "each", "no": "each",
}
MASS_UNITS = {"g": 1.0, "kg": 1000.0, "oz": 28.3495, "lb": 453.592}
# Volume fallbacks for foods without a specific measure. Only used for foods whose
# density is close to water (milk, yogurt drinks, juices, water itself).
VOLUME_ML = {"ml": 1.0, "l": 1000.0, "cup": 240.0, "tbsp": 15.0, "tsp": 5.0}
WATER_LIKE = {"milk-whole", "milk-2pct", "milk-skim", "lemon-juice", "coconut-water"}
ZERO_FOODS = {"water", "spices", "ice", "salt-free-spices"}


class InputError(Exception):
    """A problem with the user's input that the caller should fix and retry."""


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _data_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.environ.get("KATORI_DATA_DIR", ""),
        os.path.join(here, "..", "references"),
        os.path.join(here, "..", "..", "data"),
        os.path.join(here, "..", "..", "..", "data"),
    ]
    for path in candidates:
        if path and os.path.isfile(os.path.join(path, "foods.csv")):
            return os.path.abspath(path)
    raise InputError(
        "Could not find foods.csv. Expected it in the skill's references/ folder "
        "or set KATORI_DATA_DIR to the folder that holds it."
    )


def load_foods(data_dir=None):
    data_dir = data_dir or _data_dir()
    foods = {}
    with open(os.path.join(data_dir, "foods.csv"), newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            entry = dict(row)
            entry["serving_g"] = float(row["serving_g"])
            for key, column in CSV_COLUMNS.items():
                raw = (row.get(column) or "").strip()
                entry[key] = float(raw) if raw else 0.0
            entry["alias_list"] = [a.strip() for a in row["aliases"].split("|") if a.strip()]
            foods[row["id"]] = entry
    return foods


def load_measures(data_dir=None):
    data_dir = data_dir or _data_dir()
    measures = {}
    path = os.path.join(data_dir, "measures.csv")
    if not os.path.isfile(path):
        return measures
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            measures.setdefault(row["food_id"], {})[row["unit"].strip().lower()] = float(row["grams"])
    return measures


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_kcal(value):
    return f"{int(round(value)):,}"


def fmt_g(value, unit="g"):
    if 0 < abs(value) < 0.5:
        return f"<1{unit}"
    return f"{int(round(value)):,}{unit}"


def round5(value):
    return int(5 * round(float(value) / 5))


def pct(total, target):
    if not target:
        return "n/a"
    return f"{int(round(100.0 * total / target))}%"


def signed(value, unit=""):
    number = int(round(value))
    return f"{number:,}{unit}"


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def mifflin_st_jeor(sex, weight_kg, height_cm, age):
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex == "male":
        return base + 5
    if sex == "female":
        return base - 161
    return base - 78  # unspecified: midpoint of the male and female constants


def compute_targets(age, sex, height_cm, weight_kg, activity, goal,
                    bmr=None, bmr_source="unknown", protein_per_kg=None):
    if age < 18:
        raise InputError(
            "Targets are for adults. For anyone under 18, set targets with a pediatrician "
            "or registered dietitian; Katori can still estimate meal macros."
        )
    if not 120 <= height_cm <= 230:
        raise InputError(f"Height {height_cm:.0f} cm looks wrong. Give height in cm, or feet and inches.")
    if not 30 <= weight_kg <= 300:
        raise InputError(f"Weight {weight_kg:.1f} kg looks wrong. Give weight in kg or lb.")
    if activity not in ACTIVITY_FACTORS:
        raise InputError(f"Activity must be one of {', '.join(ACTIVITY_FACTORS)}.")
    if goal not in GOAL_FACTORS:
        raise InputError(f"Goal must be one of {', '.join(GOAL_FACTORS)}.")

    notes = []
    msj = mifflin_st_jeor(sex, weight_kg, height_cm, age)
    if bmr is None:
        bmr_used, bmr_note = msj, "Mifflin-St Jeor (no BMR given)"
    elif bmr_source == "lab":
        bmr_used, bmr_note = float(bmr), "lab-measured"
    else:
        gap = (float(bmr) - msj) / msj
        if abs(gap) <= BMR_AGREEMENT:
            bmr_used = float(bmr)
            bmr_note = f"yours, within 10% of Mifflin-St Jeor {fmt_kcal(msj)}"
        else:
            bmr_used = msj
            bmr_note = f"Mifflin-St Jeor; your {fmt_kcal(bmr)} differs by {gap * 100:+.0f}%"
            notes.append(
                f"Your BMR ({fmt_kcal(bmr)}, from {bmr_source}) is {gap * 100:+.0f}% off the "
                f"Mifflin-St Jeor estimate ({fmt_kcal(msj)}). Scale and app BMRs are estimates, so "
                "I used the formula. Say so if you want yours used instead."
            )

    tdee = bmr_used * ACTIVITY_FACTORS[activity]
    kcal = tdee * GOAL_FACTORS[goal]
    if kcal < bmr_used:
        kcal = bmr_used
        notes.append("The goal adjustment fell below BMR, so calories are set at BMR.")

    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    ref_kg = min(weight_kg, REFERENCE_BMI * height_m * height_m)
    if ref_kg < weight_kg:
        notes.append(
            f"BMI is above 25, so protein is sized from {ref_kg:.1f} kg (your weight at BMI 25)."
        )

    per_kg = protein_per_kg if protein_per_kg else PROTEIN_PER_KG[goal]
    protein = ref_kg * per_kg
    fat = max(kcal * FAT_SHARE / 9.0, ref_kg * FAT_FLOOR_G_PER_KG)
    carbs = (kcal - protein * 4 - fat * 9) / 4.0
    if carbs < 100:
        notes.append("Carbs land under 100 g. Check the inputs; this is unusually low.")
    carbs = max(carbs, 0.0)

    kcal_r = int(10 * round(kcal / 10.0))
    low, high = ASIAN_BMI_POINTS
    if bmi >= high:
        asian = f"above {high} (WHO high-risk action point for Asian adults)"
    elif bmi >= low:
        asian = f"above {low} (WHO increased-risk action point for Asian adults)"
    else:
        asian = f"below {low} (WHO action point for Asian adults)"

    return {
        "targets": {
            "kcal": kcal_r,
            "protein": int(round(protein)),
            "carbs": int(round(carbs)),
            "fat": int(round(fat)),
            "fiber": int(round(kcal_r / 1000.0 * FIBER_G_PER_1000_KCAL)),
            "added_sugar": int(round(kcal_r * ADDED_SUGAR_SHARE / 4.0)),
            "sodium": SODIUM_LIMIT_MG,
        },
        "bmr_mifflin": int(round(msj)),
        "bmr_used": int(round(bmr_used)),
        "bmr_note": bmr_note,
        "tdee": int(10 * round(tdee / 10.0)),
        "activity": activity,
        "activity_factor": ACTIVITY_FACTORS[activity],
        "goal": goal,
        "goal_factor": GOAL_FACTORS[goal],
        "protein_per_kg": per_kg,
        "reference_kg": round(ref_kg, 1),
        "bmi": round(bmi, 1),
        "bmi_asian_note": asian,
        "notes": notes,
    }


GOAL_LABELS = {"fat_loss": "fat loss", "recomp": "recomposition",
               "maintenance": "maintenance", "lean_gain": "lean gain"}


def render_targets(result):
    t = result["targets"]
    lines = [
        "| Target | Daily |",
        "|---|---|",
        f"| Calories | {fmt_kcal(t['kcal'])} kcal |",
        f"| Protein | {t['protein']}g |",
        f"| Carbs | {t['carbs']}g |",
        f"| Fat | {t['fat']}g |",
        f"| Fiber | {t['fiber']}g+ |",
        f"| Added sugar | under {t['added_sugar']}g |",
        f"| Sodium | under {t['sodium']:,}mg |",
        "",
        (f"Math: BMR {fmt_kcal(result['bmr_used'])} ({result['bmr_note']}) x "
         f"{result['activity_factor']} {result['activity'].replace('_', ' ')} = TDEE "
         f"{fmt_kcal(result['tdee'])}; {GOAL_LABELS[result['goal']]} x {result['goal_factor']:.2f} = "
         f"{fmt_kcal(t['kcal'])} kcal. Protein {result['protein_per_kg']} g/kg of "
         f"{result['reference_kg']} kg."),
        f"BMI {result['bmi']}: {result['bmi_asian_note']}.",
    ]
    for note in result["notes"]:
        lines.append(f"Note: {note}")
    lines.append("")
    lines.append("TARGETS_JSON " + json.dumps(t, separators=(",", ":")))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def _normalize(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


TOKEN_MATCH_MIN = 0.75  # spelling variants like chapati/chapatti score about 0.9
SEARCH_MIN_SCORE = 35


def _token_score(q_tokens, n_tokens):
    """Average best fuzzy match of each query token against the name's tokens."""
    if not q_tokens or not n_tokens:
        return 0.0
    total = 0.0
    for qt in q_tokens:
        best = max(difflib.SequenceMatcher(None, qt, nt).ratio() for nt in n_tokens)
        total += best if best >= TOKEN_MATCH_MIN else 0.0
    return total / len(q_tokens)


def search_foods(foods, query, kind=None, limit=8):
    q = _normalize(query)
    q_tokens = q.split()
    scored = []
    for food in foods.values():
        if kind and food["kind"] != kind:
            continue
        names = [food["id"].replace("-", " "), food["name"]] + food["alias_list"]
        best = 0.0
        for name in names:
            n = _normalize(name)
            if not n:
                continue
            if n == q:
                score = 100.0
            else:
                ratio = difflib.SequenceMatcher(None, q, n).ratio()
                contains = 15.0 if (len(q) >= 3 and (q in n or n in q)) else 0.0
                score = 55.0 * _token_score(q_tokens, n.split()) + 30.0 * ratio + contains
            best = max(best, score)
        if best >= SEARCH_MIN_SCORE:
            scored.append((best, food))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [food for _, food in scored[:limit]]


def scale_food(food, factor):
    return {key: food[key] * factor for key in NUTRIENTS}


def render_lookup(matches, grams=None, servings=None):
    if not matches:
        return "No matches. Try a simpler name (for example 'dal', 'paneer', 'roti') or an English name."
    header = "| id | Food | Portion | Cal | Protein | Carbs | Fat | Fiber | Added sugar | Sodium | Basis |"
    lines = [header, "|---|---|---|---|---|---|---|---|---|---|---|"]
    for food in matches:
        if grams is not None:
            factor, portion = grams / food["serving_g"], f"{grams:g} g"
        elif servings is not None:
            factor, portion = servings, f"{servings:g} x {food['serving']}"
        else:
            factor = 1.0
            if re.search(r"\d\s*(g|ml)\b", food["serving"]):
                portion = food["serving"]
            else:
                portion = f"{food['serving']} ({food['serving_g']:g} g)"
        v = scale_food(food, factor)
        lines.append(
            f"| {food['id']} | {food['name']} | {portion} | {fmt_kcal(v['kcal'])} | {v['protein']:.1f}g | "
            f"{v['carbs']:.1f}g | {v['fat']:.1f}g | {v['fiber']:.1f}g | {v['added_sugar']:.1f}g | "
            f"{fmt_kcal(v['sodium'])}mg | {food['basis']} |"
        )
    notes = [f"- {f['id']}: {f['notes']}" for f in matches if f.get("notes")]
    if notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(notes)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Units and item resolution
# ---------------------------------------------------------------------------

def to_grams(food_id, qty, unit, measures, foods):
    if qty is None:
        raise InputError(f"'{food_id}': give qty with unit '{unit}'.")
    unit_key = UNIT_ALIASES.get(str(unit).strip().lower(), str(unit).strip().lower())
    if unit_key in MASS_UNITS:
        return float(qty) * MASS_UNITS[unit_key]
    known = measures.get(food_id, {})
    if unit_key in known:
        return float(qty) * known[unit_key]
    if unit_key == "each" and "piece" in known:
        return float(qty) * known["piece"]
    if unit_key == "piece" and "each" in known:
        return float(qty) * known["each"]
    food = foods.get(food_id, {})
    # Dishes served by the cup (dal, sabzi, curry, rice) also accept katori and cup.
    if unit_key in {"cup", "katori"} and str(food.get("serving", "")).startswith("1 cup"):
        per_cup = food["serving_g"]
        return float(qty) * (per_cup if unit_key == "cup" else per_cup * KATORI_ML / CUP_ML)
    if unit_key in VOLUME_ML and (food_id in WATER_LIKE or food.get("kind") == "drink"):
        return float(qty) * VOLUME_ML[unit_key]
    if unit_key in {"tsp", "tbsp"} and "tbsp" in known and unit_key == "tsp":
        return float(qty) * known["tbsp"] / 3.0
    if unit_key in {"tsp", "tbsp"} and "tsp" in known and unit_key == "tbsp":
        return float(qty) * known["tsp"] * 3.0
    available = ", ".join(sorted(known)) or "none"
    raise InputError(
        f"No '{unit}' measure for '{food_id}'. Known units: {available}; or give grams "
        f"(g, oz, lb). Weighing is most accurate."
    )


def _suggest(foods, food_id):
    matches = search_foods(foods, food_id.replace("-", " "), limit=5)
    if not matches:
        return ""
    return " Did you mean: " + ", ".join(m["id"] for m in matches) + "?"


def resolve_item(item, foods, measures):
    """Return (label, values, flags) for one item dict."""
    if not isinstance(item, dict):
        raise InputError("Each item must be a JSON object.")
    flags = []
    food_id = item.get("food")
    if not food_id and item.get("query"):
        matches = search_foods(foods, str(item["query"]), limit=1)
        if not matches:
            raise InputError(
                f"Nothing in the database matches '{item['query']}'. Estimate it and pass "
                "name, kcal, protein, carbs and fat instead."
            )
        food_id = matches[0]["id"]
        flags.append(f"matched:{item['query']}=>{food_id}")
        item = dict(item, food=food_id)
    if food_id in ZERO_FOODS:
        return item.get("label") or food_id, {k: 0.0 for k in NUTRIENTS}, flags
    if food_id:
        if food_id not in foods:
            raise InputError(f"Unknown food id '{food_id}'.{_suggest(foods, food_id)}")
        food = foods[food_id]
        if "grams" in item:
            grams = float(item["grams"])
            qty_text = f"{grams:g} g"
        elif "unit" in item:
            grams = to_grams(food_id, item.get("qty", 1), item["unit"], measures, foods)
            qty_text = f"{float(item.get('qty', 1)):g} {item['unit']}"
        else:
            servings = float(item.get("servings", 1))
            grams = servings * food["serving_g"]
            qty_text = food["serving"] if servings == 1 else f"{servings:g} x {food['serving']}"
        factor = grams / food["serving_g"] * float(item.get("multiplier", 1.0))
        if factor <= 0:
            raise InputError(f"'{food_id}': the amount must be more than zero.")
        values = scale_food(food, factor)
        label = item.get("label") or f"{food['name']}, {qty_text}"
        if food["basis"] == "estimate":
            flags.append("estimate")
    else:
        missing = [k for k in ("kcal", "protein", "carbs", "fat") if k not in item]
        if "name" not in item and "label" not in item:
            raise InputError("Items without a food id need a 'name' (or 'label').")
        if missing:
            raise InputError(
                f"Item '{item.get('label') or item.get('name')}' needs {', '.join(missing)}. "
                "Estimate them first, or use a food id from lookup."
            )
        values = {k: float(item.get(k, 0) or 0) for k in NUTRIENTS}
        mult = float(item.get("multiplier", 1.0))
        values = {k: v * mult for k, v in values.items()}
        label = item.get("label") or item.get("name")
        for optional in ("fiber", "added_sugar", "sodium"):
            if optional not in item:
                flags.append(f"no-{optional}")
    for key, grams_per_tsp, fat_food in (("oil_tsp", OIL_G_PER_TSP, "oil"), ("ghee_tsp", GHEE_G_PER_TSP, "ghee")):
        tsp = float(item.get(key, 0) or 0)
        if tsp:
            extra = scale_food(foods[fat_food], tsp * grams_per_tsp / foods[fat_food]["serving_g"])
            values = {k: values[k] + extra[k] for k in NUTRIENTS}
    return label, values, flags


# ---------------------------------------------------------------------------
# Log
# ---------------------------------------------------------------------------

def _read_payload(path):
    text = sys.stdin.read() if path in (None, "-") else open(path, encoding="utf-8").read()
    if not text.strip():
        raise InputError("Expected a JSON object on stdin (use a heredoc).")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"Invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise InputError("The JSON payload must be an object.")
    return payload


def _clean_totals(raw):
    raw = raw or {}
    return {k: float(raw.get(k, 0) or 0) for k in NUTRIENTS}


def _round_item(values):
    out = {k: float(round(values[k])) for k in NUTRIENTS}
    out["kcal"] = float(round5(values["kcal"]))
    out["sodium"] = float(int(10 * round(values["sodium"] / 10.0)))
    return out


def build_log(payload, foods, measures):
    items = payload.get("items") or []
    if not items:
        raise InputError("No items to log.")
    targets = payload.get("targets") or {}
    prior = _clean_totals(payload.get("prior"))
    rows, meal, flags_by_item = [], {k: 0.0 for k in NUTRIENTS}, {}
    for item in items:
        label, values, flags = resolve_item(item, foods, measures)
        shown = _round_item(values)
        rows.append((label, shown))
        for key in NUTRIENTS:
            meal[key] += shown[key]
        if flags:
            flags_by_item[label] = flags
    today = {k: prior[k] + meal[k] for k in NUTRIENTS}
    return rows, meal, today, targets, flags_by_item


def render_log(rows, meal, today, targets, flags_by_item):
    t = {k: float(targets.get(k, 0) or 0) for k in TARGET_KEYS}
    have_targets = all(t[k] > 0 for k in ("kcal", "protein", "carbs", "fat"))

    def head(name, key, unit):
        if not have_targets:
            return name
        return f"{name} ({fmt_kcal(t[key])})" if key == "kcal" else f"{name} ({int(t[key])}{unit})"

    lines = [
        f"| Item | {head('Cal', 'kcal', '')} | {head('Protein', 'protein', 'g')} | "
        f"{head('Carbs', 'carbs', 'g')} | {head('Fat', 'fat', 'g')} |",
        "|---|---|---|---|---|",
    ]
    for label, v in rows:
        lines.append(f"| {label} | {fmt_kcal(v['kcal'])} | {fmt_g(v['protein'])} | {fmt_g(v['carbs'])} | {fmt_g(v['fat'])} |")
    if meal is not None:
        lines.append(f"| **This meal** | **{fmt_kcal(meal['kcal'])}** | **{fmt_g(meal['protein'])}** | "
                     f"**{fmt_g(meal['carbs'])}** | **{fmt_g(meal['fat'])}** |")
    lines.append(f"| **Today so far** | **{fmt_kcal(today['kcal'])}** | **{fmt_g(today['protein'])}** | "
                 f"**{fmt_g(today['carbs'])}** | **{fmt_g(today['fat'])}** |")
    if have_targets:
        lines.append(f"| **% of target** | **{pct(today['kcal'], t['kcal'])}** | **{pct(today['protein'], t['protein'])}** | "
                     f"**{pct(today['carbs'], t['carbs'])}** | **{pct(today['fat'], t['fat'])}** |")
        lines.append(f"| **Remaining** | **{signed(t['kcal'] - today['kcal'])}** | **{signed(t['protein'] - today['protein'], 'g')}** | "
                     f"**{signed(t['carbs'] - today['carbs'], 'g')}** | **{signed(t['fat'] - today['fat'], 'g')}** |")
    lines.append("")
    lines.append("| | Today | Target |")
    lines.append("|---|---|---|")
    fiber_t = f"{int(t['fiber'])}g+" if t["fiber"] else "set targets"
    sugar_t = f"under {int(t['added_sugar'])}g" if t["added_sugar"] else "set targets"
    sodium_t = f"under {int(t['sodium']):,}mg" if t["sodium"] else "under 2,300mg"
    lines.append(f"| Fiber | {fmt_g(today['fiber'])} | {fiber_t} |")
    lines.append(f"| Added sugar | {fmt_g(today['added_sugar'])} | {sugar_t} |")
    lines.append(f"| Sodium | ~{int(today['sodium']):,}mg | {sodium_t} |")
    if today["alcohol"] > 0:
        lines.append("")
        lines.append(f"Includes {fmt_g(today['alcohol'])} alcohol today ({fmt_kcal(today['alcohol'] * 7)} kcal), "
                     "which is in calories but not in the protein, carb or fat columns.")
    estimates = [label for label, flags in flags_by_item.items() if "estimate" in flags]
    unknown = sorted({f.split("-", 1)[1] for flags in flags_by_item.values() for f in flags if f.startswith("no-")})
    matched = dict(f.split(":", 1)[1].split("=>", 1) for flags in flags_by_item.values()
                   for f in flags if f.startswith("matched:"))
    lines.append("")
    lines.append("CHECKS " + json.dumps({"matched_queries": matched, "estimated_items": estimates,
                                        "nutrients_not_counted": unknown}))
    totals = {k: (int(today[k]) if float(today[k]).is_integer() else round(today[k], 1)) for k in NUTRIENTS}
    lines.append("TODAY_JSON " + json.dumps(totals, separators=(",", ":")))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------------

KATORI_G = KATORI_ML  # cooked dishes are close to 1 g per ml
CUP_G = CUP_ML


def build_recipe(payload, foods, measures):
    ingredients = payload.get("ingredients") or []
    if not ingredients:
        raise InputError("A recipe needs an 'ingredients' list.")
    servings = float(payload.get("servings") or 0)
    cooked = payload.get("cooked_weight_g")
    cooked = float(cooked) if cooked else None
    if servings <= 0 and not cooked:
        raise InputError("Give 'servings' (how many portions the batch makes) or 'cooked_weight_g'.")
    rows, total = [], {k: 0.0 for k in NUTRIENTS}
    raw_weight = 0.0
    for ing in ingredients:
        label, values, _ = resolve_item(ing, foods, measures)
        grams = None
        fid = ing.get("food")
        if fid and fid in foods:
            if "grams" in ing:
                grams = float(ing["grams"])
            elif "unit" in ing:
                grams = to_grams(fid, ing.get("qty", 1), ing["unit"], measures, foods)
            elif fid not in ZERO_FOODS:
                grams = float(ing.get("servings", 1)) * foods[fid]["serving_g"]
        if grams:
            raw_weight += grams
        rows.append((label, grams, values))
        for key in NUTRIENTS:
            total[key] += values[key]
    return rows, total, servings, cooked, raw_weight


def _per(total, divisor):
    return {k: total[k] / divisor for k in NUTRIENTS}


def render_recipe(name, rows, total, servings, cooked, raw_weight):
    lines = [f"Recipe: {name}", "",
             "| Ingredient | Grams | Cal | Protein | Carbs | Fat |",
             "|---|---|---|---|---|---|"]
    for label, grams, v in rows:
        grams_text = f"{grams:,.0f}" if grams else "-"
        lines.append(f"| {label} | {grams_text} | {fmt_kcal(v['kcal'])} | {v['protein']:.1f}g | {v['carbs']:.1f}g | {v['fat']:.1f}g |")
    lines.append(f"| **Whole batch** | **{raw_weight:,.0f} raw** | **{fmt_kcal(total['kcal'])}** | **{total['protein']:.0f}g** | "
                 f"**{total['carbs']:.0f}g** | **{total['fat']:.0f}g** |")
    lines.append("")
    portions = []
    if servings > 0:
        portions.append((f"1 serving (1/{servings:g} of the batch)", _per(total, servings)))
    if cooked:
        portions.append(("100 g cooked", _per(total, cooked / 100.0)))
        portions.append((f"1 katori (~{KATORI_G} g)", _per(total, cooked / KATORI_G)))
        portions.append((f"1 cup (~{CUP_G} g)", _per(total, cooked / CUP_G)))
    lines.append("| Portion | Cal | Protein | Carbs | Fat | Fiber | Added sugar | Sodium |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for label, v in portions:
        lines.append(f"| {label} | {fmt_kcal(round5(v['kcal']))} | {fmt_g(v['protein'])} | {fmt_g(v['carbs'])} | "
                     f"{fmt_g(v['fat'])} | {fmt_g(v['fiber'])} | {fmt_g(v['added_sugar'])} | ~{int(round(v['sodium'], -1)):,}mg |")
    lines.append("")
    if total["sodium"] < 50:
        lines.append("Note: no salt listed, so sodium is near zero. Add the salt (for example 1 tsp) for a real sodium figure.")
    if not cooked:
        lines.append("Tip: weigh the empty pot, then the pot with the finished dish. The difference is the "
                     "cooked weight, and per-100 g values become exact for any portion you weigh.")
    if servings > 0:
        per = _per(total, servings)
        item = {"name": f"{name} (1 serving)", **{k: round(per[k], 1) for k in NUTRIENTS if k != "alcohol"}}
        lines.append("LOG_ITEM_JSON " + json.dumps(item, separators=(",", ":")))
    if cooked:
        per100 = _per(total, cooked / 100.0)
        lines.append("PER_100G_JSON " + json.dumps({k: round(per100[k], 2) for k in NUTRIENTS if k != "alcohol"},
                                                    separators=(",", ":")))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plan check
# ---------------------------------------------------------------------------

def build_plan(payload, foods, measures):
    meals = payload.get("meals") or []
    if not meals:
        raise InputError("A plan needs a 'meals' list.")
    targets = {k: float((payload.get("targets") or {}).get(k, 0) or 0) for k in TARGET_KEYS}
    if not all(targets[k] > 0 for k in ("kcal", "protein")):
        raise InputError("A plan needs targets with at least kcal and protein.")
    out, day = [], {k: 0.0 for k in NUTRIENTS}
    for meal in meals:
        meal_total = {k: 0.0 for k in NUTRIENTS}
        labels = []
        for item in meal.get("items") or []:
            label, values, _ = resolve_item(item, foods, measures)
            shown = _round_item(values)
            labels.append(label)
            for key in NUTRIENTS:
                meal_total[key] += shown[key]
        for key in NUTRIENTS:
            day[key] += meal_total[key]
        out.append((meal.get("meal", "Meal"), labels, meal_total))
    return out, day, targets


def plan_checks(day, targets):
    """Return (label, passed, detail, core). Core checks decide PLAN_OK; the rest are advisory.

    Sodium, fiber and added sugar are advisory because typical Indian home cooking runs
    3,000-4,000 mg sodium a day; failing every plan on it would hide the checks that matter
    for the targets. The plan still reports them so the reply can flag them plainly.
    """
    checks = []
    kcal_gap = (day["kcal"] - targets["kcal"]) / targets["kcal"]
    checks.append(("Calories within 5% of target", abs(kcal_gap) <= PLAN_KCAL_TOLERANCE,
                   f"{fmt_kcal(day['kcal'])} vs {fmt_kcal(targets['kcal'])} ({kcal_gap * 100:+.0f}%)", True))
    checks.append(("Protein at least 95% of target", day["protein"] >= PLAN_PROTEIN_MIN_SHARE * targets["protein"],
                   f"{day['protein']:.0f}g vs {targets['protein']:.0f}g", True))
    fat_share = day["fat"] * 9 / day["kcal"] if day["kcal"] else 0
    low, high = PLAN_FAT_SHARE_RANGE
    checks.append(("Fat 20-35% of calories", low <= fat_share <= high, f"{fat_share * 100:.0f}%", True))
    if targets["fiber"]:
        checks.append(("Fiber at or above target", day["fiber"] >= targets["fiber"],
                       f"{day['fiber']:.0f}g vs {targets['fiber']:.0f}g", False))
    if targets["added_sugar"]:
        checks.append(("Added sugar under limit", day["added_sugar"] <= targets["added_sugar"],
                       f"{day['added_sugar']:.0f}g vs under {targets['added_sugar']:.0f}g", False))
    sodium_limit = targets["sodium"] or SODIUM_LIMIT_MG
    checks.append(("Sodium under limit", day["sodium"] <= sodium_limit,
                   f"~{day['sodium']:,.0f}mg vs under {sodium_limit:,.0f}mg", False))
    return checks


def render_plan(out, day, targets):
    lines = ["| Meal | What | Cal | Protein | Carbs | Fat |", "|---|---|---|---|---|---|"]
    for name, labels, v in out:
        lines.append(f"| {name} | {'; '.join(labels)} | {fmt_kcal(v['kcal'])} | {fmt_g(v['protein'])} | "
                     f"{fmt_g(v['carbs'])} | {fmt_g(v['fat'])} |")
    lines.append(f"| **Day total** | | **{fmt_kcal(day['kcal'])}** | **{fmt_g(day['protein'])}** | "
                 f"**{fmt_g(day['carbs'])}** | **{fmt_g(day['fat'])}** |")
    lines.append(f"| **Target** | | **{fmt_kcal(targets['kcal'])}** | **{int(targets['protein'])}g** | "
                 f"**{int(targets['carbs'])}g** | **{int(targets['fat'])}g** |")
    lines.append("")
    checks = plan_checks(day, targets)
    for label, ok, detail, core in checks:
        status = "PASS" if ok else ("ADJUST" if core else "NOTE")
        lines.append(f"- {status}: {label}: {detail}")
    verdict = "PLAN_OK" if all(ok for _, ok, _, core in checks if core) else "PLAN_NEEDS_ADJUSTMENT"
    lines.append("")
    lines.append(verdict)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _height_cm(args):
    if args.height_cm:
        return args.height_cm
    inches = (args.height_ft or 0) * 12 + (args.height_in or 0)
    if inches <= 0:
        raise InputError("Give height as --height-cm, or --height-ft with --height-in.")
    return inches * 2.54


def _weight_kg(args):
    if args.weight_kg:
        return args.weight_kg
    if args.weight_lb:
        return args.weight_lb * 0.45359237
    raise InputError("Give weight as --weight-kg or --weight-lb.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("targets", help="daily targets")
    p.add_argument("--age", type=float, required=True)
    p.add_argument("--sex", choices=["male", "female", "unspecified"], required=True)
    p.add_argument("--height-cm", type=float)
    p.add_argument("--height-ft", type=float)
    p.add_argument("--height-in", type=float)
    p.add_argument("--weight-kg", type=float)
    p.add_argument("--weight-lb", type=float)
    p.add_argument("--bmr", type=float)
    p.add_argument("--bmr-source", choices=["lab", "scale", "app", "formula", "unknown"], default="unknown")
    p.add_argument("--activity", choices=list(ACTIVITY_FACTORS), required=True)
    p.add_argument("--goal", choices=list(GOAL_FACTORS), required=True)
    p.add_argument("--protein-per-kg", type=float, help="override protein g/kg")
    p.add_argument("--json", action="store_true", help="print JSON only")

    p = sub.add_parser("lookup", help="search foods")
    p.add_argument("query", nargs="+")
    p.add_argument("--kind", choices=["ingredient", "dish", "grocery", "restaurant", "drink"])
    p.add_argument("--grams", type=float)
    p.add_argument("--servings", type=float)
    p.add_argument("--limit", type=int, default=8)

    p = sub.add_parser("units", help="household units for a food id")
    p.add_argument("food_id")

    for name in ("log", "summary", "recipe", "plan"):
        p = sub.add_parser(name, help=f"{name} (JSON on stdin)")
        p.add_argument("--input", help="read JSON from this file instead of stdin")

    args = parser.parse_args(argv)
    try:
        if args.command == "targets":
            result = compute_targets(args.age, args.sex, _height_cm(args), _weight_kg(args), args.activity,
                                     args.goal, args.bmr, args.bmr_source, args.protein_per_kg)
            print(json.dumps(result, indent=2) if args.json else render_targets(result))
            return 0
        foods = load_foods()
        measures = load_measures()
        if args.command == "lookup":
            # Several foods in one call: separate them with commas ("roti, dal, bhindi").
            queries = [q.strip() for q in " ".join(args.query).split(",") if q.strip()]
            blocks = []
            for query in queries:
                matches = search_foods(foods, query, kind=args.kind, limit=args.limit)
                table = render_lookup(matches, args.grams, args.servings)
                blocks.append(f"### {query}\n{table}" if len(queries) > 1 else table)
            print("\n\n".join(blocks))
        elif args.command == "units":
            if args.food_id not in foods:
                raise InputError(f"Unknown food id '{args.food_id}'.{_suggest(foods, args.food_id)}")
            known = measures.get(args.food_id, {})
            food = foods[args.food_id]
            print(f"{args.food_id}: serving '{food['serving']}' = {food['serving_g']:g} g")
            for unit, grams in sorted(known.items()):
                print(f"- 1 {unit} = {grams:g} g")
            print("- also accepts g, kg, oz, lb")
        elif args.command == "log":
            print(render_log(*build_log(_read_payload(args.input), foods, measures)))
        elif args.command == "summary":
            payload = _read_payload(args.input)
            today = _clean_totals(payload.get("today"))
            print(render_log([], None, today, payload.get("targets") or {}, {}))
        elif args.command == "recipe":
            payload = _read_payload(args.input)
            print(render_recipe(payload.get("name", "Recipe"), *build_recipe(payload, foods, measures)))
        elif args.command == "plan":
            print(render_plan(*build_plan(_read_payload(args.input), foods, measures)))
        return 0
    except InputError as exc:
        print(f"Input problem: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
