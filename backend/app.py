import os
import sys
import json
import time
from functools import wraps
from datetime import timedelta, datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ai-service"))
sys.path.insert(0, CURRENT_DIR)

from embedding_engine import ai_engine
import database as db
import nutrition_engine as nutrition
from nutrition_coach import coach_service
from meal_planner import meal_planner_service
from grocery_engine import generate_grocery_list_from_plan
from preference_engine import preference_engine
from food_vision_engine import food_vision_engine
from validators import (
    validate_email,
    validate_password,
    validate_rating,
    validate_serving_size,
    validate_profile_payload,
    sanitize_text
)

TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "web-app", "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "web-app", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR if os.path.exists(TEMPLATE_DIR) else "templates",
    static_folder=STATIC_DIR if os.path.exists(STATIC_DIR) else "static"
)

# Secrets & Session Hardening
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

INSECURE_FALLBACK_KEYS = {
    "supersecret-recipe-key-2026",
    "secret",
    "secret_key",
    "default",
    "changeme",
    "development",
    "dev",
}

def resolve_secret_key():
    """
    Validates and configures Flask SECRET_KEY with strict production enforcement.
    In production environments (e.g. Render, FLASK_ENV=production, ENV=production),
    refuses to start if SECRET_KEY is missing, empty, or using a known fallback.
    In local development, safely falls back to a development key.
    """
    is_production = any([
        os.environ.get("RENDER", "").lower() in ("true", "1"),
        os.environ.get("FLASK_ENV", "").lower() in ("production", "prod"),
        os.environ.get("ENV", "").lower() in ("production", "prod"),
        os.environ.get("ENVIRONMENT", "").lower() in ("production", "prod"),
        os.environ.get("PRODUCTION", "").lower() in ("true", "1"),
    ])

    raw_secret = os.environ.get("SECRET_KEY")
    clean_secret = raw_secret.strip() if raw_secret else ""

    if is_production:
        if not clean_secret or clean_secret in INSECURE_FALLBACK_KEYS or len(clean_secret) < 16:
            raise RuntimeError(
                "CRITICAL SECURITY CONFIGURATION ERROR: A strong, unique SECRET_KEY environment variable "
                "(minimum 16 characters) must be configured in production (detected production environment). "
                "Refusing to start with missing, empty, or known default fallback key."
            )
        return clean_secret
    else:
        # Development / local testing mode fallback
        return clean_secret if clean_secret else "supersecret-recipe-key-2026"

app.secret_key = resolve_secret_key()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# In-memory sliding-window rate limiter for auth endpoints
AUTH_ATTEMPTS = {}

def check_rate_limit(key, max_attempts=15, window_seconds=60):
    """Sliding-window rate limiter to mitigate brute-force attacks."""
    now = time.time()
    attempts = AUTH_ATTEMPTS.get(key, [])
    attempts = [t for t in attempts if now - t < window_seconds]
    if len(attempts) >= max_attempts:
        return False
    attempts.append(now)
    AUTH_ATTEMPTS[key] = attempts
    return True

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session or not session.get("user_id"):
            return redirect(url_for("home", message="Please login to access this feature."))
        return f(*args, **kwargs)
    return decorated_function

def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id and request.is_json:
            payload = request.get_json(silent=True) or {}
            user_id = payload.get("user_id")
        if not user_id:
            user_id = request.args.get("user_id") or request.headers.get("X-User-Id")
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized", "message": "Authentication required to access this resource."}), 401
        return f(*args, **kwargs)
    return decorated_function

try:
    from flask_cors import CORS
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
    CORS(app, resources={r"/api/*": {"origins": allowed_origins if allowed_origins != ["*"] else "*"}})
    print("[Backend] CORS enabled for /api/* endpoints")
except ImportError:
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-User-Id"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

def _normalize_image_url(recipe):
    """Ensures image_link is absolute for API clients if it points to a local static route."""
    if not isinstance(recipe, dict):
        return recipe
    r = dict(recipe)
    img = r.get("image_link", "")
    if img and img.startswith("/static/"):
        try:
            r["image_link"] = request.host_url.rstrip("/") + img
        except Exception:
            pass
    return r

def _normalize_recipe_list(recipes):
    if not recipes:
        return []
    return [_normalize_image_url(r) for r in recipes if r]

def _get_user_context(user_id):
    """Helper to retrieve user profile, meal history, reviews, favorites, and learned preference profile."""
    if not user_id:
        return {}, [], {}, [], {}
    profile = db.get_user_profile(user_id) or {}
    cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id) or []
    reviews = db.get_all_user_reviews(user_id) or {}
    favorites = db.get_user_favorites(user_id) or []
    pref_profile = preference_engine.get_user_preference_profile(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id)
    return profile, cooked, reviews, favorites, pref_profile

