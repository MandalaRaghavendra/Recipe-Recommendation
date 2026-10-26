import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

VALID_DIET_GOALS = {"weight_loss", "muscle_gain", "maintenance", "keto", "balanced", "festive"}
VALID_FOOD_PREFS = {"veg", "non-veg", "both"}
VALID_GENDERS = {"male", "female", "other"}

def validate_email(email):
    """Validates email format."""
    if not email or not isinstance(email, str):
        return False, "Email is required."
    clean = email.strip()
    if len(clean) > 254:
        return False, "Email exceeds maximum length."
    if not EMAIL_REGEX.match(clean):
        return False, "Invalid email address format."
    return True, clean.lower()

def validate_password(password, min_len=4):
    """Validates password length and complexity."""
    if not password or not isinstance(password, str):
        return False, "Password is required."
    clean_pwd = password.strip()
    if len(clean_pwd) < min_len:
        return False, f"Password must be at least {min_len} characters long."
    if len(clean_pwd) > 128:
        return False, "Password cannot exceed 128 characters."
    return True, clean_pwd

def validate_rating(rating):
    """Validates recipe rating between 1 and 5."""
    try:
        r = int(rating)
        if 1 <= r <= 5:
            return True, r
        return False, "Rating must be an integer between 1 and 5."
    except (ValueError, TypeError):
        return False, "Invalid rating format. Expected integer 1-5."

def validate_serving_size(serving):
    """Validates meal serving size multiplier."""
    try:
        s = float(serving)
        if 0.1 <= s <= 10.0:
            return True, round(s, 2)
        return False, "Serving size must be between 0.1 and 10.0."
    except (ValueError, TypeError):
        return False, "Invalid serving size format."

def validate_profile_payload(payload):
    """Validates user health and nutrition profile inputs."""
    if not isinstance(payload, dict):
        return False, "Invalid profile payload format."

    clean = {}

    # Age: 5 - 120
    if "age" in payload and payload["age"] is not None:
        try:
            age = int(payload["age"])
            if 5 <= age <= 120:
                clean["age"] = age
            else:
                return False, "Age must be between 5 and 120 years."
        except (ValueError, TypeError):
            return False, "Invalid age format."
    else:
        clean["age"] = 25

    # Gender
    gender = str(payload.get("gender", "male")).strip().lower()
    clean["gender"] = gender if gender in VALID_GENDERS else "male"

    # Height: 50cm - 260cm
    if "height" in payload and payload["height"] is not None:
        try:
            height = float(payload["height"])
            if 50.0 <= height <= 260.0:
                clean["height"] = round(height, 1)
            else:
                return False, "Height must be between 50cm and 260cm."
        except (ValueError, TypeError):
            return False, "Invalid height format."
    else:
        clean["height"] = 170.0

    # Weight: 20kg - 350kg
    if "weight" in payload and payload["weight"] is not None:
        try:
            weight = float(payload["weight"])
            if 20.0 <= weight <= 350.0:
                clean["weight"] = round(weight, 1)
            else:
                return False, "Weight must be between 20kg and 350kg."
        except (ValueError, TypeError):
            return False, "Invalid weight format."
    else:
        clean["weight"] = 70.0

    # Diet Goal
    goal = str(payload.get("diet_goal", "weight_loss")).strip().lower().replace(" ", "_")
    clean["diet_goal"] = goal if goal in VALID_DIET_GOALS else "weight_loss"

    # Food Preference
    pref = str(payload.get("food_pref", "both")).strip().lower()
    clean["food_pref"] = pref if pref in VALID_FOOD_PREFS else "both"

    # Allergies
    allergies_raw = payload.get("allergies", "")
    if isinstance(allergies_raw, list):
        clean["allergies"] = ", ".join([str(a).strip().lower() for a in allergies_raw if str(a).strip()])
    elif isinstance(allergies_raw, str):
        clean["allergies"] = sanitize_text(allergies_raw, max_len=200)
    else:
        clean["allergies"] = ""

    # Duration: 1 - 24 months
    if "duration_months" in payload and payload["duration_months"] is not None:
        try:
            dur = int(payload["duration_months"])
            if 1 <= dur <= 24:
                clean["duration_months"] = dur
            else:
                return False, "Target duration must be between 1 and 24 months."
        except (ValueError, TypeError):
            return False, "Invalid duration format."
    else:
        clean["duration_months"] = 3

    return True, clean

def sanitize_text(text, max_len=500):
    """Sanitizes text strings to prevent oversized or malformed inputs."""
    if not text:
        return ""
    clean = str(text).strip()
    # Strip dangerous HTML tags / script elements
    clean = re.sub(r"<[^>]*>", "", clean)
    return clean[:max_len]
