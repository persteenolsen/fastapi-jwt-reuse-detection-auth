from datetime import datetime, timedelta, timezone
import jwt

from security.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
)

# ==========================================================
# JWT VALIDATION TESTS
# ==========================================================


def test_valid_token():
    """
    Verify that a valid access token is accepted.
    """

    token = create_access_token({"sub": "testuser"})

    assert verify_token(token, expected_type="access") == "testuser"

    print("   ✅ Access token accepted")


def test_wrong_type():
    """
    Verify that an access token cannot be used as a refresh token.
    """

    token = create_access_token({"sub": "testuser"})

    assert verify_token(token, expected_type="refresh") is None

    print("   ✅ Wrong token type rejected")


def test_refresh_token_type():
    """
    Verify that a refresh token is accepted as refresh type
    and rejected as access type.
    """

    token = create_refresh_token({"sub": "testuser"})

    assert verify_token(token, expected_type="refresh") == "testuser"

    assert verify_token(token, expected_type="access") is None

    print("   ✅ Refresh token type validation successful")


def test_expired_token():
    """
    Verify that expired access tokens are rejected.
    """

    token = jwt.encode(
        {
            "sub": "testuser",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert verify_token(token, expected_type="access") is None

    print("   ✅ Expired token rejected")


def test_invalid_signature():
    """
    Verify that tokens signed with an invalid secret are rejected.
    """

    token = jwt.encode(
        {
            "sub": "testuser",
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "WRONG_SECRET",
        algorithm=ALGORITHM,
    )

    assert verify_token(token, expected_type="access") is None

    print("   ✅ Invalid token signature rejected")


# ==========================================================
# RUNNER
# ==========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("JWT VALIDATION TESTS")
    print("========================================")

    test_valid_token()
    test_wrong_type()
    test_refresh_token_type()
    test_expired_token()
    test_invalid_signature()

    print("\n🎉 ALL JWT TESTS COMPLETED SUCCESSFULLY")
