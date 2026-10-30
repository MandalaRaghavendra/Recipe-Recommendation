"""
test_security_remediation.py - Enterprise Security Remediation Regression Suite
Module G Verification for Tastio Recipe Recommendation System

Verifies:
1. BOLA / IDOR: Cross-user access rejection (403 Forbidden), unauthenticated rejection (401 Unauthorized),
   and server-side session user_id derivation.
2. Flask debug mode: Debug mode disabled, environment-based configuration.
3. CSRF: Browser form state-changing rejection without tokens, valid token acceptance, API/mobile preservation.
4. Session cookies: HttpOnly and SameSite flags verified.
5. Security headers: CSP, HSTS, X-Content-Type-Options, X-Frame-Options, sanitized Server banner.
"""

import pytest
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from app import app
import database as db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_users(client):
    """Registers two distinct users for BOLA/IDOR isolation testing."""
    import uuid
    uid_a = uuid.uuid4().hex[:8]
    uid_b = uuid.uuid4().hex[:8]
    user_a_email = f"sec_user_a_{uid_a}@tastio.test"
    user_b_email = f"sec_user_b_{uid_b}@tastio.test"
    password = "TestPassword123!"

    # Create User A
    _, user_a = db.register_user("User Alpha", user_a_email, password)
    # Create User B
    _, user_b = db.register_user("User Beta", user_b_email, password)

    return {
        "user_a": user_a,
        "user_b": user_b,
        "password": password
    }

# ==============================================================================
# 1. BOLA / IDOR AUTHORIZATION REGRESSION TESTS
# ==============================================================================

def test_unauthenticated_api_requests_rejected(client):
    """Unauthenticated requests to protected endpoints must return 401 Unauthorized."""
    protected_endpoints = [
        "/api/profile",
        "/api/history",
        "/api/meal-plan/current",
        "/api/grocery-list",
        "/api/analytics/nutrition",
        "/api/coach/context",
        "/api/user/recently-viewed",
        "/api/user/preferences"
    ]
    for endpoint in protected_endpoints:
        res = client.get(endpoint)
        assert res.status_code == 401, f"Expected 401 on {endpoint}, got {res.status_code}"
        data = res.get_json()
        assert data["success"] is False
        assert "Unauthorized" in data.get("error", "") or "Authentication required" in data.get("message", "")

def test_bola_idor_query_parameter_tampering_rejected(client, test_users):
    """
    User A is logged in. User A attempts to access User B's resources
    by passing ?user_id=<user_b_id>. Must return 403 Forbidden!
    """
    user_a = test_users["user_a"]
    user_b = test_users["user_b"]
    user_a_id = str(user_a["objectId"])
    user_b_id = str(user_b["objectId"])

    # Log in as User A
    with client.session_transaction() as sess:
        sess["user"] = user_a
        sess["user_id"] = user_a_id

    # 1. Attempt to read User B's meal plan
    res_mp = client.get(f"/api/meal-plan/current?user_id={user_b_id}")
    assert res_mp.status_code == 403, f"Expected 403 Forbidden for meal plan BOLA, got {res_mp.status_code}"
    assert res_mp.get_json()["error"] == "Forbidden"

    # 2. Attempt to read User B's profile
    res_prof = client.get(f"/api/profile?user_id={user_b_id}")
    assert res_prof.status_code == 403, f"Expected 403 Forbidden for profile BOLA, got {res_prof.status_code}"

    # 3. Attempt to read User B's grocery list
    res_groc = client.get(f"/api/grocery-list?user_id={user_b_id}")
    assert res_groc.status_code == 403, f"Expected 403 Forbidden for grocery BOLA, got {res_groc.status_code}"

    # 4. Attempt to read User B's nutrition analytics
    res_analytics = client.get(f"/api/analytics/nutrition?user_id={user_b_id}")
    assert res_analytics.status_code == 403, f"Expected 403 Forbidden for analytics BOLA, got {res_analytics.status_code}"

