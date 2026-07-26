import pytest
from httpx import AsyncClient

from app.core.enums import TaskStatus, UserRole
from app.schemas.task import (
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
)


@pytest.mark.integration
@pytest.mark.tasks
class TestTasks:
    PREFIX = "/api/v1/teams"
    PREFIX_EVALUATION = "/api/v1/tasks"

    async def test_get_all_tasks_200(self, client, factory):
        tasks_amount = 3

        user, team, access_token = await factory.user_team_membership()

        tasks = []

        for i in range(tasks_amount):
            task = await factory.task(
                team_id=team.id,
                assignee_id=user.id,
                title=f"task{i}",
            )
            tasks.append(task)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/tasks",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == tasks_amount

        expected_ids = {task.id for task in tasks}
        returned_ids = {task["id"] for task in data}

        assert returned_ids == expected_ids

    async def test_get_all_tasks_401(self, client):
        response = await client.get(f"{self.PREFIX}/{0}/tasks")

        assert response.status_code == 401

    async def test_get_all_tasks_403(self, client, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()

        response = await client.get(
            f"{self.PREFIX}/{team.id}/tasks",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_get_all_tasks_404(self, client, factory):
        user, _, access_token = await factory.user()

        response = await client.get(
            f"{self.PREFIX}/{0}/tasks",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_all_tasks_422(self, client, factory):
        user, _, access_token = await factory.user()

        response = await client.get(
            f"{self.PREFIX}/{'a'}/tasks",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_create_task_201(
        self, client, factory, task_create_payload: TaskCreateSchema
    ):
        user, team, access_token = await factory.user_team_membership(UserRole.MANAGER)

        response = await client.post(
            f"{self.PREFIX}/{team.id}/tasks",
            json=task_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        assert data.get("team_id") == team.id
        assert data.get("assignee_id") == user.id
        assert data.get("status") == TaskStatus.OPEN

    async def test_create_task_401(self, client, task_create_payload: TaskCreateSchema):
        response = await client.post(
            f"{self.PREFIX}/{0}/tasks",
            json=task_create_payload.model_dump(mode="json"),
        )

        assert response.status_code == 401

    async def test_create_task_403_role_is_user(
        self, client, factory, task_create_payload: TaskCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.USER)
        response = await client.post(
            f"{self.PREFIX}/{0}/tasks",
            json=task_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_create_task_403_not_a_team_member(
        self, client, factory, task_create_payload: TaskCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.post(
            f"{self.PREFIX}/{team.id}/tasks",
            json=task_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_create_task_404(
        self, client, factory, task_create_payload: TaskCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        response = await client.post(
            f"{self.PREFIX}/{0}/tasks",
            json=task_create_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_create_task_422(
        self, client, factory, task_create_payload: TaskCreateSchema
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        payload = task_create_payload.model_dump(mode="json")
        payload["title"] = 123

        response = await client.post(
            f"{self.PREFIX}/{0}/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_get_task_200(self, client, factory):
        user, team, access_token = await factory.user_team_membership()

        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.get(
            f"{self.PREFIX}/{team.id}/tasks/{task.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == task.id
        assert data.get("assignee_id") == user.id
        assert data.get("team_id") == team.id
        assert data.get("evaluation") is None

    async def test_get_task_401(self, client):
        response = await client.get(
            f"{self.PREFIX}/{0}/tasks/{0}",
        )

        assert response.status_code == 401

    async def test_get_task_403_user_not_a_team_member(self, client, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.get(
            f"{self.PREFIX}/{team.id}/tasks/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_get_task_404(self, client, factory):
        user, team, access_token = await factory.user_team_membership(UserRole.MANAGER)

        response = await client.get(
            f"{self.PREFIX}/{team.id}/tasks/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_task_422(self, client, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        response = await client.get(
            f"{self.PREFIX}/{'a'}/tasks/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_update_task_200(
        self, client, factory, task_update_payload: TaskUpdateSchema
    ):
        _, member, team, access_token, task = await factory.manager_team_member_task()

        task_update_payload.assignee_id = member.id

        response = await client.patch(
            f"{self.PREFIX}/{team.id}/tasks/{task.id}",
            json=task_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == task.id
        assert data.get("assignee_id") == member.id
        assert data.get("title") == task_update_payload.title
        assert data.get("description") == task_update_payload.description
        assert data.get("status") == task_update_payload.status

    async def test_update_task_401(self, client, task_update_payload):
        response = await client.patch(
            f"{self.PREFIX}/{1}/tasks/{1}",
            json=task_update_payload.model_dump(mode="json"),
        )

        assert response.status_code == 401

    async def test_update_task_403_role_is_user(
        self, client, factory, task_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.USER)
        response = await client.patch(
            f"{self.PREFIX}/{1}/tasks/{1}",
            json=task_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_update_task_403_not_a_team_member(
        self, client, factory, task_update_payload
    ):
        user, _, access_token = await factory.user(UserRole.MANAGER)
        team = await factory.team()
        response = await client.patch(
            f"{self.PREFIX}/{team.id}/tasks/{1}",
            json=task_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_update_task_404(self, client, factory, task_update_payload):
        user, team, access_token = await factory.user_team_membership(UserRole.MANAGER)

        response = await client.patch(
            f"{self.PREFIX}/{team.id}/tasks/{1}",
            json=task_update_payload.model_dump(mode="json"),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_update_task_422(self, client, factory, task_update_payload):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        payload = task_update_payload.model_dump(mode="json")
        payload["title"] = 123

        response = await client.patch(
            f"{self.PREFIX}/{1}/tasks/{1}",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_delete_task_204(self, client, factory):
        user, team, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/tasks/{task.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    async def test_delete_task_401(self, client):
        response = await client.delete(f"{self.PREFIX}/{0}/tasks/{0}")

        assert response.status_code == 401

    async def test_delete_task_403_role_is_user(self, client, factory):
        user, _, access_token = await factory.user(role=UserRole.USER)

        response = await client.delete(
            f"{self.PREFIX}/{1}/tasks/{1}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_delete_task_403_not_a_team_member(self, client, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/tasks/{1}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_delete_task_404(self, client, factory):
        user, team, access_token = await factory.user_team_membership(UserRole.MANAGER)

        response = await client.delete(
            f"{self.PREFIX}/{team.id}/tasks/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_delete_task_422(self, client, factory):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        response = await client.delete(
            f"{self.PREFIX}/{'a'}/tasks/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_create_evaluation_201(
        self,
        client: AsyncClient,
        factory,
        evaluation_create_payload: EvaluationCreateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

    async def test_create_evaluation_401(self, client: AsyncClient):
        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{1}/evaluation",
        )

        assert response.status_code == 401

    async def test_create_evaluation_403_role_is_user(
        self,
        client: AsyncClient,
        factory,
        evaluation_create_payload: EvaluationCreateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.USER
        )

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_create_evaluation_403_not_a_team_member(
        self,
        client: AsyncClient,
        factory,
        evaluation_create_payload: EvaluationCreateSchema,
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()

        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_create_evaluation_404(
        self,
        client: AsyncClient,
        factory,
        evaluation_create_payload: EvaluationCreateSchema,
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{0}/evaluation",
            json=evaluation_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_create_evaluation_409(
        self,
        client: AsyncClient,
        factory,
        evaluation_create_payload: EvaluationCreateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        await factory.evaluation(
            manager_id=user.id,
            task_id=task.id,
        )

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 409

    async def test_create_evaluation_422(
        self,
        client: AsyncClient,
        factory,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        payload = {"score": 6}

        response = await client.post(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_update_evaluation_200(
        self,
        client: AsyncClient,
        factory,
        evaluation_update_payload: EvaluationUpdateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        await factory.evaluation(
            manager_id=user.id,
            task_id=task.id,
        )

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["score"] == evaluation_update_payload.score
        assert data["comment"] == evaluation_update_payload.comment

    async def test_update_evaluation_401(self, client: AsyncClient):
        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{1}/evaluation",
        )

        assert response.status_code == 401

    async def test_update_evaluation_403_role_is_user(
        self,
        client: AsyncClient,
        factory,
        evaluation_update_payload: EvaluationUpdateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.USER
        )

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "Manager or admin role required"

    async def test_update_evaluation_403_not_a_team_member(
        self,
        client: AsyncClient,
        factory,
        evaluation_update_payload: EvaluationUpdateSchema,
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)
        team = await factory.team()

        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_update_evaluation_404_task_not_found(
        self,
        client: AsyncClient,
        factory,
        evaluation_update_payload: EvaluationUpdateSchema,
    ):
        user, _, access_token = await factory.user(role=UserRole.MANAGER)

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{0}/evaluation",
            json=evaluation_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "Task not found"

    async def test_update_evaluation_404_evaluation_not_found(
        self,
        client: AsyncClient,
        factory,
        evaluation_update_payload: EvaluationUpdateSchema,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=evaluation_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "Evaluation not found"

    async def test_update_evaluation_422(
        self,
        client: AsyncClient,
        factory,
    ):
        user, _, access_token, task = await factory.user_team_membership_task(
            UserRole.MANAGER
        )

        payload = {"score": 6}

        response = await client.patch(
            f"{self.PREFIX_EVALUATION}/{task.id}/evaluation",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422
