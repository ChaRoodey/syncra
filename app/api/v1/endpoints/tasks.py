from fastapi import APIRouter

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/{id}/comments")
async def create_comment(
    task_id: int,
): ...


@router.post("/{id}/evaluation")
async def create_evaluation(
    task_id: int,
): ...
