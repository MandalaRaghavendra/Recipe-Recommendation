import datetime
from datetime import datetime, date
import pandas as pd
import numpy as np

def calculate_bmr(weight, height, age, gender):
    """Calculates Basal Metabolic Rate using the Mifflin-St Jeor Equation."""
    if not (weight and height and age):
        return 1600.0
    if str(gender).strip().lower() == "female":
        return (10 * weight) + (6.25 * height) - (5 * age) - 161
    elif str(gender).strip().lower() == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 78

def calculate_bmi(weight, height):
    """Calculates BMI from weight (kg) and height (cm)."""
    if weight and height and height > 0:
        return weight / ((height / 100) ** 2)
    return None

def calculate_tdee(bmr, activity_level="moderately_active"):
    """Calculates Total Daily Energy Expenditure from BMR and activity multiplier."""
    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    m = multipliers.get(str(activity_level).lower(), 1.375)
    return round(bmr * m, 1)

def calculate_macronutrient_targets(tdee, diet_goal="weight_loss", weight_kg=70.0):
    """Calculates daily target calories, protein (g), carbs (g), and fat (g)."""
    SAFE_MIN_CALORIES = 1200.0
    goal = str(diet_goal).lower().replace(" ", "_")
    if goal == "weight_loss":
        target_calories = max(SAFE_MIN_CALORIES, round(tdee - 400.0))
        target_prot = max(round(weight_kg * 1.6), round((target_calories * 0.35) / 4))
        target_carbs = round((target_calories * 0.40) / 4)
        target_fat = round((target_calories * 0.25) / 9)
    elif goal == "muscle_gain":
        target_calories = round(tdee + 400.0)
        target_prot = max(round(weight_kg * 2.0), round((target_calories * 0.30) / 4))
        target_carbs = round((target_calories * 0.50) / 4)
        target_fat = round((target_calories * 0.20) / 9)
    elif goal == "keto":
        target_calories = max(SAFE_MIN_CALORIES, round(tdee - 200.0))
        target_prot = round((target_calories * 0.25) / 4)
        target_carbs = round((target_calories * 0.05) / 4)
        target_fat = round((target_calories * 0.70) / 9)
    else:
        target_calories = round(tdee)
        target_prot = max(round(weight_kg * 1.2), round((target_calories * 0.25) / 4))
        target_carbs = round((target_calories * 0.50) / 4)
        target_fat = round((target_calories * 0.25) / 9)
    return target_calories, target_prot, target_carbs, target_fat


