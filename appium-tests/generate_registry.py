import re
import json
import os

plan_path = r"D:\recipie\Recipe-Recommendation\TESTING-PLAN.md"
out_path = r"D:\recipie\Recipe-Recommendation\appium-tests\utils\test-registry.js"

groups = [
    (1, 30, "App Lifecycle & Launch"),
    (31, 55, "Server Configuration & Network Management"),
    (56, 85, "Bottom Tab Navigation & State Preservation"),
    (86, 120, "Home Screen Discovery & Recipe Feed"),
    (121, 155, "Search & Multi-Param Filtering"),
    (156, 190, "Recipe Detail Modal & Servings Scaler"),
    (191, 230, "7-Day AI Meal Plan Matrix & Slot Swapping"),
    (231, 265, "Smart Grocery List & Categorized Checklist"),
    (266, 285, "Food Scanner & Image Recognition"),
    (286, 300, "AI Nutrition Coach, Profile & Accessibility")
]

def get_module(num):
    for start, end, name in groups:
        if start <= num <= end:
            return name
    return "Mobile E2E Testing"

test_cases = []

with open(plan_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('|') and re.search(r'MOB-\d{3}', line):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5 and re.search(r'MOB-\d{3}', parts[0]):
                m = re.search(r'MOB-(\d{3})', parts[0])
                test_id = m.group(0)
                num = int(m.group(1))
                scenario = parts[1].replace('`', '')
                category = parts[2].replace('`', '')
                steps = parts[3].replace('`', '')
                expected = parts[4].replace('`', '')

                # Determine priority and severity
                if num <= 30 or (56 <= num <= 70) or (156 <= num <= 170):
                    priority = "Critical"
                    severity = "Blocker"
                elif (31 <= num <= 55) or (86 <= num <= 120) or (191 <= num <= 210) or (231 <= num <= 245):
                    priority = "High"
                    severity = "Critical"
                elif (121 <= num <= 155) or (211 <= num <= 230) or (266 <= num <= 285):
                    priority = "Medium"
                    severity = "Major"
                else:
                    priority = "Low"
                    severity = "Normal"

                test_cases.append({
                    "testId": test_id,
                    "module": get_module(num),
                    "testScenario": scenario,
                    "category": category,
                    "preconditions": f"Tastio Android App (com.mandalaraghavendra.tastio) deployed; Appium server ready",
                    "testSteps": steps,
                    "testData": f"Input: {steps[:40]}...",
                    "expectedResult": expected,
                    "actualResult": "Not Executed",
                    "status": "Not Executed",
                    "priority": priority,
                    "severity": severity,
                    "executionDate": None,
                    "defectReference": ""
                })

print(f"Extracted {len(test_cases)} MOB test scenarios.")

os.makedirs(os.path.dirname(out_path), exist_ok=True)

js_content = f"""// test-registry.js - Master Registry of All 300 Distinct Android Mobile Test Cases (MOB-001 to MOB-300)
// Extracted from TESTING-PLAN.md specification

class TestRegistry {{
  constructor() {{
    this.testCases = {json.dumps(test_cases, indent=2)};
  }}

  getAll() {{
    return this.testCases;
  }}

  getById(testId) {{
    return this.testCases.find(tc => tc.testId === testId);
  }}

  updateResult(testId, status, actualResult, defectRef = '') {{
    const tc = this.getById(testId);
    if (tc) {{
      tc.status = status; // 'Passed', 'Failed', 'Blocked', 'Not Executed'
      tc.actualResult = actualResult;
      tc.executionDate = new Date().toISOString();
      if (defectRef) {{
        tc.defectReference = defectRef;
      }}
    }}
  }}

  markAllBlocked(reason = 'Android device / emulator or Appium server unavailable') {{
    this.testCases.forEach(tc => {{
      if (tc.status === 'Not Executed') {{
        tc.status = 'Blocked';
        tc.actualResult = reason;
        tc.executionDate = new Date().toISOString();
      }}
    }});
  }}

  getSummary() {{
    const total = this.testCases.length;
    const passed = this.testCases.filter(tc => tc.status === 'Passed').length;
    const failed = this.testCases.filter(tc => tc.status === 'Failed').length;
    const blocked = this.testCases.filter(tc => tc.status === 'Blocked').length;
    const notExecuted = this.testCases.filter(tc => tc.status === 'Not Executed').length;
    const passPercentage = total > 0 ? ((passed / total) * 100).toFixed(2) : 0;

    return {{
      totalTestCases: total,
      passed,
      failed,
      blocked,
      notExecuted,
      passPercentage: `${{passPercentage}}%`,
      executionDuration: '0s'
    }};
  }}
}}

// Export singleton instance
const registryInstance = new TestRegistry();
module.exports = registryInstance;
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Master test-registry.js created at {out_path} with {len(test_cases)} cases.")

