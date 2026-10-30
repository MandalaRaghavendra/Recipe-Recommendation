# Tastio Performance & 100 VU Load Testing Framework (k6)

Enterprise performance and concurrent stress-testing automation framework for the **Tastio Recipe Recommendation System**, built with **k6 v0.54.0** and **Node.js ExcelJS reporting**.

---

## 1. Overview & Architecture

This module implements **Module C** of the Tastio Testing Architecture Plan, covering **300 distinct performance scenarios** (`PERF-001` through `PERF-300`).

```text
performance-tests/
├── bin/
│   └── k6.exe                     # High-throughput Go/C++ load generator v0.54.0
├── config/
│   └── perf-config.js             # Base URL, SLA latency thresholds & VU curves
├── data/                          # Realistic workload data feeds
│   ├── coach_queries.json         # AI chatbot prompts & contexts
│   ├── ingredients.json           # Pantry sets for intersection testing
│   ├── meal_plans.json            # Caloric target & diet split profiles
│   ├── queries.json               # Full-text, cuisine & dietary filter permutations
│   ├── scanner_samples.json       # Vision engine benchmark payloads
│   └── users.json                 # 100 concurrent test user profiles
├── k6-scripts/                    # k6 JavaScript load test scripts
│   ├── 01-baseline-health.js      # PERF-001 to PERF-030 (30 scenarios)
│   ├── 02-catalog-concurrency.js  # PERF-031 to PERF-070 (40 scenarios)
│   ├── 03-vector-similarity.js    # PERF-071 to PERF-110 (40 scenarios)
│   ├── 04-pantry-intersection.js  # PERF-111 to PERF-145 (35 scenarios)
│   ├── 05-meal-plan-stress.js     # PERF-146 to PERF-185 (40 scenarios)
│   ├── 06-grocery-compilation.js  # PERF-186 to PERF-220 (35 scenarios)
│   ├── 07-coach-throughput.js     # PERF-221 to PERF-255 (35 scenarios)
│   ├── 08-vision-ingestion.js     # PERF-256 to PERF-280 (25 scenarios)
│   ├── 09-soak-spike-100vu.js     # PERF-281 to PERF-300 (20 scenarios)
│   └── master-100vu-load-suite.js # Comprehensive 100 VU 1-minute full suite
├── reports/
│   ├── k6-summary.json            # Machine-readable raw latency & percentile dump
│   └── perf-test-report.xlsx      # Master 5-Worksheet Enterprise Excel Report
├── scripts/
│   ├── generate-k6-suites.js      # Generator for modular k6 scripts
│   ├── generate-test-data.js      # Generator for data feeds
│   ├── generate-excel-report.js   # Standalone Excel report builder
│   ├── run-100vu-load-test.js     # Master execution orchestrator & threshold evaluator
│   └── verify-excel-report.js     # Schema and completeness validation script
└── utils/
    ├── excel-reporter.js          # ExcelJS workbook formatting engine
    └── perf-registry.js           # Master catalog of 300 PERF test scenarios
```

---

## 2. SLA Benchmarks & Latency Budgets

| Endpoint / Subsystem | Concurrency | Expected Throughput | $p_{50}$ Latency | $p_{95}$ SLA Target | $p_{99}$ Max | Error Budget |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`/api/health`** | 100 VUs | $\ge 250\text{ RPS}$ | $\le 10\text{ ms}$ | $\le 50\text{ ms}$ | $\le 85\text{ ms}$ | $0.0\%$ |
| **`/api/recipes` (Page 1 & Filter)** | 100 VUs | $\ge 150\text{ RPS}$ | $\le 65\text{ ms}$ | $\le 150\text{ ms}$ | $\le 250\text{ ms}$ | $< 0.1\%$ |
| **`/api/recommend` (AI Cosine)** | 100 VUs | $\ge 80\text{ RPS}$ | $\le 120\text{ ms}$ | $\le 300\text{ ms}$ | $\le 500\text{ ms}$ | $< 0.5\%$ |
| **`/api/pantry-match` (What Can I Cook)** | 100 VUs | $\ge 90\text{ RPS}$ | $\le 95\text{ ms}$ | $\le 250\text{ ms}$ | $\le 450\text{ ms}$ | $< 0.5\%$ |
| **`/api/meal-plan/current & swap`** | 100 VUs | $\ge 70\text{ RPS}$ | $\le 130\text{ ms}$ | $\le 350\text{ ms}$ | $\le 600\text{ ms}$ | $< 1.0\%$ |
| **`/api/grocery-list` Operations** | 100 VUs | $\ge 100\text{ RPS}$ | $\le 75\text{ ms}$ | $\le 200\text{ ms}$ | $\le 350\text{ ms}$ | $< 0.5\%$ |
| **`/api/coach/chat` (AI Stream)** | 50 VUs | $\ge 40\text{ RPS}$ | $\le 180\text{ ms}$ | $\le 450\text{ ms}$ | $\le 800\text{ ms}$ | $< 1.0\%$ |
| **`/api/vision/status`** | 50 VUs | $\ge 120\text{ RPS}$ | $\le 45\text{ ms}$ | $\le 180\text{ ms}$ | $\le 300\text{ ms}$ | $< 0.5\%$ |

---

## 3. Execution Commands

### Prerequisites
1. Ensure the Flask backend is running on `http://127.0.0.1:5000`:
   ```powershell
   python d:\recipie\Recipe-Recommendation\backend\app.py
   ```

### Run Full 100 VU 1-Minute Load Test Suite
```powershell
cd d:\recipie\Recipe-Recommendation\performance-tests
node scripts/run-100vu-load-test.js
```

### Run a Specific Modular Test with k6 Directly
```powershell
cd d:\recipie\Recipe-Recommendation\performance-tests
./bin/k6.exe run k6-scripts/01-baseline-health.js
./bin/k6.exe run k6-scripts/03-vector-similarity.js
./bin/k6.exe run k6-scripts/05-meal-plan-stress.js
```

### Verify Excel Report Schema & Catalog
```powershell
cd d:\recipie\Recipe-Recommendation\performance-tests
node scripts/verify-excel-report.js
```

---

## 4. Excel Report Structure

The generated report at `reports/perf-test-report.xlsx` contains 5 worksheets:
1. **`Test Summary`**: Executive metrics, RPS, percentiles ($p_{50}, p_{90}, p_{95}, p_{99}$), error rate, SLA status.
2. **`Test Case Details`**: Complete row-by-row tracking of all 300 PERF test cases (`PERF-001` to `PERF-300`) with thresholds and measured metrics.
3. **`Execution Results`**: Staged workload metrics (Warmup, Peak 100 VUs, Sustained, Rampdown).
4. **`Failed Tests`**: Root cause analysis and remediation suggestions for any breached thresholds.
5. **`Performance Metrics`**: Granular endpoint breakdown matrix with percentile latency distributions.

