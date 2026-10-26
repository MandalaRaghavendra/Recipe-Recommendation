import os
import sqlite3
import hashlib
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from validators import (
    validate_email,
    validate_password,
    validate_profile_payload,
    validate_rating,
    validate_serving_size,
    sanitize_text
)

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipes.db"))

def get_db_connection():
    """Returns a SQLite database connection with row dictionary factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Securely hashes password using Werkzeug's default PBKDF2/scrypt algorithm."""
    return generate_password_hash(password)

def init_db():
    """Initializes SQLite database tables and migrations on first launch."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. User Profile Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT UNIQUE NOT NULL,
        age INTEGER,
        gender TEXT,
        height REAL,
        weight REAL,
        diet_goal TEXT,
        food_pref TEXT,
        allergies TEXT,
        duration_months INTEGER DEFAULT 3,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Cooked Recipes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cooked_recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        recipe_id TEXT NOT NULL,
        serving_size REAL DEFAULT 1.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check for serving_size migration if table already existed
    cursor.execute("PRAGMA table_info(cooked_recipes)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "serving_size" not in columns:
        cursor.execute("ALTER TABLE cooked_recipes ADD COLUMN serving_size REAL DEFAULT 1.0")

    # 4. Recipe Reviews Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipe_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        recipe_id TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Favorites Table (NEW)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        recipe_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, recipe_id)
    )
    """)

    # 6. Meal Plans Table (7-Day AI Meal Planner)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        plan_name TEXT DEFAULT '7-Day Personalized AI Meal Plan',
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        plan_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. Grocery Lists Table (Smart Grocery List)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grocery_lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        name TEXT DEFAULT 'My Smart Grocery List',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 8. Grocery Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grocery_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        list_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        item_name TEXT NOT NULL,
        quantity REAL,
        unit TEXT,
        category TEXT DEFAULT 'Other',
        checked INTEGER DEFAULT 0,
        is_custom INTEGER DEFAULT 0,
        recipe_sources TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 9. Viewed Recipes Table (Preference Learning)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS viewed_recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objectId TEXT UNIQUE NOT NULL,
        user_id TEXT NOT NULL,
        recipe_id TEXT NOT NULL,
        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print(f"[SQLite DB] Initialized and verified database at {DB_PATH}")

init_db()

def register_user(name, email, password):
    """Registers a new user in SQLite with secure password hashing and input validation."""
    if not name or not str(name).strip():
        return False, "Name is required."

    is_valid_email, email_res = validate_email(email)
    if not is_valid_email:
        return False, email_res

    is_valid_pwd, pwd_res = validate_password(password)
    if not is_valid_pwd:
        return False, pwd_res

    clean_name = sanitize_text(name, max_len=100)
    email_clean = email_res

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT objectId FROM users WHERE email = ?", (email_clean,))
        if cursor.fetchone():
            conn.close()
            return False, "An account with this email already exists."

        user_objectId = str(uuid.uuid4())
        hashed_pwd = generate_password_hash(pwd_res)

        cursor.execute(
            "INSERT INTO users (objectId, name, email, password) VALUES (?, ?, ?, ?)",
            (user_objectId, clean_name, email_clean, hashed_pwd)
        )

        profile_objectId = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO user_profile (objectId, user_id, age, gender, height, weight, diet_goal, food_pref, allergies, duration_months) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (profile_objectId, user_objectId, 25, "male", 170.0, 70.0, "weight_loss", "both", "", 3)
        )

        conn.commit()
        conn.close()

        user_dict = {
            "objectId": user_objectId,
            "name": clean_name,
            "email": email_clean
        }
        return True, user_dict
    except Exception as e:
        conn.close()
        print(f"[SQLite DB Error] register_user failed: {e}")
        return False, f"Registration error: {str(e)}"

