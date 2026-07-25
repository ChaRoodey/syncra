import pytest
from httpx import AsyncClient

from app.core.enums import UserRole
from app.schemas.team import TeamNameSchema


@pytest.mark.integration
@pytest.mark.teams
class TestTeams:
    PREFIX = "/api/v1/teams"

    async def test_create_team_201(
        self, client: AsyncClient, team_name_payload: TeamNameSchema, factory
    ):
        _, _, access_token = await factory.user(role=UserRole.MANAGER)
        response = await client.post(
            f"{self.PREFIX}",
            json=team_name_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == team_name_payload.name
        assert "invite_code" in data

    async def test_create_team_403(
        self, client: AsyncClient, team_name_payload: TeamNameSchema, factory
    ):
        _, _, access_token = await factory.user(role=UserRole.USER)
        response = await client.post(
            f"{self.PREFIX}",
            json=team_name_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_create_team_409(
        self, client: AsyncClient, team_name_payload: TeamNameSchema, factory
    ):
        _, _, access_token = await factory.user(role=UserRole.MANAGER)
        await client.post(
            f"{self.PREFIX}",
            json=team_name_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response2 = await client.post(
            f"{self.PREFIX}",
            json=team_name_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response2.status_code == 409

    async def test_create_team_422(
        self, client: AsyncClient, team_name_payload: TeamNameSchema, factory
    ):
        _, _, access_token = await factory.user(role=UserRole.MANAGER)
        payload = team_name_payload.model_dump()
        payload["name"] = 1

        response = await client.post(
            f"{self.PREFIX}",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_join_team_201(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()

        response = await client.post(
            f"{self.PREFIX}/{team.id}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

    async def test_join_team_401(self, client: AsyncClient, factory):
        team = await factory.team()

        response = await client.post(
            f"{self.PREFIX}/{team.id}/join",
        )

        assert response.status_code == 401

    async def test_join_team_404(self, client: AsyncClient, factory):
        _, _, access_token = await factory.user()

        response = await client.post(
            f"{self.PREFIX}/{0}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_join_team_409(self, client: AsyncClient, factory):
        _, _, access_token = await factory.user()
        team = await factory.team()

        await client.post(
            f"{self.PREFIX}/{team.id}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = await client.post(
            f"{self.PREFIX}/{team.id}/join",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 409

    async def test_get_team_members_200(self, client: AsyncClient, factory):
        member_amount = 4

        curr_user, _, access_token = await factory.user()
        users = [curr_user]

        for i in range(member_amount - 1):
            user, _, _ = await factory.user(username=f"user{i}")
            users.append(user)

        team = await factory.team()
        for user in users:
            await factory.team_member(team.id, user.id)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == member_amount

        expected_ids = {user.id for user in users}
        returned_ids = {member["id"] for member in data}

        assert returned_ids == expected_ids

    async def test_get_team_members_403(self, client: AsyncClient, factory):
        curr_user, _, access_token = await factory.user()
        team = await factory.team()

        response = await client.get(
            f"{self.PREFIX}/{team.id}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_get_team_members_404(self, client: AsyncClient, factory):
        _, _, access_token = await factory.user()

        response = await client.get(
            f"{self.PREFIX}/{0}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_remove_team_member_204(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()

        user, _, _ = await factory.user(username="user1")
        await factory.team_member(team.id, user.id)

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/remove_member/{user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    async def test_remove_team_member_403_user_not_a_team_member(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()
        response = await client.delete(
            f"{self.PREFIX}/{team.id}/remove_member/{user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_remove_team_member_403_role_is_user(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(role=UserRole.USER)
        team = await factory.team()
        response = await client.delete(
            f"{self.PREFIX}/{team.id}/remove_member/{user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_remove_team_member_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        response = await client.delete(
            f"{self.PREFIX}/{0}/remove_member/{user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
