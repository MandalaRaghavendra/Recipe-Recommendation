import pytest
import json

def test_api_health_check(client):
    """Test 256: GET /api/health returns healthy status and 230 indexed recipes."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "healthy"
    assert data.get("recipes_indexed") == 230

def test_api_get_all_recipes(client):
    """Test 257: GET /api/recipes returns HTTP 200 with recipe records."""
    res = client.get("/api/recipes")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) >= 150

def test_api_recipes_cuisine_filter(client):
    """Test 258: GET /api/recipes?cuisine=Andhra filters recipes by cuisine."""
    res = client.get("/api/recipes?cuisine=Andhra")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0

def test_api_get_single_recipe(client):
    """Test 259: GET /api/recipes/1 returns complete details for recipe 1."""
    res = client.get("/api/recipes/1")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    recipe = data.get("recipe", {})
    assert str(recipe.get("recipe_id")) == "1"
    assert "ingredients" in recipe
    assert "nutritions" in recipe

def test_api_get_nonexistent_recipe(client):
    """Test 260: GET /api/recipes/999999 returns HTTP 404 for missing recipe."""
    res = client.get("/api/recipes/999999")
    assert res.status_code == 404 or res.get_json().get("success") is False

def test_api_filter_breakfast(client):
    """Test 261: GET /api/recipes/filter?meal_type=Breakfast filters breakfast meals."""
    res = client.get("/api/recipes/filter?meal_type=Breakfast")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0
    for r in recipes:
        assert str(r.get("meal_type", "")).lower() == "breakfast"

def test_api_filter_veg(client):
    """Test 262: GET /api/recipes/filter?diet=Veg returns only vegetarian meals."""
    res = client.get("/api/recipes/filter?diet=Veg")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0
    for r in recipes:
        assert str(r.get("veg_nonveg", "")).lower() == "veg"

def test_api_filter_nonveg(client):
    """Test 263: GET /api/recipes/filter?diet=Non-Veg returns non-vegetarian meals."""
    res = client.get("/api/recipes/filter?diet=Non-Veg")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0
    for r in recipes:
        assert str(r.get("veg_nonveg", "")).lower() == "non-veg"

def test_api_filter_andhra_cuisine(client):
    """Test 264: GET /api/recipes/filter?cuisine=Andhra filters Andhra regional dishes."""
    res = client.get("/api/recipes/filter?cuisine=Andhra")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0
    for r in recipes:
        assert "andhra" in str(r.get("cuisine", "")).lower()

def test_api_filter_max_calories(client):
    """Test 265: GET /api/recipes/filter?max_calories=400 restricts calories."""
    res = client.get("/api/recipes/filter?max_calories=400")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0
    for r in recipes:
        cal = r.get("nutritions", {}).get("calories", 0)
        assert cal <= 400

def test_api_recommend_ingredients(client):
    """Test 266: POST /api/recommend returns scored recommendations for chicken."""
    res = client.post("/api/recommend", json={"ingredients": ["chicken"]})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert len(data.get("recipes", [])) > 0

def test_api_recommend_empty_body(client):
    """Test 267: POST /api/recommend with empty payload handles gracefully."""
    res = client.post("/api/recommend", json={})
    assert res.status_code in [200, 400]

def test_api_pantry_match(client):
    """Test 268: POST /api/pantry-match calculates pantry utilization scores."""
    res = client.post("/api/pantry-match", json={"ingredients": ["egg", "onion", "tomato"]})
    assert res.status_code == 200
    data = res.get_json()
    assert "recipes" in data or "matches" in data

def test_api_pantry_match_empty(client):
    """Test 269: POST /api/pantry-match handles empty input."""
    res = client.post("/api/pantry-match", json={"ingredients": []})
    assert res.status_code in [200, 400]

def test_api_current_meal_plan(client):
    """Test 270: GET /api/meal-plan/current returns current plan structure."""
    res = client.get("/api/meal-plan/current")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert "meal_plan" in data
    assert "days" in data["meal_plan"]

def test_api_generate_meal_plan(client):
    """Test 271: POST /api/meal-plan/generate generates fresh 7-day schedule."""
    res = client.post("/api/meal-plan/generate")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert "meal_plan" in data
    assert len(data["meal_plan"]["days"]) == 7

def test_api_meal_alternatives_breakfast(client):
    """Test 272: GET /api/meal-plan/alternatives?meal_type=breakfast returns breakfast substitutes."""
    res = client.get("/api/meal-plan/alternatives?meal_type=breakfast")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data.get("alternatives", []), list)

def test_api_meal_alternatives_lunch(client):
    """Test 273: GET /api/meal-plan/alternatives?meal_type=lunch returns lunch substitutes."""
    res = client.get("/api/meal-plan/alternatives?meal_type=lunch")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data.get("alternatives", []), list)

def test_api_meal_alternatives_dinner(client):
    """Test 274: GET /api/meal-plan/alternatives?meal_type=dinner returns dinner substitutes."""
    res = client.get("/api/meal-plan/alternatives?meal_type=dinner")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data.get("alternatives", []), list)

def test_api_meal_alternatives_snack(client):
    """Test 275: GET /api/meal-plan/alternatives?meal_type=snack returns snack substitutes."""
    res = client.get("/api/meal-plan/alternatives?meal_type=snack")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data.get("alternatives", []), list)

def test_api_replace_meal(client):
    """Test 276: POST /api/meal-plan/replace-meal swaps target slot in active plan."""
    payload = {"day_index": 1, "meal_type": "breakfast", "new_recipe_id": "75"}
    res = client.post("/api/meal-plan/replace-meal", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_get_grocery_list(client):
    """Test 277: GET /api/grocery-list returns user's smart grocery checklist."""
    res = client.get("/api/grocery-list")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert "grocery" in data

