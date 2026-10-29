import pytest

# Sample recipe indices across the 230 dataset (covering batches 1 through 230)
SAMPLE_RECIPE_INDICES_20 = [0, 10, 25, 40, 55, 70, 85, 100, 115, 130, 145, 160, 175, 190, 200, 210, 215, 220, 225, 229]
SAMPLE_RECIPE_INDICES_10_A = [1, 15, 30, 45, 60, 75, 90, 105, 120, 135]
SAMPLE_RECIPE_INDICES_10_B = [5, 20, 35, 50, 65, 80, 95, 110, 125, 140]

def test_total_recipe_count(all_recipes):
    """Test 1: Verify all 230 verified recipes are loaded into memory."""
    assert len(all_recipes) == 230, f"Expected 230 recipes, found {len(all_recipes)}"

def test_unique_recipe_ids(all_recipes):
    """Test 2: Ensure all recipe IDs are unique across the entire database."""
    ids = [str(r.get("recipe_id")) for r in all_recipes]
    assert len(ids) == len(set(ids)), "Duplicate recipe IDs found in dataset!"

@pytest.mark.parametrize("idx", SAMPLE_RECIPE_INDICES_20)
def test_recipe_schema_fields(all_recipes, idx):
    """Tests 3-22: Verify complete schema integrity across 20 diverse recipes."""
    recipe = all_recipes[idx]
    required_keys = ["recipe_id", "recipe_name", "ingredients", "nutritions", "steps", "cuisine", "meal_type", "veg_nonveg", "health_score"]
    for k in required_keys:
        assert k in recipe, f"Recipe index {idx} ({recipe.get('recipe_name')}) is missing required key '{k}'"
    assert len(recipe["ingredients"]) > 0, f"Recipe {recipe.get('recipe_name')} has empty ingredients"
    assert len(recipe["steps"]) > 0, f"Recipe {recipe.get('recipe_name')} has empty steps"

@pytest.mark.parametrize("idx", SAMPLE_RECIPE_INDICES_10_A)
def test_nutritional_integrity(all_recipes, idx):
    """Tests 23-32: Validate macronutrient ranges and caloric sanity."""
    recipe = all_recipes[idx]
    nutr = recipe.get("nutritions", {})
    calories = nutr.get("calories", 0)
    protein = nutr.get("protein_g", 0)
    carbs = nutr.get("carbs_g", 0)
    fat = nutr.get("fat_g", 0)

    assert calories >= 20, f"Recipe {recipe.get('recipe_name')} has invalid calories: {calories}"
    assert protein >= 0, f"Recipe {recipe.get('recipe_name')} has negative protein"
    assert carbs >= 0, f"Recipe {recipe.get('recipe_name')} has negative carbs"
    assert fat >= 0, f"Recipe {recipe.get('recipe_name')} has negative fat"

@pytest.mark.parametrize("idx", SAMPLE_RECIPE_INDICES_10_B)
def test_health_score_range(all_recipes, idx):
    """Tests 33-42: Validate algorithmic health score is normalized between 50 and 100."""
    recipe = all_recipes[idx]
    score = recipe.get("health_score", 0)
    assert 50 <= score <= 100, f"Recipe {recipe.get('recipe_name')} health score {score} out of range [50, 100]"

def test_meal_type_breakfast_exists(all_recipes):
    """Test 43: Ensure breakfast recipes are represented."""
    breakfasts = [r for r in all_recipes if str(r.get("meal_type", "")).lower() == "breakfast"]
    assert len(breakfasts) >= 20

def test_meal_type_lunch_exists(all_recipes):
    """Test 44: Ensure lunch recipes are represented."""
    lunches = [r for r in all_recipes if str(r.get("meal_type", "")).lower() == "lunch"]
    assert len(lunches) >= 40

def test_meal_type_dinner_exists(all_recipes):
    """Test 45: Ensure dinner recipes are represented."""
    dinners = [r for r in all_recipes if str(r.get("meal_type", "")).lower() == "dinner"]
    assert len(dinners) >= 40

def test_meal_type_snack_exists(all_recipes):
    """Test 46: Ensure snack recipes are represented."""
    snacks = [r for r in all_recipes if str(r.get("meal_type", "")).lower() == "snack"]
    assert len(snacks) >= 15

def test_cuisine_andhra_represented(all_recipes):
    """Test 47: Verify authentic Andhra regional cuisine representation."""
    andhra = [r for r in all_recipes if "andhra" in str(r.get("cuisine", "")).lower()]
    assert len(andhra) >= 25

def test_cuisine_telangana_represented(all_recipes):
    """Test 48: Verify authentic Telangana regional cuisine representation."""
    telangana = [r for r in all_recipes if "telangana" in str(r.get("cuisine", "")).lower()]
    assert len(telangana) >= 15

def test_cuisine_south_indian_represented(all_recipes):
    """Test 49: Verify broader South Indian cuisine representation."""
    south = [r for r in all_recipes if any(k in str(r.get("cuisine", "")).lower() for k in ["south", "tamil", "kerala", "karnataka"])]
    assert len(south) >= 30

def test_veg_nonveg_diversity(all_recipes):
    """Test 50: Verify dataset contains both vegetarian and non-vegetarian recipes."""
    veg_count = sum(1 for r in all_recipes if str(r.get("veg_nonveg", "")).lower() == "veg")
    nonveg_count = sum(1 for r in all_recipes if str(r.get("veg_nonveg", "")).lower() == "non-veg")
    assert veg_count >= 100, f"Expected at least 100 veg recipes, found {veg_count}"
    assert nonveg_count >= 50, f"Expected at least 50 non-veg recipes, found {nonveg_count}"
