import json
import re
import os

PROJECT_ROOT = r"d:\recipie\Recipe-Recommendation"
DATA_PATH = os.path.join(PROJECT_ROOT, "ai-service", "data.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

PLURAL_STEMS = {
    "tomatoes": "tomato", "potatoes": "potato", "onions": "onion", "chillies": "chilli",
    "chilis": "chili", "chile": "chili", "chiles": "chili", "eggs": "egg",
    "lentils": "lentil", "mushrooms": "mushroom", "carrots": "carrot", "beans": "bean",
    "peas": "pea", "leaves": "leaf", "corianders": "coriander", "garlics": "garlic",
    "gingers": "ginger", "lemons": "lemon", "limes": "lime", "peanuts": "peanut",
    "groundnuts": "groundnut", "cashews": "cashew", "almonds": "almond", "chickpeas": "chickpea"
}

MEASUREMENT_WORDS = {
    "cup", "cups", "tbsp", "tsp", "tablespoon", "tablespoons", "teaspoon", "teaspoons",
    "gram", "grams", "gm", "g", "kg", "ml", "liter", "litres", "pinch", "handful",
    "sliced", "chopped", "diced", "grated", "crushed", "fresh", "dry", "dried", "powder",
    "paste", "raw", "cooked", "boiled", "fried", "roasted", "ripe", "boneless", "skinless",
    "medium", "large", "small", "piece", "pieces", "clove", "cloves", "bunch", "spoon",
    "of", "in", "and", "or", "with", "a", "an", "the", "to", "taste"
}

NON_VEG_WORDS = {
    "chicken", "mutton", "fish", "prawn", "prawns", "egg", "eggs", "crab",
    "meat", "lamb", "shrimp", "seafood", "keema", "boti", "liver", "pork", "beef"
}

def normalize_token(token):
    clean = re.sub(r'[^a-zA-Z]', '', token.strip().lower())
    if clean in PLURAL_STEMS:
        return PLURAL_STEMS[clean]
    if clean.endswith("s") and len(clean) > 3 and not clean.endswith("ss"):
        singular = clean[:-1]
        if singular in PLURAL_STEMS.values():
            return singular
    return clean

def parse_tokens(text):
    raw_words = re.findall(r'[a-zA-Z]+', str(text).lower())
    tokens = set()
    for w in raw_words:
        norm = normalize_token(w)
        if norm and len(norm) > 1 and norm not in MEASUREMENT_WORDS:
            tokens.add(norm)
    return tokens

def rank_recipes(query_str, all_recipes, top_n=10):
    q_clean = (query_str or "").strip().lower()
    if not q_clean:
        return all_recipes[:top_n]
        
    query_tokens = parse_tokens(q_clean)
    query_nonveg = query_tokens & NON_VEG_WORDS
    
    scored = []
    for r in all_recipes:
        r_name = str(r.get("recipe_name", "")).lower()
        r_name_tokens = parse_tokens(r_name)
        r_ings = [str(i).lower() for i in r.get("ingredients", [])]
        r_ings_tokens = set()
        for ing in r_ings:
            r_ings_tokens.update(parse_tokens(ing))
        r_ings_text = " ".join(r_ings)
        r_veg = str(r.get("veg_nonveg", "")).lower()
        r_tags = [str(t).lower() for t in r.get("nutrition_tags", [])]
        health_sc = float(r.get("health_score", 80) or 80)

        # Non-veg enforcement:
        if query_nonveg:
            if r_veg == "veg":
                continue # Strictly exclude veg dishes when non-veg meat is queried!
            if not any(nv in r_ings_tokens or nv in r_name_tokens or nv in r_ings_text for nv in query_nonveg):
                continue # Exclude dishes that don't have the requested meat!

        # Match calculation:
        matched_tokens = []
        for qt in query_tokens:
            if qt in r_name_tokens or qt in r_name:
                matched_tokens.append(qt)
            elif qt in r_ings_tokens or any(qt in ing for ing in r_ings):
                matched_tokens.append(qt)
            elif any(qt in tag for tag in r_tags):
                matched_tokens.append(qt)

        matched_tokens = list(set(matched_tokens))
        match_count = len(matched_tokens)
        
        # If query has tokens and none matched, check nutrient intents
        nutrient_match = False
        if match_count == 0:
            if "high protein" in q_clean and (float(r.get("nutritions", {}).get("protein_g", 0)) >= 20 or "high protein" in r_tags):
                nutrient_match = True
            elif "low calorie" in q_clean and (float(r.get("nutritions", {}).get("calories", 0)) <= 350 or "low calorie" in r_tags):
                nutrient_match = True
            if not nutrient_match:
                continue

        # Score computation:
        score = 0.0
        # 1. Coverage of user query terms (Dishes with MORE user terms win!)
        coverage = match_count / max(1, len(query_tokens))
        score += coverage * 350.0

        # 2. Exact match in name
        if q_clean in r_name:
            score += 150.0
        elif any(qt in r_name for qt in query_tokens):
            score += 40.0

        # 3. Ingredients match bonus
        for qt in matched_tokens:
            if qt in r_ings_tokens:
                score += 25.0

        # 4. Non-veg alignment bonus
        if query_nonveg and any(nv in r_name_tokens for nv in query_nonveg):
            score += 50.0

        # 5. Health score tie-breaker
        score += (health_sc * 0.2)

        entry = dict(r)
        pct = round(coverage * 100) if match_count > 0 else 75
        entry["match_score_pct"] = max(pct, min(100, round((match_count / max(1, len(r_ings))) * 100) + 50))
        if match_count >= len(query_tokens) and match_count > 1:
            entry["recommendation_reason"] = f"Includes all your ingredients: {', '.join(matched_tokens)}"
        elif matched_tokens:
            entry["recommendation_reason"] = f"Matches: {', '.join(matched_tokens)}"
        else:
            entry["recommendation_reason"] = "Recommended healthy meal"

        scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:top_n]]

# Test queries
print("=== Testing 'chicken, potato, rice' ===")
for r in rank_recipes("chicken, potato, rice", recipes, 5):
    print(f"[{str(r['recipe_id']):3s}] {r['recipe_name']:35s} | Reason: {r.get('recommendation_reason')}")

print("\n=== Testing 'chicken, rice' ===")
for r in rank_recipes("chicken, rice", recipes, 5):
    print(f"[{str(r['recipe_id']):3s}] {r['recipe_name']:35s} | Reason: {r.get('recommendation_reason')}")

print("\n=== Testing 'paneer, spinach' ===")
for r in rank_recipes("paneer, spinach", recipes, 5):
    print(f"[{str(r['recipe_id']):3s}] {r['recipe_name']:35s} | Reason: {r.get('recommendation_reason')}")

print("\n=== Testing 'tomatoes, onions' ===")
for r in rank_recipes("tomatoes, onions", recipes, 5):
    print(f"[{str(r['recipe_id']):3s}] {r['recipe_name']:35s} | Reason: {r.get('recommendation_reason')}")
