#!/usr/bin/env python3
"""Compute daily calorie and macro targets for the macro-tracker skill.

Usage examples:
  python targets.py --age 28 --sex male --height-cm 175 --weight-kg 78 \
      --bmr 1720 --bmr-source scale --activity moderate --goal recomp
  python targets.py --age 28 --sex male --height-in 69 --weight-lb 172 \
      --activity light --goal fat_loss

Units: give height as --height-cm or --height-in (or --height-ft + --height-in),
weight as --weight-kg or --weight-lb. --bmr is optional; if omitted, Mifflin-St Jeor is used.
"""

import argparse
import json

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "very_active": 1.725}
GOAL = {"fat_loss": 0.80, "recomp": 0.90, "maintenance": 1.00, "lean_gain": 1.10}
PROTEIN_PER_KG = {"fat_loss": 1.8, "recomp": 1.8, "maintenance": 1.6, "lean_gain": 1.6}


def r10(x):
    return int(round(x / 10.0) * 10)


def mifflin(sex, kg, cm, age):
    base = 10 * kg + 6.25 * cm - 5 * age
    return base + 5 if sex == "male" else base - 161


def compute(age, sex, cm, kg, activity, goal, bmr=None, bmr_source="unknown"):
    msj = mifflin(sex, kg, cm, age)
    notes = []

    if bmr is None:
        bmr_used = msj
        notes.append("No BMR given; used Mifflin-St Jeor.")
    elif bmr_source == "lab":
        bmr_used = bmr
        notes.append("Used lab-measured BMR.")
    else:
        diff = (bmr - msj) / msj
        if abs(diff) <= 0.10:
            bmr_used = bmr
            notes.append(f"User BMR is within 10% of Mifflin-St Jeor ({msj:.0f}); used user BMR.")
        else:
            bmr_used = msj
            notes.append(
                f"User BMR {bmr:.0f} differs from Mifflin-St Jeor {msj:.0f} by {diff*100:+.0f}%; "
                "used Mifflin-St Jeor. User can override."
            )

    tdee = bmr_used * ACTIVITY[activity]
    cal = tdee * GOAL[goal]
    if cal < bmr_used:
        cal = bmr_used
        notes.append("Goal calories fell below BMR; floored at BMR.")

    m = cm / 100.0
    bmi = kg / (m * m)
    ref_kg = min(kg, 25 * m * m)
    if ref_kg < kg:
        notes.append(f"BMI above 25; protein and fat floor based on {ref_kg:.1f} kg reference weight.")

    protein = ref_kg * PROTEIN_PER_KG[goal]
    fat = max(cal * 0.28 / 9, ref_kg * 0.6)
    carbs = (cal - protein * 4 - fat * 9) / 4
    if carbs < 0:
        carbs = 0
        notes.append("Protein and fat already exceed calorie target; review inputs.")

    if bmi >= 27.5:
        asian = "high risk (WHO Asian action point 27.5)"
    elif bmi >= 23:
        asian = "increased risk (WHO Asian action point 23)"
    else:
        asian = "below Asian action point 23"

    cal_r = r10(cal)
    return {
        "bmr_mifflin": round(msj),
        "bmr_used": round(bmr_used),
        "tdee": r10(tdee),
        "calories": cal_r,
        "protein_g": round(protein),
        "carbs_g": round(carbs),
        "fat_g": round(fat),
        "fiber_g_min": round(cal_r / 1000 * 14),
        "added_sugar_g_max": round(cal_r * 0.10 / 4),
        "sodium_mg_max": 2300,
        "bmi": round(bmi, 1),
        "bmi_asian_note": asian,
        "notes": notes,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--age", type=float, required=True)
    p.add_argument("--sex", choices=["male", "female"], required=True)
    p.add_argument("--height-cm", type=float)
    p.add_argument("--height-ft", type=float, default=0)
    p.add_argument("--height-in", type=float, default=0)
    p.add_argument("--weight-kg", type=float)
    p.add_argument("--weight-lb", type=float)
    p.add_argument("--bmr", type=float)
    p.add_argument("--bmr-source", choices=["lab", "scale", "app", "formula", "unknown"], default="unknown")
    p.add_argument("--activity", choices=list(ACTIVITY), required=True)
    p.add_argument("--goal", choices=list(GOAL), required=True)
    a = p.parse_args()

    cm = a.height_cm if a.height_cm else (a.height_ft * 12 + a.height_in) * 2.54
    kg = a.weight_kg if a.weight_kg else (a.weight_lb or 0) * 0.45359237
    if cm <= 0 or kg <= 0:
        p.error("Provide height and weight.")

    print(json.dumps(compute(a.age, a.sex, cm, kg, a.activity, a.goal, a.bmr, a.bmr_source), indent=2))


if __name__ == "__main__":
    main()
