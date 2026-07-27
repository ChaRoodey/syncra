import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_comment import TaskCommentModel

logger = logging.getLogger(__name__)


class TaskCommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task_comment(
        self, task_comment: TaskCommentModel
    ) -> TaskCommentModel:
        self.session.add(task_comment)
        await self.session.flush()
        return task_comment

    async def get_task_comment_by_id(
        self, task_id: int, task_comment_id: int
    ) -> TaskCommentModel | None:
        stmt = select(TaskCommentModel).where(
            TaskCommentModel.id == task_comment_id,
            TaskCommentModel.task_id == task_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_task_comments(self, task_id: int) -> list[TaskCommentModel]:
        stmt = select(TaskCommentModel).where(TaskCommentModel.task_id == task_id)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def update_task_comment(
        self, task_id: int, task_comment_id: int, data: dict
    ) -> TaskCommentModel | None:
        stmt = (
            update(TaskCommentModel)
            .where(
                TaskCommentModel.id == task_comment_id,
                TaskCommentModel.task_id == task_id,
            )
            .values(**data)
            .returning(TaskCommentModel)
        )

        updated_task_comment = await self.session.execute(stmt)
        await self.session.flush()

        return updated_task_comment.scalar_one_or_none()

    async def delete_task_comment(self, task_id: int, task_comment_id: int) -> None:
        stmt = delete(TaskCommentModel).where(
            TaskCommentModel.id == task_comment_id,
            TaskCommentModel.task_id == task_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()
