import logging

from fastapi import HTTPException, status

from app.models.task import TaskModel
from app.repositories.task import TaskRepository
from app.repositories.team import TeamRepository
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.permissions.task import TaskPermissionService
from app.services.permissions.team import TeamPermissionService

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        team_repo: TeamRepository,
        team_permission: TeamPermissionService,
        task_permission: TaskPermissionService,
    ):
        self.task_repo = task_repo
        self.team_repo = team_repo
        self.team_permission = team_permission
        self.task_permission = task_permission

    async def get_all_tasks(self, team_id: int, curr_user_id: int) -> list[TaskSchema]:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, curr_user_id)

        tasks = await self.task_repo.get_all_tasks(team_id)

        return [TaskSchema.model_validate(task) for task in tasks]

    async def get_task_by_id(
        self, team_id: int, task_id: int, curr_user_id: int
    ) -> TaskSchema:
        await self.team_permission.require_membership(team_id, curr_user_id)
        task = await self.task_permission.require_task(team_id, task_id)

        return TaskSchema.model_validate(task)

    async def create_task(
        self, team_id: int, curr_user_id: int, task: TaskCreateSchema
    ) -> TaskSchema:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, curr_user_id)

        new_task = await self.task_repo.create_task(
            TaskModel(
                assignee_id=curr_user_id,
                team_id=team_id,
                **task.model_dump(),
            )
        )

        return TaskSchema.model_validate(new_task)

    async def update_task(
        self, team_id: int, task_id: int, curr_user_id: int, task: TaskUpdateSchema
    ) -> TaskSchema:
        await self.team_permission.require_membership(team_id, curr_user_id)
        await self.task_permission.require_task(team_id, task_id)

        updated_task = await self.task_repo.update_task(
            team_id,
            task_id,
            task.model_dump(exclude_none=True),
        )

        if updated_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return TaskSchema.model_validate(updated_task)

    async def delete_task(self, team_id: int, task_id: int, curr_user_id: int) -> None:
        await self.team_permission.require_membership(team_id, curr_user_id)
        await self.task_permission.require_task(team_id, task_id)
        await self.task_repo.delete_task(team_id, task_id)