@app.route("/favicon.ico")
def favicon():
    icon_dir = os.path.join(STATIC_DIR, "icons")
    icon_file = "icon-192x192.png"
    if os.path.exists(os.path.join(icon_dir, icon_file)):
        return send_from_directory(icon_dir, icon_file, mimetype="image/png")
    return ("", 204)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("main.html", message=request.args.get("message"))

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)

    all_recipes = ai_engine.get_all_recipes()
    user_allergies = user_profile.get("allergies", []) if isinstance(user_profile.get("allergies"), list) else []

    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    today_summary = diet_report.get("today_summary", {})

    if user_id:
        recipes = ai_engine.recommend_personalized(
            query_str="",
            user_profile=user_profile,
            user_history=cooked,
            user_reviews=reviews,
            preference_profile=pref_profile,
            top_n=9
        )
    else:
        recipes = all_recipes[:9]

    return render_template(
        "index.html",
        recipes=recipes,
        all_recipes=all_recipes,
        user_allergies=user_allergies,
        favorites=favorites,
        today_summary=today_summary,
        message=request.args.get("message"),
        session=session
    )

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return redirect(url_for("home"))

    client_ip = request.remote_addr or "127.0.0.1"
    if not check_rate_limit(f"signup_{client_ip}", max_attempts=30, window_seconds=60):
        return redirect(url_for("home", message="Too many signup attempts. Please wait a minute and try again."))

    name = str(request.form.get("name") or "").strip()
    email = str(request.form.get("email") or "").strip()
    password = str(request.form.get("password") or "")

    success, res = db.register_user(name, email, password)
    if success:
        session["user"] = res
        session["user_id"] = res.get("objectId")
        return redirect(url_for("dashboard", message=f"Welcome to Tastio, {res.get('name', 'User')}! Your personalized dashboard is ready."))
    else:
        return redirect(url_for("home", message=f"Signup failed: {res}"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("home"))

    client_ip = request.remote_addr or "127.0.0.1"
    if not check_rate_limit(f"login_{client_ip}", max_attempts=40, window_seconds=60):
        return redirect(url_for("home", message="Too many login attempts. Please wait a minute and try again."))

    email = str(request.form.get("email") or "").strip()
    password = str(request.form.get("password") or "")

    success, user = db.login_user(email, password)
    if success:
        session["user"] = user
        session["user_id"] = user.get("objectId")
        return redirect(url_for("dashboard", message=f"Welcome back, {user.get('name', 'User')}!"))
    else:
        session.clear()
        return redirect(url_for("home", message=f"Login failed: {user}"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home", message="Logged out successfully."))

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if request.method == "POST":
        query = request.form.get("query", "").strip()
    else:
        query = request.args.get("query", "").strip()

    all_recipes = ai_engine.get_all_recipes()

    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
    user_allergies = user_profile.get("allergies", []) if isinstance(user_profile.get("allergies"), list) else []

    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    today_summary = diet_report.get("today_summary", {})

    if user_id:
        results = ai_engine.recommend_personalized(
            query_str=query,
            user_profile=user_profile,
            user_history=cooked,
            user_reviews=reviews,
            preference_profile=pref_profile,
            top_n=12
        )
    else:
        results = ai_engine.recommend_semantic(query, top_n=12)

    if query:
        if results:
            message = f"Found {len(results)} personalized recommendations matching '{query}'"
        else:
            message = f"❌ No recipes found matching '{query}' within your dietary preferences. Showing popular dishes instead."
            results = all_recipes[:10]
    else:
        message = "Showing your personalized AI recommendations."

    return render_template(
        "index.html",
        recipes=results,
        all_recipes=all_recipes,
        user_allergies=user_allergies,
        favorites=favorites,
        today_summary=today_summary,
        query=query,
        message=message,
        session=session
    )

@app.route("/what-can-i-cook", methods=["GET", "POST"])
def what_can_i_cook():
    """'What Can I Cook?' Pantry Matcher Route."""
    if request.method == "POST":
        pantry_input = request.form.get("pantry_ingredients", "").strip()
    else:
        pantry_input = request.args.get("pantry_ingredients", "").strip()

    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
    user_allergies = user_profile.get("allergies", []) if isinstance(user_profile.get("allergies"), list) else []

    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    today_summary = diet_report.get("today_summary", {})
    all_recipes = ai_engine.get_all_recipes()

    if pantry_input:
        results = ai_engine.match_pantry_ingredients(
            pantry_ingredients_str=pantry_input,
            user_profile=user_profile,
            top_n=12
        )
        message = f"🥘 Found {len(results)} recipes you can cook with your pantry ingredients!"
    else:
        results = all_recipes[:10]
        message = "Enter your pantry ingredients above to discover what you can cook right now."

    return render_template(
        "index.html",
        recipes=results,
        all_recipes=all_recipes,
        user_allergies=user_allergies,
        favorites=favorites,
        today_summary=today_summary,
        pantry_query=pantry_input,
        is_pantry_mode=True,
        message=message,
        session=session
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("home", message="Please login to view profile."))

    user_id = user.get("objectId") if isinstance(user, dict) else None

    if request.method == "POST":
        payload = {
            "age": int(request.form.get("age", 25)) if request.form.get("age") else None,
            "gender": request.form.get("gender"),
            "height": float(request.form.get("height", 170)) if request.form.get("height") else None,
            "weight": float(request.form.get("weight", 70)) if request.form.get("weight") else None,
            "diet_goal": request.form.get("diet_goal"),
            "food_pref": request.form.get("food_pref", "both"),
            "allergies": request.form.get("allergies"),
            "duration_months": int(request.form.get("duration_months", 3)) if request.form.get("duration_months") else 3
        }
        db.save_user_profile(user_id, payload)
        return redirect(url_for("profile", message="✅ Profile & AI nutrition targets updated!"))

    user_profile = db.get_user_profile(user_id) or {}
    cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id) or []
    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    active_tab = request.args.get("active_tab", "v-pills-profile")

    return render_template(
        "profile.html",
        profile=user_profile,
        user_profile=user_profile,
        cooked_recipes=cooked,
        diet_report=diet_report,
        analytics=diet_report.get("analytics", {}),
        active_tab=active_tab,
        message=request.args.get("message"),
        session=session
    )

@app.route("/analytics")
@app.route("/nutrition-dashboard")
def analytics():
    """Direct route to Nutrition Analytics Dashboard."""
    return redirect(url_for("profile", active_tab="v-pills-diet-history"))

@app.route("/history")
def history():
    return redirect(url_for("profile", active_tab="v-pills-history"))

@app.route("/coach")
@app.route("/ai-coach")
def coach():
    """Tastio AI Nutrition Coach Web View"""
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    all_recipes = ai_engine.get_all_recipes()

    # Initial greeting and baseline suggestions from coach service
    initial_res = coach_service.process_query("Hello coach", user_id=user_id)

    return render_template(
        "coach.html",
        user_profile=user_profile,
        diet_report=diet_report,
        today_summary=diet_report.get("today_summary", {}),
        target_goals=diet_report.get("target_goals", {}),
        initial_coach=initial_res,
        favorites=favorites,
        all_recipes=all_recipes,
        session=session
    )

@app.route("/meal-plan")
@app.route("/mealplan")
def meal_plan():
    """Tastio 7-Day AI Meal Planner Web View"""
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    all_recipes = ai_engine.get_all_recipes()

    # Get active or newly generated plan
    current_plan = meal_planner_service.get_current_plan(user_id=user_id)

    return render_template(
        "meal_plan.html",
        user_profile=user_profile,
        diet_report=diet_report,
        today_summary=diet_report.get("today_summary", {}),
        target_goals=diet_report.get("target_goals", {}),
        meal_plan=current_plan,
        favorites=favorites,
        all_recipes=all_recipes,
        session=session
    )

@app.route("/mark_eaten/<recipe_id>", methods=["POST"])
def mark_eaten(recipe_id):
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else request.json.get("user_id") if request.is_json else None
    if not user_id:
        if request.is_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return redirect(url_for("home", message="Please login first."))

    serving_size = float(request.json.get("serving_size", 1.0)) if request.is_json else float(request.form.get("serving_size", 1.0))
    success, res = db.mark_recipe_eaten(user_id, recipe_id, serving_size=serving_size)

    if request.is_json:
        return jsonify({"success": success, "message": "Recipe logged!" if success else "Failed to log recipe"})
    return redirect(url_for("dashboard", message="✅ Meal logged successfully!"))

@app.route("/favorite/<recipe_id>", methods=["POST"])
def favorite(recipe_id):
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else request.json.get("user_id") if request.is_json else None
    if not user_id:
        if request.is_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return redirect(url_for("home", message="Please login first."))

    is_fav, msg = db.toggle_favorite(user_id, recipe_id)
    if request.is_json:
        return jsonify({"success": True, "is_favorite": is_fav, "message": msg})
    return redirect(url_for("dashboard", message=f"⭐ {msg}"))

@app.route("/review/<recipe_id>", methods=["POST"])
def review(recipe_id):
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else request.json.get("user_id") if request.is_json else None
    if not user_id:
        if request.is_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return redirect(url_for("home", message="Please login first."))

    if request.is_json:
        data = request.get_json() or {}
        rating = data.get("rating", 5)
        comment = data.get("comment", "")
    else:
        rating = request.form.get("rating", 5)
        comment = request.form.get("comment", "")

    success = db.save_recipe_review(user_id, recipe_id, rating, comment)
    if request.is_json:
        return jsonify({"success": success, "message": "Review saved!" if success else "Failed to save review"})
    return redirect(url_for("profile"))

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "healthy",
        "service": "Recipe Recommendation API",
        "version": "2.0 (Personalized AI & What Can I Cook Engine)",
        "database": "Local SQLite (100% Keyless & Offline)",
        "recipes_indexed": len(ai_engine.recipes_by_id)
    })

