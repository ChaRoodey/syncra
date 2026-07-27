import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.auth
class TestAuth:
    PREFIX = "/api/v1/auth"

    async def test_register_200(self, client: AsyncClient):
        payload = {
            "username": "string",
            "password": "string",
            "email": "user@example.com",
            "first_name": "string",
            "last_name": "string",
        }

        response = await client.post(
            f"{self.PREFIX}/register",
            json=payload,
        )

        assert response.status_code == 201

    async def test_register_409(self, client: AsyncClient):
        payload = {
            "username": "string",
            "password": "string",
            "email": "user@example.com",
            "first_name": "string",
            "last_name": "string",
        }

        await client.post(
            f"{self.PREFIX}/register",
            json=payload,
        )

        response2 = await client.post(
            f"{self.PREFIX}/register",
            json=payload,
        )

        assert response2.status_code == 409

    @pytest.mark.parametrize(
        "payload",
        [
            (
                {
                    "username": "string",
                    "password": "string",
                }
            ),
            (
                {
                    "username": "string",
                    "password": "string",
                    "email": "user@example",
                    "first_name": "string",
                    "last_name": "string",
                }
            ),
            (
                {
                    "username": "string",
                    "password": 12,
                    "email": "user@example.com",
                    "first_name": "string",
                    "last_name": "string",
                }
            ),
        ],
    )
    async def test_register_422(self, client: AsyncClient, payload: dict):
        response = await client.post(
            f"{self.PREFIX}/register",
            json=payload,
        )

        assert response.status_code == 422

    async def test_login_200(self, client: AsyncClient, factory):
        user, password, _ = await factory.user()

        response = await client.post(
            f"{self.PREFIX}/login",
            json={
                "username": user.username,
                "password": password,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "token" in data
        assert data["token_type"] == "bearer"
        assert "refresh_token" in response.cookies

    @pytest.mark.parametrize(
        "payload",
        [
            (
                {
                    "username": "string",
                    "password": "string1",
                }
            ),
            (
                {
                    "username": "string1",
                    "password": "string",
                }
            ),
        ],
    )
    async def test_login_401(self, client: AsyncClient, payload: dict):
        response = await client.post(
            f"{self.PREFIX}/login",
            json=payload,
        )

        assert response.status_code == 401

    async def test_refresh_200(self, client: AsyncClient, refresh_token: str):
        client.cookies.set("refresh_token", refresh_token)

        response = await client.post(f"{self.PREFIX}/refresh")

        assert response.status_code == 200

        data = response.json()

        assert "token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_401(self, client: AsyncClient, refresh_token: str):
        client.cookies.set("refresh_token", "invalid-token")

        response = await client.post(f"{self.PREFIX}/refresh")

        assert response.status_code == 401