def login_user(email, password):
    """
    Authenticates user in SQLite using secure Werkzeug password hashing.
    Seamlessly verifies and upgrades legacy SHA-256 password hashes.
    """
    if not email or not password:
        return False, "Email and password are required."

    is_valid_email, email_res = validate_email(email)
    if not is_valid_email:
        return False, "Invalid email or password."

    email_clean = email_res
    clean_pwd = str(password).strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Invalid email or password."

    stored_hash = row["password"]
    is_authenticated = False

    # 1. Standard Werkzeug verify
    try:
        if check_password_hash(stored_hash, clean_pwd) or check_password_hash(stored_hash, password):
            is_authenticated = True
    except Exception:
        is_authenticated = False

    # 2. Legacy SHA-256 fallback with automatic hash upgrade
    if not is_authenticated:
        legacy_hash_clean = hashlib.sha256(clean_pwd.encode("utf-8")).hexdigest()
        legacy_hash_raw = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if legacy_hash_clean == stored_hash or legacy_hash_raw == stored_hash:
            is_authenticated = True
            # Transparently upgrade database record to modern Werkzeug hash
            new_hash = generate_password_hash(clean_pwd)
            cursor.execute("UPDATE users SET password = ? WHERE objectId = ?", (new_hash, row["objectId"]))
            conn.commit()

    conn.close()

    if is_authenticated:
        user_dict = {
            "objectId": row["objectId"],
            "name": row["name"],
            "email": row["email"]
        }
        return True, user_dict

    return False, "Invalid email or password."

def get_user_profile(user_id):
    """Fetches user profile dictionary from SQLite."""
    if not user_id:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        profile = dict(row)
        if profile.get("allergies"):
            profile["allergies"] = [a.strip().lower() for a in str(profile["allergies"]).split(",") if a.strip()]
        else:
            profile["allergies"] = []
        return profile
    return None

def save_user_profile(user_id, payload):
    """Updates user profile in SQLite with strict input validation."""
    if not user_id:
        return False

    is_valid, clean = validate_profile_payload(payload)
    if not is_valid:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    allergies_str = clean.get("allergies", "")
    age = clean.get("age", 25)
    gender = clean.get("gender", "male")
    height = clean.get("height", 170.0)
    weight = clean.get("weight", 70.0)
    diet_goal = clean.get("diet_goal", "weight_loss")
    food_pref = clean.get("food_pref", "both")
    duration_months = clean.get("duration_months", 3)

    if existing:
        cursor.execute("""
        UPDATE user_profile 
        SET age = ?, gender = ?, height = ?, weight = ?, diet_goal = ?, food_pref = ?, allergies = ?, duration_months = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """, (age, gender, height, weight, diet_goal, food_pref, allergies_str, duration_months, user_id))
    else:
        profile_objectId = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO user_profile (objectId, user_id, age, gender, height, weight, diet_goal, food_pref, allergies, duration_months)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (profile_objectId, user_id, age, gender, height, weight, diet_goal, food_pref, allergies_str, duration_months))

    conn.commit()
    conn.close()
    return True

def get_all_user_reviews(user_id):
    """Fetches all reviews by user as a dictionary {recipe_id: review_dict}."""
    if not user_id:
        return {}

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe_reviews WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return {str(row["recipe_id"]): dict(row) for row in rows}

def save_recipe_review(user_id, recipe_id, rating, comment):
    """Saves or updates a recipe review with rating validation and comment sanitization."""
    if not user_id or not recipe_id:
        return False

    is_valid_r, clean_rating = validate_rating(rating)
    if not is_valid_r:
        return False

    clean_comment = sanitize_text(comment, max_len=500)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe_reviews WHERE user_id = ? AND recipe_id = ?", (user_id, str(recipe_id)))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
        UPDATE recipe_reviews 
        SET rating = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND recipe_id = ?
        """, (clean_rating, clean_comment, user_id, str(recipe_id)))
    else:
        review_objectId = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO recipe_reviews (objectId, user_id, recipe_id, rating, comment)
        VALUES (?, ?, ?, ?, ?)
        """, (review_objectId, user_id, str(recipe_id), clean_rating, clean_comment))

    conn.commit()
    conn.close()
    return True

def get_cooked_recipes(user_id, recipe_lookup_fn=None):
    """
    Fetches list of cooked recipes with review ratings, comments, and portion sizes.
    Never drops entries even if recipe is not in memory.
    """
    if not user_id:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cooked_recipes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    cooked_rows = cursor.fetchall()
    conn.close()

    reviews_map = get_all_user_reviews(user_id)
    detailed_list = []

    for item in cooked_rows:
        rid = str(item["recipe_id"])
        recipe_obj = recipe_lookup_fn(rid) if recipe_lookup_fn else None

        if recipe_obj:
            entry = dict(recipe_obj)
        else:
            entry = {
                "recipe_id": rid,
                "recipe_name": f"Recipe #{rid}",
                "nutritions": {"calories": 300, "protein_g": 15, "carbs_g": 40, "fat_g": 10}
            }

        entry["cooked_at"] = item["created_at"]
        entry["cooked_objectId"] = item["objectId"]
        entry["serving_size"] = float(item["serving_size"] or 1.0) if "serving_size" in item.keys() else 1.0

        review = reviews_map.get(rid)
        if review:
            entry["user_rating"] = review.get("rating")
            entry["user_comment"] = review.get("comment")
            entry["review_objectId"] = review.get("objectId")
        else:
            entry["user_rating"] = None
            entry["user_comment"] = None

        detailed_list.append(entry)

    return detailed_list