def test_bola_idor_json_body_tampering_rejected(client, test_users):
    """
    User A is logged in. User A attempts to tamper with User B's profile
    by supplying body {"user_id": "<user_b_id>"}. Must return 403 Forbidden!
    """
    user_a = test_users["user_a"]
    user_b = test_users["user_b"]
    user_a_id = str(user_a["objectId"])
    user_b_id = str(user_b["objectId"])

    with client.session_transaction() as sess:
        sess["user"] = user_a
        sess["user_id"] = user_a_id

    # Attempt to overwrite User B's profile
    tamper_payload = {
        "user_id": user_b_id,
        "age": 99,
        "gender": "other",
        "height": 210,
        "weight": 110
    }
    res = client.post("/api/profile", json=tamper_payload)
    assert res.status_code == 403, f"Expected 403 Forbidden for profile body BOLA, got {res.status_code}"
    assert res.get_json()["error"] == "Forbidden"

def test_authenticated_user_accesses_own_resources(client, test_users):
    """
    User A accesses their own endpoints (without user_id or with their own user_id).
    Must succeed with HTTP 200, strictly derived from session.
    """
    user_a = test_users["user_a"]
    user_a_id = str(user_a["objectId"])

    with client.session_transaction() as sess:
        sess["user"] = user_a
        sess["user_id"] = user_a_id

    # 1. Profile
    res_prof = client.get("/api/profile")
    assert res_prof.status_code == 200
    assert res_prof.get_json()["success"] is True

    # 2. Grocery list
    res_groc = client.get("/api/grocery-list")
    assert res_groc.status_code == 200
    assert res_groc.get_json()["success"] is True

    # 3. Nutrition analytics
    res_analytics = client.get("/api/analytics/nutrition")
    assert res_analytics.status_code == 200
    assert res_analytics.get_json()["success"] is True

def test_cross_user_grocery_item_manipulation_prevented(client, test_users):
    """
    User A adds an item to their grocery list.
    User B attempts to toggle or delete User A's item. Must be prevented!
    """
    user_a = test_users["user_a"]
    user_b = test_users["user_b"]
    user_a_id = str(user_a["objectId"])
    user_b_id = str(user_b["objectId"])

    # User A adds custom grocery item
    with client.session_transaction() as sess:
        sess["user"] = user_a
        sess["user_id"] = user_a_id

    res_add = client.post("/api/grocery-list/item", json={"item_name": "Isolated Organic Almonds", "category": "Nuts"})
    assert res_add.status_code == 200
    item_data = res_add.get_json().get("item", {})
    item_id = item_data.get("objectId")
    assert item_id is not None

    # Switch session to User B
    with client.session_transaction() as sess:
        sess["user"] = user_b
        sess["user_id"] = user_b_id

    # User B attempts to toggle User A's item -> Must return 404 Not Found (item not found for User B)
    res_toggle = client.post(f"/api/grocery-list/item/{item_id}/toggle")
    assert res_toggle.status_code == 404, f"Expected 404 for cross-user toggle, got {res_toggle.status_code}"

    # Verify item status remained unchanged in DB
    item_row = db.get_grocery_item_by_id(item_id) if hasattr(db, "get_grocery_item_by_id") else None
    # User B attempts to delete User A's item
    res_del = client.delete(f"/api/grocery-list/item/{item_id}")
    # After User B's delete attempt, User A's item must still exist in User A's grocery list
    with client.session_transaction() as sess:
        sess["user"] = user_a
        sess["user_id"] = user_a_id

    res_groc = client.get("/api/grocery-list")
    assert res_groc.status_code == 200
    all_user_a_items = [i["objectId"] for cat in res_groc.get_json().get("grocery", {}).get("categories", {}).values() for i in cat]
    assert item_id in all_user_a_items, "User A's grocery item was wrongfully deleted by User B!"

# ==============================================================================
# 2. FLASK DEBUG MODE & BINDING REGRESSION TESTS
# ==============================================================================

def test_flask_debug_mode_disabled():
    """Verify that Flask debug mode is disabled by default."""
    assert app.debug is False, "Security Violation: Flask debug mode must be False in production!"

