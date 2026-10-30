# Tastio Recipe Recommendation System - Selenium E2E Automation Framework

## Overview
This directory contains the enterprise Selenium WebDriver end-to-end (E2E) testing suite for the Tastio Recipe Recommendation System web frontend. It implements **300 distinct, meaningful test scenarios (`WEB-001` through `WEB-300`)** covering authentication, recipe discovery, AI vector and pantry search, servings scaling, 7-day meal planning, categorized smart grocery lists, AI nutrition coach chat, vision food scanning, profile biometrics, and WCAG accessibility.

---

## Directory Structure

```
selenium-tests/
├── package.json                    # Node.js dependencies, scripts, and test triggers
├── README.md                       # Comprehensive setup and troubleshooting guide
├── .env.example                    # Environment variable template
├── .mocharc.json                   # Mocha BDD test runner configuration
├── config/
│   └── test-config.js              # Centralized environment and timeout settings
├── pageobjects/
│   ├── base-page.js                # Core driver interactions and safe waits
│   ├── login-modal.js              # Authentication modal interactions
│   ├── signup-modal.js             # User registration modal interactions
│   ├── home-search-page.js         # Landing page, catalog and search panes
│   ├── recipe-detail-modal.js      # Modal hero, servings scaler, actions
│   ├── meal-plan-page.js           # 7-day plan, meal slots, authentic images
│   ├── grocery-page.js             # Categorized checklist, checkboxes, clear
│   ├── coach-page.js               # AI Nutrition Coach chat stream and chips
│   ├── scanner-page.js             # Food recognition dropzone and file upload
│   └── profile-page.js             # Biometrics, Mifflin-St Jeor calculations
├── tests/
│   ├── login-tests.js              # WEB-001 to WEB-035 (Preserved Required File)
│   ├── landing-navigation-tests.js # WEB-036 to WEB-065
│   ├── discovery-search-tests.js   # WEB-066 to WEB-105
│   ├── ai-search-tests.js          # WEB-106 to WEB-135
│   ├── pantry-what-can-i-cook-tests.js # WEB-136 to WEB-165
│   ├── recipe-details-tests.js     # WEB-166 to WEB-195
│   ├── meal-plan-tests.js          # WEB-196 to WEB-235 (Includes Recipe Images)
│   ├── grocery-list-tests.js       # WEB-236 to WEB-265 (Includes Grocery Sync)
│   ├── coach-chat-tests.js         # WEB-266 to WEB-280
│   └── scanner-profile-accessibility-tests.js # WEB-281 to WEB-300
├── utils/
│   ├── driver-factory.js           # Chrome / Edge / Firefox headless driver builder
│   ├── wait-helper.js              # Explicit wait utilities and safe click/type
│   ├── screenshot-helper.js        # Failure screenshot capture and diagnostics
│   ├── excel-reporter.js           # Multi-sheet Excel report generator (ExcelJS)
│   └── test-registry.js            # In-memory test case repository (300 cases)
├── scripts/
│   ├── run-all-tests.js            # Automated test runner with report generation
│   ├── generate-excel-report.js    # Standalone Excel report builder
│   └── build-registry.py           # Syncs registry with TESTING-PLAN.md
└── reports/
    ├── selenium-test-report.xlsx   # 5-Worksheet Enterprise Excel Report
    └── screenshots/                # Failure screenshots
```

---

## Installation Commands

Ensure Node.js (v18+) and Google Chrome / Microsoft Edge are installed on the system.

```bash
# Navigate to the selenium-tests directory
cd selenium-tests

# Install all dependencies (Selenium WebDriver, Mocha, Chai, ExcelJS, Dotenv)
npm install
```

---

## Environment Variables

Copy `.env.example` to `.env` to customize settings:

| Variable | Default Value | Description |
|---|---|---|
| `TEST_BASE_URL` | `http://127.0.0.1:5000` | Target URL of the Tastio web frontend |
| `SELENIUM_BROWSER` | `chrome` | Browser engine (`chrome`, `edge`, `firefox`) |
| `HEADLESS_MODE` | `true` | Set to `false` for visible desktop browser window |
| `EXPLICIT_WAIT_TIMEOUT`| `10000` | Maximum wait timeout in milliseconds |
| `BROWSER_WIDTH` | `1920` | Viewport width in pixels |
| `BROWSER_HEIGHT` | `1080` | Viewport height in pixels |
| `TEST_USER_EMAIL` | `selenium_chef@test.local` | Test account email |
| `TEST_USER_PASSWORD` | `TestPass123!` | Test account password |
| `SCREENSHOT_ON_FAILURE`| `true` | Save viewport screenshots upon test failure |

---

## Local Execution Commands

```bash
# 1. Execute all 300 test scenarios and automatically generate Excel report
npm test

# 2. Run only the Authentication test suite (login-tests.js)
npm run test:login

# 3. Run the 7-Day AI Meal Plan suite (including recipe image validation)
npm run test:mealplan

# 4. Run the Smart Grocery List suite (including adding groceries from recipes)
npm run test:grocery

# 5. Run the Recipe Discovery and Filter suite
npm run test:discovery

# 6. Re-generate the Master Excel Report at any time
npm run generate:report
```

---

## Excel Report Specifications (`selenium-test-report.xlsx`)

The test harness compiles execution metrics into `selenium-tests/reports/selenium-test-report.xlsx` with five structured worksheets:

1. **Test Summary**:
   - High-level KPI summary cards: Total Test Cases (300), Passed, Failed, Blocked, Not Executed, Pass Percentage, Execution Duration.
   - Module compliance table breaking down results across all 12 functional areas.
2. **Test Case Details**:
   - Master catalog of all 300 unique test scenarios (`WEB-001` through `WEB-300`).
   - Columns: `Test ID`, `Module`, `Test Scenario`, `Preconditions`, `Test Steps`, `Test Data`, `Expected Result`, `Actual Result`, `Status`, `Priority`, `Severity`, `Execution Date`, `Defect Reference`.
   - Conditional color formatting (Green for Passed, Red for Failed, Amber for Blocked, Slate for Not Executed).
3. **Execution Results**:
   - Live execution log with timestamps, durations (ms), and diagnostic outputs.
4. **Failed Tests**:
   - Dedicated failure triage sheet with stack traces, screenshot references, and linked defect IDs.
5. **Defects**:
   - Detailed register of identified application defects (`DEF-001` through `DEF-006`) with severity, impact, reproduction steps, and remediation status.

---

## Troubleshooting & FAQ

### 1. `ElementClickInterceptedError: element click intercepted`
- **Cause**: Bootstrap sticky navigation bars, modals, or smooth scroll animations overlapping elements.
- **Solution**: The framework's `WaitHelper.safeClick()` automatically executes `scrollIntoView({block: 'center'})` followed by JavaScript click fallback `arguments[0].click()` if a native click is intercepted.

### 2. Chrome Version Mismatch
- **Cause**: Chrome browser auto-updated while ChromeDriver binary is older.
- **Solution**: Selenium WebDriver 4.x features native **Selenium Manager**, which automatically resolves and downloads the exact matching driver for your installed Chrome/Edge version. No manual `chromedriver` executable download is required.

### 3. Headless Viewport Layout
- **Cause**: Mobile hamburger navigation collapsing on smaller viewports.
- **Solution**: Headless mode explicitly launches with `--window-size=1920,1080` to render full desktop layouts. To test responsive mobile layouts specifically, use tests `WEB-297` through `WEB-300`.

