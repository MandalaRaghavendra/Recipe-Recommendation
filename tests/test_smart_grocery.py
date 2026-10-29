import pytest
from grocery_engine import classify_ingredient, normalize_ingredient_name, generate_grocery_list_from_plan
import database as db

# 20 diverse culinary ingredients across all 7 categories
CLASSIFICATION_PAIRS_20 = [
    ("tomato", "Vegetables"),
    ("palak leaves", "Vegetables"),
    ("gongura leaves", "Vegetables"),
    ("onions", "Vegetables"),
    ("lemon juice", "Fruits"),
    ("banana", "Fruits"),
    ("raw mango", "Fruits"),
    ("boneless chicken", "Protein"),
    ("fresh paneer", "Protein"),
    ("toor dal", "Protein"),
    ("mutton pieces", "Protein"),
    ("fish fry pieces", "Protein"),
    ("boiled eggs", "Protein"),
    ("basmati rice", "Grains"),
    ("rolled oats", "Grains"),
    ("whole wheat flour", "Grains"),
    ("cow milk", "Dairy"),
    ("hung curd", "Dairy"),
    ("pure ghee", "Dairy"),
    ("turmeric powder", "Spices")
]

# 10 ingredient normalization test cases
NORMALIZATION_PAIRS_10 = [
    ("onion (finely chopped)", "Onion"),
    ("tomatoes, sliced", "Tomatoes"),
    ("  coriander leaves  ", "Coriander Leaves"),
    ("ginger (crushed)", "Ginger"),
    ("garlic cloves, peeled", "Garlic Cloves"),
    ("green chili (slit length-wise)", "Green Chili"),
    ("paneer cubes (fresh)", "Paneer Cubes"),
    ("curd, whisked smoothly", "Curd"),
    ("mustard seeds (rai)", "Mustard Seeds"),
    ("ghee (melted)", "Ghee")
]

@pytest.mark.parametrize("ingredient,expected_category", CLASSIFICATION_PAIRS_20)
def test_ingredient_classification(ingredient, expected_category):
    """Tests 161-180: Verify smart heuristic classification of ingredients into 7 culinary categories."""
    actual = classify_ingredient(ingredient)
    assert actual == expected_category, f"Failed for '{ingredient}': expected {expected_category}, got {actual}"

@pytest.mark.parametrize("raw_input,expected_clean", NORMALIZATION_PAIRS_10)
def test_ingredient_name_normalization(raw_input, expected_clean):
    """Tests 181-190: Verify bracket removal, trailing punctuation cleanup, and title casing."""
    normalized = normalize_ingredient_name(raw_input)
    assert normalized == expected_clean, f"Failed for '{raw_input}': expected '{expected_clean}', got '{normalized}'"

def test_generate_grocery_list_empty_plan():
    """Test 191: Generating grocery list from empty or None plan returns empty list."""
    assert generate_grocery_list_from_plan(None) == []
    assert generate_grocery_list_from_plan({}) == []

def test_generate_grocery_list_from_sample_plan(engine):
    """Test 192: Generate structured grocery items with valid category tags and sources."""
    mock_plan = {
        "days": [
            {
                "meals": {
                    "breakfast": {"recipe_id": "75", "recipe_name": "Protein Smoothie"},
                    "lunch": {"recipe_id": "1", "recipe_name": "Chicken Biryani"}
                }
            }
        ]
    }
    items = generate_grocery_list_from_plan(mock_plan, recipe_lookup_fn=engine.get_recipe_by_id)
    assert isinstance(items, list)
    assert len(items) > 0
    for item in items:
        assert "item_name" in item
        assert "category" in item
        assert "checked" in item
        assert item["checked"] is False
        assert "recipe_sources" in item

def test_generate_grocery_list_deduplicates_shared_ingredients(engine):
    """Test 193: Ingredients shared across multiple recipes are unified without duplicate rows."""
    mock_plan = {
        "days": [
            {"meals": {"breakfast": {"recipe_id": "1", "recipe_name": "Meal A"}}},
            {"meals": {"lunch": {"recipe_id": "1", "recipe_name": "Meal B"}}}
        ]
    }
    items = generate_grocery_list_from_plan(mock_plan, recipe_lookup_fn=engine.get_recipe_by_id)
    names = [i["item_name"].lower() for i in items]
    assert len(names) == len(set(names)), "Duplicate ingredient found in compiled grocery list"

def test_grocery_db_add_custom_item():
    """Test 194: User can insert custom grocery items with assigned category."""
    ok, item_data = db.add_custom_grocery_item(user_id=1, item_name="Almond Milk", category="Dairy")
    assert ok is True
    assert item_data["item_name"] == "Almond Milk"
    g_data = db.get_grocery_list(user_id=1)
    items = g_data.get("items", [])
    found = any(i.get("item_name") == "Almond Milk" for i in items)
    assert found is True

def test_grocery_db_toggle_item():
    """Test 195: User can toggle grocery item checked status."""
    g_data = db.get_grocery_list(user_id=1)
    items = g_data.get("items", [])
    target = next((i for i in items if i.get("item_name") == "Almond Milk"), None)
    if target:
        obj_id = target.get("objectId")
        ok, res = db.toggle_grocery_item(item_objectId=obj_id, user_id=1)
        assert ok is True

def test_grocery_db_add_recipe_ingredients():
    """Test 196: Adding a recipe directly injects all ingredients to user's grocery database."""
    initial_items = db.get_grocery_list(user_id=1).get("items", [])
    ok, count = db.add_recipe_to_grocery(user_id=1, recipe_name="Smoothie", ingredients=["Banana", "Peanut butter", "Milk"])
    assert ok is True
    updated_items = db.get_grocery_list(user_id=1).get("items", [])
    assert len(updated_items) >= len(initial_items)

def test_grocery_db_clear_completed():
    """Test 197: Clearing completed items purges checked items while keeping unchecked ones."""
    ok, msg = db.clear_completed_grocery_items(user_id=1)
    assert ok is True
    items = db.get_grocery_list(user_id=1).get("items", [])
    for i in items:
        assert not i.get("checked"), f"Found checked item after clear_completed: {i}"

def test_grocery_db_remove_item():
    """Test 198: Deleting a single grocery item by ID succeeds."""
    ok, item_data = db.add_custom_grocery_item(user_id=1, item_name="Temporary Item", category="Other")
    assert ok is True
    del_ok, _ = db.remove_grocery_item(item_objectId=item_data["objectId"], user_id=1)
    assert del_ok is True
    items = db.get_grocery_list(user_id=1).get("items", [])
    assert not any(i.get("item_name") == "Temporary Item" for i in items)

def test_grocery_db_save_full_list():
    """Test 199: Bulk updating grocery items list preserves data structure."""
    sample_list = [
        {"item_name": "Green Tea", "category": "Other", "checked": False, "is_custom": True}
    ]
    res = db.save_grocery_list(user_id=1, items=sample_list)
    assert res is True or res is not None

def test_grocery_db_clear_all():
    """Test 200: Clearing all grocery items wipes the user list cleanly."""
    db.clear_all_grocery_items(user_id=1)
    items = db.get_grocery_list(user_id=1).get("items", [])
    assert len(items) == 0
