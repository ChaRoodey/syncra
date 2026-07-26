from fastapi import HTTPException, status

from app.models.task import TaskModel
from app.repositories.task import TaskRepository


class TaskNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


class TaskPermissionService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def require_task(self, team_id: int, task_id: int) -> TaskModel:
        task = await self.task_repo.get_task_by_id(team_id, task_id)

        if task is None:
            raise TaskNotFoundException

        return task

    async def require_task_by_id(self, task_id: int) -> TaskModel:
        task = await self.task_repo.get_task_by_id_without_team(task_id)

        if task is None:
            raise TaskNotFoundException

        return task

    async def require_evaluation_exist(self, task: TaskModel) -> None:
        if task.evaluation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found",
            )

    async def require_evaluation_doesnt_exist(self, task: TaskModel) -> None:
        if task.evaluation is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Evaluation already exists",
            )