@app.route("/api/auth/signup", methods=["POST"])
def api_signup():
    client_ip = request.remote_addr or "127.0.0.1"
    if not check_rate_limit(f"api_signup_{client_ip}", max_attempts=30, window_seconds=60):
        return jsonify({"success": False, "error": "Too Many Requests", "message": "Too many signup attempts. Please try again later."}), 429

    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name") or "").strip()
    email = str(payload.get("email") or "").strip()
    password = str(payload.get("password") or "")

    if not name:
        return jsonify({"success": False, "message": "Name is required."}), 400
    if not email:
        return jsonify({"success": False, "message": "Email is required."}), 400
    if not password:
        return jsonify({"success": False, "message": "Password is required."}), 400

    success, res = db.register_user(name, email, password)
    if success:
        session["user"] = res
        session["user_id"] = res.get("objectId")
        return jsonify({"success": True, "user": res})
    return jsonify({"success": False, "message": str(res)}), 400

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    client_ip = request.remote_addr or "127.0.0.1"
    if not check_rate_limit(f"api_login_{client_ip}", max_attempts=40, window_seconds=60):
        return jsonify({"success": False, "error": "Too Many Requests", "message": "Too many login attempts. Please try again later."}), 429

    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email") or payload.get("login") or "").strip()
    password = str(payload.get("password") or "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    success, res = db.login_user(email, password)
    if success:
        session["user"] = res
        session["user_id"] = res.get("objectId")
        return jsonify({"success": True, "user": res})
    return jsonify({"success": False, "message": str(res)}), 401

@app.route("/api/recipes", methods=["GET"])
def api_recipes():
    """
    Multi-facet recipe endpoint supporting Indian regional cuisines, meal types,
    diet categories, nutrition tags, difficulty, cooking time, and calorie/protein filters.
    """
    cuisine = request.args.get("cuisine")
    meal_type = request.args.get("meal_type")
    diet = request.args.get("diet") or request.args.get("category")
    nutrition_tag = request.args.get("nutrition_tag")
    difficulty = request.args.get("difficulty")
    max_time = request.args.get("max_time")
    max_calories = request.args.get("max_calories") or request.args.get("max_cal")
    min_protein = request.args.get("min_protein")
    query = request.args.get("search") or request.args.get("query")
    top_n = int(request.args.get("top_n", 150))

    filtered = ai_engine.filter_recipes(
        cuisine=cuisine,
        meal_type=meal_type,
        diet=diet,
        nutrition_tag=nutrition_tag,
        difficulty=difficulty,
        max_time=max_time,
        max_calories=max_calories,
        min_protein=min_protein,
        query=query,
        top_n=top_n
    )

    return jsonify({"success": True, "count": len(filtered), "recipes": _normalize_recipe_list(filtered)})

@app.route("/api/recipes/filter", methods=["POST", "GET"])
def api_filter_recipes():
    """Multi-facet filter endpoint accepting JSON payload or query parameters."""
    if request.is_json:
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()

    cuisine = payload.get("cuisine")
    meal_type = payload.get("meal_type")
    diet = payload.get("diet") or payload.get("category")
    nutrition_tag = payload.get("nutrition_tag")
    difficulty = payload.get("difficulty")
    max_time = payload.get("max_time")
    max_calories = payload.get("max_calories") or payload.get("max_cal")
    min_protein = payload.get("min_protein")
    query = payload.get("query") or payload.get("search")
    top_n = int(payload.get("top_n", 150))

    filtered = ai_engine.filter_recipes(
        cuisine=cuisine,
        meal_type=meal_type,
        diet=diet,
        nutrition_tag=nutrition_tag,
        difficulty=difficulty,
        max_time=max_time,
        max_calories=max_calories,
        min_protein=min_protein,
        query=query,
        top_n=top_n
    )

    return jsonify({"success": True, "count": len(filtered), "recipes": _normalize_recipe_list(filtered)})

@app.route("/api/recipes/<recipe_id>", methods=["GET"])
def api_get_recipe_detail(recipe_id):
    recipe = ai_engine.get_recipe_by_id(recipe_id)
    if recipe:
        return jsonify({"success": True, "recipe": _normalize_image_url(recipe)})
    return jsonify({"success": False, "message": "Recipe not found"}), 404

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    payload = request.get_json() or {}
    query = payload.get("query", "")
    user_id = payload.get("user_id")
    top_n = int(payload.get("top_n", 10))

    if user_id:
        user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
        results = ai_engine.recommend_personalized(
            query_str=query,
            user_profile=user_profile,
            user_history=cooked,
            user_reviews=reviews,
            preference_profile=pref_profile,
            top_n=top_n
        )
    else:
        results = ai_engine.recommend_semantic(query, top_n=top_n)

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "is_personalized": bool(user_id),
        "recipes": _normalize_recipe_list(results)
    })