def mark_recipe_eaten(user_id, recipe_id, serving_size=1.0):
    """Logs recipe as cooked/eaten with portion size validation in SQLite."""
    if not user_id or not recipe_id:
        return False, "Missing user_id or recipe_id"

    is_valid_s, clean_serving = validate_serving_size(serving_size)
    if not is_valid_s:
        clean_serving = 1.0

    conn = get_db_connection()
    cursor = conn.cursor()
    cooked_objectId = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO cooked_recipes (objectId, user_id, recipe_id, serving_size) VALUES (?, ?, ?, ?)",
        (cooked_objectId, user_id, str(recipe_id), clean_serving)
    )
    conn.commit()
    conn.close()

    reviews = get_all_user_reviews(user_id)
    review_exists = str(recipe_id) in reviews
    return True, {"review_exists": review_exists}

def toggle_favorite(user_id, recipe_id):
    """Toggles favorite status for a recipe. Returns (is_favorite, message)."""
    if not user_id or not recipe_id:
        return False, "Missing user_id or recipe_id"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND recipe_id = ?", (user_id, str(recipe_id)))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?", (user_id, str(recipe_id)))
        conn.commit()
        conn.close()
        return False, "Removed from favorites"
    else:
        fav_objectId = str(uuid.uuid4())
        cursor.execute("INSERT INTO favorites (objectId, user_id, recipe_id) VALUES (?, ?, ?)", (fav_objectId, user_id, str(recipe_id)))
        conn.commit()
        conn.close()
        return True, "Added to favorites"

def get_user_favorites(user_id):
    """Returns list of favorite recipe_id strings for user."""
    if not user_id:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recipe_id FROM favorites WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return [str(row["recipe_id"]) for row in rows]

# ==============================================================================
# MEAL PLAN DATABASE HELPERS
# ==============================================================================