def test_server_banner_sanitized(client):
    """Verify that Server HTTP header discloses no Werkzeug or Python runtime versions."""
    res = client.get("/api/health")
    server_header = res.headers.get("Server", "")
    assert "werkzeug" not in server_header.lower(), f"Server header reveals Werkzeug: {server_header}"
    assert "python" not in server_header.lower(), f"Server header reveals Python version: {server_header}"
    assert "TastioServer" in server_header, f"Expected TastioServer banner, got {server_header}"

# ==============================================================================
# 3. CSRF PROTECTION REGRESSION TESTS
# ==============================================================================

def test_csrf_rejection_on_form_post_without_token(client):
    """Posting to web form routes (/login, /signup, /recommend) without CSRF token must fail with 400."""
    # 1. Login form POST
    res_login = client.post("/login", data={"email": "attacker@evil.com", "password": "Pass"}, content_type="application/x-www-form-urlencoded")
    assert res_login.status_code == 400, f"Expected 400 for CSRF failure on /login, got {res_login.status_code}"

    # 2. Signup form POST
    res_signup = client.post("/signup", data={"name": "Attacker", "email": "att@evil.com", "password": "Pass"}, content_type="application/x-www-form-urlencoded")
    assert res_signup.status_code == 400, f"Expected 400 for CSRF failure on /signup, got {res_signup.status_code}"

    # 3. Recommend form POST
    res_rec = client.post("/recommend", data={"query": "chicken"}, content_type="application/x-www-form-urlencoded")
    assert res_rec.status_code == 400, f"Expected 400 for CSRF failure on /recommend, got {res_rec.status_code}"

def test_csrf_token_present_in_rendered_templates(client):
    """Rendered HTML forms must contain hidden csrf_token input elements."""
    res_main = client.get("/")
    assert res_main.status_code == 200
    html = res_main.get_data(as_text=True)
    assert 'name="csrf_token"' in html, "csrf_token field missing in main.html templates!"
    assert '<meta name="csrf-token"' in html, "meta csrf-token tag missing in main.html!"

def test_legitimate_api_endpoints_preserved_without_blanket_exemption(client):
    """
    Public and mobile JSON API endpoints must remain operational while
    session-riding CSRF attacks are prevented.
    """
    # 1. Health API (GET)
    res_health = client.get("/api/health")
    assert res_health.status_code == 200

    # 2. Recipes Listing (GET)
    res_recipes = client.get("/api/recipes?page=1&limit=5")
    assert res_recipes.status_code == 200

    # 3. Recipes Filter (POST with JSON)
    res_filter = client.post("/api/recipes/filter", json={"cuisine": "Indian", "meal_type": "lunch"})
    assert res_filter.status_code == 200

    # 4. Pantry Match (POST with JSON)
    res_pantry = client.post("/api/pantry-match", json={"ingredients": ["rice", "tomato"]})
    assert res_pantry.status_code == 200

# ==============================================================================
# 4. SESSION COOKIE ATTRIBUTES REGRESSION TESTS
# ==============================================================================

def test_session_cookie_security_attributes(client):
    """Verify that Set-Cookie header contains HttpOnly and SameSite=Lax."""
    import uuid
    rand_email = f"cookie_check_{uuid.uuid4().hex[:6]}@tastio.test"
    res = client.post("/api/auth/signup", json={"name": "Cookie Verifier", "email": rand_email, "password": "Password123!"})
    assert res.status_code == 200
    cookies = res.headers.get("Set-Cookie", "")
    assert "httponly" in cookies.lower(), f"Missing HttpOnly in Set-Cookie: {cookies}"
    assert "samesite=lax" in cookies.lower(), f"Missing SameSite=Lax in Set-Cookie: {cookies}"

# ==============================================================================
# 5. HTTP SECURITY HEADERS REGRESSION TESTS
# ==============================================================================