@app.route("/api/pantry-match", methods=["POST"])
def api_pantry_match():
    """'What Can I Cook?' REST API endpoint."""
    payload = request.get_json() or {}
    ingredients = payload.get("ingredients") or payload.get("query", "")
    user_id = payload.get("user_id")
    top_n = int(payload.get("top_n", 10))

    user_profile = db.get_user_profile(user_id) if user_id else None
    results = ai_engine.match_pantry_ingredients(
        pantry_ingredients_str=ingredients,
        user_profile=user_profile,
        top_n=top_n
    )

    return jsonify({
        "success": True,
        "ingredients": ingredients,
        "count": len(results),
        "recipes": _normalize_recipe_list(results)
    })

@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    user_id = request.args.get("user_id") or session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Unauthorized", "message": "Authentication required"}), 401

    if request.method == "POST":
        payload = request.get_json() or {}
        is_valid, clean = validate_profile_payload(payload)
        if not is_valid:
            return jsonify({"success": False, "error": "Invalid Input", "message": clean}), 400
        clean["user_id"] = user_id
        success = db.save_user_profile(user_id, clean)
        return jsonify({"success": success, "message": "Profile updated" if success else "Failed to update profile"})

    profile = db.get_user_profile(user_id)
    cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id)
    diet_report = nutrition.generate_diet_report(cooked, profile)

    return jsonify({
        "success": True,
        "profile": profile,
        "diet_report": diet_report
    })

