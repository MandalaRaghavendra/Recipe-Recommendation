import re
import json

# ==============================================================================
# CATEGORY DEFINITIONS FOR INDIAN & GLOBAL INGREDIENTS
# ==============================================================================

CATEGORY_MAPPINGS = {
    "Vegetables": [
        "onion", "onions", "shallot", "shallots", "sambar onion", "tomato", "tomatoes",
        "spinach", "palak", "gongura", "gongura leaves", "ginger", "garlic", "ginger-garlic paste",
        "green chili", "green chilies", "chili", "chilies", "coriander leaves", "coriander",
        "mint leaves", "mint", "curry leaves", "cucumber", "dosakaya", "brinjal", "vankaya",
        "eggplant", "potato", "potatoes", "carrot", "carrots", "capsicum", "bell pepper",
        "cauliflower", "gobi", "cabbage", "cluster beans", "goruchikkudu", "ivy gourd",
        "dondakaya", "tindora", "ridge gourd", "beerakaya", "bottle gourd", "sorakaya",
        "anapakaya", "snake gourd", "potlakaya", "bitter gourd", "kakarakaya", "taro root",
        "chamadumpa", "arbi", "yam", "kanda", "drumstick", "munakkaya", "fenugreek leaves",
        "methi", "methi leaves", "malabar spinach", "bachali", "bachali kura", "sorrel leaves",
        "tender tamarind leaves", "chintachiguru", "mushroom", "mushrooms", "green peas",
        "peas", "beetroot", "radish", "mooli", "lady finger", "okra", "bhindi", "bhendi"
    ],
    "Fruits": [
        "lemon", "lime", "banana", "raw mango", "mamidikaya", "mango", "apple",
        "tamarind", "pomegranate", "orange", "berries", "strawberry", "blueberry",
        "raisins", "dates", "dry dates"
    ],
    "Protein": [
        "chicken", "country chicken", "natu kodi", "mutton", "lamb", "tripe", "boti",
        "fish", "fish pieces", "rohu", "katla", "prawns", "royyalu", "crab", "peethala",
        "egg", "eggs", "guddu", "egg white", "egg whites", "paneer", "tofu", "soya chunks",
        "soy chunks", "toor dal", "kandi pappu", "moong dal", "pesara pappu", "chana dal",
        "senagapappu", "urad dal", "minapappu", "masoor dal", "chickpeas", "kabuli chana",
        "kala chana", "black-eyed peas", "alasandalu", "lobia", "rajma", "kidney beans",
        "keema", "meatball", "whey protein", "protein powder", "lentils", "dal"
    ],
    "Grains": [
        "basmati rice", "rice", "brown rice", "sona masoori", "wheat flour", "atta",
        "flour", "maida", "oats", "rolled oats", "poha", "atukulu", "flattened rice",
        "rava", "sooji", "semolina", "rice rava", "biyyam rava", "broken wheat",
        "godhuma rava", "sorghum", "jowar", "jonna", "sorghum flour", "jowar flour",
        "rice noodle", "palathalikalu", "rice paper", "pootharekulu", "puffed rice",
        "borugulu", "quinoa", "millet", "ragi", "vermicelli", "semiya", "besan",
        "gram flour", "baking flour", "corn flour", "cornstarch", "bread"
    ],
    "Dairy": [
        "milk", "cow milk", "coconut milk", "yogurt", "curd", "hung curd", "dahi",
        "ghee", "clarified butter", "butter", "buttermilk", "majjiga", "challa",
        "cheese", "cream", "heavy cream", "malai", "condensed milk"
    ],
    "Spices": [
        "salt", "crystal salt", "rock salt", "turmeric", "haldi", "red chili powder",
        "chili powder", "coriander powder", "cumin seeds", "jeera", "roasted cumin powder",
        "mustard seeds", "rai", "fenugreek seeds", "methi seeds", "biryani masala",
        "garam masala", "pepper", "black pepper", "miriyalu", "cardamom", "cardamoms",
        "elaichi", "cloves", "laung", "cinnamon", "cinnamon stick", "dalchini",
        "bay leaf", "bay leaves", "tej patta", "star anise", "fennel seeds", "saunf",
        "asafoetida", "hing", "saffron", "kesar", "nutmeg", "jaiphal", "mace",
        "javitri", "kasuri methi", "curry powder", "chaat masala", "amchur"
    ],
    "Other": [
        "oil", "cooking oil", "peanut oil", "groundnut oil", "sesame oil", "gingelly oil",
        "mustard oil", "sunflower oil", "olive oil", "peanuts", "groundnuts", "cashews",
        "kaju", "almonds", "badam", "walnuts", "coconut", "kobbari", "grated coconut",
        "dry coconut", "jaggery", "bellam", "sugar", "brown sugar", "honey",
        "peanut butter", "cocoa powder", "baking powder", "baking soda", "vanilla essence",
        "water", "rose water"
    ]
}

