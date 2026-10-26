import re
import datetime
from datetime import datetime, date, timedelta
import math

try:
    import database as db
    import nutrition_engine as nutrition
    from embedding_engine import ai_engine, parse_ingredient_tokens
except ImportError:
    from backend import database as db
    from backend import nutrition_engine as nutrition
    from embedding_engine import ai_engine, parse_ingredient_tokens


def extract_recipe_prep_time(recipe):
    """
    Extracts or computes realistic preparation and cooking time in minutes from recipe steps.
    Never invents arbitrary time; parses explicit minutes/hours from steps or defaults
    rationally based on step complexity.
    """
    if not recipe:
        return "25 mins"

    steps = recipe.get("steps", [])
    if isinstance(steps, str):
        steps = [steps]

    total_mins = 0
    found_explicit_time = False

    for s in steps:
        s_text = str(s)
        # Match e.g. "5-6 minutes", "20 to 25 mins", "15 min", "10 minutes"
        min_matches = re.findall(r'(\d+)(?:\s*(?:-|to)\s*(\d+))?\s*(?:min|minute|mins)', s_text, re.IGNORECASE)
        for m in min_matches:
            val = int(m[1]) if m[1] else int(m[0])
            total_mins += val
            found_explicit_time = True

        # Match e.g. "1 hour", "1-2 hours", "1.5 hrs"
        hr_matches = re.findall(r'(\d+(?:\.\d+)?)(?:\s*(?:-|to)\s*(\d+(?:\.\d+)?))?\s*(?:hr|hour|hours|hrs)', s_text, re.IGNORECASE)
        for h in hr_matches:
            val = float(h[1]) if h[1] else float(h[0])
            total_mins += int(val * 60)
            found_explicit_time = True

    # Check if beverage/smoothie/chutney/salad
    r_name = str(recipe.get("recipe_name", "")).lower()
    is_quick_dish = any(q in r_name for q in ["smoothie", "shake", "juice", "salad", "chutney", "drink", "lassi", "tea"])

    if found_explicit_time and total_mins > 0:
        if not is_quick_dish and total_mins < 15 and len(steps) >= 3:
            total_mins = max(total_mins, len(steps) * 6)

        if total_mins >= 60:
            hrs = total_mins // 60
            remaining_m = total_mins % 60
            if remaining_m > 0:
                return f"{hrs} hr {remaining_m} mins"
            return f"{hrs} hr" if hrs == 1 else f"{hrs} hrs"
        return f"{total_mins} mins"

    # Default estimation based on dish type & step count
    if is_quick_dish:
        return "10 mins"
    step_count = len(steps) if steps else 4
    estimated = max(20, min(50, step_count * 8))
    return f"{estimated} mins"