@app.route("/api/history", methods=["GET"])
def api_history():
    user_id = request.args.get("user_id") or session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    cooked = db.get_cooked_recipes(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id)
    return jsonify({"success": True, "history": cooked})

@app.route("/api/mark_eaten/<recipe_id>", methods=["POST"])
def api_mark_eaten(recipe_id):
    payload = request.get_json() or {}
    user_id = payload.get("user_id") or session.get("user_id")
    serving_size = float(payload.get("serving_size", 1.0))
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    success, res = db.mark_recipe_eaten(user_id, recipe_id, serving_size=serving_size)
    if success:
        return jsonify({"success": True, "message": "Recipe logged as eaten!", "review_exists": res.get("review_exists", False)})
    return jsonify({"success": False, "message": "Failed to log recipe", "error": str(res)}), 400

@app.route("/api/favorites", methods=["GET", "POST"])
def api_favorites():
    user_id = request.args.get("user_id") or (request.json.get("user_id") if request.is_json else session.get("user_id"))
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    if request.method == "POST":
        payload = request.get_json() or {}
        recipe_id = payload.get("recipe_id")
        is_fav, msg = db.toggle_favorite(user_id, recipe_id)
        return jsonify({"success": True, "is_favorite": is_fav, "message": msg})

    favs = db.get_user_favorites(user_id)
    recipes = [ai_engine.get_recipe_by_id(rid) for rid in favs if ai_engine.get_recipe_by_id(rid)]
    return jsonify({"success": True, "favorites": favs, "recipes": recipes})

@app.route("/api/review/<recipe_id>", methods=["POST"])
def api_review(recipe_id):
    payload = request.get_json() or {}
    user_id = payload.get("user_id") or session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Authentication required"}), 401

    rating = payload.get("rating", 5)
    comment = payload.get("comment", "")
    success = db.save_recipe_review(user_id, recipe_id, rating, comment)
    return jsonify({"success": success, "message": "Review submitted successfully!" if success else "Failed to save review"})

# ==============================================================================
# TASTIO AI NUTRITION COACH API
# ==============================================================================

@app.route("/api/coach/chat", methods=["POST"])
@app.route("/api/ai-coach", methods=["POST"])
def api_coach_chat():
    """
    Main endpoint for Tastio AI Nutrition Coach.
    Uses profile, Mifflin-St Jeor targets, today's eaten history, and recipe database.
    """
    payload = request.get_json() or {}
    message = payload.get("message") or payload.get("query") or ""
    user_id = payload.get("user_id") or session.get("user_id")

    if not message.strip():
        message = "Hello coach"

    result = coach_service.process_query(message, user_id=user_id)
    return jsonify(result)

@app.route("/api/coach/context", methods=["GET"])
def api_coach_context():
    """Fetches user live context snapshot for nutrition coach UI widget."""
    user_id = request.args.get("user_id") or session.get("user_id")
    ctx = coach_service.get_user_context(user_id)
    metrics = coach_service._build_metrics_dict(ctx)
# ==============================================================================
# TASTIO 7-DAY AI MEAL PLANNER API
# ==============================================================================

@app.route("/api/meal-plan/generate", methods=["POST"])
def api_generate_meal_plan():
    """Generates fresh 7-day personalized meal plan."""
    payload = request.get_json(silent=True) or {}
    user = session.get("user")
    user_id = payload.get("user_id") or (user.get("objectId") if isinstance(user, dict) else None) or session.get("user_id")
    start_date = payload.get("start_date")
    plan = meal_planner_service.generate_7day_plan(user_id=user_id, start_date=start_date)
    return jsonify({"success": True, "meal_plan": plan})

@app.route("/api/meal-plan/current", methods=["GET"])
def api_get_current_meal_plan():
    """Fetches active 7-day meal plan."""
    user_id = request.args.get("user_id") or session.get("user_id")
    plan = meal_planner_service.get_current_plan(user_id=user_id)
    return jsonify({"success": True, "meal_plan": plan})

