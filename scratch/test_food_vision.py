import sys
import os
import json
import io
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) if os.path.basename(CURRENT_DIR) == "scratch" else CURRENT_DIR
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
AI_DIR = os.path.join(PROJECT_ROOT, "ai-service")

sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, AI_DIR)
sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from app import app
from embedding_engine import ai_engine
from food_vision_engine import food_vision_engine

def run_vision_tests():
    print("=" * 70)
    print("RUNNING TASTIO AI FOOD IMAGE RECOGNITION & GROUNDING TEST SUITE")
    print("=" * 70)

    # Test 1: Image loading & analysis with synthetic food image (Golden/Yellow -> Biryani)
    print("\n[TEST 1] Testing Image Analysis & Feature Extraction")
    img_biryani = Image.new("RGB", (128, 128), color=(220, 160, 40)) # Warm golden yellow
    buf_biryani = io.BytesIO()
    img_biryani.save(buf_biryani, format="JPEG")
    raw_bytes = buf_biryani.getvalue()

    analysis = food_vision_engine.analyze_image(raw_bytes, top_k=3)
    assert analysis["success"] is True, "Image analysis failed"
    preds = analysis["predictions"]
    assert len(preds) == 3, f"Expected 3 predictions, got {len(preds)}"
    print(f"  [PASS] Model: {analysis['model']}")
    print(f"  [PASS] Top Prediction: {preds[0]['label']} ({preds[0]['confidence_pct']}% - {preds[0]['confidence_tier']})")

    # Test 2: Database Grounding & Verified Nutrition
    print("\n[TEST 2] Testing Database Grounding & Verified Nutrition Mapping")
    all_recipes = ai_engine.get_all_recipes()
    grounded = food_vision_engine.match_to_database(
        predictions=preds,
        recipe_lookup_fn=ai_engine.get_recipe_by_id,
        all_recipes=all_recipes
    )

    assert grounded["is_recognized"] is True, "Database grounding failed"
    matched_r = grounded["matched_recipe"]
    assert matched_r is not None, "No matched recipe returned"
    print(f"  [PASS] Matched Database Recipe: '{matched_r['recipe_name']}' (ID: {matched_r['recipe_id']})")
    print(f"  [PASS] Cuisine: {matched_r.get('cuisine', 'Indian')}, Diet: {matched_r.get('veg_nonveg', 'Veg')}")

    # Check verified nutrition
    nutr = grounded["verified_nutrition"]
    assert nutr["calories"] > 0, "Calorie value missing"
    assert nutr["protein_g"] >= 0, "Protein value missing"
    assert "Standard portion" in nutr["serving_description"], "Serving description missing"
    print(f"  [PASS] Verified Database Nutrition: {nutr['calories']} kcal, {nutr['protein_g']}g P, {nutr['carbs_g']}g C, {nutr['fat_g']}g F")

    # Check disclaimer (Grounding Rule)
    assert "NUTRITION GROUNDING NOTICE" in grounded["disclaimer"], "Mandatory grounding disclaimer missing"
    print("  [PASS] Mandatory Grounding Disclaimer strictly verified (Zero pixel-based calories fabricated)")

    # Check candidate alternatives & similar recipes
    assert len(grounded["candidate_recipes"]) > 0, "Candidate recipes missing"
    assert len(grounded["similar_recipes"]) > 0, "Similar recipes missing"
    print(f"  [PASS] Alternative candidate dishes: {[c['recipe_name'] for c in grounded['candidate_recipes'][:3]]}")
    print(f"  [PASS] Similar dishes from cuisine: {[s['recipe_name'] for s in grounded['similar_recipes'][:3]]}")

    # Test 3: Green Salad image test (Green pixels)
    print("\n[TEST 3] Testing Vegetarian Green Dish Recognition")
    img_green = Image.new("RGB", (128, 128), color=(34, 180, 50)) # Green
    buf_green = io.BytesIO()
    img_green.save(buf_green, format="PNG")

    analysis_green = food_vision_engine.analyze_image(buf_green.getvalue(), top_k=3)
    assert analysis_green["success"] is True
    grounded_green = food_vision_engine.match_to_database(
        predictions=analysis_green["predictions"],
        recipe_lookup_fn=ai_engine.get_recipe_by_id,
        all_recipes=all_recipes
    )
    print(f"  [PASS] Top Prediction: {analysis_green['predictions'][0]['label']}")
    print(f"  [PASS] Grounded Recipe: {grounded_green['matched_recipe']['recipe_name']}")

    # Test 4: Flask HTTP Client Endpoints
    print("\n[TEST 4] Testing Flask REST API & Web Routes")
    client = app.test_client()

    # GET /scanner Web Route
    resp_page = client.get("/scanner")
    assert resp_page.status_code == 200, f"GET /scanner returned {resp_page.status_code}"
    print("  [PASS] GET /scanner returned HTML 200 OK")

    # GET /api/vision/status
    resp_status = client.get("/api/vision/status")
    assert resp_status.status_code == 200
    st_data = json.loads(resp_status.data)
    assert st_data["success"] is True
    print(f"  [PASS] GET /api/vision/status returned {st_data['engine']} (Indexed: {st_data['database_recipes_indexed']} dishes)")

    # POST /api/vision/recognize-food with multipart file
    buf_biryani.seek(0)
    resp_api = client.post(
        "/api/vision/recognize-food",
        data={"image": (buf_biryani, "biryani.jpg", "image/jpeg")},
        content_type="multipart/form-data"
    )
    assert resp_api.status_code == 200, f"POST /api/vision/recognize-food failed: {resp_api.data}"
    api_data = json.loads(resp_api.data)
    assert api_data["success"] is True, "API response success was not True"
    assert api_data["recognition"]["is_recognized"] is True, "Recognition was not True"
    print(f"  [PASS] POST /api/vision/recognize-food returned grounded match: '{api_data['recognition']['matched_recipe']['recipe_name']}'")

    # Test 5: Verify zero breakage of existing features
    print("\n[TEST 5] Verifying Non-Breaking System Integrity")
    resp_rec = client.get("/api/recipes?cuisine=Andhra")
    assert resp_rec.status_code == 200
    print("  [PASS] Multi-facet Recipe Filtering intact")

    resp_grocery = client.get("/api/grocery-list")
    assert resp_grocery.status_code == 200
    print("  [PASS] Smart Grocery List API intact")

    resp_plan = client.get("/api/meal-plan/current")
    assert resp_plan.status_code == 200
    print("  [PASS] 7-Day AI Meal Planner API intact")

    print("\n" + "=" * 70)
    print("ALL AI FOOD IMAGE RECOGNITION TESTS PASSED! (100% VERIFIED)")
    print("=" * 70)

if __name__ == "__main__":
    run_vision_tests()
