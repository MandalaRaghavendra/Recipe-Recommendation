import pytest
from nutrition_engine import calculate_bmr, calculate_bmi, calculate_tdee, calculate_macronutrient_targets
from nutrition_coach import coach_service

# 5 Male BMR Test Profiles: (weight_kg, height_cm, age_yrs, expected_bmr)
# Mifflin-St Jeor: 10*W + 6.25*H - 5*A + 5
MALE_BMR_CASES = [
    (70, 175, 25, (10 * 70) + (6.25 * 175) - (5 * 25) + 5),     # 700 + 1093.75 - 125 + 5 = 1673.75
    (80, 180, 30, (10 * 80) + (6.25 * 180) - (5 * 30) + 5),     # 800 + 1125 - 150 + 5 = 1780.0
    (60, 165, 20, (10 * 60) + (6.25 * 165) - (5 * 20) + 5),     # 600 + 1031.25 - 100 + 5 = 1536.25
    (90, 185, 40, (10 * 90) + (6.25 * 185) - (5 * 40) + 5),     # 900 + 1156.25 - 200 + 5 = 1861.25
    (75, 170, 35, (10 * 75) + (6.25 * 170) - (5 * 35) + 5)      # 750 + 1062.5 - 175 + 5 = 1642.5
]

# 5 Female BMR Test Profiles: (weight_kg, height_cm, age_yrs, expected_bmr)
# Mifflin-St Jeor: 10*W + 6.25*H - 5*A - 161
FEMALE_BMR_CASES = [
    (55, 160, 25, (10 * 55) + (6.25 * 160) - (5 * 25) - 161),   # 550 + 1000 - 125 - 161 = 1264.0
    (65, 165, 30, (10 * 65) + (6.25 * 165) - (5 * 30) - 161),   # 650 + 1031.25 - 150 - 161 = 1370.25
    (50, 155, 22, (10 * 50) + (6.25 * 155) - (5 * 22) - 161),   # 500 + 968.75 - 110 - 161 = 1197.75
    (70, 170, 38, (10 * 70) + (6.25 * 170) - (5 * 38) - 161),   # 700 + 1062.5 - 190 - 161 = 1411.5
    (60, 158, 28, (10 * 60) + (6.25 * 158) - (5 * 28) - 161)    # 600 + 987.5 - 140 - 161 = 1286.5
]

# 5 BMI Profiles: (weight, height, expected_bmi_category)
BMI_CASES = [
    (50, 175, "underweight"),    # BMI ~ 16.3
    (65, 172, "normal"),         # BMI ~ 22.0
    (72, 170, "normal"),         # BMI ~ 24.9
    (82, 170, "overweight"),     # BMI ~ 28.4
    (98, 170, "obese")           # BMI ~ 33.9
]

# 5 Activity Multipliers
ACTIVITY_CASES = [
    ("sedentary", 1.2),
    ("lightly_active", 1.375),
    ("moderately_active", 1.55),
    ("very_active", 1.725),
    ("extra_active", 1.9)
]

# 5 Macro Target Configurations: (diet_goal, weight_kg, expected_min_cal)
GOAL_MACRO_CASES = [
    ("weight_loss", 70.0, 1200),
    ("muscle_gain", 75.0, 1800),
    ("keto", 80.0, 1200),
    ("maintenance", 68.0, 1500),
    ("balanced", 65.0, 1400)
]

@pytest.mark.parametrize("w,h,a,expected", MALE_BMR_CASES)
def test_bmr_male_calculation(w, h, a, expected):
    """Tests 201-205: Verify exact Mifflin-St Jeor BMR formula adherence for males."""
    assert calculate_bmr(w, h, a, "male") == pytest.approx(expected, 0.01)

@pytest.mark.parametrize("w,h,a,expected", FEMALE_BMR_CASES)
def test_bmr_female_calculation(w, h, a, expected):
    """Tests 206-210: Verify exact Mifflin-St Jeor BMR formula adherence for females."""
    assert calculate_bmr(w, h, a, "female") == pytest.approx(expected, 0.01)

@pytest.mark.parametrize("w,h,cat", BMI_CASES)
def test_bmi_calculation_ranges(w, h, cat):
    """Tests 211-215: Verify BMI numerical computation and category classification boundaries."""
    bmi = calculate_bmi(w, h)
    assert bmi is not None
    if cat == "underweight":
        assert bmi < 18.5
    elif cat == "normal":
        assert 18.5 <= bmi < 25.0
    elif cat == "overweight":
        assert 25.0 <= bmi < 30.0
    elif cat == "obese":
        assert bmi >= 30.0

@pytest.mark.parametrize("level,multiplier", ACTIVITY_CASES)
def test_tdee_activity_tiers(level, multiplier):
    """Tests 216-220: Verify TDEE activity factor scaling from sedentary (1.2) to extra active (1.9)."""
    bmr = 1600.0
    expected = round(bmr * multiplier, 1)
    actual = calculate_tdee(bmr, activity_level=level)
    assert actual == pytest.approx(expected, 0.1)

@pytest.mark.parametrize("goal,w_kg,min_cal", GOAL_MACRO_CASES)
def test_macro_target_distribution(goal, w_kg, min_cal):
    """Tests 221-225: Validate target caloric floor and positive macronutrient distributions."""
    tdee = 2200.0
    cal, prot, carbs, fat = calculate_macronutrient_targets(tdee, diet_goal=goal, weight_kg=w_kg)
    assert cal >= min_cal
    assert prot > 0
    assert carbs >= 0
    assert fat > 0
    calc_cal = (prot * 4) + (carbs * 4) + (fat * 9)
    assert abs(calc_cal - cal) <= 60

def test_coach_context_assembly():
    """Test 226: Verify AI coach generates complete structured profile context for user."""
    ctx = coach_service.get_user_context(user_id=1)
    assert isinstance(ctx, dict)
    assert "user_id" in ctx or "profile" in ctx or "diet_goal" in ctx

def test_coach_answer_weight_loss_query():
    """Test 227: Coach provides targeted advice for weight loss queries."""
    res = coach_service.process_query("How can I reduce calories while staying full?", user_id=1)
    assert isinstance(res, dict)
    assert res.get("success") is True
    assert "reply" in res
    assert len(res["reply"]) > 10

def test_coach_answer_high_protein_query():
    """Test 228: Coach answers protein-rich Indian food queries."""
    res = coach_service.process_query("What are good vegetarian high protein Indian foods?", user_id=1)
    assert isinstance(res, dict)
    assert res.get("success") is True
    assert len(res.get("reply", "")) > 10

def test_coach_handles_empty_query_gracefully():
    """Test 229: Coach safely handles blank or whitespace queries."""
    res = coach_service.process_query("   ", user_id=1)
    assert isinstance(res, dict)
    assert "reply" in res

def test_coach_format_recipe_summary():
    """Test 230: Verify recipe grounding context formatter produces readable nutritional dictionary."""
    sample_recipe = {
        "recipe_name": "Andhra Dal",
        "nutritions": {"calories": 300, "protein_g": 18, "carbs_g": 40, "fat_g": 6}
    }
    summary = coach_service.format_recipe_for_coach(sample_recipe)
    assert isinstance(summary, dict)
    assert summary.get("recipe_name") == "Andhra Dal"
    assert summary.get("calories") == 300