def save_meal_plan(user_id, plan_dict):
    """
    Saves or replaces the active 7-day meal plan for a user.
    """
    import json
    if not user_id or not plan_dict:
        return False, "Missing user_id or plan data"

    conn = get_db_connection()
    cursor = conn.cursor()

    start_date = str(plan_dict.get("start_date", datetime.now().strftime("%Y-%m-%d")))
    end_date = str(plan_dict.get("end_date", datetime.now().strftime("%Y-%m-%d")))
    plan_name = str(plan_dict.get("plan_name", "7-Day Personalized AI Meal Plan"))
    plan_json = json.dumps(plan_dict)

    # Check if a plan already exists for this user
    cursor.execute("SELECT * FROM meal_plans WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
        UPDATE meal_plans
        SET plan_name = ?, start_date = ?, end_date = ?, plan_data = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """, (plan_name, start_date, end_date, plan_json, user_id))
    else:
        plan_objectId = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO meal_plans (objectId, user_id, plan_name, start_date, end_date, plan_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (plan_objectId, user_id, plan_name, start_date, end_date, plan_json))

    conn.commit()
    conn.close()
    return True, "Meal plan saved successfully"

def get_current_meal_plan(user_id):
    """
    Fetches the active 7-day meal plan for the given user.
    """
    import json
    if not user_id:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meal_plans WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row and row["plan_data"]:
        try:
            plan = json.loads(row["plan_data"])
            plan["objectId"] = row["objectId"]
            plan["updated_at"] = row["updated_at"]
            return plan
        except Exception as e:
            print(f"[DB] Error parsing meal plan JSON: {e}")
            return None
    return None

def delete_meal_plan(user_id=None):
    """
    Deletes active meal plan for the user or test instance.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("DELETE FROM meal_plans WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("DELETE FROM meal_plans WHERE user_id IS NULL OR user_id = ''")
    conn.commit()
    conn.close()
    return True, "Meal plan deleted"

# ==============================================================================
# SMART GROCERY LIST DATABASE HELPERS
# ==============================================================================

def save_grocery_list(user_id, items, list_name="My Smart Grocery List"):
    """
    Replaces or creates the grocery list for the user with structured items.
    """
    import json
    if not user_id or not isinstance(items, list):
        return False, "Missing user_id or items"

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Find or create grocery_lists entry
    cursor.execute("SELECT objectId FROM grocery_lists WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    list_row = cursor.fetchone()

    if list_row:
        list_objectId = list_row["objectId"]
        cursor.execute("UPDATE grocery_lists SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE objectId = ?", (list_name, list_objectId))
        # Remove non-custom items to refresh with newly generated ones, or keep custom items
        cursor.execute("DELETE FROM grocery_items WHERE list_id = ? AND is_custom = 0", (list_objectId,))
    else:
        list_objectId = str(uuid.uuid4())
        cursor.execute("INSERT INTO grocery_lists (objectId, user_id, name) VALUES (?, ?, ?)", (list_objectId, user_id, list_name))

    # 2. Insert items
    for it in items:
        item_objectId = str(uuid.uuid4())
        item_name = str(it.get("item_name") or it.get("name") or "").strip()
        if not item_name:
            continue
        qty = it.get("quantity")
        unit = it.get("unit")
        cat = str(it.get("category") or "Other")
        checked = 1 if it.get("checked") else 0
        is_custom = 1 if it.get("is_custom") else 0
        sources = json.dumps(it.get("recipe_sources") or [])

        cursor.execute("""
        INSERT INTO grocery_items (objectId, list_id, user_id, item_name, quantity, unit, category, checked, is_custom, recipe_sources)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_objectId, list_objectId, user_id, item_name, qty, unit, cat, checked, is_custom, sources))

    conn.commit()
    conn.close()
    return True, {"list_id": list_objectId, "items_count": len(items)}

def get_grocery_list(user_id):
    """
    Fetches the user's active grocery list grouped by the 7 categories.
    """
    import json
    if not user_id:
        return {"items": [], "categories": {}, "total_items": 0, "completed_items": 0}

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT objectId, name, updated_at FROM grocery_lists WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    list_row = cursor.fetchone()

    if not list_row:
        conn.close()
        return {"items": [], "categories": {}, "total_items": 0, "completed_items": 0, "list_name": "My Smart Grocery List"}

    list_objectId = list_row["objectId"]
    cursor.execute("SELECT * FROM grocery_items WHERE list_id = ? ORDER BY checked ASC, category ASC, item_name ASC", (list_objectId,))
    rows = cursor.fetchall()
    conn.close()

    items = []
    categories = {
        "Vegetables": [],
        "Fruits": [],
        "Protein": [],
        "Grains": [],
        "Dairy": [],
        "Spices": [],
        "Other": []
    }

    total = 0
    completed = 0

    for r in rows:
        total += 1
        is_checked = bool(r["checked"])
        if is_checked:
            completed += 1

        try:
            sources = json.loads(r["recipe_sources"]) if r["recipe_sources"] else []
        except Exception:
            sources = []

        item_dict = {
            "objectId": r["objectId"],
            "item_name": r["item_name"],
            "quantity": r["quantity"],
            "unit": r["unit"],
            "category": r["category"] if r["category"] in categories else "Other",
            "checked": is_checked,
            "is_custom": bool(r["is_custom"]),
            "recipe_sources": sources,
            "created_at": r["created_at"]
        }
        items.append(item_dict)
        cat_key = item_dict["category"]
        if cat_key not in categories:
            categories[cat_key] = []
        categories[cat_key].append(item_dict)

    return {
        "list_id": list_objectId,
        "list_name": list_row["name"],
        "updated_at": list_row["updated_at"],
        "items": items,
        "categories": categories,
        "total_items": total,
        "completed_items": completed
    }

def toggle_grocery_item(item_objectId, user_id=None):
    """
    Toggles the checked status of a grocery item.
    """
    if not item_objectId:
        return False, "Missing item_objectId"

    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT checked FROM grocery_items WHERE objectId = ? AND user_id = ?", (item_objectId, user_id))
    else:
        cursor.execute("SELECT checked FROM grocery_items WHERE objectId = ?", (item_objectId,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Item not found"

    new_status = 0 if row["checked"] else 1
    cursor.execute("UPDATE grocery_items SET checked = ? WHERE objectId = ?", (new_status, item_objectId))
    conn.commit()
    conn.close()
    return True, {"checked": bool(new_status)}

def add_custom_grocery_item(user_id, item_name, category="Other", quantity=None, unit=None):
    """
    Adds a custom item directly to the user's active grocery list.
    """
    import json
    if not user_id or not item_name:
        return False, "Missing user_id or item_name"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find or create list
    cursor.execute("SELECT objectId FROM grocery_lists WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    list_row = cursor.fetchone()

    if list_row:
        list_objectId = list_row["objectId"]
    else:
        list_objectId = str(uuid.uuid4())
        cursor.execute("INSERT INTO grocery_lists (objectId, user_id, name) VALUES (?, ?, ?)", (list_objectId, user_id, "My Smart Grocery List"))

    item_objectId = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO grocery_items (objectId, list_id, user_id, item_name, quantity, unit, category, checked, is_custom, recipe_sources)
    VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1, ?)
    """, (item_objectId, list_objectId, user_id, item_name.strip(), quantity, unit, category, json.dumps(["Custom Item"])))

    conn.commit()
    conn.close()
    return True, {"objectId": item_objectId, "item_name": item_name, "category": category}

def remove_grocery_item(item_objectId, user_id=None):
    """
    Deletes a single item from the grocery list.
    """
    if not item_objectId:
        return False, "Missing item_objectId"

    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("DELETE FROM grocery_items WHERE objectId = ? AND user_id = ?", (item_objectId, user_id))
    else:
        cursor.execute("DELETE FROM grocery_items WHERE objectId = ?", (item_objectId,))
    conn.commit()
    conn.close()
    return True, "Item removed"

def clear_completed_grocery_items(user_id):
    """
    Removes all checked/completed items from the user's grocery list.
    """
    if not user_id:
        return False, "Missing user_id"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grocery_items WHERE user_id = ? AND checked = 1", (user_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return True, {"deleted_count": deleted_count, "cleared_count": deleted_count}

def add_recipe_to_grocery(user_id, recipe_name, ingredients):
    """
    Adds all ingredients of a recipe directly to the user's active grocery list.
    De-duplicates if already in list and links recipe_sources.
    """
    from grocery_engine import classify_ingredient, normalize_ingredient_name
    import json

    if not user_id or not ingredients:
        return False, 0

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT objectId FROM grocery_lists WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    list_row = cursor.fetchone()
    if list_row:
        list_objectId = list_row["objectId"]
    else:
        list_objectId = str(uuid.uuid4())
        cursor.execute("INSERT INTO grocery_lists (objectId, user_id, name) VALUES (?, ?, ?)", (list_objectId, user_id, "My Smart Grocery List"))

    cursor.execute("SELECT objectId, item_name, recipe_sources FROM grocery_items WHERE list_id = ?", (list_objectId,))
    existing_rows = cursor.fetchall()
    existing_map = {row["item_name"].strip().lower(): row for row in existing_rows}

    added_count = 0
    for raw_ing in ingredients:
        clean_name = normalize_ingredient_name(str(raw_ing).strip())
        if not clean_name:
            continue
        key = clean_name.lower()

        if key in existing_map:
            row = existing_map[key]
            try:
                sources = json.loads(row["recipe_sources"]) if row["recipe_sources"] else []
            except Exception:
                sources = []
            if recipe_name and recipe_name not in sources:
                sources.append(recipe_name)
                cursor.execute("UPDATE grocery_items SET recipe_sources = ? WHERE objectId = ?", (json.dumps(sources), row["objectId"]))
        else:
            item_objectId = str(uuid.uuid4())
            category = classify_ingredient(clean_name)
            cursor.execute("""
            INSERT INTO grocery_items (objectId, list_id, user_id, item_name, quantity, unit, category, checked, is_custom, recipe_sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
            """, (item_objectId, list_objectId, user_id, clean_name, None, None, category, json.dumps([recipe_name] if recipe_name else [])))
            added_count += 1

    conn.commit()
    conn.close()
    return True, added_count

# ==============================================================================
# VIEWED RECIPES & RECENT HISTORY HELPERS
# ==============================================================================

def record_recipe_view(user_id, recipe_id):
    """
    Records recipe view event for preference learning.
    """
    if not user_id or not recipe_id:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    view_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO viewed_recipes (objectId, user_id, recipe_id)
    VALUES (?, ?, ?)
    """, (view_id, user_id, str(recipe_id)))
    conn.commit()
    conn.close()
    return True

def get_recently_viewed_recipe_ids(user_id, limit=10):
    """
    Returns list of recently viewed recipe_ids for a user ordered by most recent.
    """
    if not user_id:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT DISTINCT recipe_id FROM viewed_recipes
    WHERE user_id = ?
    ORDER BY viewed_at DESC
    LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    return [str(r["recipe_id"]) for r in rows]



