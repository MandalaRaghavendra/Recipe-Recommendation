import json

data = json.load(open("ai-service/data.json", encoding="utf-8"))
with open("scratch/all_names.txt", "w", encoding="utf-8") as f:
    for r in data:
        f.write(f"{r['recipe_id']} | {r['recipe_name']} | {r.get('cuisine', '')} | {r.get('diet', '')} | {r.get('meal_type', '')}\n")

print(f"Dumped {len(data)} recipes to scratch/all_names.txt")
