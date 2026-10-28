import json
import os
import subprocess
import sys

import pytest

from conftest import DATA, ROOT, SCRIPT

TARGETS = {"kcal": 2400, "protein": 138, "carbs": 294, "fat": 75, "fiber": 34, "added_sugar": 30, "sodium": 2300}


def run_cli(*args, stdin=None):
    env = dict(os.environ, KATORI_DATA_DIR=DATA)
    return subprocess.run([sys.executable, SCRIPT, *args], input=stdin, capture_output=True, text=True, env=env)


# --- targets ---------------------------------------------------------------

def test_mifflin_known_values(m):
    assert m.mifflin_st_jeor("male", 80, 180, 30) == pytest.approx(1780)
    assert m.mifflin_st_jeor("female", 60, 165, 30) == pytest.approx(1320.25)
    assert m.mifflin_st_jeor("unspecified", 70, 170, 30) == pytest.approx(1534.5)


def test_macros_add_up_to_calories(m):
    for goal in m.GOAL_FACTORS:
        t = m.compute_targets(30, "male", 175, 78, "moderate", goal)["targets"]
        assert abs(4 * t["protein"] + 4 * t["carbs"] + 9 * t["fat"] - t["kcal"]) <= 15


def test_user_bmr_within_ten_percent_is_used(m):
    r = m.compute_targets(28, "male", 175.3, 78, "moderate", "recomp", bmr=1720, bmr_source="scale")
    assert r["bmr_used"] == 1720


def test_user_bmr_far_off_falls_back_to_formula(m):
    r = m.compute_targets(30, "male", 170, 90, "sedentary", "fat_loss", bmr=2100, bmr_source="scale")
    assert r["bmr_used"] == r["bmr_mifflin"]
    assert any("off the Mifflin-St Jeor" in n for n in r["notes"])


def test_lab_bmr_is_trusted(m):
    r = m.compute_targets(30, "male", 170, 90, "sedentary", "fat_loss", bmr=2100, bmr_source="lab")
    assert r["bmr_used"] == 2100


def test_calories_never_below_bmr(m):
    r = m.compute_targets(30, "male", 170, 90, "sedentary", "fat_loss")
    assert r["targets"]["kcal"] >= r["bmr_used"] - 5


def test_protein_uses_bmi_25_weight_when_heavier(m):
    r = m.compute_targets(35, "male", 170, 100, "light", "fat_loss")
    assert r["reference_kg"] == pytest.approx(25 * 1.7 * 1.7, abs=0.1)
    assert r["targets"]["protein"] == round(r["reference_kg"] * 1.8)


def test_minors_get_no_targets(m):
    with pytest.raises(m.InputError):
        m.compute_targets(16, "female", 160, 50, "light", "fat_loss")


def test_implausible_height_is_rejected(m):
    with pytest.raises(m.InputError):
        m.compute_targets(30, "male", 5.9, 78, "light", "recomp")


def test_targets_cli_prints_json_line():
    out = run_cli("targets", "--age", "28", "--sex", "male", "--height-ft", "5", "--height-in", "9",
                  "--weight-lb", "172", "--activity", "moderate", "--goal", "recomp")
    assert out.returncode == 0, out.stderr
    line = [l for l in out.stdout.splitlines() if l.startswith("TARGETS_JSON ")][0]
    data = json.loads(line.split(" ", 1)[1])
    assert set(data) == {"kcal", "protein", "carbs", "fat", "fiber", "added_sugar", "sodium"}


# --- lookup ----------------------------------------------------------------

@pytest.mark.parametrize("query,expected", [
    ("chapatti", "roti"), ("phulka", "roti"), ("dahi", "yogurt-whole"), ("idly", "idli"),
    ("biriyani", "biryani-chicken"), ("mutter paneer", "matar-paneer"), ("bhindi", "bhindi-masala"),
    ("fairlife", "ultrafiltered-milk"), ("old monk", "spirits"), ("kanda poha", "poha"),
])
def test_lookup_finds_common_names(m, foods, query, expected):
    ids = [f["id"] for f in m.search_foods(foods, query, limit=3)]
    assert expected in ids, ids


def test_lookup_scales_grams(m, foods):
    v = m.scale_food(foods["paneer-store"], 150 / 100)
    assert v["protein"] == pytest.approx(31.5)


# --- log -------------------------------------------------------------------

def test_log_totals_percent_and_remaining(m, foods, measures):
    payload = {"targets": TARGETS, "prior": {"kcal": 500, "protein": 20},
               "items": [{"food": "roti", "servings": 2}, {"food": "dal-home"}]}
    rows, meal, today, targets, _ = m.build_log(payload, foods, measures)
    expected_meal = m.round5(2 * foods["roti"]["kcal"]) + m.round5(foods["dal-home"]["kcal"])
    assert meal["kcal"] == expected_meal
    assert today["kcal"] == 500 + expected_meal
    text = m.render_log(rows, meal, today, targets, {})
    assert f"| **Remaining** | **{2400 - 500 - expected_meal:,}** |" in text
    assert f"**{round(100 * (500 + expected_meal) / 2400)}%**" in text


def test_summary_has_no_meal_row(m):
    text = m.render_log([], None, m._clean_totals({"kcal": 1200, "protein": 70}), TARGETS, {})
    assert "This meal" not in text and "Today so far" in text and "50%" in text


def test_katori_is_150_ml_of_a_cup_dish(m, foods, measures):
    grams = m.to_grams("dal-home", 1, "katori", measures, foods)
    assert grams == pytest.approx(150)


