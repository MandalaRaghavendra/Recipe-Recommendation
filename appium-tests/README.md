# Tastio Mobile E2E Automation Framework (Appium + Android)

Enterprise-grade mobile test automation framework targeting the **Tastio Recipe Recommendation & Nutrition System** React Native / Expo Android application (`com.mandalaraghavendra.tastio`).

---

## 1. Architecture & Technology Stack

| Component | Technology | Specification / Version |
| :--- | :--- | :--- |
| **Mobile OS Platform** | Android | API Level 30 – 34 (Android 11.0 to 14.0) |
| **Target App Package** | React Native / Expo SDK 57 | `com.mandalaraghavendra.tastio` (`MainActivity`) |
| **Automation Engine** | Appium 2.x | UiAutomator2 Driver (`appium-uiautomator2-driver`) |
| **Test Runner** | Mocha BDD | JavaScript ES6+ / Node.js 18+ |
| **Assertion Library** | Chai | `expect` BDD assertions |
| **Design Pattern** | Screen Object Model (SOM) | Decoupled screen element locators & user gestures |
| **Reporting Engine** | ExcelJS | Multi-worksheet XLSX report (`appium-test-report.xlsx`) |

---

## 2. Directory Structure

```text
appium-tests/
├── config/
│   └── mobile-config.js                  # Device caps, app package, activity & Appium endpoint
├── pageobjects/                          # Screen Object Model (SOM)
│   ├── base-screen.js                    # Generic gesture, scroll, tap & wait primitives
│   ├── app-root-screen.js                # Top status bar & 8 bottom navigation tabs
│   ├── auth-modal-screen.js              # Login, registration, credential validation & logout
│   ├── server-config-modal-screen.js     # Dynamic server IP, presets (WiFi, localhost, USB)
│   ├── home-screen.js                    # Recipe discovery feed, cuisine & diet filter chips
│   ├── search-screen.js                  # AI vector search & ingredient intersection inputs
│   ├── recipe-detail-modal-screen.js     # Servings scaler (0.5x–3x), grocery sync, review widget
│   ├── meal-plan-screen.js               # 7-day strip, meal slots (breakfast/lunch/snack/dinner)
│   ├── grocery-screen.js                 # 7 categories, compile from plan, custom item add modal
│   ├── scanner-screen.js                 # Camera/gallery dish recognition & nutritional grounding
│   ├── coach-screen.js                   # AI Nutrition Coach chat stream & quick prompts
│   ├── history-screen.js                 # Dietary analytics (today, week, month) & log stream
│   └── profile-screen.js                 # Metabolic metrics (BMR, TDEE, weight goals)
├── utils/
│   ├── appium-driver-factory.js          # W3C Appium 2.x session client & gesture dispatch
│   ├── device-helper.js                  # Probing ADB connected devices & Appium server
│   ├── test-registry.js                  # In-memory registry of all 300 MOB scenarios
│   └── excel-reporter.js                 # 5-worksheet Excel report generator
├── tests/                                # 10 Test Suites (MOB-001 through MOB-300)
│   ├── 01-lifecycle-launch-tests.js       # MOB-001 to MOB-030 (30 scenarios)
│   ├── 02-server-config-tests.js          # MOB-031 to MOB-055 (25 scenarios)
│   ├── 03-tab-navigation-tests.js         # MOB-056 to MOB-085 (30 scenarios)
│   ├── 04-home-discovery-tests.js         # MOB-086 to MOB-120 (35 scenarios)
│   ├── 05-search-filters-tests.js         # MOB-121 to MOB-155 (35 scenarios)
│   ├── 06-recipe-modal-servings-tests.js  # MOB-156 to MOB-190 (35 scenarios)
│   ├── 07-meal-plan-matrix-tests.js       # MOB-191 to MOB-230 (40 scenarios)
│   ├── 08-grocery-checklist-tests.js      # MOB-231 to MOB-265 (35 scenarios)
│   ├── 09-scanner-camera-tests.js         # MOB-266 to MOB-285 (20 scenarios)
│   └── 10-coach-profile-tests.js          # MOB-286 to MOB-300 (15 scenarios)
├── scripts/
│   ├── run-all-mobile-tests.js           # Master test runner with automated device probe
│   ├── generate-excel-report.js          # Standalone report generator
│   └── verify-excel-report.js            # Integrity audit of 300 test IDs and worksheets
├── reports/
│   └── appium-test-report.xlsx           # 5-sheet Master Excel Report
├── package.json
└── README.md
```

