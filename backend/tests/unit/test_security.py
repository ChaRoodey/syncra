import pytest

from app.auth.utils import (
    check_password,
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
)


@pytest.mark.unit
class TestSecurity:
    def test_hash_password_and_verify(self):
        password = "abc"
        hashed = hash_password("abc")

        assert password != hashed
        assert check_password(password, hashed) is True
        assert check_password("wrong", hashed) is False

    def test_create_and_decode_access_token(self):
        token = create_access_token(1)
        payload = decode_jwt(token)

        assert payload.sub == "1"
        assert payload.type == "access"

    def test_create_and_decode_refresh_token(self):
        token = create_refresh_token(1)
        payload = decode_jwt(token)

        assert payload.sub == "1"
        assert payload.type == "refresh"