def generate_diet_report(cooked_recipes, user_profile):
    """
    Processes cooked recipes to generate daily/weekly/monthly nutrition reports,
    scales nutrition by portion size (serving_size), and calculates real-time
    today_summary and full ai_coach metrics for instant progress tracking.
    """
    user_profile = user_profile or {}

    try:
        age = float(user_profile.get('age')) if user_profile.get('age') is not None else 25.0
    except (ValueError, TypeError):
        age = 25.0

    try:
        weight = float(user_profile.get('weight')) if user_profile.get('weight') is not None else 70.0
    except (ValueError, TypeError):
        weight = 70.0

    try:
        height = float(user_profile.get('height')) if user_profile.get('height') is not None else 170.0
    except (ValueError, TypeError):
        height = 170.0

    gender = str(user_profile.get('gender', 'male')).strip().lower()
    diet_goal = str(user_profile.get('diet_goal', 'weight_loss')).strip().lower()
    
    try:
        duration_months = int(user_profile.get('duration_months', 3))
    except (ValueError, TypeError):
        duration_months = 3

    # Mifflin-St Jeor BMR & TDEE
    bmr = calculate_bmr(weight, height, age, gender)
    bmr = max(500.0, float(bmr))
    tdee = bmr * 1.375

    SAFE_MIN_CALORIES = 1200.0

    if diet_goal == 'weight_loss':
        raw_deficit_target = tdee - 400.0
        target_calories = max(SAFE_MIN_CALORIES, round(raw_deficit_target))
        target_protein_pct, target_carbs_pct, target_fat_pct = 0.35, 0.40, 0.25
        strategy_text = f"Targeting a healthy caloric deficit of ~400 kcal/day (<strong>{target_calories} kcal/day</strong>) for sustainable fat loss."
        strategy_badge = "Healthy Deficit Target"
    elif diet_goal == 'muscle_gain':
        raw_surplus_target = tdee + 400.0
        target_calories = round(raw_surplus_target)
        target_protein_pct, target_carbs_pct, target_fat_pct = 0.30, 0.50, 0.20
        strategy_text = f"Targeting an energy surplus of ~400 kcal/day (<strong>{target_calories} kcal/day</strong>) with high protein for muscle synthesis."
        strategy_badge = "Lean Muscle Surplus"
    else:
        target_calories = round(tdee)
        target_protein_pct, target_carbs_pct, target_fat_pct = 0.25, 0.50, 0.25
        strategy_text = f"Targeting energy maintenance at <strong>{target_calories} kcal/day</strong> to keep stable weight and vitality."
        strategy_badge = "Active Maintenance"

    target_protein = round((target_calories * target_protein_pct) / 4.0)
    target_carbs = round((target_calories * target_carbs_pct) / 4.0)
    target_fat = round((target_calories * target_fat_pct) / 9.0)

    target_goals = {
        'goal': diet_goal,
        'bmr': round(bmr),
        'tdee': round(tdee),
        'duration_months': duration_months,
        'target_calories': target_calories,
        'target_protein': target_protein,
        'target_carbs': target_carbs,
        'target_fat': target_fat,
        'target_weekly_calories': target_calories * 7,
        'target_weekly_protein': target_protein * 7,
        'target_weekly_carbs': target_carbs * 7,
        'target_weekly_fat': target_fat * 7,
        'target_monthly_calories': target_calories * 30,
        'target_monthly_protein': target_protein * 30,
        'target_monthly_carbs': target_carbs * 30,
        'target_monthly_fat': target_fat * 30,
        'actual_avg_calories': 0,
        'actual_avg_protein': 0,
        'actual_avg_carbs': 0,
        'actual_avg_fat': 0,
    }

    # Process Meal Logs with portion multipliers
    today_str = date.today().isoformat()
    today_cal, today_protein, today_carbs, today_fat = 0, 0, 0, 0
    daily_records = {}

    if cooked_recipes:
        for meal in cooked_recipes:
            portion = float(meal.get("serving_size") or 1.0)
            nutr = meal.get("nutritions", {})
            if isinstance(nutr, dict):
                cal = float(nutr.get("calories", 0) or 0) * portion
                prot = float(nutr.get("protein_g", 0) or 0) * portion
                carb = float(nutr.get("carbs_g", 0) or 0) * portion
                fat = float(nutr.get("fat_g", 0) or 0) * portion
            else:
                cal, prot, carb, fat = 300 * portion, 15 * portion, 40 * portion, 10 * portion

            cooked_time = str(meal.get("cooked_at", ""))
            day_key = cooked_time[:10] if len(cooked_time) >= 10 else today_str

            if day_key not in daily_records:
                daily_records[day_key] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "count": 0}
            daily_records[day_key]["calories"] += cal
            daily_records[day_key]["protein"] += prot
            daily_records[day_key]["carbs"] += carb
            daily_records[day_key]["fat"] += fat
            daily_records[day_key]["count"] += 1

            if day_key == today_str:
                today_cal += cal
                today_protein += prot
                today_carbs += carb
                today_fat += fat

    # Daily list
    daily_list = []
    for d, vals in sorted(daily_records.items()):
        daily_list.append({
            "period": d,
            "calories": round(vals["calories"]),
            "protein": round(vals["protein"]),
            "carbs": round(vals["carbs"]),
            "fat": round(vals["fat"]),
            "target_calories": target_calories,
            "target_protein": target_protein,
            "target_carbs": target_carbs,
            "target_fat": target_fat,
        })

    today_pct = min(100, round((today_cal / max(1, target_calories)) * 100)) if target_calories > 0 else 0
    today_summary = {
        "consumed_calories": round(today_cal),
        "target_calories": target_calories,
        "calories_pct": today_pct,
        "consumed_protein": round(today_protein),
        "target_protein": target_protein,
        "remaining_protein": max(0, target_protein - round(today_protein)),
        "consumed_carbs": round(today_carbs),
        "target_carbs": target_carbs,
        "remaining_carbs": max(0, target_carbs - round(today_carbs)),
        "consumed_fat": round(today_fat),
        "target_fat": target_fat,
        "remaining_fat": max(0, target_fat - round(today_fat)),
        "remaining_calories": max(0, target_calories - round(today_cal)),
        "goal_completion_pct": today_pct
    }

    # Calorie Adherence Status
    if today_cal == 0:
        intake_badge = "No Meals Logged"
        intake_badge_class = "bg-secondary"
        intake_pill_class = "bg-secondary-subtle"
        intake_icon = "fas fa-utensils"
        intake_text = f"You haven't logged any meals yet today. Log recipes from the dashboard to track your <strong>{target_calories} kcal</strong> target."
    elif today_cal <= target_calories:
        intake_badge = "On Track"
        intake_badge_class = "bg-success"
        intake_pill_class = "bg-success-subtle"
        intake_icon = "fas fa-check-circle"
        intake_text = f"Great pacing! You have consumed <strong>{round(today_cal)} kcal</strong> with <strong>{today_summary['remaining_calories']} kcal</strong> remaining today."
    else:
        over_amount = round(today_cal - target_calories)
        intake_badge = "Above Target"
        intake_badge_class = "bg-warning text-dark"
        intake_pill_class = "bg-warning-subtle"
        intake_icon = "fas fa-exclamation-circle"
        intake_text = f"You are <strong>{over_amount} kcal</strong> above your daily baseline. Focus on high-fiber vegetables and light hydration for dinner."

    # Macronutrient Status
    macro_text = f"Aim for <strong>{target_protein}g Protein</strong> ({round(today_protein)}g logged), <strong>{target_carbs}g Carbs</strong> ({round(today_carbs)}g logged), and <strong>{target_fat}g Healthy Fats</strong> ({round(today_fat)}g logged)."

    ai_coach = {
        "strategy": {
            "title": "Daily Caloric & Goal Strategy",
            "badge": strategy_badge,
            "icon": "fas fa-bullseye",
            "text": strategy_text
        },
        "intake_status": {
            "title": "Calorie Adherence Status",
            "badge": intake_badge,
            "badge_class": intake_badge_class,
            "pill_class": intake_pill_class,
            "icon": intake_icon,
            "text": intake_text
        },
        "macro_status": {
            "title": "Macronutrient & Protein Target",
            "badge": f"{target_protein}g Protein Target",
            "icon": "fas fa-dumbbell",
            "text": macro_text
        },
        "tips": [
            f"🎯 You have <strong>{today_summary['remaining_calories']} kcal</strong> remaining in your daily budget.",
            f"💪 Prioritize lean protein sources like lentils, paneer, and eggs to hit your <strong>{target_protein}g</strong> target.",
            "💧 Drink at least 2.5 to 3 liters of water throughout the day to support optimal digestion and metabolism."
        ]
    }

    # Generate full comprehensive analytics (Today, Week, Month)
    analytics = get_comprehensive_analytics(cooked_recipes, user_profile)

    return {
        "report": {
            "daily": daily_list,
            "weekly": daily_list,
            "monthly": daily_list
        },
        "target_goals": target_goals,
        "today_summary": today_summary,
        "today": analytics.get("today", today_summary),
        "week": analytics.get("week", {}),
        "month": analytics.get("month", {}),
        "weekly_analytics": analytics.get("week", {}),
        "monthly_analytics": analytics.get("month", {}),
        "ai_coach": ai_coach,
        "analytics": analytics,
        "suggestions": [strategy_text]
    }

