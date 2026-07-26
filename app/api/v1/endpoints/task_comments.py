from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_auth_user, get_task_comment_service
from app.models.user import UserModel
from app.schemas.task_comment import (
    TaskCommentCreateSchema,
    TaskCommentSchema,
    TaskCommentUpdateSchema,
)
from app.services.task_comment import TaskCommentService

router_comments = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Comments"],
)

router_comments_id = APIRouter(
    prefix="/{task_comment_id}",
    tags=["Comments"],
)

router_comments.include_router(router_comments_id)


@router_comments.get("")
async def get_all_task_comments(
    task_id: int,
    service: TaskCommentService = Depends(get_task_comment_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_all_task_comments(task_id, user.id)


@router_comments.post("", status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: int,
    data: TaskCommentCreateSchema,
    service: TaskCommentService = Depends(get_task_comment_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.create_task_comment(task_id, user.id, data)


@router_comments_id.get("", response_model=TaskCommentSchema)
async def get_task_comment_by_id(
    task_id: int,
    task_comment_id: int,
    service: TaskCommentService = Depends(get_task_comment_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_task_comment_by_id(
        task_id,
        user.id,
        task_comment_id,
    )


@router_comments_id.patch("")
async def update_task_comment(
    task_id: int,
    task_comment_id: int,
    data: TaskCommentUpdateSchema,
    service: TaskCommentService = Depends(get_task_comment_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.update_task_comment(task_id, task_comment_id, user.id, data)


@router_comments_id.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_comment(
    task_id: int,
    task_comment_id: int,
    service: TaskCommentService = Depends(get_task_comment_service),
    user: UserModel = Depends(get_current_auth_user),
):
    await service.delete_task_comment(task_id, task_comment_id, user.id)
