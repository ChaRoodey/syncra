from app.models.task_comment import TaskCommentModel
from app.repositories.task_comment import TaskCommentRepository
from app.schemas.task_comment import (
    TaskCommentCreateSchema,
    TaskCommentSchema,
    TaskCommentUpdateSchema,
)
from app.services.permissions.task import TaskPermissionService
from app.services.permissions.task_comment import TaskCommentPermissionService
from app.services.permissions.team import TeamPermissionService


class TaskCommentService:
    def __init__(
        self,
        task_comment_repo: TaskCommentRepository,
        team_permission: TeamPermissionService,
        task_permission: TaskPermissionService,
        task_comment_permission: TaskCommentPermissionService,
    ):
        self.task_comment_repo = task_comment_repo
        self.team_permission = team_permission
        self.task_permission = task_permission
        self.task_comment_permission = task_comment_permission

    async def check_task_and_membership(self, task_id: int, curr_user_id: int) -> None:
        task = await self.task_permission.require_task_by_id(task_id)
        await self.team_permission.require_membership(task.team_id, curr_user_id)

    async def get_all_task_comments(
        self, task_id: int, curr_user_id: int
    ) -> list[TaskCommentSchema]:
        await self.check_task_and_membership(task_id, curr_user_id)

        task_comments = await self.task_comment_repo.get_all_task_comments(task_id)

        return [
            TaskCommentSchema.model_validate(task_comment)
            for task_comment in task_comments
        ]

    async def create_task_comment(
        self, task_id: int, curr_user_id: int, data: TaskCommentCreateSchema
    ) -> TaskCommentSchema:
        await self.check_task_and_membership(task_id, curr_user_id)

        new_task_comment = await self.task_comment_repo.create_task_comment(
            TaskCommentModel(
                author_id=curr_user_id,
                task_id=task_id,
                **data.model_dump(),
            )
        )

        return TaskCommentSchema.model_validate(new_task_comment)

    async def get_task_comment_by_id(
        self,
        task_id: int,
        curr_user_id: int,
        task_comment_id: int,
    ) -> TaskCommentSchema:
        await self.check_task_and_membership(task_id, curr_user_id)
        task_comment = await self.task_comment_permission.require_task_comment(
            task_id, task_comment_id
        )

        return TaskCommentSchema.model_validate(task_comment)

    async def update_task_comment(
        self,
        task_id: int,
        task_comment_id: int,
        curr_user_id: int,
        data: TaskCommentUpdateSchema,
    ) -> TaskCommentSchema:
        await self.check_task_and_membership(task_id, curr_user_id)
        task_comment = await self.task_comment_permission.require_task_comment(
            task_id, task_comment_id
        )
        self.task_comment_permission.require_comment_ownership(
            curr_user_id, task_comment.author_id
        )

        updated_task_comment = await self.task_comment_repo.update_task_comment(
            task_id,
            task_comment_id,
            data.model_dump(exclude_none=True),
        )

        return TaskCommentSchema.model_validate(updated_task_comment)

    async def delete_task_comment(
        self, task_id: int, task_comment_id: int, curr_user_id: int
    ) -> None:
        await self.check_task_and_membership(task_id, curr_user_id)
        task_comment = await self.task_comment_permission.require_task_comment(
            task_id, task_comment_id
        )

        self.task_comment_permission.require_comment_ownership(
            curr_user_id, task_comment.author_id
        )

        await self.task_comment_repo.delete_task_comment(task_id, task_comment_id)
