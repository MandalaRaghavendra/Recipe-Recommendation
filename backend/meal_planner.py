import os
import sys
import json
import math
import secrets
from datetime import datetime, date, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
AI_SERVICE_DIR = os.path.join(PROJECT_ROOT, "ai-service")
if AI_SERVICE_DIR not in sys.path:
    sys.path.insert(0, AI_SERVICE_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    import database as db
    import nutrition_engine as nutrition
    from embedding_engine import ai_engine
    from nutrition_coach import extract_recipe_prep_time
except ImportError:
    from backend import database as db
    from backend import nutrition_engine as nutrition
    from embedding_engine import ai_engine
    from backend.nutrition_coach import extract_recipe_prep_time


MEAL_SLOT_SPLITS = {
    "breakfast": 0.25,
    "lunch":     0.35,
    "snack":     0.15,
    "dinner":    0.25
}

BREAKFAST_KEYWORDS = [
    "dosa", "idli", "upma", "poha", "oats", "egg", "smoothie", "paratha",
    "pesarattu", "pongal", "toast", "pancake", "chutney", "shake", "bread", "omelet"
]

SNACK_KEYWORDS = [
    "soup", "salad", "snack", "chips", "sundal", "sprout", "cutlet", "tikki",
    "pakora", "tea", "chutney", "roast", "shake", "smoothie", "makhana", "kachori", "chaat"
]

LUNCH_KEYWORDS = [
    "biryani", "pulao", "rice", "curry", "dal", "sambar", "rasam", "korma",
    "masala", "roti", "paneer", "chicken", "mutton", "fish", "prawn", "thali", "gravy"
]

DINNER_KEYWORDS = [
    "soup", "curry", "roti", "khichdi", "dal", "paneer", "sankati", "fish",
    "chicken", "salad", "bhurji", "stew", "boiled", "stir", "tikka"
]


class MealPlannerService:
    """
    Tastio 7-Day AI Meal Planner:
    Generates personalized, structured 7-day meal plans (Breakfast, Lunch, Snack, Dinner)
    enforcing zero allergens, vegetarian/non-veg rules, metabolic macro budgets,
    goal preferences, user star ratings, and anti-repetition variety.
    """

    def __init__(self):
        pass

    def _get_user_context(self, user_id):
        """Fetches profile, metabolic targets, cooked history, and reviews."""
        if not user_id:
            default_profile = {
                "age": 25, "gender": "male", "height": 170.0, "weight": 70.0,
                "diet_goal": "weight_loss", "food_pref": "both", "allergies": [], "duration_months": 3
            }
            diet_rep = nutrition.generate_diet_report([], default_profile)
            return {
                "user_id": None,
                "profile": default_profile,
                "cooked": [],
                "reviews": {},
                "favorites": [],
                "target_goals": diet_rep.get("target_goals", {})
            }

        profile = db.get_user_profile(user_id) or {}
        cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id) or []
        reviews = db.get_all_user_reviews(user_id) or {}
        favorites = db.get_user_favorites(user_id) or []
        diet_rep = nutrition.generate_diet_report(cooked, profile)

        return {
            "user_id": user_id,
            "profile": profile,
            "cooked": cooked,
            "reviews": reviews,
            "favorites": favorites,
            "target_goals": diet_rep.get("target_goals", {})
        }

    def _passes_dietary_filters(self, recipe, profile):
        """Strictly checks allergies and vegetarian preferences."""
        if not recipe:
            return False

        food_pref = (profile.get("food_pref") or "both").lower()
        if food_pref == "veg":
            if str(recipe.get("veg_nonveg", "")).lower() == "non-veg":
                return False
            # Check non-veg ingredient traces
            r_ing_text = " ".join([str(i).lower() for i in recipe.get("ingredients", [])])
            r_name = str(recipe.get("recipe_name", "")).lower()
            if any(kw in r_ing_text or kw in r_name for kw in ["chicken", "mutton", "fish", "prawn", "meat", "shrimp", "crab"]):
                return False

        # Check allergies
        allergies = profile.get("allergies", [])
        if allergies:
            r_ing = [str(i).lower() for i in recipe.get("ingredients", [])]
            r_text = " ".join(r_ing) + " " + str(recipe.get("recipe_name", "")).lower()
            for a in allergies:
                a_clean = str(a).strip().lower()
                if a_clean and (a_clean in r_text or any(a_clean in i for i in r_ing)):
                    return False

        return True

    def _matches_meal_slot(self, recipe, meal_type, slot_cal_budget):
        """Determines suitability of a recipe for Breakfast, Lunch, Snack, or Dinner."""
        name = str(recipe.get("recipe_name", "")).lower()
        nutr = recipe.get("nutritions", {}) or {}
        cal = float(nutr.get("calories", 0) or 0)

        if meal_type == "breakfast":
            if any(k in name for k in BREAKFAST_KEYWORDS):
                return True
            # Allow light healthy dishes for breakfast
            if cal <= 380 and not any(heavy in name for heavy in ["biryani", "mutton", "fish curry", "prawn", "kodi chips", "thali"]):
                return True
            return False

        elif meal_type == "snack":
            if any(k in name for k in SNACK_KEYWORDS):
                return True
            # Allow light items under 260 kcal
            if cal <= 260 and not any(heavy in name for heavy in ["biryani", "mutton", "pulao", "curry"]):
                return True
            return False

        elif meal_type == "lunch":
            if any(k in name for k in LUNCH_KEYWORDS):
                return True
            if cal >= 260:
                return True
            return False

        elif meal_type == "dinner":
            if any(k in name for k in DINNER_KEYWORDS):
                return True
            if 200 <= cal <= 600:
                return True
            return False

        return True

    def _format_meal_entry(self, recipe, meal_type, diet_goal="weight_loss"):
        """Formats recipe as a structured meal entry in the plan."""
        nutr = recipe.get("nutritions", {}) or {}
        cal = int(nutr.get("calories", 0) or 0)
        prot = int(nutr.get("protein_g", 0) or 0)
        carbs = int(nutr.get("carbs_g", 0) or 0)
        fat = int(nutr.get("fat_g", 0) or 0)
        prep = extract_recipe_prep_time(recipe)

        reasons = []
        if meal_type == "breakfast":
            reasons.append(f"Energizing morning meal with {prot}g protein and balanced carbs")
        elif meal_type == "lunch":
            reasons.append(f"Wholesome midday fuel ({cal} kcal) tailored to your {diet_goal.replace('_', ' ')} goal")
        elif meal_type == "snack":
            reasons.append(f"Nutritious light snack ({cal} kcal) to sustain afternoon focus")
        else:
            reasons.append(f"Satisfying dinner with {prot}g protein for optimal evening satiety")

        return {
            "meal_type": meal_type.capitalize(),
            "recipe_id": str(recipe.get("recipe_id")),
            "recipe_name": recipe.get("recipe_name"),
            "calories": cal,
            "protein": prot,
            "carbs": carbs,
            "fat": fat,
            "prep_time": prep,
            "image_link": recipe.get("image_link", ""),
            "veg_nonveg": recipe.get("veg_nonveg", "Veg"),
            "health_score": int(recipe.get("health_score", 80) or 80),
            "diet_goal": recipe.get("diet_goal", "Balanced"),
            "reason": reasons[0] if reasons else "Aligned with your daily macro targets."
        }

    def generate_7day_plan(self, user_id=None, start_date=None):
        """
        Generates a 7-day meal plan (28 meals) with Breakfast, Lunch, Snack, Dinner.
        Calculates exact daily totals, targets, and difference from target.
        start_date: Optional 'YYYY-MM-DD' string or date/datetime object. Defaults to date.today().
        """
        ctx = self._get_user_context(user_id)
        profile = ctx["profile"]
        targets = ctx["target_goals"]
        reviews = ctx["reviews"]
        cooked_history = ctx["cooked"]

        target_daily_cal = int(targets.get("target_calories", 1800))
        target_daily_prot = int(targets.get("target_protein", 100))
        target_daily_carbs = int(targets.get("target_carbs", 200))
        target_daily_fat = int(targets.get("target_fat", 50))
        diet_goal = str(profile.get("diet_goal", "weight_loss")).lower()

        all_recipes = ai_engine.get_all_recipes()

        # Filter valid candidates (zero allergens, veg rule)
        valid_candidates = [r for r in all_recipes if self._passes_dietary_filters(r, profile)]

        if not valid_candidates:
            # Fallback to all recipes if strict filtering emptied database
            valid_candidates = all_recipes

        # Separate pools by meal slot
        slot_pools = {
            "breakfast": [],
            "lunch": [],
            "snack": [],
            "dinner": []
        }

        for slot, split_pct in MEAL_SLOT_SPLITS.items():
            budget = target_daily_cal * split_pct
            for r in valid_candidates:
                if self._matches_meal_slot(r, slot, budget):
                    slot_pools[slot].append(r)

            # Ensure non-empty slot pool
            if not slot_pools[slot]:
                slot_pools[slot] = valid_candidates

        # Anti-repetition tracker across the 7 days
        used_recipe_counts = {str(r.get("recipe_id")): 0 for r in valid_candidates}

        days = []
        today_dt = date.today()
        if start_date:
            try:
                if isinstance(start_date, datetime):
                    today_dt = start_date.date()
                elif isinstance(start_date, date):
                    today_dt = start_date
                elif isinstance(start_date, str) and start_date.strip():
                    today_dt = datetime.strptime(start_date.strip()[:10], "%Y-%m-%d").date()
            except Exception as e:
                print(f"[MealPlanner] Invalid start_date '{start_date}': {e}, defaulting to today.")
                today_dt = date.today()

        for day_idx in range(7):
            day_date = today_dt + timedelta(days=day_idx)
            day_name = day_date.strftime("%A")
            formatted_date = day_date.strftime("%b %d, %Y")

            day_meals = {}
            day_total_cal = 0
            day_total_prot = 0
            day_total_carbs = 0
            day_total_fat = 0

            for slot in ["breakfast", "lunch", "snack", "dinner"]:
                slot_budget = target_daily_cal * MEAL_SLOT_SPLITS[slot]
                pool = slot_pools[slot]

                # Score candidates for this slot
                scored = []
                for r in pool:
                    rid = str(r.get("recipe_id"))
                    nutr = r.get("nutritions", {}) or {}
                    cal = float(nutr.get("calories", 300) or 300)
                    prot = float(nutr.get("protein_g", 15) or 15)
                    health_sc = float(r.get("health_score", 80) or 80)

                    # Calorie proximity
                    cal_diff = abs(cal - slot_budget)
                    s_cal = math.exp(-cal_diff / 150.0)

                    # Goal fit
                    if diet_goal == "muscle_gain":
                        s_goal = min(1.0, prot / 30.0)
                    elif diet_goal == "weight_loss":
                        s_goal = 1.0 if cal <= slot_budget else math.exp(-(cal - slot_budget) / 100.0)
                    else:
                        s_goal = s_cal

                    # User rating bonus (+0.3 for 4 or 5 stars)
                    user_rev = reviews.get(rid)
                    s_rating = 0.3 if user_rev and int(user_rev.get("rating", 0)) >= 4 else 0.0

                    # Anti-repetition penalty
                    times_used = used_recipe_counts.get(rid, 0)
                    s_repetition_penalty = times_used * 0.4

                    total_score = (s_cal * 0.4) + (s_goal * 0.3) + (health_sc / 100.0 * 0.2) + s_rating - s_repetition_penalty
                    # Add tiny random jitter to prevent static repetition on ties
                    total_score += secrets.SystemRandom().uniform(0.0, 0.05)

                    scored.append((total_score, r))

                scored.sort(key=lambda x: x[0], reverse=True)
                chosen_recipe = scored[0][1] if scored else pool[0]

                # Record usage
                chosen_rid = str(chosen_recipe.get("recipe_id"))
                used_recipe_counts[chosen_rid] = used_recipe_counts.get(chosen_rid, 0) + 1

                meal_entry = self._format_meal_entry(chosen_recipe, slot, diet_goal)
                day_meals[slot] = meal_entry

                day_total_cal += meal_entry["calories"]
                day_total_prot += meal_entry["protein"]
                day_total_carbs += meal_entry["carbs"]
                day_total_fat += meal_entry["fat"]

            diff = day_total_cal - target_daily_cal
            if diff > 0:
                diff_str = f"+{diff} kcal"
            elif diff < 0:
                diff_str = f"{diff} kcal"
            else:
                diff_str = "0 kcal (100% target match)"

            day_obj = {
                "day_index": day_idx + 1,
                "day_name": day_name,
                "date": formatted_date,
                "date_iso": day_date.strftime("%Y-%m-%d"),
                "total_calories": day_total_cal,
                "total_protein": day_total_prot,
                "total_carbs": day_total_carbs,
                "total_fat": day_total_fat,
                "target_calories": target_daily_cal,
                "target_protein": target_daily_prot,
                "target_carbs": target_daily_carbs,
                "target_fat": target_daily_fat,
                "difference": diff,
                "difference_str": diff_str,
                "calories_pct": round((day_total_cal / max(1, target_daily_cal)) * 100),
                "meals": day_meals
            }
            days.append(day_obj)

        plan_dict = {
            "plan_name": f"7-Day AI {diet_goal.replace('_', ' ').title()} Meal Plan",
            "start_date": days[0]["date_iso"],
            "end_date": days[-1]["date_iso"],
            "target_calories": target_daily_cal,
            "target_protein": target_daily_prot,
            "target_carbs": target_daily_carbs,
            "target_fat": target_daily_fat,
            "diet_goal": diet_goal,
            "food_pref": profile.get("food_pref", "both"),
            "allergies": profile.get("allergies", []),
            "days": days,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to SQLite
        if user_id:
            db.save_meal_plan(user_id, plan_dict)

        return plan_dict

    def get_current_plan(self, user_id):
        """Fetches active meal plan from SQLite or generates one if absent."""
        if not user_id:
            return self.generate_7day_plan(user_id=None)

        plan = db.get_current_meal_plan(user_id)
        if not plan:
            plan = self.generate_7day_plan(user_id=user_id)
        return plan

    def replace_meal(self, user_id, day_index=None, meal_type="breakfast", new_recipe_id=None, day_number=None):
        """
        Replaces an individual meal slot in the user's active plan.
        Supports both 0-indexed day_index and 1-indexed day_number.
        Recalculates the day's totals and difference.
        """
        if day_index is None and day_number is not None:
            day_index = int(day_number) - 1 if int(day_number) > 0 else int(day_number)
        if day_index is None:
            day_index = 0

        plan = self.get_current_plan(user_id)
        if not plan or "days" not in plan:
            return None, "No active meal plan found"

        days = plan["days"]
        target_day = None
        for d in days:
            idx = int(d.get("day_index", 1))
            num = int(d.get("day_number", idx))
            t_idx = int(day_index)
            if idx == t_idx or idx == t_idx + 1 or num == t_idx or num == t_idx + 1:
                target_day = d
                break

        if not target_day:
            return None, f"Day {day_index} not found in meal plan"

        meal_key = str(meal_type).lower()
        if meal_key not in target_day["meals"]:
            return None, f"Invalid meal type '{meal_type}'"

        ctx = self._get_user_context(user_id)
        profile = ctx["profile"]
        diet_goal = str(profile.get("diet_goal", "weight_loss")).lower()

        # If user explicitly chose a recipe
        if new_recipe_id:
            chosen = ai_engine.get_recipe_by_id(new_recipe_id)
            if not chosen:
                return None, "Selected recipe not found"
        else:
            # Pick best alternative from database
            current_rid = str(target_day["meals"][meal_key].get("recipe_id"))
            all_r = ai_engine.get_all_recipes()
            slot_budget = plan.get("target_calories", 1800) * MEAL_SLOT_SPLITS.get(meal_key, 0.25)

            candidates = []
            for r in all_r:
                rid = str(r.get("recipe_id"))
                if rid == current_rid:
                    continue
                if not self._passes_dietary_filters(r, profile):
                    continue
                if not self._matches_meal_slot(r, meal_key, slot_budget):
                    continue

                cal = float(r.get("nutritions", {}).get("calories", 300) or 300)
                cal_diff = abs(cal - slot_budget)
                candidates.append((cal_diff, r))

            candidates.sort(key=lambda x: x[0])
            if candidates:
                # Pick from top 3 alternatives securely for nice variety
                chosen = secrets.choice(candidates[:min(3, len(candidates))])[1]
            else:
                chosen = all_r[0]

        # Update meal
        new_meal_entry = self._format_meal_entry(chosen, meal_key, diet_goal)
        target_day["meals"][meal_key] = new_meal_entry

        # Recalculate day totals
        day_total_cal = sum(m["calories"] for m in target_day["meals"].values())
        day_total_prot = sum(m["protein"] for m in target_day["meals"].values())
        day_total_carbs = sum(m["carbs"] for m in target_day["meals"].values())
        day_total_fat = sum(m["fat"] for m in target_day["meals"].values())

        target_cal = target_day.get("target_calories", 1800)
        diff = day_total_cal - target_cal
        diff_str = f"+{diff} kcal" if diff > 0 else f"{diff} kcal" if diff < 0 else "0 kcal (100% target match)"

        target_day["total_calories"] = day_total_cal
        target_day["total_protein"] = day_total_prot
        target_day["total_carbs"] = day_total_carbs
        target_day["total_fat"] = day_total_fat
        target_day["difference"] = diff
        target_day["difference_str"] = diff_str
        target_day["calories_pct"] = round((day_total_cal / max(1, target_cal)) * 100)

        # Save back to DB
        if user_id:
            db.save_meal_plan(user_id, plan)

        return plan, "Meal replaced successfully"

    def get_alternatives_for_slot(self, user_id, meal_type, current_recipe_id=None):
        """Fetches top 6 alternative recipes for a meal slot picker modal."""
        ctx = self._get_user_context(user_id)
        profile = ctx["profile"]
        plan = self.get_current_plan(user_id)
        target_cal = plan.get("target_calories", 1800) if plan else 1800
        slot_budget = target_cal * MEAL_SLOT_SPLITS.get(str(meal_type).lower(), 0.25)

        all_r = ai_engine.get_all_recipes()
        alternatives = []

        for r in all_r:
            rid = str(r.get("recipe_id"))
            if current_recipe_id and rid == str(current_recipe_id):
                continue
            if not self._passes_dietary_filters(r, profile):
                continue
            if not self._matches_meal_slot(r, str(meal_type).lower(), slot_budget):
                continue

            nutr = r.get("nutritions", {}) or {}
            cal = float(nutr.get("calories", 0) or 0)
            cal_diff = abs(cal - slot_budget)
            alternatives.append((cal_diff, self._format_meal_entry(r, meal_type, profile.get("diet_goal", "weight_loss"))))

        alternatives.sort(key=lambda x: x[0])
        return [item[1] for item in alternatives[:8]]


meal_planner_service = MealPlannerService()
