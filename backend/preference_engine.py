from collections import defaultdict
import database as db

# ==============================================================================
# USER PREFERENCE LEARNING ENGINE
# ==============================================================================

class PreferenceEngine:
    """
    Lightweight User Preference Learning Engine:
    Learns dynamic user taste, regional cuisine, ingredient, and macro affinities
    from favorites, viewed history, eaten history, and 1-5 star reviews.
    """

    @staticmethod
    def get_user_preference_profile(user_id, recipe_lookup_fn=None):
        """
        Analyzes user's interaction history to build a lightweight preference profile.
        """
        if not user_id:
            return {
                "cuisine_affinities": {},
                "ingredient_affinities": {},
                "macro_affinities": {},
                "disliked_recipe_ids": set(),
                "liked_recipe_ids": set(),
                "favorite_recipe_ids": set(),
                "top_cuisines": [],
                "top_ingredients": []
            }

        # 1. Fetch user data
        favorites = db.get_user_favorites(user_id)
        reviews = db.get_all_user_reviews(user_id)
        recent_views = db.get_recently_viewed_recipe_ids(user_id, limit=20)
        cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=recipe_lookup_fn)

        cuisine_scores = defaultdict(float)
        ingredient_scores = defaultdict(float)
        macro_scores = defaultdict(float)
        disliked_ids = set()
        liked_ids = set()
        favorite_ids = set(str(f) for f in favorites)

        # 2. Process Favorites (High positive signal: +2.0 per recipe)
        for rid in favorites:
            r = recipe_lookup_fn(str(rid)) if recipe_lookup_fn else None
            if r:
                liked_ids.add(str(rid))
                cuisine = str(r.get("cuisine", "")).strip()
                if cuisine:
                    cuisine_scores[cuisine] += 2.0
                
                goal = str(r.get("diet_goal", "")).lower()
                if "protein" in goal:
                    macro_scores["high_protein"] += 2.0
                if "weight loss" in goal:
                    macro_scores["weight_loss"] += 2.0

                for ing in r.get("ingredients", []):
                    clean_ing = str(ing).lower().strip()
                    if clean_ing:
                        ingredient_scores[clean_ing] += 1.0

        # 3. Process Eaten / Cooked History (Medium positive signal: +1.5 per log)
        for entry in cooked:
            rid = str(entry.get("recipe_id", ""))
            r = recipe_lookup_fn(rid) if recipe_lookup_fn else None
            if r:
                cuisine = str(r.get("cuisine", "")).strip()
                if cuisine:
                    cuisine_scores[cuisine] += 1.5

                goal = str(r.get("diet_goal", "")).lower()
                if "protein" in goal:
                    macro_scores["high_protein"] += 1.5

                for ing in r.get("ingredients", []):
                    clean_ing = str(ing).lower().strip()
                    if clean_ing:
                        ingredient_scores[clean_ing] += 0.8

        # 4. Process Reviews (Rating-dependent)
        for rid, rev in reviews.items():
            rating = int(rev.get("rating", 3))
            r = recipe_lookup_fn(str(rid)) if recipe_lookup_fn else None
            if not r:
                continue

            if rating >= 4:
                liked_ids.add(str(rid))
                boost = (rating - 3) * 2.0 # 4 stars -> +2.0, 5 stars -> +4.0
                cuisine = str(r.get("cuisine", "")).strip()
                if cuisine:
                    cuisine_scores[cuisine] += boost

                for ing in r.get("ingredients", []):
                    clean_ing = str(ing).lower().strip()
                    if clean_ing:
                        ingredient_scores[clean_ing] += (boost * 0.5)

            elif rating <= 2:
                # Soft negative signal: Do NOT permanently exclude; mark as low preference
                disliked_ids.add(str(rid))
                penalty = (3 - rating) * 1.5 # 2 stars -> -1.5, 1 star -> -3.0
                cuisine = str(r.get("cuisine", "")).strip()
                if cuisine:
                    cuisine_scores[cuisine] = max(0.0, cuisine_scores[cuisine] - penalty)

        # 5. Process Recently Viewed (Mild interest signal: +0.5)
        for rid in recent_views:
            r = recipe_lookup_fn(str(rid)) if recipe_lookup_fn else None
            if r:
                cuisine = str(r.get("cuisine", "")).strip()
                if cuisine:
                    cuisine_scores[cuisine] += 0.5

        # Normalize top preferences
        top_cuisines = sorted(cuisine_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_ingredients = sorted(ingredient_scores.items(), key=lambda x: x[1], reverse=True)[:8]

        return {
            "cuisine_affinities": dict(cuisine_scores),
            "ingredient_affinities": dict(ingredient_scores),
            "macro_affinities": dict(macro_scores),
            "disliked_recipe_ids": disliked_ids,
            "liked_recipe_ids": liked_ids,
            "favorite_recipe_ids": favorite_ids,
            "top_cuisines": [c[0] for c in top_cuisines],
            "top_ingredients": [i[0] for i in top_ingredients]
        }

    @staticmethod
    def compute_recipe_preference_score(recipe, profile):
        """
        Calculates a dynamic preference multiplier / score in [0.2, 1.0] for a given recipe.
        - Neutral baseline: 0.5
        - Boosted for preferred cuisines, high-protein favorites, liked ingredients: up to 1.0
        - Soft penalty for 1-2 star reviewed recipes: ~0.35 (Never 0.0, not permanently excluded).
        """
        if not profile or not recipe:
            return 0.5

        rid = str(recipe.get("recipe_id", ""))
        
        # Soft negative check
        if rid in profile.get("disliked_recipe_ids", set()):
            return 0.35

        score = 0.5 # Neutral baseline

        # Favorite direct match boost
        if rid in profile.get("favorite_recipe_ids", set()):
            score += 0.25

        # Cuisine affinity boost
        r_cuisine = str(recipe.get("cuisine", "")).strip()
        cuisine_affinities = profile.get("cuisine_affinities", {})
        if r_cuisine and r_cuisine in cuisine_affinities:
            c_score = cuisine_affinities[r_cuisine]
            score += min(0.20, c_score * 0.04)

        # Ingredient affinity boost
        ing_affinities = profile.get("ingredient_affinities", {})
        r_ingredients = [str(i).lower().strip() for i in recipe.get("ingredients", [])]
        matched_ing_score = sum(ing_affinities.get(i, 0.0) for i in r_ingredients)
        if matched_ing_score > 0:
            score += min(0.20, matched_ing_score * 0.03)

        # Macro affinity boost (e.g. high protein)
        macro_affinities = profile.get("macro_affinities", {})
        r_goal = str(recipe.get("diet_goal", "")).lower()
        if "protein" in r_goal and macro_affinities.get("high_protein", 0) > 0:
            score += min(0.15, macro_affinities["high_protein"] * 0.03)

        return min(1.0, max(0.2, score))

preference_engine = PreferenceEngine()
