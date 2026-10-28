import os
import re
import json
import math
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_MODEL_AVAILABLE = True
except ImportError:
    SENTENCE_MODEL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data.json')
EMBEDDINGS_PATH = os.path.join(BASE_DIR, 'bert_embeddings.npy')

DEFAULT_SCORING_WEIGHTS = {
    "semantic_similarity": 0.35,
    "ingredient_match": 0.20,
    "nutrition_goal": 0.15,
    "diet_preference": 0.10,
    "health_score": 0.10,
    "user_history": 0.05,
    "user_rating": 0.05
}

# Stopwords & common culinary measurement units to strip during normalization
MEASUREMENT_WORDS = {
    "cup", "cups", "tbsp", "tsp", "tablespoon", "tablespoons", "teaspoon", "teaspoons",
    "gram", "grams", "gm", "g", "kg", "ml", "liter", "litres", "pinch", "handful",
    "sliced", "chopped", "diced", "grated", "crushed", "fresh", "dry", "dried", "powder",
    "paste", "raw", "cooked", "boiled", "fried", "roasted", "ripe", "boneless", "skinless",
    "medium", "large", "small", "piece", "pieces", "clove", "cloves", "bunch", "spoon",
    "of", "in", "and", "or", "with", "a", "an", "the", "to", "taste"
}

PLURAL_STEMS = {
    "tomatoes": "tomato", "potatoes": "potato", "onions": "onion", "chillies": "chilli",
    "chilis": "chili", "chile": "chili", "chiles": "chili", "eggs": "egg",
    "lentils": "lentil", "mushrooms": "mushroom", "carrots": "carrot", "beans": "bean",
    "peas": "pea", "leaves": "leaf", "corianders": "coriander", "garlics": "garlic",
    "gingers": "ginger", "lemons": "lemon", "limes": "lime", "peanuts": "peanut",
    "groundnuts": "groundnut", "cashews": "cashew", "almonds": "almond", "chickpeas": "chickpea"
}

NON_VEG_WORDS = {
    "chicken", "mutton", "fish", "prawn", "prawns", "egg", "eggs", "crab",
    "meat", "lamb", "shrimp", "seafood", "keema", "boti", "liver", "pork", "beef"
}

def normalize_token(token):
    """Normalizes a single ingredient word (strips punctuation & maps plurals)."""
    clean = re.sub(r'[^a-zA-Z]', '', token.strip().lower())
    if clean in PLURAL_STEMS:
        return PLURAL_STEMS[clean]
    if clean.endswith("s") and len(clean) > 3 and not clean.endswith("ss"):
        singular = clean[:-1]
        if singular in PLURAL_STEMS.values():
            return singular
    return clean

def parse_ingredient_tokens(text):
    """Extracts clean set of semantic ingredient words from text/ingredient string."""
    raw_words = re.findall(r'[a-zA-Z]+', str(text).lower())
    tokens = set()
    for w in raw_words:
        norm = normalize_token(w)
        if norm and len(norm) > 2 and norm not in MEASUREMENT_WORDS:
            tokens.add(norm)
    return tokens

class EmbeddingEngine:
    """Manages recipe dataset, precomputed BERT embeddings, and Tastio 2.0 AI Recommendation & Pantry Matching."""

    def __init__(self, data_path=DATA_PATH, embeddings_path=EMBEDDINGS_PATH):
        self.data_path = data_path
        self.embeddings_path = embeddings_path
        self.data = pd.DataFrame()
        self.recipes_by_id = {}
        self.embeddings = None
        self.embedding_id_map = {}
        self.model = None
        self.load_dataset()
        self.load_embeddings()

    def _index_recipes(self, df):
        indexed = {}
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                r_dict = row.to_dict()
                for key in ['ingredients', 'steps']:
                    if key in r_dict and not isinstance(r_dict[key], list):
                        try:
                            r_dict[key] = json.loads(str(r_dict[key]).replace("'", '"'))
                        except (json.JSONDecodeError, AttributeError, TypeError):
                            r_dict[key] = [r_dict[key]] if r_dict[key] else []
                indexed[str(r_dict.get('recipe_id'))] = r_dict
        return indexed

    def load_dataset(self):
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data_list = json.load(f)
                self.data = pd.DataFrame(data_list)
            elif os.path.exists(os.path.join(BASE_DIR, 'data_with_embeddings.csv')):
                self.data = pd.read_csv(os.path.join(BASE_DIR, 'data_with_embeddings.csv'))

            if not self.data.empty:
                for col in ['ingredients', 'steps']:
                    if col in self.data.columns:
                        self.data[col] = self.data[col].apply(lambda x: x if isinstance(x, list) else [])
                if 'recipe_id' in self.data.columns:
                    self.data['recipe_id'] = self.data['recipe_id'].astype(str)
                self.recipes_by_id = self._index_recipes(self.data)
                print(f"[AI Service] Loaded {len(self.data)} recipes into memory.")
        except Exception as e:
            print(f"[AI Service] Error loading data: {e}")
            self.data = pd.DataFrame()
            self.recipes_by_id = {}

    def load_embeddings(self):
        try:
            if os.path.exists(self.embeddings_path):
                self.embeddings = np.load(self.embeddings_path)
                print(f"[AI Service] Loaded BERT Embeddings: {self.embeddings.shape}")
                if not self.data.empty and self.data.shape[0] == self.embeddings.shape[0]:
                    self.embedding_id_map = {str(recipe_id): i for i, recipe_id in enumerate(self.data['recipe_id'])}
        except Exception as e:
            print(f"[AI Service] Error loading embeddings: {e}")
            self.embeddings = None

    def get_recipe_by_id(self, recipe_id):
        """O(1) Instant Recipe Retrieval"""
        return self.recipes_by_id.get(str(recipe_id))

    def get_all_recipes(self):
        """Returns all recipe records."""
        return list(self.recipes_by_id.values())

    def search_by_ingredients(self, query_str, top_n=10):
        """Fast multi-keyword scoring for direct search queries with token stemming and non-veg intelligence."""
        if not query_str or not self.recipes_by_id:
            return []

        clean_query = query_str.strip().lower()
        query_tokens = parse_ingredient_tokens(clean_query)
        if not query_tokens:
            return []

        query_nonveg = query_tokens & NON_VEG_WORDS

        scored_recipes = []
        for rid, r in self.recipes_by_id.items():
            name = str(r.get("recipe_name", "")).lower()
            name_tokens = parse_ingredient_tokens(name)
            ingredients = [str(i).lower() for i in r.get("ingredients", [])]
            r_ings_tokens = set()
            for ing in ingredients:
                r_ings_tokens.update(parse_ingredient_tokens(ing))
            r_ings_text = " ".join(ingredients)
            veg = str(r.get("veg_nonveg", "")).lower()
            health_score = float(r.get("health_score", 80) or 80)

            PROTEIN_CLUSTERS = [
                {"egg", "eggs", "guddu", "anda"},
                {"chicken", "kodi", "murgh"},
                {"mutton", "lamb", "goat", "gosht"},
                {"fish", "chepa", "chepala", "machli", "salmon"},
                {"prawn", "prawns", "royyalu", "shrimp"},
                {"crab", "peethala"},
                {"paneer"},
                {"tofu"},
            ]
            queried_protein_clusters = [cluster for cluster in PROTEIN_CLUSTERS if (cluster & query_tokens)]

            # Non-veg keyword enforcement:
            if query_nonveg:
                if veg == "veg":
                    continue
                if not any(nv in r_ings_tokens or nv in name_tokens or nv in r_ings_text for nv in query_nonveg):
                    continue
            else:
                # If query did not ask for any non-veg/meat/fish ingredient, avoid recommending non-veg dishes
                if veg == "non-veg":
                    continue

            # Protein cluster exclusivity:
            if queried_protein_clusters:
                has_queried = any(any(p in name or p in r_ings_text for p in qc) for qc in queried_protein_clusters)
                if not has_queried:
                    continue
                has_conflict = False
                for other_cluster in PROTEIN_CLUSTERS:
                    if other_cluster not in queried_protein_clusters:
                        has_other = any(p in name or p in r_ings_text for p in other_cluster)
                        if has_other:
                            has_conflict = True
                            break
                if has_conflict:
                    continue

            matched_tokens = [qt for qt in query_tokens if qt in name_tokens or qt in name or qt in r_ings_tokens or any(qt in ing for ing in ingredients)]
            matched_unique = list(set(matched_tokens))
            match_count = len(matched_unique)

            if match_count == 0 and clean_query not in name and clean_query not in r_ings_text:
                continue

            coverage = match_count / max(1, len(query_tokens))
            score = coverage * 350.0

            title_matches = [qt for qt in query_tokens if qt in name_tokens or qt in name]
            if clean_query in name:
                score += 300.0
            elif len(title_matches) == len(query_tokens) and len(query_tokens) > 1:
                score += 250.0
            elif len(title_matches) > 0:
                score += len(title_matches) * 50.0

            for qt in matched_unique:
                if qt in r_ings_tokens:
                    score += 25.0

            if query_nonveg and any(nv in name_tokens for nv in query_nonveg):
                score += 50.0

            score += (health_score * 0.2)

            entry = dict(r)
            pct = round(coverage * 100) if match_count > 0 else 75
            entry["match_score_pct"] = max(pct, min(100, round((match_count / max(1, len(ingredients))) * 100) + 50))
            if match_count >= len(query_tokens) and match_count > 1:
                entry["recommendation_reason"] = f"Includes all your ingredients: {', '.join(matched_unique)}"
            elif matched_unique:
                entry["recommendation_reason"] = f"Matches: {', '.join(matched_unique)}"
            else:
                entry["recommendation_reason"] = "Recommended dish based on search"

            scored_recipes.append((score, entry))

        if scored_recipes:
            scored_recipes.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in scored_recipes[:top_n]]

        return []

    def recommend_semantic(self, query_str, top_n=10):
        """Generic fallback semantic recommendation for anonymous users."""
        if not query_str or not self.recipes_by_id:
            return self.get_all_recipes()[:top_n]

        keyword_matches = self.search_by_ingredients(query_str, top_n=top_n)
        if keyword_matches:
            return keyword_matches

        if self.embeddings is not None:
            if SENTENCE_MODEL_AVAILABLE and self.model is None:
                try:
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception:
                    self.model = None

            if self.model is not None:
                try:
                    query_vec = self.model.encode([query_str])
                    sim_scores = cosine_similarity(query_vec, self.embeddings)[0]
                    top_indices = np.argsort(sim_scores)[::-1][:top_n]
                    return [self.get_recipe_by_id(self.data.iloc[i]['recipe_id']) for i in top_indices if self.get_recipe_by_id(self.data.iloc[i]['recipe_id'])]
                except Exception as e:
                    print(f"Error during semantic embedding search: {e}")

        return self.get_all_recipes()[:top_n]

    def _generate_explanation(self, recipe, user_profile, query_str, scores):
        """Generates dynamic, human-readable AI rationale for recommending this dish."""
        reasons = []
        nutr = recipe.get("nutritions", {}) or {}
        cal = int(nutr.get("calories", 0) or 0)
        prot = int(nutr.get("protein_g", 0) or 0)
        goal = (user_profile.get("diet_goal") or "").lower() if user_profile else ""
        pref = (user_profile.get("food_pref") or "").lower() if user_profile else ""

        if query_str and scores.get("ingredient", 0) > 0.4:
            reasons.append(f"contains ingredients matching '{query_str}'")

        if goal == "weight_loss" and cal > 0:
            if cal <= 400:
                reasons.append(f"low-calorie portion ({cal} kcal) ideal for weight loss deficit")
            else:
                reasons.append("balanced nutrient density for healthy calorie control")
        elif goal == "muscle_gain" and prot > 0:
            reasons.append(f"high protein content ({prot}g protein) supporting lean muscle gain")
        elif goal == "maintenance":
            reasons.append("optimal macronutrient balance for stable daily energy")

        if pref == "veg" and str(recipe.get("veg_nonveg", "")).lower() == "veg":
            reasons.append("100% vegetarian")

        health_sc = int(recipe.get("health_score", 0) or 0)
        if health_sc >= 85:
            reasons.append(f"top health score ({health_sc}/100)")

        if not reasons:
            reasons.append(f"aligned with your nutrition goals ({cal} kcal, {prot}g protein)")

        return f"Recommended because it {', and '.join(reasons[:2])}."

    def recommend_personalized(self, query_str="", user_profile=None, user_history=None, user_reviews=None, preference_profile=None, top_n=10, weights=None):
        """Tastio 2.0: Multi-factor Weighted Personalized AI Recommendation Engine."""
        if not self.recipes_by_id:
            return []

        if not user_profile and not query_str:
            results = self.get_all_recipes()[:top_n]
            for r in results:
                r_dict = dict(r)
                r_dict["recommendation_reason"] = "Popular recipe with high health score and balanced nutrients."
            return results

        if not user_profile:
            results = self.recommend_semantic(query_str, top_n=top_n)
            for r in results:
                r_dict = dict(r)
                r_dict["recommendation_reason"] = f"Matches your search for '{query_str}'."
            return results

        return self.recommend(
            user_profile=user_profile,
            query_str=query_str,
            user_history=user_history,
            user_reviews=user_reviews,
            preference_profile=preference_profile,
            top_n=top_n,
            weights=weights
        )

    def recommend(self, user_profile=None, query_str="", user_history=None, user_reviews=None, preference_profile=None, top_n=10, weights=None):
        """
        Calculates multidimensional recommendation score combining BERT semantics,
        ingredient matching, nutritional goal alignment, dietary constraints,
        historical ratings, and learned user preferences (cuisines, ingredients, macros).
        """
        w = dict(DEFAULT_SCORING_WEIGHTS)
        if weights and isinstance(weights, dict):
            w.update(weights)

        user_profile = user_profile or {}
        diet_goal = str(user_profile.get("diet_goal", "weight_loss")).lower()
        food_pref = str(user_profile.get("food_pref", "both")).lower()
        allergies_raw = user_profile.get("allergies", [])
        if isinstance(allergies_raw, str):
            allergies = [a.strip().lower() for a in allergies_raw.split(",") if a.strip()]
        elif isinstance(allergies_raw, list):
            allergies = [str(a).strip().lower() for a in allergies_raw if str(a).strip()]
        else:
            allergies = []

        history_ids = set()
        if user_history and isinstance(user_history, list):
            for h in user_history:
                if isinstance(h, dict) and "recipe_id" in h:
                    history_ids.add(str(h["recipe_id"]))
                elif isinstance(h, str):
                    history_ids.add(str(h))

        reviews_map = {}
        if user_reviews and isinstance(user_reviews, dict):
            reviews_map = {str(k): dict(v) for k, v in user_reviews.items()}

        target_daily_cal = float(user_profile.get("target_calories") or 1800)
        target_meal_cal = target_daily_cal / 3.0

        query_sim_map = {}
        clean_query = (query_str or "").strip().lower()
        if clean_query and self.embeddings is not None:
            if SENTENCE_MODEL_AVAILABLE and self.model is None:
                try:
                    self.model = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception:
                    self.model = None
            if self.model is not None:
                try:
                    q_vec = self.model.encode([clean_query])
                    sims = cosine_similarity(q_vec, self.embeddings)[0]
                    for rid, idx in self.embedding_id_map.items():
                        query_sim_map[str(rid)] = float(sims[idx])
                except Exception as e:
                    print(f"[AI Service] Vector computation error: {e}")

        query_terms = [t.strip() for t in clean_query.replace(",", " ").split() if t.strip()]
        scored_candidates = []

        for rid, r in self.recipes_by_id.items():
            r_veg = str(r.get("veg_nonveg", "")).lower()
            r_name = str(r.get("recipe_name", "")).lower()
            r_ingredients = [str(i).lower() for i in r.get("ingredients", [])]
            r_ing_text = " ".join(r_ingredients)
            r_nutr = r.get("nutritions", {}) or {}
            r_cal = float(r_nutr.get("calories", 350) or 350)
            r_prot = float(r_nutr.get("protein_g", 15) or 15)
            r_health = float(r.get("health_score", 80) or 80)
            r_diet = str(r.get("diet_goal", "")).lower()

            if food_pref == "veg":
                if r_veg == "non-veg":
                    continue
                non_veg_keywords = ["chicken", "mutton", "fish", "prawn", "egg", "meat", "shrimp", "crab"]
                if any(kw in r_ing_text or kw in r_name for kw in non_veg_keywords):
                    continue

            is_allergic = False
            for allergy in allergies:
                if allergy and any(allergy in ing for ing in r_ingredients):
                    is_allergic = True
                    break
                elif allergy and allergy in r_ing_text:
                    is_allergic = True
                    break
            if is_allergic:
                continue

            if clean_query:
                PROTEIN_CLUSTERS = [
                    {"egg", "eggs", "guddu", "anda"},
                    {"chicken", "kodi", "murgh"},
                    {"mutton", "lamb", "goat", "gosht"},
                    {"fish", "chepa", "chepala", "machli", "salmon"},
                    {"prawn", "prawns", "royyalu", "shrimp"},
                    {"crab", "peethala"},
                    {"paneer"},
                    {"tofu"},
                ]
                queried_protein_clusters = [cluster for cluster in PROTEIN_CLUSTERS if any(term in cluster for term in query_terms)]
                if queried_protein_clusters:
                    has_queried = any(any(p in r_name or p in r_ing_text for p in qc) for qc in queried_protein_clusters)
                    if not has_queried:
                        continue
                    has_conflict = False
                    for other_cluster in PROTEIN_CLUSTERS:
                        if other_cluster not in queried_protein_clusters:
                            has_other = any(p in r_name or p in r_ing_text for p in other_cluster)
                            if has_other:
                                has_conflict = True
                                break
                    if has_conflict:
                        continue
                else:
                    query_nonveg = set(query_terms) & NON_VEG_WORDS
                    if not query_nonveg and r_veg == "non-veg":
                        continue

                s_semantic = query_sim_map.get(str(rid), 0.0)
                if s_semantic == 0.0 and (clean_query in r_name or clean_query in r_ing_text):
                    s_semantic = 0.85
            else:
                s_semantic = 0.5

            if query_terms:
                matches = sum(1 for t in query_terms if t in r_name or any(t in ing for ing in r_ingredients))
                s_ingredient = min(1.0, matches / max(1, len(query_terms)))
                title_matches = [t for t in query_terms if t in r_name]
                if clean_query in r_name:
                    s_ingredient = 2.5
                elif len(title_matches) == len(query_terms) and len(query_terms) > 1:
                    s_ingredient = 2.0
                elif len(title_matches) > 0:
                    s_ingredient = 1.0 + (len(title_matches) * 0.3)
            else:
                s_ingredient = 0.5

            cal_diff = abs(r_cal - target_meal_cal)
            s_cal = math.exp(-cal_diff / 350.0)

            if diet_goal == "muscle_gain":
                s_prot = min(1.0, r_prot / 30.0)
                s_nutrition = (s_cal * 0.4) + (s_prot * 0.6)
            elif diet_goal == "weight_loss":
                s_low_cal = 1.0 if r_cal <= 400 else math.exp(-(r_cal - 400) / 200.0)
                s_nutrition = (s_low_cal * 0.7) + (min(1.0, r_prot / 20.0) * 0.3)
            else:
                s_nutrition = s_cal

            if diet_goal in r_diet or diet_goal in r_name:
                s_diet = 1.0
            elif not r_diet or r_diet == "balanced":
                s_diet = 0.7
            else:
                s_diet = 0.4

            s_health = min(1.0, max(0.0, r_health / 100.0))

            if str(rid) in history_ids:
                s_history = 0.9 if clean_query and clean_query in r_name else 0.4
            else:
                s_history = 1.0

            user_rev = reviews_map.get(str(rid))
            if user_rev:
                user_rating = float(user_rev.get("rating", 3))
                s_rating = min(1.0, user_rating / 5.0)
            else:
                s_rating = 0.5

            # Base multidimensional score
            base_score = (
                w["semantic_similarity"] * s_semantic +
                w["ingredient_match"]    * s_ingredient +
                w["nutrition_goal"]      * s_nutrition +
                w["diet_preference"]     * s_diet +
                w["health_score"]        * s_health +
                w["user_history"]        * s_history +
                w["user_rating"]         * s_rating
            )

            # Preference Learning integration
            s_pref = 0.5
            if preference_profile:
                from preference_engine import PreferenceEngine
                s_pref = PreferenceEngine.compute_recipe_preference_score(r, preference_profile)
                # Blend preference score
                total_score = (base_score * 0.75) + (s_pref * 0.25)
                # Soft negative penalty for 1-2 star reviews (Do NOT permanently exclude)
                if str(rid) in preference_profile.get("disliked_recipe_ids", set()):
                    total_score *= 0.80
            else:
                total_score = base_score

            scores_breakdown = {
                "semantic": s_semantic,
                "ingredient": s_ingredient,
                "nutrition": s_nutrition,
                "diet": s_diet,
                "health": s_health,
                "history": s_history,
                "rating": s_rating,
                "preference": s_pref
            }

            candidate_entry = dict(r)
            candidate_entry["match_score_pct"] = round(total_score * 100)
            candidate_entry["recommendation_reason"] = self._generate_explanation(r, user_profile, clean_query, scores_breakdown)
            scored_candidates.append((total_score, candidate_entry))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_candidates[:top_n]]

    def filter_recipes(self, cuisine=None, meal_type=None, diet=None, nutrition_tag=None, difficulty=None, max_time=None, max_calories=None, min_protein=None, query=None, top_n=100):
        """
        Multi-facet recipe filter supporting Indian regional cuisines, meal types,
        dietary restrictions, nutrition tags, time, difficulty, and calories/protein.
        Scores and ranks results by relevance to query and user ingredients.
        """
        all_r = self.get_all_recipes()
        scored_results = []

        # 1. Normalize facet filter tokens (treat 'all' / 'All' / None as unconstrained)
        norm_cuisine = str(cuisine).strip().lower() if cuisine and str(cuisine).strip().lower() != "all" else None
        norm_meal_type = str(meal_type).strip().lower() if meal_type and str(meal_type).strip().lower() != "all" else None
        norm_diet = str(diet).strip().lower() if diet and str(diet).strip().lower() != "all" else None
        norm_nutrition_tag = str(nutrition_tag).strip().lower() if nutrition_tag and str(nutrition_tag).strip().lower() != "all" else None
        norm_difficulty = str(difficulty).strip().lower() if difficulty and str(difficulty).strip().lower() != "all" else None

        # 2. Parse query and detect nutrient search intents
        q_clean = (query or "").strip().lower()
        query_tokens = parse_ingredient_tokens(q_clean) if q_clean else set()
        query_nonveg = query_tokens & NON_VEG_WORDS

        # Detect calorie/protein numeric constraints from query string if not explicitly set
        eff_max_cal = float(max_calories) if max_calories else None
        eff_min_prot = float(min_protein) if min_protein else None

        if q_clean and not eff_max_cal:
            cal_match = re.search(r'(?:under|<|below|max)\s*(\d+)\s*(?:cal|kcal|calories)?', q_clean)
            if cal_match:
                eff_max_cal = float(cal_match.group(1))

        if q_clean and not eff_min_prot:
            prot_match = re.search(r'(?:over|>|min|at least)?\s*(\d+)\s*(?:g)?\s*protein', q_clean)
            if prot_match:
                eff_min_prot = float(prot_match.group(1))

        for r in all_r:
            nutr = r.get("nutritions", {}) or {}
            cal = float(nutr.get("calories", 0) or 0)
            prot = float(nutr.get("protein_g", 0) or 0)
            carbs = float(nutr.get("carbs_g", 0) or 0)
            fat = float(nutr.get("fat_g", 0) or 0)

            r_name = str(r.get("recipe_name", "")).lower()
            r_name_tokens = parse_ingredient_tokens(r_name)
            r_ingredients = r.get("ingredients", []) or []
            r_ings_tokens = set()
            for ing in r_ingredients:
                r_ings_tokens.update(parse_ingredient_tokens(ing))
            r_ings_text = " ".join([str(i).lower() for i in r_ingredients])

            r_tags = [str(t).lower() for t in r.get("nutrition_tags", [])]
            r_diet_goal = str(r.get("diet_goal", "")).lower().replace("_", " ")
            r_cuisine = str(r.get("cuisine", "")).lower()
            r_meal = str(r.get("meal_type", "")).lower()
            r_diet = str(r.get("diet", "")).lower()
            r_veg = str(r.get("veg_nonveg", "")).lower()
            health_sc = float(r.get("health_score", 80) or 80)

            # 3. Regional Cuisine filter
            if norm_cuisine:
                if norm_cuisine not in r_cuisine and r_cuisine not in norm_cuisine:
                    continue

            # 4. Meal Type filter
            if norm_meal_type:
                if norm_meal_type != r_meal:
                    continue

            # 5. Diet filter (strict veg / non-veg separation)
            if norm_diet:
                if norm_diet in ["veg", "vegetarian"]:
                    if r_veg != "veg" and r_diet != "vegetarian":
                        continue
                elif norm_diet in ["non-veg", "non_veg", "non-vegetarian"]:
                    if r_veg != "non-veg" and r_diet != "non-vegetarian":
                        continue
                else:
                    if norm_diet not in r_diet and norm_diet not in r_veg:
                        continue

            # 6. Nutrition tag filter (compares tags, goals, and macro benchmarks)
            if norm_nutrition_tag:
                tag_matched = False
                if any(norm_nutrition_tag in t for t in r_tags):
                    tag_matched = True
                elif norm_nutrition_tag in r_diet_goal:
                    tag_matched = True
                elif "high protein" in norm_nutrition_tag and prot >= 20:
                    tag_matched = True
                elif "low calorie" in norm_nutrition_tag and cal <= 350:
                    tag_matched = True
                elif "high fiber" in norm_nutrition_tag and ("high fiber" in r_tags or carbs >= 25):
                    tag_matched = True
                elif "muscle gain" in norm_nutrition_tag and ("muscle gain" in r_tags or prot >= 25):
                    tag_matched = True
                elif "weight loss" in norm_nutrition_tag and ("weight loss" in r_tags or cal <= 380):
                    tag_matched = True
                elif "balanced" in norm_nutrition_tag and (prot >= 12 and cal <= 500):
                    tag_matched = True

                if not tag_matched:
                    continue

            # 7. Difficulty filter
            if norm_difficulty:
                r_diff = str(r.get("difficulty", "")).lower()
                if norm_difficulty != r_diff:
                    continue

            # 8. Max Time (prep + cook)
            if max_time:
                try:
                    total_time = int(r.get("prep_time_mins", 15)) + int(r.get("cook_time_mins", 20))
                    if total_time > int(max_time):
                        continue
                except Exception:
                    pass

            # 9. Calories & Protein thresholds
            if eff_max_cal and cal > eff_max_cal:
                continue
            if eff_min_prot and prot < eff_min_prot:
                continue

            # 10. Query Matching & Relevance Ranking
            entry = dict(r)
            if q_clean:
                # Protein exclusivity: If user requested specific protein(s) (e.g. egg, paneer, chicken),
                # strictly require that protein and prevent conflicting proteins from taking over.
                PROTEIN_CLUSTERS = {
                    'egg': {'egg', 'eggs', 'guddu', 'anda', 'muttai'},
                    'chicken': {'chicken', 'kodi', 'murgh'},
                    'mutton': {'mutton', 'mamsam', 'lamb', 'goat', 'boti', 'keema'},
                    'fish': {'fish', 'chepala', 'meen', 'vanjaram', 'bommidala'},
                    'prawn': {'prawn', 'prawns', 'royyalu', 'shrimp', 'chingri'},
                    'crab': {'crab', 'peethala', 'nandu'},
                    'paneer': {'paneer'},
                    'tofu': {'tofu'}
                }
                requested_proteins = set()
                for p_key, p_words in PROTEIN_CLUSTERS.items():
                    if any(pw in query_tokens or pw in q_clean for pw in p_words):
                        requested_proteins.add(p_key)

                if requested_proteins:
                    r_all_text = f"{r_name} {r_ings_text}".lower()
                    has_requested = any(any(pw in r_all_text for pw in PROTEIN_CLUSTERS[rp]) for rp in requested_proteins)
                    if not has_requested:
                        continue

                # Non-veg keyword enforcement:
                if query_nonveg:
                    if r_veg == "veg":
                        continue
                    if not any(nv in r_ings_tokens or nv in r_name_tokens or nv in r_ings_text for nv in query_nonveg):
                        continue
                else:
                    if r_veg == "non-veg" and not norm_diet:
                        continue

                matched_tokens = [qt for qt in query_tokens if qt in r_name_tokens or qt in r_name or qt in r_ings_tokens or any(qt in ing for ing in r_ingredients) or any(qt in tag for tag in r_tags)]
                matched_unique = list(set(matched_tokens))
                match_count = len(matched_unique)

                nutrient_match = False
                if match_count == 0:
                    if "high protein" in q_clean or "protein" in q_clean:
                        if prot >= 20 or "high protein" in r_tags or "muscle gain" in r_tags:
                            nutrient_match = True
                    if "low calorie" in q_clean or "low cal" in q_clean or "low carb" in q_clean:
                        if cal <= 350 or "low calorie" in r_tags or "weight loss" in r_tags:
                            nutrient_match = True
                    if "high fiber" in q_clean or "fiber" in q_clean:
                        if "high fiber" in r_tags or carbs >= 25:
                            nutrient_match = True
                    if "muscle gain" in q_clean:
                        if "muscle gain" in r_tags or prot >= 25:
                            nutrient_match = True
                    if "weight loss" in q_clean:
                        if "weight loss" in r_tags or cal <= 380:
                            nutrient_match = True
                    if "keto" in q_clean:
                        if carbs <= 20 or prot >= 25:
                            nutrient_match = True
                    if q_clean in r_name or q_clean in r_ings_text:
                        nutrient_match = True

                    if not nutrient_match:
                        continue

                coverage = match_count / max(1, len(query_tokens)) if query_tokens else 0.5
                score = coverage * 350.0

                # Huge boost for exact query or direct title matches
                title_matches = [qt for qt in query_tokens if qt in r_name_tokens or qt in r_name]
                if q_clean in r_name:
                    score += 300.0
                elif len(title_matches) == len(query_tokens) and len(query_tokens) > 1:
                    score += 250.0
                elif len(title_matches) > 0:
                    score += len(title_matches) * 50.0

                for qt in matched_unique:
                    if qt in r_ings_tokens:
                        score += 30.0

                if query_nonveg and any(nv in r_name_tokens for nv in query_nonveg):
                    score += 50.0

                score += (health_sc * 0.2)

                pct = round(coverage * 100) if match_count > 0 else 75
                entry["match_score_pct"] = max(pct, min(100, round((match_count / max(1, len(r_ingredients))) * 100) + 50))
                if match_count >= len(query_tokens) and match_count > 1:
                    entry["recommendation_reason"] = f"Includes all your ingredients: {', '.join(matched_unique)}"
                elif matched_unique:
                    entry["recommendation_reason"] = f"Matches: {', '.join(matched_unique)}"
                elif nutrient_match:
                    entry["recommendation_reason"] = f"Aligned with '{q_clean}' nutrition goal ({cal:.0f} kcal, {prot:.0f}g protein)"
                else:
                    entry["recommendation_reason"] = "Recommended healthy dish"

                scored_results.append((score, entry))
            else:
                scored_results.append((health_sc, entry))

        # 11. If query search yielded no direct matches, gracefully fall back to BERT semantic recommendations
        if not scored_results and q_clean:
            semantic_results = self.recommend_semantic(query, top_n=top_n)
            return semantic_results

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_n]]

    # =========================================================================
    # WHAT CAN I COOK? - PANTRY INGREDIENT MATCHER
    # =========================================================================
    def match_pantry_ingredients(self, pantry_ingredients_str, user_profile=None, top_n=10):
        """
        'What Can I Cook?' Engine:
        Compares user's pantry ingredients with all recipes, categorizes available
        vs. missing ingredients, calculates exact match %, and ranks cookable meals.
        """
        if not pantry_ingredients_str or not self.recipes_by_id:
            return self.get_all_recipes()[:top_n]

        # 1. Parse & Normalize User Pantry Tokens
        user_pantry_tokens = parse_ingredient_tokens(pantry_ingredients_str)
        if not user_pantry_tokens:
            return self.recommend_semantic(pantry_ingredients_str, top_n=top_n)

        pantry_nonveg = user_pantry_tokens & NON_VEG_WORDS

        # 2. Hard Exclusions (Vegetarian & Allergies)
        food_pref = (user_profile.get("food_pref") or "both").lower() if user_profile else "both"
        allergies_raw = user_profile.get("allergies", []) if user_profile else []
        if isinstance(allergies_raw, str):
            allergies = [a.strip().lower() for a in allergies_raw.split(",") if a.strip()]
        elif isinstance(allergies_raw, list):
            allergies = [str(a).strip().lower() for a in allergies_raw if str(a).strip()]
        else:
            allergies = []

        matched_results = []

        for rid, r in self.recipes_by_id.items():
            r_veg = str(r.get("veg_nonveg", "")).lower()
            r_name = str(r.get("recipe_name", "")).lower()
            r_ingredients = r.get("ingredients", []) or []
            r_ing_text = " ".join([str(i).lower() for i in r_ingredients])

            # Filter vegetarian user preference
            if food_pref == "veg":
                if r_veg == "non-veg":
                    continue
                non_veg_kw = ["chicken", "mutton", "fish", "prawn", "egg", "meat", "shrimp", "crab"]
                if any(kw in r_ing_text or kw in r_name for kw in non_veg_kw):
                    continue

            # Non-veg pantry enforcement: If user has chicken/meat in pantry, exclude veg dishes
            if pantry_nonveg:
                if r_veg == "veg":
                    continue
                if not any(nv in r_ing_text or nv in r_name for nv in pantry_nonveg):
                    continue

            # Filter allergies
            is_allergic = False
            for allergy in allergies:
                if allergy and (allergy in r_ing_text or any(allergy in str(i).lower() for i in r_ingredients)):
                    is_allergic = True
                    break
            if is_allergic:
                continue

            available = []
            missing = []
            r_ings_tokens_all = set()

            for ing in r_ingredients:
                ing_str = str(ing).strip()
                ing_tokens = parse_ingredient_tokens(ing_str)
                r_ings_tokens_all.update(ing_tokens)

                # Check if any user pantry token matches
                if any(pt in ing_tokens for pt in user_pantry_tokens) or any(pt in ing_str.lower() for pt in user_pantry_tokens):
                    available.append(ing_str)
                else:
                    missing.append(ing_str)

            total_count = len(r_ingredients)
            available_count = len(available)

            if total_count > 0:
                match_pct = round((available_count / total_count) * 100)
            else:
                match_pct = 0

            # Measure how many of the USER'S stated pantry tokens are covered in this recipe
            user_tokens_covered = sum(1 for pt in user_pantry_tokens if pt in r_ings_tokens_all or pt in r_name or any(pt in a.lower() for a in available))
            user_coverage_pct = user_tokens_covered / max(1, len(user_pantry_tokens))

            # Must match at least one user pantry ingredient
            if user_tokens_covered == 0 and available_count == 0:
                continue

            # Compute rank score prioritizing user ingredients coverage + high recipe match percentage + health score
            health_sc = float(r.get("health_score", 80) or 80)
            name_bonus = 60 if any(pt in r_name for pt in user_pantry_tokens) else 0
            meat_bonus = 80 if pantry_nonveg and any(nv in r_name for nv in pantry_nonveg) else 0
            composite_score = (user_coverage_pct * 400.0) + (match_pct * 15.0) + (health_sc * 0.3) + name_bonus + meat_bonus

            # Build rationale
            if available_count == total_count and total_count > 0:
                reason = "✨ 100% Ready to Cook! You have all ingredients in your pantry."
            elif user_coverage_pct >= 0.8:
                reason = f"Includes all your ingredients ({', '.join(user_pantry_tokens)}). Only missing {len(missing)} items to complete."
            elif match_pct >= 60:
                reason = f"You have {available_count} of {total_count} ingredients ({match_pct}% Match). Only missing {len(missing)} items."
            elif available_count > 0:
                reason = f"Pantry Match: {available_count}/{total_count} ingredients ({match_pct}%). Missing: {', '.join(missing[:2])}."
            else:
                reason = "Similar dish suggestion based on your ingredients."

            entry = dict(r)
            entry["pantry_match_pct"] = match_pct
            entry["user_coverage_pct"] = round(user_coverage_pct * 100)
            entry["available_ingredients"] = available
            entry["missing_ingredients"] = missing
            entry["total_ingredients_count"] = total_count
            entry["recommendation_reason"] = reason
            entry["match_score_pct"] = max(match_pct, round(user_coverage_pct * 100))

            matched_results.append((composite_score, entry))

        # If zero recipes matched pantry items, fall back to semantic recommendations
        if not matched_results:
            fallback = self.recommend_semantic(pantry_ingredients_str, top_n=top_n)
            return fallback

        # Sort by composite score (highest match % first)
        matched_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in matched_results[:top_n]]

ai_engine = EmbeddingEngine()