---

## 3. Test Suites & Coverage Scope (300 Scenarios)

| Suite File | ID Range | Scenarios | Functional Scope |
| :--- | :--- | :---: | :--- |
| `01-lifecycle-launch-tests.js` | **MOB-001 to MOB-030** | 30 | Clean APK install, cold/warm start, back key, offline airplane mode, OS permissions |
| `02-server-config-tests.js` | **MOB-031 to MOB-055** | 25 | Server config modal, custom IP input, test connection, WiFi/Localhost/USB presets |
| `03-tab-navigation-tests.js` | **MOB-056 to MOB-085** | 30 | 8-tab bottom bar, horizontal swipe, active indicator, state preservation across tab switches |
| `04-home-discovery-tests.js` | **MOB-086 to MOB-120** | 35 | Recipe cards, health scores, calorie tags, cuisine chips, pull-to-refresh |
| `05-search-filters-tests.js` | **MOB-121 to MOB-155** | 35 | AI keyword search, pantry ingredient matching, filter matrix (veg/non-veg, calories) |
| `06-recipe-modal-servings-tests.js` | **MOB-156 to MOB-190** | 35 | Servings multiplier (0.5x, 1x, 1.5x, 2x, 3x), add to grocery, star rating & reviews |
| `07-meal-plan-matrix-tests.js` | **MOB-191 to MOB-230** | 40 | 7-day pill strip, slot cards (breakfast/lunch/snack/dinner), meal swap modal, regenerate |
| `08-grocery-checklist-tests.js` | **MOB-231 to MOB-265** | 35 | 7 category grouping, compile from 7-day plan, custom item addition, checklist checkboxes |
| `09-scanner-camera-tests.js` | **MOB-266 to MOB-285** | 20 | ImagePicker camera/gallery trigger, sample dish chips (Biryani, Dosa), recognition card |
| `10-coach-profile-tests.js` | **MOB-286 to MOB-300** | 15 | AI Nutrition Coach chat stream, quick prompt chips, metabolic BMR/TDEE calculation, WCAG AA |

---

## 4. Setup & Execution Guide

### Prerequisites
1. **Android SDK & ADB**: Ensure `adb` is in your `PATH` (e.g. `%LOCALAPPDATA%\Android\Sdk\platform-tools`).
2. **Appium 2.x**: Install Appium and the UiAutomator2 driver:
   ```powershell
   npm install -g appium
   appium driver install uiautomator2
   ```

### Step 1: Start the Backend Server
Ensure the Python Flask backend is running on `http://127.0.0.1:5000`:
```powershell
python backend/app.py
```

### Step 2: Connect an Android Device or Launch Emulator
- **Physical Device**: Connect phone via USB with **USB Debugging** enabled.
- **Android Virtual Device (AVD)**: Launch an emulator from Android Studio.
- Verify connected device:
  ```powershell
  adb devices
  ```
- Forward backend port 5000 so the mobile device can reach your computer's local backend:
  ```powershell
  adb reverse tcp:5000 tcp:5000
  ```

### Step 3: Start Appium Server
Open a dedicated terminal and start Appium:
```powershell
appium --port 4723 --relaxed-security
```

### Step 4: Run the Mobile Test Suite
In another terminal, navigate to `appium-tests` and run:
```powershell
cd D:\recipie\Recipe-Recommendation\appium-tests
node scripts/run-all-mobile-tests.js
```

### Step 5: Verify the Excel Report
To inspect and verify all 5 worksheets in the generated report:
```powershell
node scripts/verify-excel-report.js
```

---

## 5. Report Verification & Quality Assurance

The generated Excel workbook at `reports/appium-test-report.xlsx` contains 5 worksheets:
1. **Test Summary**: Total Scenarios (300), Passed, Failed, Blocked, Not Executed, Pass Percentage, Execution Duration.
2. **Test Case Details**: All 300 scenarios with exact columns:
   `Test ID | Module | Test Scenario | Preconditions | Test Steps | Test Data | Expected Result | Actual Result | Status | Priority | Severity | Execution Date | Defect Reference`.
3. **Execution Results**: Logged live test runs and environment probe assertions.
4. **Failed Tests**: Detailed failure traces and root cause taxonomy.
5. **Defects**: Known defect traceability cataloged during test design.