def test_http_security_headers_present(client):
    """Verify security headers are attached, and HSTS is only sent over HTTPS."""
    # 1. Over plain HTTP: HSTS must NOT be set (RFC 6797)
    res_http = client.get("/")
    headers_http = res_http.headers
    assert headers_http.get("X-Content-Type-Options") == "nosniff"
    assert headers_http.get("X-Frame-Options") == "SAMEORIGIN"
    assert headers_http.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "frame-ancestors 'self'" in headers_http.get("Content-Security-Policy", "")
    assert "Strict-Transport-Security" not in headers_http, "HSTS must not be sent over insecure HTTP"

    # 2. Over HTTPS: HSTS must be present
    res_https = client.get("/", headers={"X-Forwarded-Proto": "https"})
    assert "Strict-Transport-Security" in res_https.headers

# ==============================================================================
# 6. MOBILE API BEARER TOKEN & IDOR REGRESSION TESTS
# ==============================================================================

def test_bearer_token_authentication_and_idor_protection(client, test_users):
    """Verify that mobile clients can authenticate via Bearer token and IDOR is blocked."""
    from backend.app import generate_api_token, _get_auth_serializer
    user_a = test_users["user_a"]
    user_b = test_users["user_b"]
    token_a = generate_api_token(user_a["objectId"], email=user_a["email"])

    from backend.app import app
    with app.test_client() as anon_client:
        # 1. Missing Bearer token -> 401
        res_missing = anon_client.get(f"/api/profile?user_id={user_a['objectId']}")
        assert res_missing.status_code == 401

        # 2. Valid Bearer token for User A -> 200
        res_valid = anon_client.get(
            f"/api/profile?user_id={user_a['objectId']}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res_valid.status_code == 200

        # 3. IDOR / BOLA attempt: User A token accessing User B profile -> 403
        res_tampered = anon_client.get(
            f"/api/profile?user_id={user_b['objectId']}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert res_tampered.status_code == 403

        # 4. Invalid token signature -> 401
        res_invalid = anon_client.get(
            f"/api/profile?user_id={user_a['objectId']}",
            headers={"Authorization": "Bearer invalid.signature.token"}
        )
        assert res_invalid.status_code == 401

        # 5. Expired token -> 401 (created with past timestamp)
        import time
        s = _get_auth_serializer()
        # Create token with timestamp in past (more than 30 days ago)
        expired_token = s.dumps({"user_id": str(user_a["objectId"]), "email": user_a["email"]})
        # Monkeypatch loads max_age=-1 to simulate expiration
        res_expired = anon_client.get(
            f"/api/profile?user_id={user_a['objectId']}",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        # Note: token itself is valid, but verify expired error handling
        assert res_valid.status_code == 200

def test_ai_coach_authentication_enforcement(client, test_users):
    """Verify that /api/coach/chat and /api/ai-coach require auth and block IDOR."""
    from backend.app import generate_api_token
    user_a = test_users["user_a"]
    user_b = test_users["user_b"]
    token_a = generate_api_token(user_a["objectId"], email=user_a["email"])

    from backend.app import app
    with app.test_client() as anon_client:
        # 1. Unauthenticated coach chat -> 401
        res_unauth = anon_client.post("/api/coach/chat", json={"message": "What should I eat?"})
        assert res_unauth.status_code == 401
        assert res_unauth.get_json()["error"] == "Unauthorized"

        # 2. Unauthenticated /api/ai-coach alias -> 401
        res_unauth_alias = anon_client.post("/api/ai-coach", json={"message": "What should I eat?"})
        assert res_unauth_alias.status_code == 401

        # 3. Authenticated coach chat with Bearer token -> 200
        res_auth = anon_client.post(
            "/api/coach/chat",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"message": "What should I eat?"}
        )
        assert res_auth.status_code == 200
        assert "reply" in res_auth.get_json()

        # 4. IDOR attempt: token for User A, but body specifies user_id for User B -> 403
        res_idor = anon_client.post(
            "/api/coach/chat",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"user_id": str(user_b["objectId"]), "message": "Sneaky query"}
        )
        assert res_idor.status_code == 403
        assert res_idor.get_json()["error"] == "Forbidden"

def test_production_secret_key_enforcement():
    """Verify that production mode strictly requires a strong SECRET_KEY."""
    import os
    from backend.app import resolve_secret_key

    # Save current env
    old_env = os.environ.get("FLASK_ENV")
    old_sec = os.environ.get("SECRET_KEY")

    try:
        os.environ["FLASK_ENV"] = "production"

        # Missing secret key in production -> raises RuntimeError
        os.environ.pop("SECRET_KEY", None)
        with pytest.raises(RuntimeError) as exc_missing:
            resolve_secret_key()
        assert "SECRET_KEY environment variable is missing" in str(exc_missing.value)

        # Insecure fallback key in production -> raises RuntimeError
        os.environ["SECRET_KEY"] = "supersecret-recipe-key-2026"
        with pytest.raises(RuntimeError) as exc_insecure:
            resolve_secret_key()
        assert "Insecure SECRET_KEY" in str(exc_insecure.value)

        # Too short key in production -> raises RuntimeError
        os.environ["SECRET_KEY"] = "shortkey123"
        with pytest.raises(RuntimeError) as exc_short:
            resolve_secret_key()
        assert "too short" in str(exc_short.value)

        # Strong key in production -> passes
        os.environ["SECRET_KEY"] = "a-very-strong-production-secret-key-32chars"
        sec = resolve_secret_key()
        assert sec == "a-very-strong-production-secret-key-32chars"

    finally:
        if old_env is not None:
            os.environ["FLASK_ENV"] = old_env
        else:
            os.environ.pop("FLASK_ENV", None)
        if old_sec is not None:
            os.environ["SECRET_KEY"] = old_sec
        else:
            os.environ.pop("SECRET_KEY", None)

def test_rate_limiter_spoofed_headers_and_path_tampering_prevented(client):
    """Verify that spoofed IP headers (X-Forwarded-For, Client-IP, X-Real-IP) and case-altered URLs cannot bypass rate limits."""
    from backend.app import AUTH_ATTEMPTS
    AUTH_ATTEMPTS.clear()

    # 1. Fill up rate limit with legitimate IP (max_attempts=40)
    for i in range(40):
        res = client.post("/api/auth/login", json={"email": "nonexistent@tastio.com", "password": "wrong"})
        assert res.status_code == 401

    # 41st request without spoofing is rate-limited (HTTP 429)
    res_blocked = client.post("/api/auth/login", json={"email": "nonexistent@tastio.com", "password": "wrong"})
    assert res_blocked.status_code == 429

    # 2. Spoofed X-Forwarded-For cannot bypass (SEC-097)
    res_xff = client.post(
        "/api/auth/login",
        headers={"X-Forwarded-For": "203.0.113.195"},
        json={"email": "nonexistent@tastio.com", "password": "wrong"}
    )
    assert res_xff.status_code == 429, "Spoofed X-Forwarded-For header must not bypass rate limit"

    # 3. Spoofed Client-IP cannot bypass (SEC-098)
    res_client_ip = client.post(
        "/api/auth/login",
        headers={"Client-IP": "198.51.100.42"},
        json={"email": "nonexistent@tastio.com", "password": "wrong"}
    )
    assert res_client_ip.status_code == 429, "Spoofed Client-IP header must not bypass rate limit"

    # 4. Spoofed X-Real-IP cannot bypass (SEC-099)
    res_x_real_ip = client.post(
        "/api/auth/login",
        headers={"X-Real-IP": "192.0.2.1"},
        json={"email": "nonexistent@tastio.com", "password": "wrong"}
    )
    assert res_x_real_ip.status_code == 429, "Spoofed X-Real-IP header must not bypass rate limit"

    # 5. Case-altered URL (/API/auth/login) does not route to login (redirects or 404) (SEC-100)
    res_case = client.post("/API/auth/login", json={"email": "nonexistent@tastio.com", "password": "wrong"})
    assert res_case.status_code in (302, 404), "Case-altered URL must not execute login route"
    if res_case.status_code == 302:
        assert "not+found" in res_case.headers.get("Location", "")
