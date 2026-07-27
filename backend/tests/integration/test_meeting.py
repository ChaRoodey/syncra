from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from app.core.enums import MeetingStatus, UserRole
from app.schemas.meeting import MeetingCreateSchema, MeetingUpdateSchema


@pytest.mark.integration
@pytest.mark.meetings
class TestMeetings:
    PREFIX = "/api/v1/teams"

    async def test_get_all_meetings_200(self, client: AsyncClient, factory):
        meetings_amount = 3

        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        meetings = []

        for i in range(meetings_amount):
            meeting = await factory.meeting(
                team_id=team.id,
                author_id=user.id,
                title=f"meeting{i}",
            )
            meetings.append(meeting)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == meetings_amount

        expected_ids = {meeting.id for meeting in meetings}
        returned_ids = {meeting["id"] for meeting in data}

        assert returned_ids == expected_ids

    async def test_get_all_meetings_401(self, client: AsyncClient):
        response = await client.get(f"{self.PREFIX}/{0}/meetings")

        assert response.status_code == 401

    async def test_get_all_meetings_403(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_get_all_meetings_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        response = await client.get(
            f"{self.PREFIX}/{0}/meetings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_all_meetings_422(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        response = await client.get(
            f"{self.PREFIX}/{'a'}/meetings",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_create_meeting_201(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        assert data.get("team_id") == team.id
        assert data.get("author_id") == user.id
        assert data.get("status") == MeetingStatus.SCHEDULED

    async def test_create_meeting_401(
        self, client: AsyncClient, meeting_create_payload: MeetingCreateSchema
    ):
        response = await client.post(
            f"{self.PREFIX}/{0}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
        )

        assert response.status_code == 401

    async def test_create_meeting_403_role_is_user(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.USER)
        response = await client.post(
            f"{self.PREFIX}/{0}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_create_meeting_403_not_a_team_member(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_create_meeting_404(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        response = await client.post(
            f"{self.PREFIX}/{0}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_create_meeting_422(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        payload = meeting_create_payload.model_dump(mode="json")
        payload["title"] = 123

        response = await client.post(
            f"{self.PREFIX}/{0}/meetings",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_create_meeting_422_invalid_time(
        self, client: AsyncClient, factory, meeting_create_payload: MeetingCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        meeting_create_payload.starts_at = datetime.now() + timedelta(days=1, hours=1)
        meeting_create_payload.ends_at = datetime.now() + timedelta(days=1)

        response = await client.post(
            f"{self.PREFIX}/{0}/meetings",
            json=meeting_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_get_meeting_200(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == meeting.id
        assert data.get("author_id") == user.id
        assert data.get("team_id") == team.id

    async def test_get_meeting_401(self, client: AsyncClient):
        response = await client.get(
            f"{self.PREFIX}/{0}/meetings/{0}",
        )

        assert response.status_code == 401

    async def test_get_meeting_403_user_not_a_team_member(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_get_meeting_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_meeting_422(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        response = await client.get(
            f"{self.PREFIX}/{'a'}/meetings/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_update_meeting_200(
        self, client: AsyncClient, factory, meeting_update_payload: MeetingUpdateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        meeting = await factory.meeting(team_id=team.id, author_id=user.id)

        response = await client.patch(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}",
            json=meeting_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == meeting.id
        assert data.get("title") == meeting_update_payload.title
        assert data.get("status") == meeting_update_payload.status

    async def test_update_meeting_401(
        self, client: AsyncClient, meeting_update_payload
    ):
        response = await client.patch(
            f"{self.PREFIX}/{1}/meetings/{1}",
            json=meeting_update_payload.model_dump(mode="json"),
        )

        assert response.status_code == 401

    async def test_update_meeting_403_role_is_user(
        self, client: AsyncClient, factory, meeting_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.USER)
        response = await client.patch(
            f"{self.PREFIX}/{1}/meetings/{1}",
            json=meeting_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_update_meeting_403_not_a_team_member(
        self, client: AsyncClient, factory, meeting_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.patch(
            f"{self.PREFIX}/{team.id}/meetings/{1}",
            json=meeting_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_update_meeting_404(
        self, client: AsyncClient, factory, meeting_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        response = await client.patch(
            f"{self.PREFIX}/{team.id}/meetings/{1}",
            json=meeting_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_update_meeting_422(
        self, client: AsyncClient, factory, meeting_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        payload = meeting_update_payload.model_dump(mode="json")
        payload["title"] = 123

        response = await client.patch(
            f"{self.PREFIX}/{1}/meetings/{1}",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_delete_meeting_204(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    async def test_delete_meeting_401(self, client: AsyncClient):
        response = await client.delete(f"{self.PREFIX}/{0}/meetings/{0}")

        assert response.status_code == 401

    async def test_delete_meeting_403_role_is_user(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.USER)

        response = await client.delete(
            f"{self.PREFIX}/{1}/meetings/{1}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_delete_meeting_403_not_a_team_member(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{1}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_delete_meeting_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_delete_meeting_422(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        response = await client.delete(
            f"{self.PREFIX}/{'a'}/meetings/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_add_meeting_participant_201(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

    async def test_add_meeting_participant_401(self, client: AsyncClient):
        response = await client.post(
            f"{self.PREFIX}/{0}/meetings/{0}/members/{0}",
        )

        assert response.status_code == 401

    async def add_participant_not_team_member_403(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
        )

        assert response.status_code == 403

    async def add_participant_manager_not_team_member_403(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, participant.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
        )

        assert response.status_code == 403

    async def test_add_meeting_participant_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{0}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_add_meeting_participant_409(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = await client.post(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 409

    async def test_get_meeting_participants_200(self, client: AsyncClient, factory):
        participants_amount = 4

        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        participants = []

        for i in range(participants_amount):
            participant, _, _ = await factory.user(username=f"user{i}")
            await factory.team_member(team.id, participant.id)
            participants.append(participant)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        for participant in participants:
            await factory.meeting_participant(meeting.id, participant.id)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == participants_amount

        expected_ids = {participant.id for participant in participants}
        returned_ids = {participant["id"] for participant in data}

        assert returned_ids == expected_ids

    async def test_get_meeting_participants_403(self, client: AsyncClient, factory):
        _, _, access_token = await factory.user()
        team = await factory.team()

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{0}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_get_meeting_participants_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()
        await factory.team_member(team.id, user.id)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/meetings/{0}/members",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_remove_team_participant_204(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        await factory.meeting_participant(meeting.id, participant.id)

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    async def test_remove_team_participant_403_user_not_a_meeting_participant(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        meeting = await factory.meeting(
            team_id=team.id,
            author_id=user.id,
        )

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{meeting.id}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User is not a participant"

    async def test_remove_team_participant_403_role_is_user(
        self, client: AsyncClient, factory
    ):
        user, _, access_token = await factory.user(role=UserRole.USER)

        response = await client.delete(
            f"{self.PREFIX}/{0}/meetings/{0}/members/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_remove_team_participant_404(self, client: AsyncClient, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        participant, _, _ = await factory.user(username="user1")
        team = await factory.team()
        await factory.team_member(team.id, user.id)
        await factory.team_member(team.id, participant.id)

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/meetings/{0}/members/{participant.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
