# Tastio Comprehensive Security Testing Framework (Module D)

Enterprise security testing and vulnerability assessment framework for the **Tastio Recipe Recommendation System**, covering **300 distinct security scenarios** (`SEC-001` through `SEC-300`) across SAST, DAST, dependency analysis, and API access controls.

---

## 1. Directory Structure

```text
security-tests/
├── config/
│   └── security-config.js             # Base URLs, paths, and severity definitions
├── reports/
│   ├── bandit-report.json             # Raw Bandit SAST static analysis output
│   ├── dependency-report.md           # Python & NPM dependency CVE evaluation
│   ├── dynamic-findings.json          # Raw dynamic probe observation output
│   ├── endpoint-inventory.xlsx        # 52 endpoints with auth, CSRF & IDOR audit
│   ├── executive-summary.md           # Executive threat assessment & risk scores
│   ├── findings.xlsx                  # Granular vulnerability catalog (9 findings)
│   ├── npm-audit-report.json          # Raw npm audit JSON output for mobile-app
│   ├── pip-audit-report.json          # Raw pip-audit JSON output for backend
│   ├── security-review.md             # 15-domain comprehensive security audit
│   └── security-test-report.xlsx      # Master 5-Worksheet Enterprise Excel Report
├── scanners/
│   └── api_security_scanner.py        # Dynamic HTTP security auditor for live API
├── scripts/
│   ├── generate-all-security-reports.js # Master Excel & Markdown report generator
│   └── verify-excel-report.js         # Schema validation & 300 test case audit
├── utils/
│   └── sec-registry.js                # Master catalog of 300 SEC test scenarios
├── package.json
└── README.md
```

---

## 2. Security Assessment Summary

- **Total Security Scenarios**: **300** (`SEC-001` to `SEC-300`)
- **Passed Scenarios (Hardened)**: **213** (Zero SQLi, Zero XSS, Strong Password Hashing, Safe Deserialization)
- **Failed Scenarios (Vulnerabilities)**: **87** (Mapped to 9 confirmed security findings)
- **Blocked / Not Executed**: **0** (All 300 scenarios audited and cataloged)
- **Security Compliance Rate**: **71.00%**

### Confirmed Findings Breakdown
- **0 Critical Vulnerabilities**
- **4 High Severity Vulnerabilities**:
  1. Missing CSRF Protection on Web Forms (`DEF-001` / CWE-352)
  2. BOLA / IDOR Authorization Bypass on `/api/meal-plan/current`, `/api/grocery-list`, `/api/profile` (`DEF-002` / CWE-639)
  3. Flask Debug Mode Enabled on Public Interface in `app.py:1199` (Bandit B201 / CWE-215)
  4. Vulnerable Dependencies in Mobile App Stack (`zod`, `node-forge`) (CWE-1395)
- **3 Medium Severity Vulnerabilities**:
  5. In-Memory Rate Limiting Storage Bottleneck (`DEF-003` / CWE-770)
  6. Missing Modern HTTP Security Headers (HSTS, CSP, X-Frame-Options) (CWE-693)
  7. Insecure Session Cookie Flags (Missing `HttpOnly`, `SameSite`) (CWE-1004)
- **2 Low Severity Vulnerabilities**:
  8. Insecure PRNG in Security Context (`random.sample`) (Bandit B311 / CWE-330)
  9. Server Framework Banner Disclosure (`Werkzeug/3.1.8 Python/3.13.2`) (CWE-200)

---

## 3. Execution Commands

### Prerequisites
Ensure the local Flask backend is active on `http://127.0.0.1:5000`:
```powershell
python d:\recipie\Recipe-Recommendation\backend\app.py
```

### 1. Run Dynamic API Security Probes
```powershell
cd d:\recipie\Recipe-Recommendation\security-tests
python scanners/api_security_scanner.py
```

### 2. Run Bandit Python Static SAST Scan
```powershell
python -m bandit -r d:\recipie\Recipe-Recommendation\backend -f json -o reports/bandit-report.json
```

### 3. Run Mobile NPM Dependency Audit
```powershell
cd d:\recipie\Recipe-Recommendation\mobile-app
npm.cmd audit
```

### 4. Run Python Backend Dependency Scan
```powershell
python -m pip_audit --local -f json -o d:\recipie\Recipe-Recommendation\security-tests\reports\pip-audit-report.json
```

### 5. Generate All Excel Reports & Artifacts
```powershell
cd d:\recipie\Recipe-Recommendation\security-tests
node scripts/generate-all-security-reports.js
```

### 6. Verify Excel Report Schema & Catalog
```powershell
cd d:\recipie\Recipe-Recommendation\security-tests
node scripts/verify-excel-report.js
```