@app.route("/api/meal-plan/date/<date_str>", methods=["GET"])
def api_get_meal_plan_by_date(date_str):
    """Fetches meal plan for a specific date or day index."""
    user_id = request.args.get("user_id") or session.get("user_id")
    plan = meal_planner_service.get_current_plan(user_id=user_id)
    if not plan or "days" not in plan:
        return jsonify({"success": False, "message": "No active meal plan"}), 404

    for d in plan["days"]:
        if d.get("date_iso") == date_str or str(d.get("day_index")) == date_str:
            return jsonify({"success": True, "day": d})

    return jsonify({"success": False, "message": f"No meal plan found for '{date_str}'"}), 404

@app.route("/api/meal-plan/replace-meal", methods=["POST"])
def api_replace_meal():
    """Replaces an individual meal slot in the user's active plan."""
    payload = request.get_json() or {}
    user_id = payload.get("user_id") or session.get("user_id")
    day_index = payload.get("day_index", 1)
    meal_type = payload.get("meal_type", "lunch")
    new_recipe_id = payload.get("new_recipe_id")

    updated_plan, msg = meal_planner_service.replace_meal(
        user_id=user_id,
        day_index=day_index,
        meal_type=meal_type,
        new_recipe_id=new_recipe_id
    )

    if updated_plan:
        return jsonify({"success": True, "message": msg, "meal_plan": updated_plan})
    return jsonify({"success": False, "message": msg}), 400

@app.route("/api/meal-plan/alternatives", methods=["GET"])
def api_get_meal_alternatives():
    """Fetches alternative recipes for a meal slot picker modal."""
    user_id = request.args.get("user_id") or session.get("user_id")
    meal_type = request.args.get("meal_type", "lunch")
    current_recipe_id = request.args.get("current_recipe_id")

    alternatives = meal_planner_service.get_alternatives_for_slot(
        user_id=user_id,
        meal_type=meal_type,
        current_recipe_id=current_recipe_id
    )
    return jsonify({"success": True, "alternatives": alternatives})

@app.route("/api/meal-plan/delete", methods=["DELETE", "POST"])
def api_delete_meal_plan():
    """Deletes active meal plan for the user."""
    payload = request.get_json() if request.is_json else {}
    user_id = (payload.get("user_id") if isinstance(payload, dict) else None) or request.args.get("user_id") or session.get("user_id")
    success, msg = db.delete_meal_plan(user_id)
    return jsonify({"success": success, "message": msg})

# ==============================================================================
# TASTIO COMPREHENSIVE NUTRITION ANALYTICS API
# ==============================================================================

@app.route("/api/analytics/nutrition", methods=["GET"])
@app.route("/api/nutrition-dashboard", methods=["GET"])
def api_nutrition_analytics():
    """
    Returns complete, multi-dimensional nutrition analytics for Today, Week, and Month
    based strictly on actual SQLite database records and recipe nutrition data.
    """
    user_id = request.args.get("user_id") or session.get("user_id")
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)
    diet_report = nutrition.generate_diet_report(cooked, user_profile)
    analytics = diet_report.get("analytics") or nutrition.get_comprehensive_analytics(cooked, user_profile)

    return jsonify({
        "success": True,
        "analytics": analytics,
        "today_summary": diet_report.get("today_summary", {}),
        "target_goals": diet_report.get("target_goals", {}),
        "ai_coach": diet_report.get("ai_coach", {})
    })

# ==============================================================================
# SMART GROCERY LIST WEB & REST APIs
# ==============================================================================

@app.route("/grocery-list")
def grocery_list_page():
    """Web route for Tastio Smart Grocery List."""
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)

    grocery_data = db.get_grocery_list(user_id)
    meal_plan = meal_planner_service.get_current_plan(user_id=user_id)

    return render_template(
        "grocery_list.html",
        grocery=grocery_data,
        meal_plan=meal_plan,
        profile=user_profile,
        session=session
    )

@app.route("/api/grocery-list/generate-from-plan", methods=["POST"])
def api_generate_grocery_from_plan():
    """
    Generates a consolidated, de-duplicated, and categorized grocery list
    directly from the user's active 7-day meal plan.
    """
    payload = request.get_json() if request.is_json else {}
    user_id = (payload.get("user_id") if isinstance(payload, dict) else None) or session.get("user_id")

    plan = meal_planner_service.get_current_plan(user_id=user_id)
    if not plan or "days" not in plan:
        return jsonify({"success": False, "message": "No active meal plan found. Generate a 7-day meal plan first."}), 404

    # Extract & categorize ingredients
    items = generate_grocery_list_from_plan(plan, recipe_lookup_fn=ai_engine.get_recipe_by_id)
    if not items:
        return jsonify({"success": False, "message": "Could not extract ingredients from the meal plan."}), 400

    # Save to SQLite
    list_name = f"Grocery List ({plan.get('start_date', 'Day 1')} to {plan.get('end_date', 'Day 7')})"
    db.save_grocery_list(user_id, items, list_name=list_name)

    # Return updated list
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({
        "success": True,
        "message": f"Generated grocery list with {len(items)} items across 7 categories!",
        "grocery": grocery_data
    })

