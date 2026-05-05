from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert verify_password("mysecret", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("mysecret")
    assert verify_password("wrong", hashed) is False


def test_token_roundtrip():
    token = create_access_token("42")
    assert isinstance(token, str) and len(token) > 20
    assert decode_token(token) == "42"


def test_decode_token_garbage_returns_none():
    assert decode_token("not-a-real-jwt") is None
