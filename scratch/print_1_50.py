import json

recipes = json.load(open('ai-service/data.json', encoding='utf-8'))
for r in recipes[:50]:
    rid = r['recipe_id']
    name = r['recipe_name']
    print(f"[{rid:2d}] {name}")