@app.route("/api/grocery-list", methods=["GET"])
def api_get_grocery_list():
    """Fetches user's active grocery list categorized into the 7 groups."""
    user_id = request.args.get("user_id") or session.get("user_id")
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({"success": True, "grocery": grocery_data})

@app.route("/api/grocery-list/item", methods=["POST"])
def api_add_grocery_item():
    """Adds a custom item to the grocery list."""
    payload = request.get_json() or {}
    user_id = payload.get("user_id") or session.get("user_id")
    item_name = payload.get("item_name") or payload.get("name")
    category = payload.get("category", "Other")
    quantity = payload.get("quantity")
    unit = payload.get("unit")

    if not item_name:
        return jsonify({"success": False, "message": "Item name is required"}), 400

    success, res = db.add_custom_grocery_item(user_id, item_name, category=category, quantity=quantity, unit=unit)
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({"success": success, "item": res, "grocery": grocery_data})

@app.route("/api/grocery-list/item/<item_id>/toggle", methods=["POST", "PUT"])
@app.route("/api/grocery-list/toggle", methods=["POST"])
def api_toggle_grocery_item(item_id=None):
    """Toggles checked/unchecked status of a grocery item."""
    if not item_id:
        payload = request.get_json() or {}
        item_id = payload.get("item_id") or payload.get("objectId")
    user_id = request.args.get("user_id") or session.get("user_id")

    success, res = db.toggle_grocery_item(item_id, user_id=user_id)
    return jsonify({"success": success, "result": res})

@app.route("/api/grocery-list/item/<item_id>", methods=["DELETE", "POST"])
@app.route("/api/grocery-list/item/<item_id>/delete", methods=["POST", "DELETE"])
def api_remove_grocery_item(item_id):
    """Removes a single item from the grocery list."""
    user_id = request.args.get("user_id") or session.get("user_id")
    success, msg = db.remove_grocery_item(item_id, user_id=user_id)
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({"success": success, "message": msg, "grocery": grocery_data})

@app.route("/api/grocery-list/clear-completed", methods=["POST"])
def api_clear_completed_grocery_items():
    """Clears all completed/checked items from the grocery list."""
    payload = request.get_json() if request.is_json else {}
    user_id = (
        (payload.get("user_id") if isinstance(payload, dict) else None)
        or request.args.get("user_id")
        or session.get("user_id")
        or (session.get("user", {}).get("objectId") if isinstance(session.get("user"), dict) else None)
    )
    success, res = db.clear_completed_grocery_items(user_id)
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({"success": success, "cleared": res, "grocery": grocery_data})

@app.route("/api/grocery-list/clear-all", methods=["POST", "DELETE"])
def api_clear_all_grocery_items():
    """Clears all items from the grocery list."""
    payload = request.get_json() if request.is_json else {}
    user_id = (
        (payload.get("user_id") if isinstance(payload, dict) else None)
        or request.args.get("user_id")
        or session.get("user_id")
        or (session.get("user", {}).get("objectId") if isinstance(session.get("user"), dict) else None)
    )
    success, res = db.clear_all_grocery_items(user_id)
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({"success": success, "cleared": res, "grocery": grocery_data})

@app.route("/api/grocery-list/add-recipe", methods=["POST"])
def api_add_recipe_to_grocery():
    """Adds all ingredients of a recipe directly to the user's Smart Grocery List."""
    payload = request.get_json() if request.is_json else {}
    user_id = (payload.get("user_id") if isinstance(payload, dict) else None) or session.get("user_id") or "1"
    recipe_name = payload.get("recipe_name") or "Recipe"
    ingredients = payload.get("ingredients") or []

    if not ingredients and payload.get("recipe_id"):
        r = ai_engine.get_recipe_by_id(str(payload.get("recipe_id")))
        if r:
            ingredients = r.get("ingredients", [])
            recipe_name = r.get("recipe_name", recipe_name)

    success, count = db.add_recipe_to_grocery(user_id, recipe_name, ingredients)
    grocery_data = db.get_grocery_list(user_id)
    return jsonify({
        "success": success,
        "added": count,
        "message": f"Added {count} ingredients to your Smart Grocery List!",
        "grocery": grocery_data
    })

# ==============================================================================
# USER PREFERENCE LEARNING & RECENTLY VIEWED APIs
# ==============================================================================

@app.route("/api/recipes/<recipe_id>/view", methods=["POST"])
def api_record_recipe_view(recipe_id):
    """Records recipe view event for dynamic taste preference learning."""
    payload = request.get_json() if request.is_json else {}
    user_id = (payload.get("user_id") if isinstance(payload, dict) else None) or session.get("user_id")
    if user_id:
        db.record_recipe_view(user_id, recipe_id)
    return jsonify({"success": True, "recipe_id": recipe_id})

