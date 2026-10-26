import json
import re

def clean_name_for_search(name):
    # Remove parenthetical translations like (Nellore Spicy Fish Fry)
    clean = re.sub(r'\(.*?\)', '', name).strip()
    return clean

data = json.load(open("ai-service/data.json", encoding="utf-8"))
print(f"Total recipes: {len(data)}")

keywords = []
for r in data:
    rid = r["recipe_id"]
    rname = r["recipe_name"]
    cuisine = r.get("cuisine", "")
    diet = r.get("diet", "")
    clean = clean_name_for_search(rname)
    keywords.append({
        "id": rid,
        "name": rname,
        "clean_name": clean,
        "cuisine": cuisine,
        "diet": diet,
        "current_img": r.get("image_link", "")
    })

with open("scratch/recipe_search_keywords.json", "w", encoding="utf-8") as f:
    json.dump(keywords, f, indent=2)

print("Saved scratch/recipe_search_keywords.json")