class NutritionCoach:
    """
    Tastio AI Nutrition Coach:
    A structured, data-grounded nutrition intelligence engine connected directly
    to the user profile, Mifflin-St Jeor metabolic calculator, meal history,
    user ratings, and verified Tastio recipe database.
    """

    def __init__(self):
        pass

    def get_user_context(self, user_id):
        """
        Gathers complete user context: profile, metabolic rates (BMR/TDEE),
        targets, today's meal log, and weekly history.
        """
        if not user_id:
            # Default generic baseline for anonymous users
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
                "target_goals": diet_rep.get("target_goals", {}),
                "today_summary": diet_rep.get("today_summary", {}),
                "weekly_meals": [],
                "weekly_total_calories": 0,
                "weekly_total_protein": 0,
                "has_profile": False
            }

        profile = db.get_user_profile(user_id) or {}
        cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id) or []
        reviews = db.get_all_user_reviews(user_id) or {}
        favorites = db.get_user_favorites(user_id) or []

        diet_rep = nutrition.generate_diet_report(cooked, profile)
        target_goals = diet_rep.get("target_goals", {})
        today_summary = diet_rep.get("today_summary", {})

        # Compute Weekly History (Past 7 days)
        today_dt = date.today()
        seven_days_ago = today_dt - timedelta(days=7)
        weekly_meals = []
        weekly_cal = 0
        weekly_protein = 0

        for meal in cooked:
            cooked_str = str(meal.get("cooked_at", ""))
            try:
                meal_date = datetime.strptime(cooked_str[:10], "%Y-%m-%d").date()
            except Exception:
                meal_date = today_dt

            if meal_date >= seven_days_ago:
                portion = float(meal.get("serving_size") or 1.0)
                nutr = meal.get("nutritions", {}) or {}
                c = float(nutr.get("calories", 300) or 300) * portion
                p = float(nutr.get("protein_g", 15) or 15) * portion

                weekly_meals.append({
                    "recipe_id": meal.get("recipe_id"),
                    "recipe_name": meal.get("recipe_name", f"Recipe #{meal.get('recipe_id')}"),
                    "date": meal_date.strftime("%b %d, %Y"),
                    "calories": round(c),
                    "protein": round(p),
                    "serving_size": portion,
                    "rating": meal.get("user_rating")
                })
                weekly_cal += c
                weekly_protein += p

        return {
            "user_id": user_id,
            "profile": profile,
            "cooked": cooked,
            "reviews": reviews,
            "favorites": favorites,
            "target_goals": target_goals,
            "today_summary": today_summary,
            "weekly_meals": weekly_meals,
            "weekly_total_calories": round(weekly_cal),
            "weekly_total_protein": round(weekly_protein),
            "has_profile": bool(profile)
        }

    def format_recipe_for_coach(self, recipe, reason=""):
        """Formats a recipe entry with required fields: name, calories, protein, prep time, reason."""
        if not recipe:
            return None

        nutr = recipe.get("nutritions", {}) or {}
        prep_time = extract_recipe_prep_time(recipe)

        return {
            "recipe_id": recipe.get("recipe_id"),
            "recipe_name": recipe.get("recipe_name", "Delicious Recipe"),
            "calories": int(nutr.get("calories", 0) or 0),
            "protein": f"{int(nutr.get('protein_g', 0) or 0)}g",
            "carbs": f"{int(nutr.get('carbs_g', 0) or 0)}g",
            "fat": f"{int(nutr.get('fat_g', 0) or 0)}g",
            "prep_time": prep_time,
            "reason": reason or recipe.get("recommendation_reason", "Recommended based on your daily targets and dietary preferences."),
            "image_link": recipe.get("image_link", ""),
            "veg_nonveg": recipe.get("veg_nonveg", "Veg"),
            "diet_goal": recipe.get("diet_goal", "Balanced"),
            "health_score": int(recipe.get("health_score", 80) or 80),
            "ingredients": recipe.get("ingredients", [])
        }

    def process_query(self, user_message, user_id=None):
        """
        Analyzes user message intent and produces structured, data-grounded coach answers.
        """
        clean_msg = (user_message or "").strip().lower()
        ctx = self.get_user_context(user_id)

        profile = ctx["profile"]
        today = ctx["today_summary"]
        targets = ctx["target_goals"]
        user_allergies = profile.get("allergies", [])
        food_pref = (profile.get("food_pref") or "both").lower()
        diet_goal = (profile.get("diet_goal") or "weight_loss").lower()

        # Extract numerical context
        target_cal = targets.get("target_calories", 1800)
        target_prot = targets.get("target_protein", 100)
        consumed_cal = today.get("consumed_calories", 0)
        consumed_prot = today.get("consumed_protein", 0)
        remaining_cal = max(0, target_cal - consumed_cal)
        remaining_prot = max(0, target_prot - consumed_prot)

        # ---------------------------------------------------------------------
        # 1. PANTRY INGREDIENTS QUERY ("I have chicken and rice. What can I cook?")
        # ---------------------------------------------------------------------
        pantry_match = re.search(r'(?:i have|what can i (?:cook|make) with|cook with|ingredients?:?)\s+([a-zA-Z0-9,\s]+)', clean_msg)
        if pantry_match or ("have" in clean_msg and any(w in clean_msg for w in ["chicken", "rice", "paneer", "tomato", "potato", "onion", "egg", "dal", "mutton", "fish", "cook", "make"])):
            ingredients_text = pantry_match.group(1) if pantry_match else clean_msg
            matched = ai_engine.match_pantry_ingredients(ingredients_text, user_profile=profile, top_n=4)

            recommended = []
            for r in matched:
                avail = r.get("available_ingredients", [])
                total_cnt = r.get("total_ingredients_count", len(r.get("ingredients", [])))
                pct = r.get("pantry_match_pct", 0)
                nutr = r.get("nutritions", {})
                cal = nutr.get("calories", 0)
                prot = nutr.get("protein_g", 0)

                reason = f"Matches {len(avail)}/{total_cnt} ({pct}%) of your pantry ingredients. Fits your {cal} kcal & {prot}g protein profile."
                recommended.append(self.format_recipe_for_coach(r, reason=reason))

            reply = f"🍳 **Pantry Recipe Recommendations**\n\n"
            if recommended:
                reply += f"Based on the ingredients you have (**{ingredients_text.strip()}**), here are the best recipes from the Tastio database:\n\n"
                for i, r in enumerate(recommended, 1):
                    reply += f"{i}. **{r['recipe_name']}** — {r['calories']} kcal | {r['protein']} protein | ⏱️ {r['prep_time']}\n   *{r['reason']}*\n"
            else:
                reply += f"I couldn't find an exact match for **{ingredients_text.strip()}** matching your dietary restrictions. Try searching with common pantry staples like tomato, onion, rice, chicken, or paneer."

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "How many calories did I eat today?",
                    "Give me a high protein vegetarian meal."
                ]
            }

        # ---------------------------------------------------------------------
        # 2. TODAY'S CALORIES & MACRO INTAKE ("How many calories did I eat today?")
        # ---------------------------------------------------------------------
        if any(p in clean_msg for p in ["how many calories", "calories did i eat", "calories today", "calorie intake", "my calories", "what did i eat today"]):
            consumed_carbs = today.get("consumed_carbs", 0)
            consumed_fat = today.get("consumed_fat", 0)
            target_carbs = targets.get("target_carbs", 200)
            target_fat = targets.get("target_fat", 50)

            reply = f"📊 **Today's Nutrition & Calorie Tracking**\n\n"
            reply += f"- **Consumed Calories:** **{consumed_cal} kcal** / {target_cal} kcal target ({today.get('calories_pct', 0)}%)\n"
            reply += f"- **Remaining Calorie Budget:** **{remaining_cal} kcal**\n\n"
            reply += f"**Macronutrient Breakdown Today:**\n"
            reply += f"- **Protein:** **{consumed_prot}g** / {target_prot}g target ({remaining_prot}g remaining)\n"
            reply += f"- **Carbohydrates:** **{consumed_carbs}g** / {target_carbs}g target\n"
            reply += f"- **Healthy Fats:** **{consumed_fat}g** / {target_fat}g target\n\n"

            if consumed_cal == 0:
                reply += "💡 *You haven't logged any meals today yet. Explore recommendations below or log meals from your dashboard.*"
            elif consumed_cal <= target_cal:
                reply += f"✅ *You are well on track! You still have **{remaining_cal} kcal** available for your remaining meals.*"
            else:
                over = consumed_cal - target_cal
                reply += f"⚠️ *You have exceeded your daily baseline by **{over} kcal**. Focus on light, high-fiber or protein-focused snacks for the rest of the day.*"

            # Recommend dishes fitting remaining calories
            recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], max_cal=remaining_cal or 500, top_n=3)

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "What should I eat to reach my protein target?",
                    "What did I eat this week?"
                ]
            }

        # ---------------------------------------------------------------------
        # 3. REACH PROTEIN TARGET ("What should I eat to reach my protein target?")
        # ---------------------------------------------------------------------
        if any(p in clean_msg for p in ["reach my protein", "hit my protein", "protein target", "need more protein", "protein goal"]):
            reply = f"💪 **Protein Target Progress & Recommendations**\n\n"
            reply += f"- **Target Protein:** **{target_prot}g**\n"
            reply += f"- **Consumed Today:** **{consumed_prot}g**\n"
            reply += f"- **Deficit Remaining:** **{remaining_prot}g protein**\n"
            reply += f"- **Remaining Calorie Budget:** **{remaining_cal} kcal**\n\n"

            if remaining_prot <= 0:
                reply += "🎉 **Congratulations!** You have already achieved your daily protein goal. Here are healthy, nutrient-rich dishes to maintain energy:\n"
            else:
                reply += f"To close your **{remaining_prot}g** protein gap within your **{remaining_cal} kcal** budget, here are top protein-dense options from Tastio:\n\n"

            # Search highest protein recipes respecting diet preferences
            all_r = ai_engine.get_all_recipes()
            candidates = []
            for r in all_r:
                if not self._passes_dietary_filters(r, profile):
                    continue
                nutr = r.get("nutritions", {})
                prot_val = int(nutr.get("protein_g", 0) or 0)
                cal_val = int(nutr.get("calories", 0) or 0)
                if prot_val >= 18:
                    candidates.append((prot_val, cal_val, r))

            candidates.sort(key=lambda x: x[0], reverse=True)
            recommended = []
            for item in candidates[:4]:
                prot_val, cal_val, r = item
                reason = f"Delivers {prot_val}g high-quality protein ({cal_val} kcal) to help fulfill your {target_prot}g target."
                recommended.append(self.format_recipe_for_coach(r, reason=reason))

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "Give me a high protein vegetarian meal.",
                    "How many calories did I eat today?",
                    "What should I eat for dinner?"
                ]
            }

        # ---------------------------------------------------------------------
        # 4. HIGH PROTEIN VEGETARIAN MEAL ("Give me a high protein vegetarian meal")
        # ---------------------------------------------------------------------
        if ("protein" in clean_msg and "veg" in clean_msg) or "high protein veg" in clean_msg:
            reply = f"🌱 **High-Protein Vegetarian Recipes**\n\n"
            reply += "Here are the top protein-packed vegetarian dishes from our database (featuring paneer, lentils, chickpeas, and soya):\n\n"

            all_r = ai_engine.get_all_recipes()
            veg_protein = []
            for r in all_r:
                if str(r.get("veg_nonveg", "")).lower() != "veg":
                    continue
                # Exclude allergens
                if self._has_allergies(r, user_allergies):
                    continue
                nutr = r.get("nutritions", {})
                prot_val = int(nutr.get("protein_g", 0) or 0)
                cal_val = int(nutr.get("calories", 0) or 0)
                veg_protein.append((prot_val, r))

            veg_protein.sort(key=lambda x: x[0], reverse=True)
            recommended = []
            for prot_val, r in veg_protein[:4]:
                nutr = r.get("nutritions", {})
                reason = f"100% vegetarian powerhouse offering {prot_val}g plant-based protein with {nutr.get('calories', 0)} kcal."
                recommended.append(self.format_recipe_for_coach(r, reason=reason))

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "Show me recipes below 500 calories.",
                    "How many calories did I eat today?"
                ]
            }

        # ---------------------------------------------------------------------
        # 5. RECIPES BELOW CALORIE THRESHOLD ("Show me recipes below 500 calories")
        # ---------------------------------------------------------------------
        cal_threshold_match = re.search(r'(?:below|under|less than|<)\s*(\d+)\s*(?:cal|calories|kcal)?', clean_msg)
        if cal_threshold_match or "low calorie" in clean_msg or "below 500" in clean_msg:
            threshold = int(cal_threshold_match.group(1)) if cal_threshold_match else 500
            reply = f"🥗 **Recipes Below {threshold} Calories**\n\n"
            reply += f"Here are nutritious dishes under **{threshold} kcal** filtered to match your dietary profile:\n\n"

            all_r = ai_engine.get_all_recipes()
            low_cal = []
            for r in all_r:
                if not self._passes_dietary_filters(r, profile):
                    continue
                nutr = r.get("nutritions", {})
                cal_val = int(nutr.get("calories", 0) or 0)
                health_sc = int(r.get("health_score", 80) or 80)
                if 0 < cal_val <= threshold:
                    low_cal.append((health_sc, cal_val, r))

            low_cal.sort(key=lambda x: (x[0], -x[1]), reverse=True)
            recommended = []
            for health_sc, cal_val, r in low_cal[:4]:
                nutr = r.get("nutritions", {})
                prot_val = nutr.get("protein_g", 0)
                reason = f"Only {cal_val} kcal ({prot_val}g protein) with a high Health Score of {health_sc}/100."
                recommended.append(self.format_recipe_for_coach(r, reason=reason))

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "Give me a high protein vegetarian meal.",
                    "How many calories did I eat today?"
                ]
            }

        # ---------------------------------------------------------------------
        # 6. WEEKLY HISTORY ("What did I eat this week?" / "Weekly history")
        # ---------------------------------------------------------------------
        if any(p in clean_msg for p in ["this week", "weekly", "past week", "eat this week", "eaten history", "my history"]):
            weekly_meals = ctx["weekly_meals"]
            total_w_cal = ctx["weekly_total_calories"]
            total_w_prot = ctx["weekly_total_protein"]

            reply = f"📅 **Your Weekly Meal History (Past 7 Days)**\n\n"
            if not weekly_meals:
                reply += "You have not logged any meals in the past 7 days.\n\n"
                reply += f"Your target baseline is **{target_cal * 7} kcal/week** and **{target_prot * 7}g protein/week**.\n"
                reply += "Start logging your dishes by clicking **'Log as Eaten'** on any recipe card!"
                recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], top_n=3)
            else:
                reply += f"- **Total Meals Logged:** {len(weekly_meals)}\n"
                reply += f"- **Total Calories Consumed:** **{total_w_cal} kcal** (Avg {round(total_w_cal / 7)} kcal/day)\n"
                reply += f"- **Total Protein Consumed:** **{total_w_prot}g** (Avg {round(total_w_prot / 7)}g/day)\n\n"
                reply += "**Recent Logged Meals:**\n"
                for m in weekly_meals[:6]:
                    star = f" | ⭐ {m['rating']}/5" if m.get("rating") else ""
                    reply += f"• **{m['recipe_name']}** ({m['date']}) — {m['calories']} kcal | {m['protein']}g protein{star}\n"

                recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], top_n=3)

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "history_data": weekly_meals,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "How many calories did I eat today?",
                    "What should I eat for dinner?",
                    "What should I eat to reach my protein target?"
                ]
            }

        # ---------------------------------------------------------------------
        # 7. MEAL SUGGESTION ("What should I eat for dinner / lunch / breakfast?")
        # ---------------------------------------------------------------------
        if any(p in clean_msg for p in ["dinner", "lunch", "breakfast", "what should i eat", "suggest a meal", "recommend a dish"]):
            meal_time = "Dinner"
            if "breakfast" in clean_msg:
                meal_time = "Breakfast"
            elif "lunch" in clean_msg:
                meal_time = "Lunch"

            reply = f"🍽️ **Personalized {meal_time} Recommendations**\n\n"
            reply += f"Taking into account your goal (**{diet_goal.replace('_', ' ').title()}**), remaining calorie budget (**{remaining_cal} kcal**), and remaining protein target (**{remaining_prot}g**):\n\n"

            # Filter dishes that fit remaining calories well
            recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], max_cal=remaining_cal or 650, top_n=4)

            for i, r in enumerate(recommended, 1):
                reply += f"{i}. **{r['recipe_name']}** — {r['calories']} kcal | {r['protein']} protein | ⏱️ {r['prep_time']}\n   *{r['reason']}*\n"

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "Give me a high protein vegetarian meal.",
                    "I have chicken and rice. What can I cook?",
                    "How many calories did I eat today?"
                ]
            }

        # ---------------------------------------------------------------------
        # 8. BMR / TDEE / TARGET EXPLANATION ("What is my BMR / TDEE?")
        # ---------------------------------------------------------------------
        if any(p in clean_msg for p in ["bmr", "tdee", "target", "how are my targets calculated", "metabolism"]):
            bmr_val = targets.get("bmr", 1600)
            tdee_val = targets.get("tdee", 2200)
            age_val = profile.get("age", 25)
            gender_val = profile.get("gender", "male")
            weight_val = profile.get("weight", 70.0)
            height_val = profile.get("height", 170.0)

            reply = f"🔬 **Your Metabolic & Target Calculations**\n\n"
            reply += f"Calculated using the medically validated **Mifflin-St Jeor Formula** based on your profile ({gender_val}, {age_val} yrs, {weight_val} kg, {height_val} cm):\n\n"
            reply += f"- **Basal Metabolic Rate (BMR):** **{bmr_val} kcal/day** *(Calories your body burns at complete rest)*\n"
            reply += f"- **Total Daily Energy Expenditure (TDEE):** **{tdee_val} kcal/day** *(Daily energy with moderate physical activity)*\n"
            reply += f"- **Goal Strategy:** **{diet_goal.replace('_', ' ').title()}**\n\n"
            reply += f"**Your Daily Macro Prescription:**\n"
            reply += f"• **Calorie Target:** **{target_cal} kcal/day**\n"
            reply += f"• **Protein:** **{target_prot}g/day** (Crucial for muscle preservation & satiety)\n"
            reply += f"• **Carbohydrates:** **{targets.get('target_carbs', 200)}g/day**\n"
            reply += f"• **Healthy Fats:** **{targets.get('target_fat', 50)}g/day**\n"

            recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], top_n=3)

            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "How many calories did I eat today?",
                    "What should I eat to reach my protein target?"
                ]
            }

        # ---------------------------------------------------------------------
        # 9. DISH COMPATIBILITY CHECK ("Can I eat Biryani?" / "Can I eat Paneer?")
        # ---------------------------------------------------------------------
        dish_query = clean_msg.replace("can i eat", "").replace("is", "").replace("healthy", "").replace("good for me", "").strip()
        matched_recipes = ai_engine.search_by_ingredients(dish_query, top_n=2) if len(dish_query) > 2 else []

        if matched_recipes:
            target_dish = matched_recipes[0]
            nutr = target_dish.get("nutritions", {})
            d_cal = nutr.get("calories", 0)
            d_prot = nutr.get("protein_g", 0)
            d_veg = target_dish.get("veg_nonveg", "Veg")
            prep = extract_recipe_prep_time(target_dish)

            # Check allergy and veg compatibility
            has_allergen = self._has_allergies(target_dish, user_allergies)
            veg_conflict = (food_pref == "veg" and d_veg.lower() == "non-veg")

            reply = f"🔍 **Dish Compatibility: {target_dish.get('recipe_name')}**\n\n"
            reply += f"- **Nutrition:** {d_cal} kcal | {d_prot}g Protein | {nutr.get('carbs_g', 0)}g Carbs | {nutr.get('fat_g', 0)}g Fat\n"
            reply += f"- **Preparation Time:** ⏱️ {prep}\n"
            reply += f"- **Health Score:** {target_dish.get('health_score', 80)}/100\n\n"

            if has_allergen:
                reply += "⚠️ **Allergy Warning:** This dish contains ingredients that match your recorded allergies.\n"
            elif veg_conflict:
                reply += "⚠️ **Dietary Conflict:** This is a Non-Veg dish, which conflicts with your Vegetarian preference.\n"
            else:
                reply += f"✅ **Compatible with your plan!** It uses {d_cal} kcal of your remaining {remaining_cal} kcal budget and supplies {d_prot}g protein.\n"

            recommended = [self.format_recipe_for_coach(target_dish, reason=f"Analyzed specifically for your {diet_goal} diet goal.")]
            return {
                "success": True,
                "reply": reply,
                "recipes": recommended,
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "Give me a high protein vegetarian meal.",
                    "How many calories did I eat today?"
                ]
            }

        # ---------------------------------------------------------------------
        # 10. GENERAL / FALLBACK NUTRITION COACHING
        # ---------------------------------------------------------------------
        # If user asks out-of-scope or uncomputable question
        if any(unsupported in clean_msg for unsupported in ["weather", "stocks", "bitcoin", "code", "movie", "song", "flight"]):
            reply = "I am the **Tastio AI Nutrition Coach**, specialized exclusively in your nutrition targets, meal logs, dietary goals, and recipe recommendations. Information outside of your culinary and nutritional profile is unavailable."
            return {
                "success": True,
                "reply": reply,
                "recipes": [],
                "metrics": self._build_metrics_dict(ctx),
                "suggested_followups": [
                    "What should I eat for dinner?",
                    "How many calories did I eat today?",
                    "Give me a high protein vegetarian meal."
                ]
            }

        # General conversational response with grounded recipe suggestions
        recommended = self._get_tailored_recommendations(profile, ctx["cooked"], ctx["reviews"], top_n=3)
        reply = f"👋 **Hello! I am your Tastio AI Nutrition Coach.**\n\n"
        reply += f"I actively track your **{diet_goal.replace('_', ' ').title()}** plan with a daily target of **{target_cal} kcal** and **{target_prot}g protein**.\n\n"
        reply += f"- **Consumed Today:** {consumed_cal} kcal ({remaining_cal} kcal remaining)\n"
        reply += f"- **Protein Target:** {consumed_prot}g / {target_prot}g\n\n"
        reply += "Here are personalized dish recommendations aligned with your goals. You can also ask me specific questions like *'What should I eat for dinner?'*, *'How many calories did I eat today?'*, or *'I have chicken and rice. What can I cook?'*."

        return {
            "success": True,
            "reply": reply,
            "recipes": recommended,
            "metrics": self._build_metrics_dict(ctx),
            "suggested_followups": [
                "What should I eat for dinner?",
                "Give me a high protein vegetarian meal.",
                "How many calories did I eat today?",
                "What did I eat this week?"
            ]
        }

    def _build_metrics_dict(self, ctx):
        """Constructs safe live metrics snapshot for client UI consumption."""
        targets = ctx.get("target_goals", {})
        today = ctx.get("today_summary", {})
        profile = ctx.get("profile", {})

        target_cal = targets.get("target_calories", 1800)
        target_prot = targets.get("target_protein", 100)
        consumed_cal = today.get("consumed_calories", 0)
        consumed_prot = today.get("consumed_protein", 0)

        return {
            "bmr": targets.get("bmr", 1600),
            "tdee": targets.get("tdee", 2200),
            "target_calories": target_cal,
            "target_protein": target_prot,
            "target_carbs": targets.get("target_carbs", 200),
            "target_fat": targets.get("target_fat", 50),
            "consumed_calories": consumed_cal,
            "consumed_protein": consumed_prot,
            "remaining_calories": max(0, target_cal - consumed_cal),
            "remaining_protein": max(0, target_prot - consumed_prot),
            "calories_pct": today.get("calories_pct", 0),
            "diet_goal": profile.get("diet_goal", "weight_loss"),
            "food_pref": profile.get("food_pref", "both")
        }

    def _passes_dietary_filters(self, recipe, profile):
        """Checks vegetarian preference and allergies against recipe."""
        if not recipe or not profile:
            return True

        food_pref = (profile.get("food_pref") or "both").lower()
        if food_pref == "veg" and str(recipe.get("veg_nonveg", "")).lower() == "non-veg":
            return False

        allergies = profile.get("allergies", [])
        return not self._has_allergies(recipe, allergies)

    def _has_allergies(self, recipe, allergies):
        """Checks if recipe contains any listed allergens."""
        if not allergies or not recipe:
            return False

        r_ing = [str(i).lower() for i in recipe.get("ingredients", [])]
        r_text = " ".join(r_ing) + " " + str(recipe.get("recipe_name", "")).lower()

        for a in allergies:
            a_clean = str(a).strip().lower()
            if a_clean and (a_clean in r_text or any(a_clean in i for i in r_ing)):
                return True
        return False

    def _get_tailored_recommendations(self, profile, history, reviews, max_cal=None, top_n=3):
        """Fetches personalized recommendations with rich reasons."""
        results = ai_engine.recommend_personalized(
            query_str="",
            user_profile=profile,
            user_history=history,
            user_reviews=reviews,
            top_n=top_n * 2
        )

        formatted = []
        for r in results:
            if not self._passes_dietary_filters(r, profile):
                continue
            nutr = r.get("nutritions", {})
            cal = int(nutr.get("calories", 0) or 0)
            prot = int(nutr.get("protein_g", 0) or 0)

            if max_cal and max_cal > 200 and cal > max_cal + 100:
                continue

            reason = r.get("recommendation_reason") or f"Optimal fit: {cal} kcal and {prot}g protein tailored for your {profile.get('diet_goal', 'health')} goal."
            formatted.append(self.format_recipe_for_coach(r, reason=reason))

            if len(formatted) >= top_n:
                break

        # Fallback if filtered too strictly
        if not formatted:
            for r in results[:top_n]:
                formatted.append(self.format_recipe_for_coach(r))

        return formatted

    # Alias for method naming flexibility
    answer_query = process_query


coach_service = NutritionCoach()
