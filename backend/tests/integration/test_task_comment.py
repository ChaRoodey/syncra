import pytest

from app.core.enums import UserRole
from app.schemas.task_comment import TaskCommentCreateSchema, TaskCommentUpdateSchema


@pytest.mark.integration
@pytest.mark.comments
class TestTaskComments:
    PREFIX = "/api/v1/tasks"

    async def test_get_all_task_comments_200(self, client, factory):
        task_comments_amount = 3

        user, _, access_token, task = await factory.user_team_membership_task()

        task_comments = []

        for i in range(task_comments_amount):
            comment = await factory.comment(
                task_id=task.id,
                author_id=user.id,
            )
            task_comments.append(comment)

        response = await client.get(
            f"{self.PREFIX}/{task.id}/comments",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == task_comments_amount

        expected_ids = {comment.id for comment in task_comments}
        returned_ids = {comment["id"] for comment in data}

        assert returned_ids == expected_ids

    async def test_get_all_task_comments_401(self, client):
        response = await client.get(f"{self.PREFIX}/{1}/comments")

        assert response.status_code == 401

    async def test_get_all_task_comments_403(self, client, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()

        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.get(
            f"{self.PREFIX}/{task.id}/comments",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

    async def test_get_all_task_comments_404(self, client, factory):
        _, _, access_token = await factory.user_team_membership()

        response = await client.get(
            f"{self.PREFIX}/{0}/comments",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_all_task_comments_422(self, client, factory):
        _, _, access_token = await factory.user()

        response = await client.get(
            f"{self.PREFIX}/{'a'}/comments",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_create_task_comment_201(
        self, client, factory, task_comment_create_payload: TaskCommentCreateSchema
    ):
        user, _, access_token, task = await factory.user_team_membership_task()

        response = await client.post(
            f"{self.PREFIX}/{task.id}/comments",
            json=task_comment_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 201

        data = response.json()

        assert data.get("task_id") == task.id
        assert data.get("author_id") == user.id

    async def test_create_task_401(
        self, client, task_comment_create_payload: TaskCommentCreateSchema
    ):
        response = await client.post(
            f"{self.PREFIX}/{0}/comments",
            json=task_comment_create_payload.model_dump(),
        )

        assert response.status_code == 401

    async def test_create_task_comment_403_not_a_team_member(
        self, client, factory, task_comment_create_payload: TaskCommentCreateSchema
    ):
        user, _, access_token = await factory.user()
        team = await factory.team()
        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.post(
            f"{self.PREFIX}/{task.id}/comments",
            json=task_comment_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_create_task_comment_404(
        self, client, factory, task_comment_create_payload: TaskCommentCreateSchema
    ):
        _, _, access_token = await factory.user_team_membership()

        response = await client.post(
            f"{self.PREFIX}/{0}/comments",
            json=task_comment_create_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_create_task_comment_422(self, client, factory):
        user, _, access_token = await factory.user(UserRole.MANAGER)

        payload = {"title": 123}

        response = await client.post(
            f"{self.PREFIX}/{0}/comments",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_get_task_comment_by_id_200(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        response = await client.get(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == comment.id
        assert data.get("author_id") == user.id
        assert data.get("task_id") == task.id

    async def test_get_task_comment_by_id_401(self, client):
        response = await client.get(
            f"{self.PREFIX}/{0}/comments/{0}",
        )

        assert response.status_code == 401

    async def test_get_task_comment_by_id_403_user_not_a_team_member(
        self, client, factory
    ):
        user, _, access_token = await factory.user()
        team = await factory.team()
        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        response = await client.get(
            f"{self.PREFIX}/{task.id}/comments/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_get_task_comment_by_id_404(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        response = await client.get(
            f"{self.PREFIX}/{task.id}/comments/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_get_task_comment_by_id_422(self, client, factory):
        _, _, access_token = await factory.user_team_membership()

        response = await client.get(
            f"{self.PREFIX}/{'a'}/comments/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_update_task_comment_200(
        self, client, factory, task_comment_update_payload: TaskCommentUpdateSchema
    ):
        user, _, access_token, task = await factory.user_team_membership_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        response = await client.patch(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            json=task_comment_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data.get("id") == comment.id
        assert data.get("author_id") == user.id
        assert data.get("task_id") == task.id
        assert data.get("text") == task_comment_update_payload.text

    async def test_update_task_comment_401(
        self, client, task_comment_update_payload: TaskCommentUpdateSchema
    ):
        response = await client.patch(
            f"{self.PREFIX}/{1}/comments/{1}",
            json=task_comment_update_payload.model_dump(),
        )

        assert response.status_code == 401

    async def test_update_task_comment_403_user_not_owner(
        self, client, factory, task_comment_update_payload: TaskCommentUpdateSchema
    ):
        (
            curr_user,
            member,
            _,
            access_token,
            task,
        ) = await factory.manager_team_member_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=member.id,
        )

        response = await client.patch(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            json=task_comment_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "You do not have permission to perform this action"

    async def test_update_task_comment_403_not_a_team_member(
        self, client, factory, task_comment_update_payload: TaskCommentUpdateSchema
    ):
        user, _, access_token = await factory.user()
        team = await factory.team()
        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        response = await client.patch(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            json=task_comment_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_update_task_comment_404(
        self, client, factory, task_comment_update_payload: TaskCommentUpdateSchema
    ):
        _, _, access_token, task = await factory.user_team_membership_task()

        response = await client.patch(
            f"{self.PREFIX}/{task.id}/comments/{0}",
            json=task_comment_update_payload.model_dump(),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_update_task_comment_422(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        payload = {"title": 123}

        response = await client.patch(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            json=payload,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

    async def test_delete_task_comment_204(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        response = await client.delete(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

    async def test_delete_task_comment_401(self, client):
        response = await client.delete(f"{self.PREFIX}/{0}/comments/{0}")

        assert response.status_code == 401

    async def test_delete_task_comment_403_user_not_owner(self, client, factory):
        (
            curr_user,
            member,
            _,
            access_token,
            task,
        ) = await factory.manager_team_member_task()

        comment = await factory.comment(
            task_id=task.id,
            author_id=member.id,
        )

        response = await client.delete(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "You do not have permission to perform this action"

    async def test_delete_task_comment_403_not_a_team_member(self, client, factory):
        user, _, access_token = await factory.user()
        team = await factory.team()
        task = await factory.task(
            team_id=team.id,
            assignee_id=user.id,
        )

        comment = await factory.comment(
            task_id=task.id,
            author_id=user.id,
        )

        response = await client.delete(
            f"{self.PREFIX}/{task.id}/comments/{comment.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 403

        data = response.json()
        assert data["detail"] == "User are not a team member"

    async def test_delete_task_comment_404(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        response = await client.delete(
            f"{self.PREFIX}/{task.id}/comments/{0}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404

    async def test_delete_task_comment_422(self, client, factory):
        user, _, access_token, task = await factory.user_team_membership_task()

        response = await client.delete(
            f"{self.PREFIX}/{'a'}/comments/{'a'}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422
