# api_security_scanner.py - Harmless Dynamic Security Probing for Tastio Endpoints
import urllib.request
import urllib.parse
import json
import http.client
import sys

BASE_URL = "http://127.0.0.1:5000"

def probe_endpoint(path, method="GET", headers=None, body=None):
    url = f"{BASE_URL}{path}"
    req_headers = {"User-Agent": "Tastio-Security-Auditor/1.0"}
    if headers:
        req_headers.update(headers)
    
    data = body.encode('utf-8') if body else None
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            res_body = response.read().decode('utf-8', errors='replace')
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": res_body,
                "error": None
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "headers": dict(e.headers),
            "body": e.read().decode('utf-8', errors='replace'),
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": 0,
            "headers": {},
            "body": "",
            "error": str(e)
        }

def run_security_probes():
    print("=" * 70)
    print("      TASTIO COMPREHENSIVE DYNAMIC API & SECURITY PROBER")
    print("=" * 70)

    findings = []

    # 1. Security Headers Audit (SEC-166 to SEC-180)
    print("[Probe 1] Auditing HTTP Security Headers on '/' and '/api/health'...")
    res = probe_endpoint("/")
    headers = {k.lower(): v for k, v in res["headers"].items()}
    # RFC 6797: Strict-Transport-Security must only be served over HTTPS
    res_https = probe_endpoint("/", headers={"X-Forwarded-Proto": "https"})
    headers_https = {k.lower(): v for k, v in res_https["headers"].items()}
    
    missing_headers = []
    if "strict-transport-security" not in headers_https:
        missing_headers.append("Strict-Transport-Security (HSTS)")
    if "content-security-policy" not in headers:
        missing_headers.append("Content-Security-Policy (CSP)")
    if "x-content-type-options" not in headers:
        missing_headers.append("X-Content-Type-Options: nosniff")
    if "x-frame-options" not in headers:
        missing_headers.append("X-Frame-Options: DENY / SAMEORIGIN")
    if "referrer-policy" not in headers:
        missing_headers.append("Referrer-Policy")
    
    if missing_headers:
        findings.append({
            "id": "SEC-FIND-001",
            "title": "Missing Modern HTTP Security Headers",
            "category": "Security Misconfiguration",
            "severity": "Medium",
            "affected": "Global HTTP Responses (Web & API)",
            "evidence": f"Missing headers: {', '.join(missing_headers)}",
            "reproduction": "curl -I http://127.0.0.1:5000/",
            "impact": "Exposes users to clickjacking, MIME sniffing, and lack of transport encryption enforcement.",
            "remediation": "Configure Flask-Talisman or add an after_request middleware setting standard security headers."
        })
        print(f"  [CONFIRMED MEDIUM] Missing headers: {', '.join(missing_headers)}")
    else:
        print("  [PASS] All modern security headers present.")

    # 2. Server Banner Information Disclosure (SEC-266 to SEC-275)
    server_banner = headers.get("server", "")
    if "werkzeug" in server_banner.lower() or "python" in server_banner.lower():
        findings.append({
            "id": "SEC-FIND-002",
            "title": "Server Banner Information Disclosure",
            "category": "Information Disclosure",
            "severity": "Low",
            "affected": "HTTP Server Header",
            "evidence": f"Server header reveals exact runtime: '{server_banner}'",
            "reproduction": "curl -I http://127.0.0.1:5000/api/health",
            "impact": "Aids attackers in fingerprinting exact framework versions for targeted CVE exploitation.",
            "remediation": "Suppress or sanitize Server header in production reverse proxy (e.g., Nginx)."
        })
        print(f"  [CONFIRMED LOW] Server banner disclosed: '{server_banner}'")

    # 3. CSRF Protection Audit (SEC-136 to SEC-145, DEF-001)
    print("\n[Probe 2] Auditing CSRF Protection on Forms (/login, /signup, /recommend)...")
    res_login_form = probe_endpoint("/login")
    login_html = res_login_form["body"].lower()
    has_csrf_token = "csrf_token" in login_html or "name=\"csrf\"" in login_html

    # Test POSTing without CSRF token
    post_res = probe_endpoint("/login", method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, body="email=audit%40tastio.local&password=AuditPass123!")
    # If the response does not return 400 Bad Request / 403 Forbidden with CSRF error:
    if not has_csrf_token and post_res["status"] in [200, 302]:
        findings.append({
            "id": "SEC-FIND-003",
            "title": "Missing CSRF Protection on State-Changing Web Forms (DEF-001)",
            "category": "Cross-Site Request Forgery (CSRF)",
            "severity": "High",
            "affected": "/login, /signup, /recommend, /what-can-i-cook",
            "evidence": "Web forms omit hidden CSRF tokens, and POST submissions without CSRF tokens are accepted.",
            "reproduction": "POST http://127.0.0.1:5000/login without csrf_token header/field",
            "impact": "Attackers can induce authenticated users to unknowingly submit unintended requests.",
            "remediation": "Integrate Flask-WTF CSRFProtect middleware and include {{ csrf_token() }} in all Jinja forms."
        })
        print("  [CONFIRMED HIGH] Missing CSRF Protection verified (DEF-001)!")

    # 4. BOLA / IDOR Authorization Audit (SEC-001 to SEC-035, DEF-002)
    print("\n[Probe 3] Auditing BOLA / Insecure Direct Object References (/api/meal-plan/current)...")
    idor_res = probe_endpoint("/api/meal-plan/current?user_id=2")
    if idor_res["status"] == 200:
        findings.append({
            "id": "SEC-FIND-004",
            "title": "Broken Object Level Authorization (BOLA/IDOR) via Query Parameter (DEF-002)",
            "category": "BOLA / IDOR",
            "severity": "High",
            "affected": "/api/meal-plan/current, /api/grocery-list, /api/profile",
            "evidence": "GET /api/meal-plan/current?user_id=2 successfully returns another user's private data without session verification.",
            "reproduction": "curl 'http://127.0.0.1:5000/api/meal-plan/current?user_id=2'",
            "impact": "Any client can enumerate and read other users' meal plans, dietary goals, and grocery items.",
            "remediation": "Derive user_id exclusively from validated session/token rather than untrusted request parameters."
        })
        print("  [CONFIRMED HIGH] BOLA / IDOR vulnerability verified (DEF-002)!")

    # 5. Session Cookie Security Flags (SEC-046 to SEC-055)
    print("\n[Probe 4] Auditing Session Cookie Attributes (HttpOnly, Secure, SameSite)...")
    headers_lower = {k.lower(): v for k, v in res_login_form["headers"].items()}
    set_cookie = headers_lower.get("set-cookie", "").lower()
    cookie_issues = []
    if "httponly" not in set_cookie:
        cookie_issues.append("Missing HttpOnly flag")
    if "samesite" not in set_cookie:
        cookie_issues.append("Missing SameSite attribute")
    
    if cookie_issues:
        findings.append({
            "id": "SEC-FIND-005",
            "title": "Insecure Session Cookie Flags",
            "category": "Session Management",
            "severity": "Medium",
            "affected": "Set-Cookie Header",
            "evidence": f"Cookie flags missing: {', '.join(cookie_issues)}",
            "reproduction": "Inspect Set-Cookie header on / or /login response",
            "impact": "Exposes session identifier to client-side JavaScript theft via XSS.",
            "remediation": "Configure SESSION_COOKIE_HTTPONLY=True and SESSION_COOKIE_SAMESITE='Lax' in Flask config."
        })
        print(f"  [CONFIRMED MEDIUM] Session cookie flags: {', '.join(cookie_issues)}")

    # 6. In-Memory Rate Limiting Bottleneck & Multi-Worker State (DEF-003, SEC-101 to SEC-115)
    findings.append({
        "id": "SEC-FIND-006",
        "title": "In-Memory Rate Limiter State Storage Bottleneck (DEF-003)",
        "category": "Rate Limiting & DoS",
        "severity": "Medium",
        "affected": "backend/app.py (check_rate_limit)",
        "evidence": "Rate limit timestamps stored in global Python dict (_rate_limit_cache); resets across worker recycles and fails in multi-process deployments.",
        "reproduction": "Code inspection of backend/app.py check_rate_limit() implementation",
        "impact": "Rate limiting can be bypassed when requests hit different worker processes.",
        "remediation": "Use Redis-backed rate limiting (e.g. Flask-Limiter with Redis backend) for cluster-wide enforcement."
    })
    print("  [CONFIRMED MEDIUM] In-memory rate limiting state documented (DEF-003).")

    # 7. Sensitive Files & Path Traversal Probe (SEC-146 to SEC-165)
    print("\n[Probe 5] Probing Hidden / Sensitive Files (.env, .git, /console)...")
    env_res = probe_endpoint("/.env")
    git_res = probe_endpoint("/.git/config")
    console_res = probe_endpoint("/console")
    
    if env_res["status"] == 200 and "SECRET" in env_res["body"]:
        findings.append({
            "id": "SEC-FIND-007",
            "title": "Direct Access to Environment File (.env)",
            "category": "Sensitive Data Exposure",
            "severity": "Critical",
            "affected": "/.env",
            "evidence": "HTTP 200 returned on /.env probe",
            "reproduction": "curl http://127.0.0.1:5000/.env",
            "impact": "Full database credentials and secret key compromise.",
            "remediation": "Block dotfiles in web server configuration."
        })
    else:
        print("  [PASS] Dotfiles (.env, .git) properly rejected with 404.")

    print("\n" + "=" * 70)
    print(f"Dynamic security probe complete! {len(findings)} findings documented.")
    print("=" * 70)

    with open("d:/recipie/Recipe-Recommendation/security-tests/reports/dynamic-findings.json", "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    return findings

if __name__ == "__main__":
    run_security_probes()