@app.route("/api/user/recently-viewed", methods=["GET"])
def api_get_recently_viewed():
    """Returns list of recently viewed recipe objects."""
    user_id = request.args.get("user_id") or session.get("user_id")
    limit = int(request.args.get("limit", 10))
    recipe_ids = db.get_recently_viewed_recipe_ids(user_id, limit=limit)
    recipes = [ai_engine.get_recipe_by_id(rid) for rid in recipe_ids if ai_engine.get_recipe_by_id(rid)]
    return jsonify({"success": True, "count": len(recipes), "recipes": recipes})

@app.route("/api/user/preferences", methods=["GET"])
def api_get_user_preferences():
    """Returns learned dynamic user preference profile."""
    user_id = request.args.get("user_id") or session.get("user_id")
    prof = preference_engine.get_user_preference_profile(user_id, recipe_lookup_fn=ai_engine.get_recipe_by_id)
    return jsonify({
        "success": True,
        "preferences": {
            "top_cuisines": prof.get("top_cuisines", []),
            "top_ingredients": prof.get("top_ingredients", []),
            "cuisine_affinities": prof.get("cuisine_affinities", {}),
            "macro_affinities": prof.get("macro_affinities", {}),
            "total_favorites": len(prof.get("favorite_recipe_ids", [])),
            "total_liked": len(prof.get("liked_recipe_ids", [])),
            "total_disliked": len(prof.get("disliked_recipe_ids", []))
        }
    })

# ==============================================================================
# TASTIO AI FOOD IMAGE RECOGNITION & NUTRITION GROUNDING APIs
# ==============================================================================

@app.route("/scanner")
def food_scanner_page():
    """Web route for Tastio AI Food Scanner."""
    user = session.get("user")
    user_id = user.get("objectId") if isinstance(user, dict) else None
    user_profile, cooked, reviews, favorites, pref_profile = _get_user_context(user_id)

    return render_template(
        "scanner.html",
        profile=user_profile,
        session=session
    )

@app.route("/api/vision/recognize-food", methods=["POST"])
def api_recognize_food():
    """
    Accepts multipart file upload or JSON payload with base64 image data.
    Identifies food items using the modular vision classifier and grounds the result
    into Tastio's verified 150-recipe database without fabricating pixel-based calories.
    """
    image_input = None

    if "image" in request.files:
        image_input = request.files["image"]
    elif "file" in request.files:
        image_input = request.files["file"]
    elif request.is_json:
        payload = request.get_json() or {}
        image_input = payload.get("image_data") or payload.get("image") or payload.get("base64")

    if not image_input:
        return jsonify({
            "success": False,
            "message": "No image provided. Please upload an image file or provide base64 data."
        }), 400

    # 1. Run visual classification
    analysis_res = food_vision_engine.analyze_image(image_input, top_k=3)
    if not analysis_res.get("success"):
        return jsonify({
            "success": False,
            "message": analysis_res.get("error", "Failed to process image.")
        }), 400

    predictions = analysis_res.get("predictions", [])
    all_recipes = ai_engine.get_all_recipes()

    # 2. Ground predictions to verified database recipes
    grounded_res = food_vision_engine.match_to_database(
        predictions=predictions,
        recipe_lookup_fn=ai_engine.get_recipe_by_id,
        all_recipes=all_recipes
    )

    return jsonify({
        "success": True,
        "model": analysis_res.get("model"),
        "predictions": predictions,
        "recognition": grounded_res
    })

@app.route("/api/vision/status", methods=["GET"])
def api_vision_status():
    """Returns status and model info for the food vision engine."""
    return jsonify({
        "success": True,
        "engine": "Tastio AI Food Scanner",
        "model": food_vision_engine.model_name,
        "version": food_vision_engine.version,
        "supported_formats": ["JPEG", "PNG", "WEBP", "BMP"],
        "database_recipes_indexed": len(ai_engine.recipes_by_id)
    })

@app.errorhandler(400)
def handle_400(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Bad Request", "message": "The request contains invalid or malformed data."}), 400
    return render_template("main.html", message="Bad request. Please verify your input."), 400

@app.errorhandler(401)
def handle_401(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Unauthorized", "message": "Authentication required to access this resource."}), 401
    return redirect(url_for("home", message="Please login to continue."))

@app.errorhandler(403)
def handle_403(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Forbidden", "message": "You do not have permission to access this resource."}), 403
    return redirect(url_for("home", message="Access forbidden."))

@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Not Found", "message": "The requested API endpoint was not found."}), 404
    dest = "dashboard" if "user" in session else "home"
    return redirect(url_for(dest, message="The page you requested was not found."))

@app.errorhandler(429)
def handle_429(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Too Many Requests", "message": "Rate limit exceeded. Please wait a minute and try again."}), 429
    return render_template("main.html", message="Too many requests. Please wait a minute and try again."), 429

@app.errorhandler(500)
def handle_500(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal Server Error", "message": "An unexpected error occurred on the server."}), 500
    return render_template("main.html", message="An unexpected error occurred. Please try again."), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Tastio Server] Running on http://localhost:{port} (Tastio 2.0 with Food Vision & Grocery List)")
    app.run(host="0.0.0.0", port=port, debug=True)
