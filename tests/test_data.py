"""Integrity checks for data/foods.csv and data/measures.csv."""

import csv
import os
import re

import pytest

from conftest import DATA

FOODS = list(csv.DictReader(open(os.path.join(DATA, "foods.csv"), newline="", encoding="utf-8")))
MEASURES = list(csv.DictReader(open(os.path.join(DATA, "measures.csv"), newline="", encoding="utf-8")))
NUMERIC = ["serving_g", "kcal", "protein_g", "carbs_g", "fat_g", "fiber_g", "added_sugar_g", "sodium_mg"]
KINDS = {"ingredient", "dish", "grocery", "restaurant", "drink"}
BASES = {"usda", "label", "recipe", "estimate"}

# Calories from macros: protein and carbs 4 kcal/g, fat 9, alcohol 7, fiber about 2.
# Labels and USDA use food-specific factors, so allow 20 kcal or 10%, whichever is larger.
ATWATER_TOLERANCE_KCAL = 20
ATWATER_TOLERANCE_SHARE = 0.10


def test_header():
    assert list(FOODS[0].keys()) == [
        "id", "name", "aliases", "kind", "category", "serving", "serving_g", "kcal", "protein_g", "carbs_g",
        "fat_g", "fiber_g", "added_sugar_g", "sodium_mg", "alcohol_g", "basis", "notes"]


def test_ids_unique_and_kebab_case():
    ids = [r["id"] for r in FOODS]
    assert len(ids) == len(set(ids))
    for food_id in ids:
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", food_id), food_id


@pytest.mark.parametrize("row", FOODS, ids=[r["id"] for r in FOODS])
def test_row_is_well_formed(row):
    assert row["kind"] in KINDS
    assert row["basis"] in BASES
    assert row["name"].strip() and row["serving"].strip()
    values = {k: float(row[k]) for k in NUMERIC}
    assert values["serving_g"] > 0
    assert all(v >= 0 for v in values.values())
    assert values["fiber_g"] <= values["carbs_g"] + 0.01
    assert values["added_sugar_g"] <= values["carbs_g"] + 0.01
    if row["kind"] == "ingredient":
        assert row["serving"] == "100 g" and values["serving_g"] == 100


@pytest.mark.parametrize("row", FOODS, ids=[r["id"] for r in FOODS])
def test_calories_match_macros(row):
    p, c, f, fib = (float(row[k]) for k in ("protein_g", "carbs_g", "fat_g", "fiber_g"))
    alcohol = float(row["alcohol_g"] or 0)
    kcal = float(row["kcal"])
    low = 4 * p + 4 * (c - fib) + 2 * fib + 9 * f + 7 * alcohol
    high = 4 * p + 4 * c + 9 * f + 7 * alcohol
    tol = max(ATWATER_TOLERANCE_KCAL, ATWATER_TOLERANCE_SHARE * kcal)
    assert low - tol <= kcal <= high + tol, f"{row['id']}: {kcal} kcal vs {low:.0f}-{high:.0f} from macros"


def test_alcohol_only_on_drinks():
    for row in FOODS:
        if row["alcohol_g"]:
            assert row["kind"] == "drink" and row["category"] == "alcohol", row["id"]


def test_measures_point_at_real_foods():
    ids = {r["id"] for r in FOODS}
    for row in MEASURES:
        assert row["food_id"] in ids, row
        assert float(row["grams"]) > 0


def test_aliases_are_clean():
    for row in FOODS:
        aliases = [a for a in row["aliases"].split("|") if a]
        assert len(aliases) == len(set(aliases)), row["id"]
        for alias in aliases:
            assert alias == alias.strip().lower(), (row["id"], alias)