def classify_ingredient(ingredient_name):
    """
    Classifies an ingredient name into one of the 7 designated groups:
    Vegetables, Fruits, Protein, Grains, Dairy, Spices, Other.
    """
    clean = ingredient_name.lower().strip()
    
    # Check exact match or substring in prioritized groups
    # 1. Protein priority (e.g. chicken, fish, paneer, dals)
    for kw in CATEGORY_MAPPINGS["Protein"]:
        if kw in clean or clean in kw:
            return "Protein"

    # 2. Dairy (e.g. ghee, milk, yogurt, buttermilk)
    for kw in CATEGORY_MAPPINGS["Dairy"]:
        if kw in clean or clean in kw:
            return "Dairy"

    # 3. Fruits (e.g. lemon, raw mango, tamarind)
    for kw in CATEGORY_MAPPINGS["Fruits"]:
        if kw in clean or clean in kw:
            return "Fruits"

    # 4. Vegetables (e.g. onions, tomatoes, gongura, leafy greens)
    for kw in CATEGORY_MAPPINGS["Vegetables"]:
        if kw in clean or clean in kw:
            return "Vegetables"

    # 5. Grains (e.g. basmati rice, oats, rava, wheat flour)
    for kw in CATEGORY_MAPPINGS["Grains"]:
        if kw in clean or clean in kw:
            return "Grains"

    # 6. Spices (e.g. turmeric, biryani masala, cumin, salt)
    for kw in CATEGORY_MAPPINGS["Spices"]:
        if kw in clean or clean in kw:
            return "Spices"

    # 7. Other (e.g. oil, peanuts, cashews, jaggery)
    for kw in CATEGORY_MAPPINGS["Other"]:
        if kw in clean or clean in kw:
            return "Other"

    return "Other"

def normalize_ingredient_name(raw_name):
    """
    Normalizes ingredient strings while preserving authentic culinary names.
    """
    name = str(raw_name).strip()
    name = re.sub(r'[\(\[].*?[\)\]]', '', name) # Remove bracketed text
    name = re.sub(r'[,;].*$', '', name) # Strip after comma
    name = name.strip()
    return name.title() if name else raw_name

def generate_grocery_list_from_plan(meal_plan, recipe_lookup_fn=None):
    """
    Generates a structured, de-duplicated grocery list from a 7-day meal plan.
    Groups items into Vegetables, Fruits, Protein, Grains, Dairy, Spices, Other.
    Does NOT invent fake quantities if not present in the database.
    """
    if not meal_plan:
        return []

    # Map of normalized_name -> item data
    aggregated = {}

    days = meal_plan.get("days", [])
    for day_obj in days:
        meals = day_obj.get("meals", {})
        # Meals is a dict with breakfast, lunch, snack, dinner
        meal_types = ["breakfast", "lunch", "snack", "dinner"]
        for m_type in meal_types:
            recipe = meals.get(m_type)
            if not recipe:
                continue

            r_id = str(recipe.get("recipe_id", ""))
            r_name = str(recipe.get("recipe_name", f"Meal #{r_id}"))

            # Fetch full recipe details if lookup function provided
            full_recipe = recipe_lookup_fn(r_id) if recipe_lookup_fn and r_id else None
            ingredients = []
            if full_recipe and full_recipe.get("ingredients"):
                ingredients = full_recipe.get("ingredients")
            elif recipe.get("ingredients"):
                ingredients = recipe.get("ingredients")

            if not isinstance(ingredients, list):
                continue

            for ing in ingredients:
                clean_name = normalize_ingredient_name(ing)
                if not clean_name:
                    continue

                lookup_key = clean_name.lower()

                if lookup_key not in aggregated:
                    category = classify_ingredient(clean_name)
                    aggregated[lookup_key] = {
                        "item_name": clean_name,
                        "category": category,
                        "quantity": None,
                        "unit": None,
                        "checked": False,
                        "is_custom": False,
                        "recipe_sources": [r_name]
                    }
                else:
                    if r_name not in aggregated[lookup_key]["recipe_sources"]:
                        aggregated[lookup_key]["recipe_sources"].append(r_name)

    # Convert to list and sort by Category and Item Name
    category_order = ["Vegetables", "Fruits", "Protein", "Grains", "Dairy", "Spices", "Other"]
    grocery_list = list(aggregated.values())
    grocery_list.sort(key=lambda x: (
        category_order.index(x["category"]) if x["category"] in category_order else 99,
        x["item_name"]
    ))

    return grocery_list
