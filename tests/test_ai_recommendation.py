import pytest
import numpy as np

# 40 diverse ingredient search queries spanning South Indian, North Indian, and core pantry staples
QUERY_INGREDIENTS_40 = [
    "chicken", "paneer", "biryani", "dal", "dosa",
    "idli", "mutton", "fish", "spinach", "gongura",
    "tamarind", "rice", "curd", "ghee", "garlic",
    "ginger", "coriander", "mustard", "fenugreek", "cumin",
    "pepper", "egg", "prawns", "tomato", "potato",
    "cauliflower", "cabbage", "carrot", "capsicum", "mushroom",
    "radish", "beetroot", "peas", "lentils", "rajma",
    "chana", "quinoa", "oats", "almonds", "cashews"
]

# 16 dietary filter configurations
DIETARY_FILTER_CONFIGS_16 = [
    {"meal_type": "Breakfast"},
    {"meal_type": "Lunch"},
    {"meal_type": "Dinner"},
    {"meal_type": "Snack"},
    {"diet": "Veg"},
    {"diet": "Non-Veg"},
    {"max_calories": 500},
    {"max_calories": 350},
    {"min_protein": 20},
    {"min_protein": 30},
    {"cuisine": "Andhra"},
    {"cuisine": "Telangana"},
    {"diet": "Veg", "meal_type": "Breakfast"},
    {"diet": "Veg", "meal_type": "Lunch"},
    {"diet": "Non-Veg", "meal_type": "Dinner"},
    {"max_calories": 600, "min_protein": 25}
]

def test_embeddings_matrix_dimensions(engine):
    """Test 51: Verify precomputed BERT embeddings matrix shape is exactly (230, 384)."""
    assert engine.embeddings is not None, "Embeddings not loaded in AI Engine"
    assert engine.embeddings.shape == (230, 384), f"Expected (230, 384), got {engine.embeddings.shape}"

def test_embeddings_dtype(engine):
    """Test 52: Verify embeddings are stored as floating point numbers."""
    assert engine.embeddings.dtype in [np.float32, np.float64]

def test_embeddings_no_nan_or_inf(engine):
    """Test 53: Verify embeddings contain zero NaN or Inf values."""
    assert not np.isnan(engine.embeddings).any(), "Embeddings contain NaN values"
    assert not np.isinf(engine.embeddings).any(), "Embeddings contain Inf values"

def test_vector_norm_stability(engine):
    """Test 54: Verify embedding vectors have positive finite L2 norms."""
    norms = np.linalg.norm(engine.embeddings, axis=1)
    assert (norms > 0).all(), "Found zero-norm vector in embeddings"
    assert (norms < 100).all(), "Norm anomaly detected"

@pytest.mark.parametrize("ingredient", QUERY_INGREDIENTS_40)
def test_search_by_single_ingredient(engine, ingredient):
    """Tests 55-94: Verify semantic and text search returns valid scored matches for 40 key ingredients."""
    matches = engine.search_by_ingredients(ingredient, top_n=5)
    assert isinstance(matches, list), f"Expected list response for {ingredient}"
    assert len(matches) <= 5
    for item in matches:
        assert "recipe_id" in item or "recipe_name" in item

@pytest.mark.parametrize("cfg", DIETARY_FILTER_CONFIGS_16)
def test_filter_recipes_constraints(engine, cfg):
    """Tests 95-110: Verify multi-facet recipe filtering satisfies caloric, macro, and regional constraints."""
    filtered = engine.filter_recipes(**cfg)
    assert isinstance(filtered, list)
    assert len(filtered) > 0, f"Expected matches for filter {cfg}"
    
    for r in filtered:
        if "meal_type" in cfg:
            assert str(r.get("meal_type", "")).lower() == cfg["meal_type"].lower()
        if "diet" in cfg:
            assert str(r.get("veg_nonveg", "")).lower() == cfg["diet"].lower()
        if "cuisine" in cfg:
            assert cfg["cuisine"].lower() in str(r.get("cuisine", "")).lower()
        if "max_calories" in cfg:
            nutr = r.get("nutritions", {})
            cal = nutr.get("calories", 0)
            assert cal <= cfg["max_calories"]
        if "min_protein" in cfg:
            nutr = r.get("nutritions", {})
            prot = nutr.get("protein_g", 0)
            assert prot >= cfg["min_protein"]
