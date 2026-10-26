import json

data = {r['recipe_id']: r for r in json.load(open('ai-service/data.json', encoding='utf-8'))}
duplicate_rids = [5, 7, 9, 11, 14, 15, 16, 17, 18, 19, 21, 23, 24, 41, 60, 67, 68, 70, 71, 75, 78, 80, 81, 82, 83, 86, 89, 94, 95, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 115, 117, 118, 122, 123, 124, 125, 127, 128, 129, 130, 135, 138, 140, 141, 142, 144, 149, 151, 152, 154, 155, 158, 162, 164, 165, 166, 171, 183, 185, 189, 192, 194, 196, 198]

with open("scratch/duplicate_recipes_info.txt", "w", encoding="utf-8") as f:
    for rid in duplicate_rids:
        r = data[rid]
        f.write(f"{rid} | {r['recipe_name']} | {r.get('cuisine')} | {r.get('diet')} | {r.get('meal_type')}\n")

print(f"Wrote {len(duplicate_rids)} duplicate recipes to scratch/duplicate_recipes_info.txt")
