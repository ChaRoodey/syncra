from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_auth_user, get_task_service, require_manager
from app.models.user import UserModel
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task import TaskService

router_tasks = APIRouter(
    prefix="/teams/{team_id}/tasks",
    tags=["Tasks"],
)

router_task = APIRouter(
    prefix="/{task_id}",
    tags=["Tasks"],
)

router_tasks.include_router(router_task)


@router_tasks.get("")
async def get_all_tasks(
    team_id: int,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_all_tasks(team_id, user.id)


@router_tasks.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    team_id: int,
    data: TaskCreateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(require_manager),
):
    return await service.create_task(team_id, user.id, data)


@router_task.get("", response_model=TaskSchema)
async def get_task(
    team_id: int,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_task_by_id(team_id, task_id, user.id)


@router_task.patch("")
async def update_task(
    team_id: int,
    task_id: int,
    data: TaskUpdateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(require_manager),
):
    return await service.update_task(team_id, task_id, user.id, data)


@router_task.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    team_id: int,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(require_manager),
):
    await service.delete_task(team_id, task_id, user.id)
