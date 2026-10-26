import os
import sys
import uuid
import sqlite3

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ai-service"))

import database as db
from app import app

def run_tests():
    print("=" * 70)
    print("TASTIO 2.0 AUTHENTICATION & SECURITY TEST SUITE (WEB & ANDROID)")
    print("=" * 70)

    client = app.test_client()
    test_id = str(uuid.uuid4())[:8]
    test_email = f"user_{test_id}@tastio.test"
    test_name = "Raghavendra Tester"
    test_pwd = "mypassword123"

    # Clean up test email if exists
    conn = db.get_db_connection()
    conn.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()
    conn.close()

    # TEST 1: Password length boundary (< 4 chars rejected)
    print("\n[TEST 1] Testing Short Password Rejection (< 4 chars)")
    res, msg = db.register_user("Short Pwd", "short@test.com", "12")
    assert res is False, "Short password (< 4 chars) should be rejected!"
    assert "at least 4 characters" in msg, f"Expected length message, got: {msg}"
    print(f"  [PASS] Short password rejected with: '{msg}'")

    # TEST 2: Invalid email format rejected
    print("\n[TEST 2] Testing Invalid Email Format Rejection")
    res, msg = db.register_user("Invalid Email", "invalid-email-address", "password123")
    assert res is False, "Invalid email should be rejected!"
    assert "Invalid email" in msg, f"Expected invalid email message, got: {msg}"
    print(f"  [PASS] Invalid email rejected with: '{msg}'")

    # TEST 3: Empty name rejected
    print("\n[TEST 3] Testing Empty Name Rejection")
    res, msg = db.register_user("   ", "valid@test.com", "password123")
    assert res is False, "Empty name should be rejected!"
    assert "Name is required" in msg, f"Expected name required message, got: {msg}"
    print(f"  [PASS] Empty name rejected with: '{msg}'")

    # TEST 4: Successful New Registration (Supports 4+ chars, including user's 4-char PIN)
    print("\n[TEST 4] Testing Successful New User Registration")
    res, user = db.register_user(test_name, test_email, test_pwd)
    assert res is True, f"Registration failed: {user}"
    assert user.get("email") == test_email.lower(), "User email mismatch!"
    assert user.get("name") == test_name, "User name mismatch!"
    assert user.get("objectId") is not None, "User objectId missing!"
    print(f"  [PASS] Registered successfully: ID={user['objectId']}, Name='{user['name']}', Email='{user['email']}'")

    # Verify Password Hashing in SQLite (Never plain text)
    conn = db.get_db_connection()
    row = conn.execute("SELECT password FROM users WHERE email = ?", (test_email,)).fetchone()
    conn.close()
    assert row is not None, "User record not found in database!"
    stored_hash = row["password"]
    assert stored_hash != test_pwd, "SECURITY VIOLATION: Password stored in plain text!"
    assert "scrypt:" in stored_hash or "pbkdf2:" in stored_hash, f"Unexpected hash format: {stored_hash}"
    print(f"  [PASS] Verified secure password hashing: '{stored_hash[:25]}...' (Never plain text)")

    # TEST 5: Duplicate registration prevention
    print("\n[TEST 5] Testing Duplicate Email Registration Prevention")
    res, msg = db.register_user("Duplicate User", test_email, "anotherpassword")
    assert res is False, "Duplicate email should be rejected!"
    assert "already exists" in msg, f"Expected duplicate message, got: {msg}"
    print(f"  [PASS] Duplicate registration rejected with: '{msg}'")

    # TEST 6: Successful Login with Correct Credentials
    print("\n[TEST 6] Testing Login with Correct Credentials")
    res, login_user = db.login_user(test_email, test_pwd)
    assert res is True, f"Login failed: {login_user}"
    assert login_user.get("objectId") == user["objectId"], "Logged in user ID mismatch!"
    print(f"  [PASS] Logged in successfully: User='{login_user['name']}'")

    # TEST 7: Login with Incorrect Password
    print("\n[TEST 7] Testing Login with Incorrect Password")
    res, msg = db.login_user(test_email, "WrongPassword999")
    assert res is False, "Login with wrong password should fail!"
    assert "Invalid email or password" in msg, f"Expected invalid credentials message, got: {msg}"
    print(f"  [PASS] Wrong password rejected with: '{msg}'")

    # TEST 8: Login with Unregistered Email
    print("\n[TEST 8] Testing Login with Unregistered Email")
    res, msg = db.login_user("nonexistent_user_999@tastio.test", test_pwd)
    assert res is False, "Login with non-existent email should fail!"
    assert "Invalid email or password" in msg, f"Expected invalid credentials message, got: {msg}"
    print(f"  [PASS] Unregistered email rejected with: '{msg}'")

    # TEST 9: Mobile API Endpoints (/api/auth/signup & /api/auth/login)
    print("\n[TEST 9] Testing Mobile / Android REST API Endpoints")
    api_email = f"mobile_{test_id}@tastio.test"
    
    # 9a. API Signup
    resp_signup = client.post("/api/auth/signup", json={
        "name": "Mobile Tester",
        "email": api_email,
        "password": "mobilepassword"
    })
    assert resp_signup.status_code == 200, f"API signup failed: {resp_signup.data}"
    signup_data = resp_signup.get_json()
    assert signup_data.get("success") is True, f"API signup error: {signup_data}"
    print(f"  [PASS] POST /api/auth/signup returned 200 OK: User='{signup_data['user']['name']}'")

    # 9b. API Login Success
    resp_login = client.post("/api/auth/login", json={
        "email": api_email,
        "password": "mobilepassword"
    })
    assert resp_login.status_code == 200, f"API login failed: {resp_login.data}"
    login_data = resp_login.get_json()
    assert login_data.get("success") is True, f"API login error: {login_data}"
    print(f"  [PASS] POST /api/auth/login returned 200 OK: ID='{login_data['user']['objectId']}'")

    # 9c. API Login Failure (Wrong Password)
    resp_bad_pwd = client.post("/api/auth/login", json={
        "email": api_email,
        "password": "WrongPassword!"
    })
    assert resp_bad_pwd.status_code == 401, f"Expected 401 for bad password, got: {resp_bad_pwd.status_code}"
    bad_pwd_data = resp_bad_pwd.get_json()
    assert bad_pwd_data.get("success") is False, "Expected success: False for bad password"
    print(f"  [PASS] POST /api/auth/login with wrong password correctly returned 401 Unauthorized")

    # TEST 10: Web Routes (/signup & /login form submissions)
    print("\n[TEST 10] Testing Web App Form Routes (/signup & /login)")
    web_email = f"web_{test_id}@tastio.test"

    # 10a. Web Signup
    resp_web_signup = client.post("/signup", data={
        "name": "Web Tester",
        "email": web_email,
        "password": "webpassword"
    }, follow_redirects=False)
    assert resp_web_signup.status_code == 302, f"Expected redirect after signup, got: {resp_web_signup.status_code}"
    assert "/dashboard" in resp_web_signup.headers.get("Location", ""), f"Expected redirect to /dashboard, got: {resp_web_signup.headers.get('Location')}"
    print("  [PASS] POST /signup redirected to /dashboard on success")

    # 10b. Web Login Success
    resp_web_login = client.post("/login", data={
        "email": web_email,
        "password": "webpassword"
    }, follow_redirects=False)
    assert resp_web_login.status_code == 302, f"Expected redirect after login, got: {resp_web_login.status_code}"
    assert "/dashboard" in resp_web_login.headers.get("Location", ""), f"Expected redirect to /dashboard, got: {resp_web_login.headers.get('Location')}"
    print("  [PASS] POST /login redirected to /dashboard on success")

    # 10c. Web Login Failure
    resp_web_bad = client.post("/login", data={
        "email": web_email,
        "password": "incorrectpassword"
    }, follow_redirects=False)
    assert resp_web_bad.status_code == 302, f"Expected redirect after failed login, got: {resp_web_bad.status_code}"
    assert "Login+failed" in resp_web_bad.headers.get("Location", "") or "Login failed" in resp_web_bad.headers.get("Location", ""), "Expected Login failed message in redirect URL"
    print("  [PASS] POST /login with bad credentials redirected to / with clear error message")

    # Clean up test users
    conn = db.get_db_connection()
    conn.execute("DELETE FROM users WHERE email IN (?, ?, ?)", (test_email, api_email, web_email))
    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("ALL 10 AUTHENTICATION & SECURITY TESTS PASSED! (100% VERIFIED)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
