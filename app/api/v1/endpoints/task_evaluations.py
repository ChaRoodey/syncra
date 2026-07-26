from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_task_service, require_manager
from app.models.user import UserModel
from app.schemas.task import EvaluationCreateSchema, EvaluationUpdateSchema
from app.services.task import TaskService

router = APIRouter(
    prefix="/tasks/{task_id}/evaluation",
    tags=["Evaluations"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    task_id: int,
    data: EvaluationCreateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(require_manager),
):
    await service.create_evaluation(task_id, user.id, data)


@router.patch("")
async def update_evaluation(
    task_id: int,
    data: EvaluationUpdateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(require_manager),
):
    return await service.update_evaluation(task_id, user.id, data)
