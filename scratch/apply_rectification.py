import json
import pandas as pd
import os

JSON_PATH = r"d:\recipie\Recipe-Recommendation\ai-service\data.json"
CSV_PATH = r"d:\recipie\Recipe-Recommendation\ai-service\data_with_embeddings.csv"

# Comprehensive rectification map (recipe_id -> image_link)
RECTIFICATIONS = {
    # 1. Aloo dishes
    13: "/static/images/recipes/aloo_curry.jpg",
    33: "/static/images/recipes/aloo_fry.jpg",

    # 2. Vada
    46: "/static/images/recipes/masala_vada.jpg",

    # 3. Paneer
    54: "/static/images/recipes/palak_paneer.jpg",

    # 4. Rajma
    62: "/static/images/recipes/rajma_masala.jpg",

    # 5. Yellow Dal & Cucumber Dal
    96: "/static/images/recipes/yellow_dal.jpg",

    # 6. Chutneys & Pachadis
    126: "/static/images/recipes/green_chutney.jpg",
    127: "/static/images/recipes/tomato_chutney.jpg",
    128: "/static/images/recipes/tomato_chutney.jpg",
    129: "/static/images/recipes/green_chutney.jpg",
    131: "/static/images/recipes/green_chutney.jpg",
    132: "/static/images/recipes/ginger_chutney.jpg",
    133: "/static/images/recipes/green_chutney.jpg",
    134: "/static/images/recipes/mango_thokku.jpg",
    135: "/static/images/recipes/green_chutney.jpg",

    # 7. Pongal
    25: "/static/images/recipes/pongal.jpg",
    143: "/static/images/recipes/pongal.jpg",

    # 8. Besan Chilla
    72: "/static/images/recipes/besan_chilla.jpg",

    # 9. Egg Porutu
    87: "/static/images/recipes/egg_porutu.jpg",

    # 10. Poriyal / Stir Fries
    114: "/static/images/recipes/cabbage_poriyal.jpg",
    120: "/static/images/recipes/cabbage_poriyal.jpg",

    # 11. Sweets & Desserts
    145: "/static/images/recipes/pootharekulu.jpg",
    148: "/static/images/recipes/rava_kesari.jpg",

    # 12. Mutton Sukka & Chops
    65: "/static/images/recipes/mutton_sukka.jpg",
    93: "/static/images/recipes/mutton_sukka.jpg",

    # 13. Crab dishes
    9: "/static/images/recipes/crab_curry.jpg",
    81: "/static/images/recipes/crab_curry.jpg",

    # 14. Fish Tikka
    59: "/static/images/recipes/fish_tikka.jpg",

    # 15. Andhra Pulusu & Vegetable Stews
    107: "/static/images/recipes/andhra_pulusu.jpg",
    108: "/static/images/recipes/andhra_pulusu.jpg",
    109: "/static/images/recipes/andhra_pulusu.jpg",
    113: "/static/images/recipes/andhra_pulusu.jpg",
    122: "/static/images/recipes/andhra_pulusu.jpg",
    123: "/static/images/recipes/andhra_pulusu.jpg",
    125: "/static/images/recipes/andhra_pulusu.jpg",

    # 16. Buttermilk Rasam
    102: "/static/images/recipes/challa_charu.jpg"
}

# 1. Update data.json
with open(JSON_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

updated_count = 0
for r in recipes:
    rid = int(r["recipe_id"])
    if rid in RECTIFICATIONS:
        old_img = r.get("image_link", "")
        new_img = RECTIFICATIONS[rid]
        r["image_link"] = new_img
        updated_count += 1
        print(f"[{rid:3d}] {r['recipe_name'][:35]:35s} | OLD: {old_img[:50]}... -> NEW: {new_img}")

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(recipes, f, indent=4)
print(f"\nSuccessfully updated {updated_count} recipes in {JSON_PATH}")

# 2. Update data_with_embeddings.csv if exists
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    if "recipe_id" in df.columns and "image_link" in df.columns:
        csv_updated = 0
        for rid, new_img in RECTIFICATIONS.items():
            mask = df["recipe_id"] == rid
            if mask.any():
                df.loc[mask, "image_link"] = new_img
                csv_updated += 1
        df.to_csv(CSV_PATH, index=False)
        print(f"Successfully updated {csv_updated} recipes in {CSV_PATH}")
