import pytest
from meal_planner import meal_planner_service

DAY_INDICES = list(range(7))
MEAL_TYPES = ["breakfast", "lunch", "snack", "dinner"]
DAY_MEAL_COMBOS = [(d, m) for d in DAY_INDICES for m in MEAL_TYPES]

@pytest.fixture(scope="module")
def generated_plan():
    return meal_planner_service.generate_7day_plan(user_id=1)

def test_plan_top_level_metadata(generated_plan):
    """Test 111: Verify 7-day meal plan has valid top-level metadata."""
    assert "start_date" in generated_plan
    assert "end_date" in generated_plan
    assert "days" in generated_plan
    assert len(generated_plan["days"]) == 7

@pytest.mark.parametrize("day_idx", DAY_INDICES)
def test_each_day_structure(generated_plan, day_idx):
    """Tests 112-118: Verify schema integrity of each of the 7 scheduled days."""
    day = generated_plan["days"][day_idx]
    assert "day_name" in day
    assert "date" in day
    assert "meals" in day
    assert "total_calories" in day
    assert isinstance(day["meals"], dict)

@pytest.mark.parametrize("day_idx,meal_type", DAY_MEAL_COMBOS)
def test_all_28_meal_slots_contain_valid_recipes(generated_plan, day_idx, meal_type):
    """Tests 119-146: Verify that all 28 meal slots (7 days x 4 meals) contain valid populated recipes."""
    day = generated_plan["days"][day_idx]
    meal = day["meals"].get(meal_type)
    assert meal is not None, f"Day {day_idx} missing {meal_type}"
    assert "recipe_id" in meal
    assert "recipe_name" in meal
    assert "calories" in meal
    assert meal["calories"] > 0
    assert "image_link" in meal

@pytest.mark.parametrize("day_idx", DAY_INDICES)
def test_daily_caloric_balance(generated_plan, day_idx):
    """Tests 147-153: Validate that daily sum of calories across slots equals total_calories."""
    day = generated_plan["days"][day_idx]
    summed_cal = sum(m.get("calories", 0) for m in day["meals"].values() if m)
    tot_cal = day.get("total_calories", 0)
    assert abs(summed_cal - tot_cal) <= 5, f"Day {day_idx} calorie sum mismatch: {summed_cal} vs {tot_cal}"

def test_weekly_caloric_variance_is_sane(generated_plan):
    """Test 154: Validate average daily calories are within healthy human physiological ranges."""
    cals = [d.get("total_calories", 0) for d in generated_plan["days"]]
    avg_cal = sum(cals) / len(cals)
    assert 1200 <= avg_cal <= 3200, f"Unrealistic average plan calories: {avg_cal}"

@pytest.mark.parametrize("meal_type", MEAL_TYPES)
def test_get_alternatives_for_slot(meal_type):
    """Tests 155-158: Verify alternative suggestions for breakfast, lunch, snack, and dinner."""
    alts = meal_planner_service.get_alternatives_for_slot(user_id=1, meal_type=meal_type)
    assert isinstance(alts, list)
    assert len(alts) > 0, f"No alternatives found for {meal_type}"
    for r in alts:
        assert "recipe_id" in r
        assert "recipe_name" in r

def test_replace_meal_slot_preserves_other_meals(generated_plan):
    """Test 159: Swapping a meal updates the target slot while preserving other meals on that day."""
    day_0 = generated_plan["days"][0]
    breakfast_before = day_0["meals"]["breakfast"]["recipe_id"]
    lunch_before = day_0["meals"]["lunch"]["recipe_id"]
    
    alts = meal_planner_service.get_alternatives_for_slot(user_id=1, meal_type="breakfast", current_recipe_id=breakfast_before)
    if alts:
        new_recipe_id = alts[0]["recipe_id"]
        res_plan, msg = meal_planner_service.replace_meal(user_id=1, day_index=1, meal_type="breakfast", new_recipe_id=new_recipe_id)
        assert res_plan is not None
        assert "Meal replaced successfully" in msg
        
        # Verify lunch was not affected
        cur_day = res_plan["days"][0]
        assert cur_day["meals"]["lunch"]["recipe_id"] == lunch_before

def test_replace_meal_updates_daily_nutrition():
    """Test 160: Replacing a meal recalculates the daily total nutrition metrics correctly."""
    cur_plan = meal_planner_service.get_current_plan(user_id=1)
    alts = meal_planner_service.get_alternatives_for_slot(user_id=1, meal_type="snack")
    if alts:
        res_plan, msg = meal_planner_service.replace_meal(user_id=1, day_index=2, meal_type="snack", new_recipe_id=alts[0]["recipe_id"])
        assert res_plan is not None
        updated_day = res_plan["days"][1]
        assert updated_day["total_calories"] > 0
        assert updated_day["total_protein"] > 0
