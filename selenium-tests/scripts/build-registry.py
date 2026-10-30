# -*- coding: utf-8 -*-
"""
Parses Module A (WEB-001 to WEB-300) from TESTING-PLAN.md
and outputs test-registry.js for the Selenium E2E suite.
"""
import re
import json

PLAN_PATH = r"d:\recipie\Recipe-Recommendation\TESTING-PLAN.md"
OUT_PATH = r"d:\recipie\Recipe-Recommendation\selenium-tests\utils\test-registry.js"

def parse_module_a():
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Find Section 5 table
    sec5_start = text.find("## 5. Module A: Selenium End-to-End Testing")
    sec6_start = text.find("## 6. Module B: Appium End-to-End Testing")
    sec5_text = text[sec5_start:sec6_start]

    test_cases = []
    lines = sec5_text.splitlines()

    module_map = {
        (1, 35): ("Authentication & Session Management", "Critical", "Blocker"),
        (36, 65): ("Landing Page & Navigation", "High", "Major"),
        (66, 105): ("Recipe Discovery & Multi-Param Filter Matrix", "High", "Major"),
        (106, 135): ("AI Vector & Keyword Search", "High", "Critical"),
        (136, 165): ("Pantry Ingredient Intersection ('What Can I Cook')", "High", "Major"),
        (166, 195): ("Recipe Detail Modal & Servings Scaler", "Critical", "Major"),
        (196, 235): ("7-Day AI Meal Plan Grid & Slot Swapping", "Critical", "Critical"),
        (236, 265): ("Categorized Smart Grocery List & Compilation", "Critical", "Critical"),
        (266, 280): ("AI Nutrition Coach Web Chat Assistant", "High", "Major"),
        (281, 290): ("Food Scanner Drag-and-Drop Vision Analysis", "Medium", "Minor"),
        (291, 296): ("User Profile Biometrics & Analytics", "High", "Major"),
        (297, 300): ("Accessibility, Responsive Viewports & Layout", "Medium", "Minor")
    }

    def get_meta(num):
        for (start, end), (mod, pri, sev) in module_map.items():
            if start <= num <= end:
                return mod, pri, sev
        return "Core Features", "Medium", "Major"

    for line in lines:
        line_clean = line.strip()
        if not line_clean.startswith("|"):
            continue
        parts = [p.strip() for p in line_clean.split("|")]
        # parts[0] is empty, parts[1] is `WEB-xxx`, parts[2] is scenario, parts[3] is category, parts[4] is input/steps, parts[5] is expected
        if len(parts) >= 6:
            raw_id = parts[1].replace("`", "").strip()
            if re.match(r"^WEB-\d{3}$", raw_id):
                test_num = int(raw_id.split("-")[1])
                scenario = parts[2]
                category = parts[3]
                steps = parts[4]
                expected = parts[5]

                mod_name, priority, severity = get_meta(test_num)

                # Precondition mapping
                if test_num <= 35:
                    precond = "Tastio web app running at baseUrl; user unauthenticated"
                elif 36 <= test_num <= 65:
                    precond = "Tastio web app loaded at baseUrl in browser"
                elif 66 <= test_num <= 105:
                    precond = "Recipes catalog loaded; filter bar rendered"
                elif 106 <= test_num <= 135:
                    precond = "BERT embedding service and keyword search engine initialized"
                elif 136 <= test_num <= 165:
                    precond = "Pantry search pane active with 230 recipes indexed"
                elif 166 <= test_num <= 195:
                    precond = "Recipe card displayed on page; modal accessible"
                elif 196 <= test_num <= 235:
                    precond = "User authenticated; 7-Day meal plan initialized"
                elif 236 <= test_num <= 265:
                    precond = "User authenticated; Smart Grocery list accessible"
                elif 266 <= test_num <= 280:
                    precond = "AI Coach service active at /coach"
                elif 281 <= test_num <= 290:
                    precond = "Food Scanner page loaded at /scanner"
                elif 291 <= test_num <= 296:
                    precond = "User profile exists in database at /profile"
                else:
                    precond = "Browser viewport configured according to test spec"

                test_cases.append({
                    "testId": raw_id,
                    "module": mod_name,
                    "testScenario": scenario,
                    "category": category,
                    "preconditions": precond,
                    "testSteps": steps,
                    "testData": f"Input: {steps[:40]}..." if len(steps) > 40 else steps,
                    "expectedResult": expected,
                    "actualResult": "Not Executed",
                    "status": "Not Executed",
                    "priority": priority,
                    "severity": severity,
                    "executionDate": None,
                    "defectReference": "DEF-001" if "CSRF" in steps or "CSRF" in expected else ("DEF-006" if "data-testid" in steps else "")
                })

    print(f"Extracted {len(test_cases)} test cases from TESTING-PLAN.md")
    assert len(test_cases) == 300, f"Expected 300 test cases, got {len(test_cases)}"

    # Generate test-registry.js
    js_content = """// test-registry.js - Master Registry of All 300 Distinct Test Cases (WEB-001 to WEB-300)
// Generated from TESTING-PLAN.md specification

class TestRegistry {
  constructor() {
    this.testCases = %s;
  }

  getAll() {
    return this.testCases;
  }

  getById(testId) {
    return this.testCases.find(tc => tc.testId === testId);
  }

  updateResult(testId, status, actualResult, defectRef = '') {
    const tc = this.getById(testId);
    if (tc) {
      tc.status = status; // 'Passed', 'Failed', 'Blocked', 'Not Executed'
      tc.actualResult = actualResult;
      tc.executionDate = new Date().toISOString();
      if (defectRef) {
        tc.defectReference = defectRef;
      }
    }
  }

  getSummary() {
    const total = this.testCases.length;
    const passed = this.testCases.filter(tc => tc.status === 'Passed').length;
    const failed = this.testCases.filter(tc => tc.status === 'Failed').length;
    const blocked = this.testCases.filter(tc => tc.status === 'Blocked').length;
    const notExecuted = this.testCases.filter(tc => tc.status === 'Not Executed').length;
    const passPercentage = total > 0 ? ((passed / total) * 100).toFixed(2) : 0;

    return {
      totalTestCases: total,
      passed,
      failed,
      blocked,
      notExecuted,
      passPercentage: `${passPercentage}%%`,
      executionDuration: '0s'
    };
  }
}

// Export singleton instance
const registryInstance = new TestRegistry();
module.exports = registryInstance;
""" % json.dumps(test_cases, indent=2)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"Successfully wrote {OUT_PATH} with 300 test cases.")

if __name__ == "__main__":
    parse_module_a()

