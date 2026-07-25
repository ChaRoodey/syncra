from fastapi import HTTPException, status

from app.models.task import TaskModel
from app.repositories.task import TaskRepository


class TaskPermissionService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def require_task(self, team_id: int, task_id: int) -> TaskModel:
        task = await self.task_repo.get_task_by_id(team_id, task_id)

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        return task
