import requests

BASE_URL = "http://localhost:8000"


# ==========================================================
# HELPERS
# ==========================================================

def login():

    response = requests.post(
        f"{BASE_URL}/tokens-spa",
        data={
            "username": "testuser",
            "password": "admin",
        },
    )

    assert response.status_code == 200

    print(f"   ✅ HTTP {response.status_code} OK - Login successful")

    return response.json()


def refresh_token_call(token):

    return requests.post(
        f"{BASE_URL}/refresh-token-spa",
        json=token,
    )


def logout_token(token):

    return requests.post(
        f"{BASE_URL}/logout",
        json=token,
    )


def cleanup():

    return requests.post(
        f"{BASE_URL}/cleanup-tokens"
    )


def admin_purge():

    return requests.post(
        f"{BASE_URL}/admin/purge-refresh-tokens"
    )


# ==========================================================
# INTEGRATION TESTS
# ==========================================================
def test_full_refresh_rotation_flow():

    print("\n==============================")
    print("REFRESH TOKEN ROTATION FLOW")
    print("==============================")

    session = login()
    refresh_token = session["refreshToken"]

    print("   ▶ Initial refresh token received")

    # First refresh
    response = refresh_token_call(refresh_token)
    assert response.status_code == 200

    print(
        f"   ✅ HTTP {response.status_code} OK - "
        "First refresh successful"
    )

    new_refresh = response.json()["refreshToken"]

    print(
        "   ▶ Testing refresh token reuse detection"
    )

    # Old token reuse should fail
    response = refresh_token_call(refresh_token)

    assert response.status_code == 401

    print(
        f"   ✅ HTTP {response.status_code} Unauthorized - "
        "Reuse detected"
    )

    # New token should also fail because the family was revoked
    response = refresh_token_call(new_refresh)

    assert response.status_code == 401

    print(
        f"   ✅ HTTP {response.status_code} Unauthorized - "
        "Token family revoked after reuse detection"
    )
    
def test_refresh_token_reuse_detection():

    print("\n==============================")
    print("REFRESH TOKEN REUSE DETECTION")
    print("==============================")

    session = login()

    original_refresh = session["refreshToken"]

    # Legitimate refresh (rotation)
    response = refresh_token_call(original_refresh)

    assert response.status_code == 200

    rotated_refresh = response.json()["refreshToken"]

    print("   ✅ Refresh token rotated")

    # Simulate attacker using the old refresh token
    response = refresh_token_call(original_refresh)

    assert response.status_code == 401

    detail = response.json()["detail"]

    assert detail in (
        "Refresh token reuse detected",
        "Refresh token revoked"
    )

    print(
        "   ✅ Refresh token reuse detected"
    )

    # Token family (or all user refresh tokens) should now be revoked
    response = refresh_token_call(rotated_refresh)

    assert response.status_code == 401

    print(
        "   ✅ Active refresh token revoked after reuse detection"
    )


def test_logout_flow():

    print("\n==============================")
    print("LOGOUT FLOW")
    print("==============================")

    session = login()

    refresh_token = session["refreshToken"]

    response = logout_token(refresh_token)

    assert response.status_code == 200

    print(
        f"   ✅ HTTP {response.status_code} OK - "
        "Logout successful"
    )


def test_refresh_after_logout_should_fail():

    print("\n==============================")
    print("REVOKED TOKEN")
    print("==============================")

    session = login()

    refresh_token = session["refreshToken"]

    logout_token(refresh_token)

    response = refresh_token_call(refresh_token)

    assert response.status_code == 401

    print(
        f"   ✅ HTTP {response.status_code} Unauthorized - "
        "Revoked refresh token correctly rejected"
    )


def test_cleanup_endpoint():

    print("\n==============================")
    print("TOKEN CLEANUP")
    print("==============================")

    response = cleanup()

    assert response.status_code == 200

    print(
        f"   ✅ HTTP {response.status_code} OK - "
        "Cleanup executed successfully"
    )


def test_admin_purge():

    print("\n==============================")
    print("ADMIN PURGE")
    print("==============================")

    response = admin_purge()

    assert response.status_code == 200

    print(
        f"   ✅ HTTP {response.status_code} OK - "
        "Admin purge executed successfully"
    )


# ==========================================================
# RUNNER
# ==========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("FASTAPI AUTH INTEGRATION TESTS")
    print("========================================")

    test_full_refresh_rotation_flow()
    test_refresh_token_reuse_detection()
    test_logout_flow()
    test_refresh_after_logout_should_fail()
    test_cleanup_endpoint()

    # test_admin_purge()

    # Requires authentication if enabled
    # test_admin_purge()

    print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY")