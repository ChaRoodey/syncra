import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import TaskModel

logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskModel) -> TaskModel:
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_task_by_id(self, team_id: int, task_id: int) -> TaskModel | None:
        stmt = select(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.team_id == team_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_task_by_id_without_team(self, task_id: int) -> TaskModel | None:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tasks(self, team_id: int) -> list[TaskModel] | None:
        stmt = select(TaskModel).where(TaskModel.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def update_task(
        self, team_id: int, task_id: int, data: dict
    ) -> TaskModel | None:
        stmt = (
            update(TaskModel)
            .where(
                TaskModel.id == task_id,
                TaskModel.team_id == team_id,
            )
            .values(**data)
            .returning(TaskModel)
        )

        updated_task = await self.session.execute(stmt)
        await self.session.flush()

        return updated_task.scalar_one_or_none()

    async def delete_task(self, team_id: int, task_id: int) -> None:
        stmt = delete(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.team_id == team_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()