def test_extra_oil_adds_40_kcal_per_tsp(m, foods, measures):
    _, base, _ = m.resolve_item({"food": "bhindi-masala"}, foods, measures)
    _, oily, _ = m.resolve_item({"food": "bhindi-masala", "oil_tsp": 1}, foods, measures)
    assert oily["kcal"] - base["kcal"] == pytest.approx(39.8, abs=0.5)
    assert oily["fat"] - base["fat"] == pytest.approx(4.5, abs=0.01)


def test_unknown_food_suggests_ids(m, foods, measures):
    with pytest.raises(m.InputError) as err:
        m.resolve_item({"food": "chapatti"}, foods, measures)
    assert "roti" in str(err.value)


def test_explicit_item_needs_macros(m, foods, measures):
    with pytest.raises(m.InputError):
        m.resolve_item({"name": "Mystery curry", "kcal": 400}, foods, measures)


def test_zero_or_negative_amount_rejected(m, foods, measures):
    with pytest.raises(m.InputError):
        m.resolve_item({"food": "roti", "servings": 0}, foods, measures)


def test_alcohol_is_reported(m, foods, measures):
    rows, meal, today, targets, flags = m.build_log({"targets": TARGETS, "items": [{"food": "beer"}]}, foods, measures)
    assert "alcohol" in m.render_log(rows, meal, today, targets, flags)


def test_log_cli_reads_heredoc_json():
    payload = json.dumps({"targets": TARGETS, "items": [{"food": "idli", "servings": 3}, {"food": "sambar"}]})
    out = run_cli("log", stdin=payload)
    assert out.returncode == 0, out.stderr
    assert "TODAY_JSON" in out.stdout


def test_log_cli_reports_bad_json():
    out = run_cli("log", stdin="{not json")
    assert out.returncode == 2
    assert "Invalid JSON" in out.stderr


# --- recipe ----------------------------------------------------------------

RECIPES = os.path.join(DATA, "recipes")


@pytest.mark.parametrize("name", sorted(os.listdir(RECIPES)))
def test_recipe_rows_match_documented_recipes(m, foods, measures, name):
    """Every food marked basis=recipe must be reproducible from data/recipes/."""
    recipe = json.load(open(os.path.join(RECIPES, name), encoding="utf-8"))
    row = foods[recipe["db_id"]]
    assert row["basis"] == "recipe"
    _, total, servings, cooked, _ = m.build_recipe(recipe, foods, measures)
    if cooked and servings and abs(cooked / servings - row["serving_g"]) > 1:
        computed = {k: total[k] * row["serving_g"] / cooked for k in m.NUTRIENTS}
    else:
        computed = {k: total[k] / servings for k in m.NUTRIENTS}
    assert computed["kcal"] == pytest.approx(row["kcal"], rel=0.05)
    for key in ("protein", "carbs", "fat"):
        assert computed[key] == pytest.approx(row[key], abs=max(1.0, 0.08 * row[key]))


def test_recipe_unknown_unit_lists_known_units(m, foods, measures):
    with pytest.raises(m.InputError) as err:
        m.to_grams("toor-dal-raw", 1, "fistful", measures, foods)
    assert "cup" in str(err.value)


def test_recipe_counts_salt_sodium(m, foods, measures):
    recipe = {"servings": 4, "ingredients": [{"food": "masoor-dal-raw", "qty": 1, "unit": "cup"},
                                             {"food": "salt", "qty": 1, "unit": "tsp"}]}
    _, total, _, _, _ = m.build_recipe(recipe, foods, measures)
    assert total["sodium"] == pytest.approx(2325 + 13, abs=5)


def test_recipe_needs_servings_or_weight(m, foods, measures):
    with pytest.raises(m.InputError):
        m.build_recipe({"ingredients": [{"food": "atta", "grams": 100}]}, foods, measures)


# --- plan ------------------------------------------------------------------

def test_plan_flags_short_day(m, foods, measures):
    payload = {"targets": TARGETS, "meals": [{"meal": "Lunch", "items": [{"food": "roti", "servings": 2}]}]}
    out, day, targets = m.build_plan(payload, foods, measures)
    text = m.render_plan(out, day, targets)
    assert "PLAN_NEEDS_ADJUSTMENT" in text
    assert "ADJUST: Calories" in text


def test_plan_sodium_is_advisory(m, foods, measures):
    small = {"kcal": 300, "protein": 30, "carbs": 30, "fat": 8, "fiber": 0, "added_sugar": 0, "sodium": 2300}
    payload = {"targets": small, "meals": [{"meal": "Snack", "items": [
        {"name": "Salty shake", "kcal": 300, "protein": 30, "carbs": 30, "fat": 8, "sodium": 5000}]}]}
    text = m.render_plan(*m.build_plan(payload, foods, measures))
    assert "NOTE: Sodium" in text and "PLAN_OK" in text


def test_plan_passes_when_on_target(m, foods, measures):
    small = {"kcal": 300, "protein": 30, "carbs": 30, "fat": 8, "fiber": 0, "added_sugar": 0, "sodium": 2300}
    payload = {"targets": small, "meals": [{"meal": "Snack", "items": [
        {"name": "Test shake", "kcal": 300, "protein": 30, "carbs": 30, "fat": 8, "fiber": 0, "added_sugar": 0, "sodium": 200}]}]}
    out, day, targets = m.build_plan(payload, foods, measures)
    assert "PLAN_OK" in m.render_plan(out, day, targets)