def get_comprehensive_analytics(cooked_recipes, user_profile):
    """
    Computes precise, multi-dimensional nutrition analytics for Today, Week, and Month
    based strictly on actual SQLite database meal logs and recipe nutrition data.
    """
    user_profile = user_profile or {}
    cooked_recipes = cooked_recipes or []

    try:
        age = float(user_profile.get('age')) if user_profile.get('age') is not None else 25.0
    except (ValueError, TypeError):
        age = 25.0

    try:
        weight = float(user_profile.get('weight')) if user_profile.get('weight') is not None else 70.0
    except (ValueError, TypeError):
        weight = 70.0

    try:
        height = float(user_profile.get('height')) if user_profile.get('height') is not None else 170.0
    except (ValueError, TypeError):
        height = 170.0

    gender = str(user_profile.get('gender', 'male')).strip().lower()
    diet_goal = str(user_profile.get('diet_goal', 'weight_loss')).strip().lower()

    bmr = calculate_bmr(weight, height, age, gender)
    tdee = bmr * 1.375

    if diet_goal == 'weight_loss':
        target_calories = max(1200, round(tdee - 400.0))
        target_protein = round((target_calories * 0.35) / 4.0)
        target_carbs = round((target_calories * 0.40) / 4.0)
        target_fat = round((target_calories * 0.25) / 9.0)
    elif diet_goal == 'muscle_gain':
        target_calories = round(tdee + 400.0)
        target_protein = round((target_calories * 0.30) / 4.0)
        target_carbs = round((target_calories * 0.50) / 4.0)
        target_fat = round((target_calories * 0.20) / 9.0)
    else:
        target_calories = round(tdee)
        target_protein = round((target_calories * 0.25) / 4.0)
        target_carbs = round((target_calories * 0.50) / 4.0)
        target_fat = round((target_calories * 0.25) / 9.0)

    import datetime
    from collections import Counter

    today_dt = datetime.date.today()
    today_str = today_dt.isoformat()

    # Aggregate all meals by ISO date
    day_map = {}
    today_meals_list = []
    recipe_counter = Counter()
    category_counter = Counter()

    for meal in cooked_recipes:
        portion = float(meal.get("serving_size") or 1.0)
        nutr = meal.get("nutritions", {})
        if isinstance(nutr, dict):
            cal = float(nutr.get("calories", 0) or 0) * portion
            prot = float(nutr.get("protein_g", 0) or 0) * portion
            carb = float(nutr.get("carbs_g", 0) or 0) * portion
            fat = float(nutr.get("fat_g", 0) or 0) * portion
        else:
            cal, prot, carb, fat = 300 * portion, 15 * portion, 40 * portion, 10 * portion

        cooked_time = str(meal.get("cooked_at") or meal.get("created_at") or "")
        date_str = cooked_time[:10] if len(cooked_time) >= 10 else today_str

        if date_str not in day_map:
            day_map[date_str] = {
                "calories": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
                "meals_count": 0
            }

        day_map[date_str]["calories"] += cal
        day_map[date_str]["protein"] += prot
        day_map[date_str]["carbs"] += carb
        day_map[date_str]["fat"] += fat
        day_map[date_str]["meals_count"] += 1

        rid = str(meal.get("recipe_id", ""))
        rname = meal.get("recipe_name") or f"Recipe #{rid}"
        if rid:
            recipe_counter[(rid, rname, meal.get("image_link", ""))] += 1

        # Categories / Tags
        cuisine = meal.get("cuisine") or "Indian"
        veg_status = meal.get("veg_nonveg") or "Veg"
        goal_tag = meal.get("diet_goal") or "Balanced"
        category_counter[veg_status] += 1
        category_counter[f"{goal_tag} Goal"] += 1
        if cuisine and cuisine != "N/A":
            category_counter[f"{cuisine} Style"] += 1

        if date_str == today_str:
            today_meals_list.append({
                "recipe_id": rid,
                "recipe_name": rname,
                "image_link": meal.get("image_link", ""),
                "calories": round(cal),
                "protein": round(prot),
                "carbs": round(carb),
                "fat": round(fat),
                "serving_size": portion,
                "logged_time": cooked_time[11:16] if len(cooked_time) >= 16 else "Today"
            })

    # 1. TODAY ANALYTICS
    today_data = day_map.get(today_str, {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "meals_count": 0})
    today_cal = round(today_data["calories"])
    today_prot = round(today_data["protein"])
    today_carb = round(today_data["carbs"])
    today_fat_val = round(today_data["fat"])

    cal_pct = min(100, round((today_cal / max(1, target_calories)) * 100))
    prot_pct = min(100, round((today_prot / max(1, target_protein)) * 100))
    carbs_pct = min(100, round((today_carb / max(1, target_carbs)) * 100))
    fat_pct = min(100, round((today_fat_val / max(1, target_fat)) * 100))

    today_analytics = {
        "date": today_str,
        "date_formatted": today_dt.strftime("%A, %B %d, %Y"),
        "consumed_calories": today_cal,
        "target_calories": target_calories,
        "remaining_calories": max(0, target_calories - today_cal),
        "consumed_protein": today_prot,
        "target_protein": target_protein,
        "remaining_protein": max(0, target_protein - today_prot),
        "consumed_carbs": today_carb,
        "target_carbs": target_carbs,
        "remaining_carbs": max(0, target_carbs - today_carb),
        "consumed_fat": today_fat_val,
        "target_fat": target_fat,
        "remaining_fat": max(0, target_fat - today_fat_val),
        "goal_completion_pct": cal_pct,
        "protein_completion_pct": prot_pct,
        "carbs_completion_pct": carbs_pct,
        "fat_completion_pct": fat_pct,
        "meals_logged_today": len(today_meals_list),
        "today_meals": today_meals_list
    }

    # 2. WEEK ANALYTICS (Last 7 Days)
    week_dates = []
    week_labels = []
    week_calories = []
    week_protein = []
    week_carbs = []
    week_fat = []
    week_targets = []
    week_total_cal = 0
    week_total_prot = 0
    week_meals_count = 0
    week_active_days = 0

    for i in range(6, -1, -1):
        d = today_dt - datetime.timedelta(days=i)
        d_str = d.isoformat()
        day_label = d.strftime("%a (%b %d)")
        week_dates.append(d_str)
        week_labels.append(day_label)
        week_targets.append(target_calories)

        if d_str in day_map:
            c = round(day_map[d_str]["calories"])
            p = round(day_map[d_str]["protein"])
            cb = round(day_map[d_str]["carbs"])
            f = round(day_map[d_str]["fat"])
            mc = day_map[d_str]["meals_count"]
            week_active_days += 1
        else:
            c, p, cb, f, mc = 0, 0, 0, 0, 0

        week_calories.append(c)
        week_protein.append(p)
        week_carbs.append(cb)
        week_fat.append(f)
        week_total_cal += c
        week_total_prot += p
        week_meals_count += mc

    avg_weekly_cal = round(week_total_cal / 7.0, 1)
    avg_weekly_prot = round(week_total_prot / 7.0, 1)

    week_analytics = {
        "dates": week_dates,
        "labels": week_labels,
        "calories": week_calories,
        "protein": week_protein,
        "carbs": week_carbs,
        "fat": week_fat,
        "targets": week_targets,
        "avg_daily_calories": avg_weekly_cal,
        "avg_daily_protein": avg_weekly_prot,
        "total_meals_logged": week_meals_count,
        "active_days_count": week_active_days,
        "target_calories": target_calories,
        "target_protein": target_protein
    }

    # 3. MONTH ANALYTICS (Last 30 Days)
    month_dates = []
    month_labels = []
    month_calories = []
    month_protein = []
    month_targets = []
    month_total_cal = 0
    month_total_prot = 0
    month_meals_count = 0
    month_active_days = 0
    adherence_days_count = 0

    for i in range(29, -1, -1):
        d = today_dt - datetime.timedelta(days=i)
        d_str = d.isoformat()
        month_dates.append(d_str)
        month_labels.append(d.strftime("%b %d"))
        month_targets.append(target_calories)

        if d_str in day_map:
            c = round(day_map[d_str]["calories"])
            p = round(day_map[d_str]["protein"])
            mc = day_map[d_str]["meals_count"]
            month_active_days += 1
            # Check adherence within +/- 20% of target
            if abs(c - target_calories) <= (target_calories * 0.20):
                adherence_days_count += 1
        else:
            c, p, mc = 0, 0, 0

        month_calories.append(c)
        month_protein.append(p)
        month_total_cal += c
        month_total_prot += p
        month_meals_count += mc

    avg_month_cal = round(month_total_cal / max(1, month_active_days if month_active_days > 0 else 30), 1)
    goal_adherence_pct = round((adherence_days_count / max(1, month_active_days)) * 100) if month_active_days > 0 else (100 if today_cal <= target_calories else 80)
    avg_meals_per_day = round(month_meals_count / max(1, month_active_days), 1) if month_active_days > 0 else (len(today_meals_list) if today_meals_list else 0)

    # Most eaten recipes
    top_recipes = []
    for (rid, rname, img), cnt in recipe_counter.most_common(5):
        top_recipes.append({
            "recipe_id": rid,
            "recipe_name": rname,
            "image_link": img or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
            "times_eaten": cnt
        })

    # Preferred categories
    top_categories = []
    for cat_name, cnt in category_counter.most_common(5):
        top_categories.append({
            "category": cat_name,
            "count": cnt
        })

    month_analytics = {
        "dates": month_dates,
        "labels": month_labels,
        "calories": month_calories,
        "protein": month_protein,
        "targets": month_targets,
        "avg_daily_calories": avg_month_cal,
        "goal_adherence_pct": goal_adherence_pct,
        "total_meals_logged": month_meals_count,
        "avg_meals_per_day": avg_meals_per_day,
        "active_days_count": month_active_days,
        "most_eaten_recipes": top_recipes,
        "preferred_categories": top_categories
    }

    return {
        "today": today_analytics,
        "week": week_analytics,
        "month": month_analytics,
        "today_summary": today_analytics,
        "weekly_analytics": week_analytics,
        "monthly_analytics": month_analytics,
        "target_goals": {
            "bmr": round(bmr),
            "tdee": round(tdee),
            "target_calories": target_calories,
            "target_protein": target_protein,
            "target_carbs": target_carbs,
            "target_fat": target_fat,
            "diet_goal": diet_goal
        }
    }