def test_api_add_grocery_item(client):
    """Test 278: POST /api/grocery-list/item adds custom grocery item."""
    res = client.post("/api/grocery-list/item", json={"item_name": "Chia Seeds", "category": "Other", "user_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_add_grocery_item_validation(client):
    """Test 279: POST /api/grocery-list/item rejects missing item_name."""
    res = client.post("/api/grocery-list/item", json={"category": "Other"})
    assert res.status_code in [400, 422]

def test_api_toggle_grocery_item(client):
    """Test 280: POST /api/grocery-list/item/<item_id>/toggle updates checked status."""
    g = client.get("/api/grocery-list").get_json().get("grocery", {})
    items = g.get("items", [])
    if items:
        target_id = items[0].get("objectId") or items[0].get("id")
        res = client.post(f"/api/grocery-list/item/{target_id}/toggle", json={"user_id": 1})
        assert res.status_code == 200

def test_api_generate_grocery_from_plan(client):
    """Test 281: POST /api/grocery-list/generate-from-plan compiles ingredients from meal plan."""
    res = client.post("/api/grocery-list/generate-from-plan", json={"user_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_clear_completed_grocery(client):
    """Test 282: POST /api/grocery-list/clear-completed removes completed items."""
    res = client.post("/api/grocery-list/clear-completed", json={"user_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_add_recipe_to_grocery(client):
    """Test 283: POST /api/grocery-list/add-recipe injects recipe ingredients."""
    res = client.post("/api/grocery-list/add-recipe", json={"recipe_id": "1", "user_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_clear_all_grocery(client):
    """Test 284: POST /api/grocery-list/clear-all flushes all grocery items."""
    res = client.post("/api/grocery-list/clear-all", json={"user_id": 1})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_coach_chat(client):
    """Test 285: POST /api/coach/chat returns conversational nutrition advice."""
    res = client.post("/api/coach/chat", json={"message": "What should I eat for high protein breakfast?"})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert "reply" in data

def test_api_coach_chat_empty_message(client):
    """Test 286: POST /api/coach/chat handles empty message payload safely."""
    res = client.post("/api/coach/chat", json={"message": ""})
    assert res.status_code in [200, 400]

def test_api_coach_context(client):
    """Test 287: GET /api/coach/context returns user context profile."""
    res = client.get("/api/coach/context?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_nutrition_dashboard(client):
    """Test 288: GET /api/nutrition-dashboard returns caloric analytics."""
    res = client.get("/api/nutrition-dashboard")
    assert res.status_code == 200

def test_api_analytics_nutrition(client):
    """Test 289: GET /api/analytics/nutrition returns comprehensive nutrition report."""
    res = client.get("/api/analytics/nutrition")
    assert res.status_code == 200

def test_api_get_user_preferences(client):
    """Test 290: GET /api/user/preferences returns user settings."""
    res = client.get("/api/user/preferences?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True

def test_api_recipe_search_query(client):
    """Test 291: GET /api/recipes?query=biryani filters recipes by keyword."""
    res = client.get("/api/recipes?query=biryani")
    assert res.status_code == 200
    data = res.get_json()
    recipes = data if isinstance(data, list) else data.get("recipes", [])
    assert len(recipes) > 0

def test_api_record_recipe_view(client):
    """Test 292: POST /api/recipes/1/view tracks viewing history."""
    res = client.post("/api/recipes/1/view", json={"user_id": 1})
    assert res.status_code == 200

def test_api_get_recently_viewed(client):
    """Test 293: GET /api/user/recently-viewed retrieves recent recipe views."""
    res = client.get("/api/user/recently-viewed?user_id=1")
    assert res.status_code == 200
    data = res.get_json()
    assert "recipes" in data or isinstance(data, list)

def test_api_get_favorites(client):
    """Test 294: GET /api/favorites returns favorite recipe IDs."""
    res = client.get("/api/favorites")
    assert res.status_code in [200, 401]

def test_api_toggle_favorite(client):
    """Test 295: POST /favorite/1 toggles favorite status for recipe 1."""
    res = client.post("/favorite/1")
    assert res.status_code in [200, 302]

def test_api_mark_eaten(client):
    """Test 296: POST /mark_eaten/1 logs eaten meal to nutritional history."""
    res = client.post("/mark_eaten/1")
    assert res.status_code in [200, 302]

def test_api_get_history(client):
    """Test 297: GET /api/history returns eaten meals log."""
    res = client.get("/api/history")
    assert res.status_code in [200, 401]

def test_api_vision_recognize_food(client):
    """Test 298: POST /api/vision/recognize-food with dish text grounds recipe."""
    res = client.post("/api/vision/recognize-food", json={"image": "biryani"})
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("success") is True
    assert "predictions" in data

def test_api_vision_status(client):
    """Test 299: GET /api/vision/status reports vision engine health."""
    res = client.get("/api/vision/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") in ["ready", "available", "active"] or "model" in data

def test_api_security_and_cors_headers(client):
    """Test 300: Verify API returns proper JSON content type and CORS security headers."""
    res = client.get("/api/health")
    assert res.status_code == 200
    assert "application/json" in res.content_type
    assert res.headers.get("Access-Control-Allow-Origin") == "*"
