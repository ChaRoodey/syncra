from fastapi import HTTPException, status

from app.models.task_comment import TaskCommentModel
from app.repositories.task_comment import TaskCommentRepository


class TaskCommentPermissionService:
    def __init__(self, task_repo: TaskCommentRepository):
        self.task_repo = task_repo

    @staticmethod
    def require_comment_ownership(user_id: int, author_id: int) -> None:
        if user_id != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

    async def require_task_comment(
        self, task_id: int, task_comment_id: int
    ) -> TaskCommentModel:
        task_comment = await self.task_repo.get_task_comment_by_id(
            task_id, task_comment_id
        )

        if task_comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task comment not found",
            )

        return task_comment

    async def not_require_task_comment(
        self, task_id: int, task_comment_id: int
    ) -> None:
        task_comment = await self.task_repo.get_task_comment_by_id(
            task_id, task_comment_id
        )

        if task_comment is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task comment not found",
            )
