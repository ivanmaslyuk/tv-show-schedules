from app.auth import create_access_token, hash_password, verify_password


def test_password_roundtrip():
    password_hash = hash_password("secret123")
    assert verify_password("secret123", password_hash)


def test_token_contains_expected_user_id():
    token = create_access_token(7, True)
    assert token.count(".") == 2

