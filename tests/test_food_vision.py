import pytest
from PIL import Image
from food_vision_engine import FoodVisionEngine

SIGNATURE_KEYS_12 = [
    "biryani", "dosa", "idli", "paneer", "chicken_curry",
    "sambar", "tikka", "salad", "dal", "roti",
    "fish_curry", "dessert"
]

@pytest.fixture(scope="module")
def vision_engine():
    return FoodVisionEngine()

@pytest.mark.parametrize("sig_key", SIGNATURE_KEYS_12)
def test_food_signatures_structure(vision_engine, sig_key):
    """Tests 231-242: Verify visual signature dictionary contains keywords, hues, and typical recipes."""
    assert sig_key in vision_engine.FOOD_SIGNATURES
    sig = vision_engine.FOOD_SIGNATURES[sig_key]
    assert "keywords" in sig and len(sig["keywords"]) > 0
    assert "dominant_hues" in sig and len(sig["dominant_hues"]) > 0
    assert "typical_recipes" in sig and len(sig["typical_recipes"]) > 0

def test_interactive_dish_grounding_text(vision_engine):
    """Test 243: Direct culinary query string returns high-confidence predictions."""
    res = vision_engine.analyze_image("Andhra Chicken Biryani")
    assert res.get("success") is True
    assert len(res.get("predictions", [])) > 0
    assert res["predictions"][0]["label"] == "Andhra Chicken Biryani"
    assert res["predictions"][0]["confidence"] >= 0.90

def test_synthetic_image_classification(vision_engine):
    """Test 244: Processing a synthetic RGB image returns structured candidate predictions."""
    img = Image.new("RGB", (120, 120), color=(180, 120, 40))
    res = vision_engine.analyze_image(img, top_k=3)
    assert res.get("success") is True
    assert len(res.get("predictions", [])) <= 3

def test_invalid_image_input_graceful_error(vision_engine):
    """Test 245: Invalid image input returns structured error instead of unhandled exception."""
    res = vision_engine.analyze_image(None)
    assert res.get("success") is False
    assert "error" in res

def test_confidence_pct_calculation(vision_engine):
    """Test 246: Confidence percentage is mathematically bounded between 0 and 100."""
    res = vision_engine.analyze_image("Masala Dosa")
    pred = res["predictions"][0]
    assert 0 <= pred["confidence_pct"] <= 100
    assert pred["confidence_pct"] == round(pred["confidence"] * 100)

def test_confidence_tier_badges(vision_engine):
    """Test 247: Predictions include user-facing confidence badge metadata."""
    res = vision_engine.analyze_image("Paneer Tikka")
    pred = res["predictions"][0]
    assert "confidence_tier" in pred
    assert "tier_badge" in pred

def test_database_grounding_success(vision_engine, engine, all_recipes):
    """Test 248: Vision predictions ground successfully to verified database recipes."""
    preds = [{"label": "biryani", "confidence": 0.95}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    assert match.get("is_recognized") is True
    assert match.get("matched_recipe") is not None

def test_grounded_top_prediction(vision_engine, engine, all_recipes):
    """Test 249: Grounded payload preserves top prediction label."""
    preds = [{"label": "dosa", "confidence": 0.92}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    assert match["top_prediction"]["label"] == "dosa"

def test_grounded_verified_nutrition_fields(vision_engine, engine, all_recipes):
    """Test 250: Grounded match extracts verified macronutrients from database."""
    preds = [{"label": "chicken_curry", "confidence": 0.88}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    nutr = match.get("verified_nutrition", {})
    assert "calories" in nutr
    assert "protein_g" in nutr
    assert "carbs_g" in nutr
    assert "fat_g" in nutr

def test_grounded_candidate_recipes_alternatives(vision_engine, engine, all_recipes):
    """Test 251: Grounded match returns candidate alternative recipes."""
    preds = [{"label": "paneer", "confidence": 0.90}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    candidates = match.get("candidate_recipes", [])
    assert isinstance(candidates, list)
    assert len(candidates) > 0

def test_grounded_unknown_food_fallback(vision_engine, engine, all_recipes):
    """Test 252: Grounding completely unrecognized dish names falls back without crashing."""
    preds = [{"label": "unrecognized_alien_berry_pie_xyz", "confidence": 0.10}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    assert isinstance(match, dict)

def test_top_k_parameter_limiting(vision_engine):
    """Test 253: analyze_image respects custom top_k prediction parameter."""
    img = Image.new("RGB", (64, 64), color=(220, 80, 30))
    res = vision_engine.analyze_image(img, top_k=2)
    assert len(res.get("predictions", [])) <= 2

def test_safety_disclaimer_present(vision_engine, engine, all_recipes):
    """Test 254: Match payload provides nutritional safety disclaimer for health guidance."""
    preds = [{"label": "dal", "confidence": 0.85}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    assert "disclaimer" in match
    assert len(match["disclaimer"]) > 10

def test_verified_nutrition_numeric_consistency(vision_engine, engine, all_recipes):
    """Test 255: Verified calories in match payload are strictly positive numbers."""
    preds = [{"label": "biryani", "confidence": 0.95}]
    match = vision_engine.match_to_database(preds, engine.get_recipe_by_id, all_recipes)
    cal = match.get("verified_nutrition", {}).get("calories", 0)
    assert cal > 0
