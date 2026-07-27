from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.calendar
class TestCalendar:
    PREFIX = "/api/v1/calendar"

    async def test_get_calendar_200(self, client: AsyncClient, factory):
        tasks_amount = 3
        meetings_amount = 3

        user, team, access_token = await factory.user_team_membership()

        tasks = []
        meetings = []

        for i in range(tasks_amount):
            task = await factory.task(
                team_id=team.id,
                assignee_id=user.id,
                title=f"task{i}",
            )
            tasks.append(task)

        for i in range(meetings_amount):
            meeting = await factory.meeting(
                team_id=team.id,
                author_id=user.id,
                title=f"meeting{i}",
            )

            await factory.meeting_participant(
                meeting_id=meeting.id,
                user_id=user.id,
            )

            meetings.append(meeting)

        response = await client.get(
            f"{self.PREFIX}",
            params={
                "from": datetime.now().isoformat(),
                "to": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        print(response.json())

        assert response.status_code == 200

        data = response.json()

        assert len(data) == meetings_amount + tasks_amount

        expected_task_ids = {task.id for task in tasks}
        returned_task_ids = {task["id"] for task in data if task["type"] == "task"}
        assert expected_task_ids == returned_task_ids

        expected_meeting_ids = {meeting.id for meeting in tasks}
        returned_meeting_ids = {
            meeting["id"] for meeting in data if meeting["type"] == "meeting"
        }
        assert expected_meeting_ids == returned_meeting_ids

    async def test_get_calendar_401(self, client: AsyncClient):
        response = await client.get(
            f"{self.PREFIX}",
            params={
                "from": datetime.now().isoformat(),
                "to": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            },
        )

        assert response.status_code == 401

    async def test_get_calendar_422(self, client: AsyncClient, factory):
        _, _, access_token = await factory.user_team_membership()

        response = await client.get(
            f"{self.PREFIX}",
            params={
                "from": "a",
                "to": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422
