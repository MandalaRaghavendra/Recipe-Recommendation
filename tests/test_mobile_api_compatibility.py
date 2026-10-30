"""
test_mobile_api_compatibility.py - Comprehensive Mobile API Compatibility Suite
Verifies that React Native Expo application workflows operate smoothly
under the hardened security model (session cookies, Bearer tokens, CSRF protection, BOLA defense).
"""

import pytest
import uuid
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from app import app
import database as db

@pytest.fixture
def mobile_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_mobile_full_user_lifecycle(mobile_client):
    """Verifies complete end-to-end mobile user journey using Bearer token authentication."""
    uid = uuid.uuid4().hex[:8]
    mobile_name = f"Mobile Chef {uid}"
    mobile_email = f"mobile_chef_{uid}@tastio.mobile"
    mobile_pass = "MobilePass123!"

    # 1. Mobile Registration (/api/auth/signup)
    res_signup = mobile_client.post("/api/auth/signup", json={
        "name": mobile_name,
        "email": mobile_email,
        "password": mobile_pass
    })
    assert res_signup.status_code == 200, f"Signup failed: {res_signup.data}"
    signup_data = res_signup.get_json()
    assert signup_data.get("success") is True
    assert "token" in signup_data
    assert "user" in signup_data
    token = signup_data["token"]
    user_id = signup_data["user"]["objectId"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Mobile Login (/api/auth/login)
    res_login = mobile_client.post("/api/auth/login", json={
        "email": mobile_email,
        "password": mobile_pass
    })
    assert res_login.status_code == 200, f"Login failed: {res_login.data}"
    login_data = res_login.get_json()
    assert login_data.get("success") is True
    assert login_data.get("token") is not None

    # 3. Recipe Search & Discovery
    res_recipes = mobile_client.get("/api/recipes?cuisine=all&search=chicken")
    assert res_recipes.status_code == 200
    recipes_data = res_recipes.get_json()
    assert "recipes" in recipes_data
    assert len(recipes_data["recipes"]) > 0

    # 4. Filter Recipes (Multi-criteria)
    res_filter = mobile_client.post("/api/recipes/filter", json={
        "cuisine": "South Indian",
        "meal_type": "breakfast"
    })
    assert res_filter.status_code == 200

    # 5. Recipe Details Lookup
    res_detail = mobile_client.get("/api/recipes/1")
    assert res_detail.status_code == 200
    assert res_detail.get_json().get("recipe") is not None

    # 6. Fetch User Profile
    res_profile = mobile_client.get(f"/api/profile?user_id={user_id}", headers=auth_headers)
    assert res_profile.status_code == 200
    profile_data = res_profile.get_json()
    assert profile_data.get("success") is True
    assert profile_data.get("profile") is not None

    # 7. Update User Profile
    res_update_prof = mobile_client.post(
        f"/api/profile?user_id={user_id}",
        headers=auth_headers,
        json={
            "user_id": user_id,
            "name": mobile_name,
            "age": 28,
            "gender": "male",
            "height": 178,
            "weight": 74,
            "diet_goal": "muscle_gain",
            "food_pref": "non_veg"
        }
    )
    assert res_update_prof.status_code == 200

    # 8. Generate 7-Day Meal Plan
    res_gen_plan = mobile_client.post(
        f"/api/meal-plan/generate?user_id={user_id}",
        headers=auth_headers,
        json={"user_id": user_id}
    )
    assert res_gen_plan.status_code == 200

    # 9. Retrieve Active Meal Plan
    res_curr_plan = mobile_client.get(f"/api/meal-plan/current?user_id={user_id}", headers=auth_headers)
    assert res_curr_plan.status_code == 200
    plan_data = res_curr_plan.get_json()
    assert plan_data.get("success") is True

    # 10. Generate Smart Grocery List From Plan
    res_gen_grocery = mobile_client.post(
        f"/api/grocery-list/generate-from-plan?user_id={user_id}",
        headers=auth_headers,
        json={"user_id": user_id}
    )
    assert res_gen_grocery.status_code == 200

    # 11. Add Custom Item to Grocery List
    res_add_item = mobile_client.post(
        f"/api/grocery-list/item?user_id={user_id}",
        headers=auth_headers,
        json={"user_id": user_id, "name": "Organic Almond Milk", "category": "Dairy", "amount": "1 liter"}
    )
    assert res_add_item.status_code == 200
    item_id = res_add_item.get_json().get("item_id")

    # 12. Toggle Grocery Item Checked State
    if item_id:
        res_toggle = mobile_client.post(
            f"/api/grocery-list/item/{item_id}/toggle?user_id={user_id}",
            headers=auth_headers,
            json={"user_id": user_id}
        )
        assert res_toggle.status_code == 200

    # 13. Fetch Grocery Checklist
    res_grocery = mobile_client.get(f"/api/grocery-list?user_id={user_id}", headers=auth_headers)
    assert res_grocery.status_code == 200

    # 14. Nutrition Analytics Dashboard
    res_nutrition = mobile_client.get(f"/api/analytics/nutrition?user_id={user_id}", headers=auth_headers)
    assert res_nutrition.status_code == 200

    # 15. AI Nutrition Coach Chat
    res_coach_chat = mobile_client.post(
        "/api/coach/chat",
        headers=auth_headers,
        json={
            "user_id": user_id,
            "message": "What is a healthy high-protein breakfast for muscle gain?"
        }
    )
    assert res_coach_chat.status_code == 200
    assert "reply" in res_coach_chat.get_json()

    # 15b. AI Coach unauthenticated and IDOR check
    with app.test_client() as anon_client:
        res_unauth_coach = anon_client.post("/api/coach/chat", json={"message": "Hello"})
        assert res_unauth_coach.status_code == 401, f"Expected 401 for unauthenticated coach chat, got {res_unauth_coach.status_code}"

    res_idor_coach = mobile_client.post(
        "/api/coach/chat",
        headers=auth_headers,
        json={"user_id": "999999", "message": "Sneaky query"}
    )
    assert res_idor_coach.status_code == 403, f"Expected 403 for mismatched user_id coach chat, got {res_idor_coach.status_code}"

    # 16. AI Nutrition Coach Context
    res_coach_ctx = mobile_client.get(f"/api/coach/context?user_id={user_id}", headers=auth_headers)
    assert res_coach_ctx.status_code == 200

    # 17. Food Vision Image Recognition & Status
    res_vision_status = mobile_client.get("/api/vision/status")
    assert res_vision_status.status_code == 200

    res_vision_rec = mobile_client.post("/api/vision/recognize-food", json={"image": "dosa"})
    assert res_vision_rec.status_code == 200

    # 18. Log Meal Eaten
    res_mark = mobile_client.post(
        f"/api/mark_eaten/1?user_id={user_id}",
        headers=auth_headers,
        json={"user_id": user_id, "serving_size": 1.0}
    )
    assert res_mark.status_code == 200

    # 19. Meal History
    res_history = mobile_client.get(f"/api/history?user_id={user_id}", headers=auth_headers)
    assert res_history.status_code == 200

    # 20. IDOR / Cross-User Defense with Mobile Token
    # Mobile Chef attempts to access User ID 999999
    res_idor = mobile_client.get(f"/api/profile?user_id=999999", headers=auth_headers)
    assert res_idor.status_code == 403, f"Expected 403 Forbidden on IDOR attempt, got {res_idor.status_code}"

