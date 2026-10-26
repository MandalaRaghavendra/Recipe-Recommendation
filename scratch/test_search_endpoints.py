import json
import urllib.request
import urllib.parse

def test_api_recipes(query):
    url = f"http://localhost:5000/api/recipes?query={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode())
            recipes = data.get("recipes", [])
            print(f"Query '{query}': {len(recipes)} recipes returned")
            for r in recipes[:3]:
                print(f"   -> [{r['recipe_id']}] {r['recipe_name']}")
    except Exception as e:
        print(f"Query '{query}' failed: {e}")

def test_pantry(ingredients):
    url = "http://localhost:5000/api/pantry-match"
    payload = json.dumps({"ingredients": ingredients}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            recipes = data.get("recipes", [])
            print(f"Pantry '{ingredients}': {len(recipes)} recipes returned")
            for r in recipes[:3]:
                print(f"   -> [{r['recipe_id']}] {r['recipe_name']} (match: {r.get('match_score_pct')}%)")
    except Exception as e:
        print(f"Pantry '{ingredients}' failed: {e}")

print("=== Testing /api/recipes with query ===")
test_api_recipes("chicken")
test_api_recipes("chicken, rice")
test_api_recipes("tomato, onion")
test_api_recipes("tomatoes")
test_api_recipes("paneer")
test_api_recipes("biryani")

print("\n=== Testing /api/pantry-match ===")
test_pantry("chicken, rice")
test_pantry("tomato, onion")
test_pantry("paneer, spinach")
