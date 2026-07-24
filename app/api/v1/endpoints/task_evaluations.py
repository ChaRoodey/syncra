from fastapi import APIRouter

router = APIRouter(
    prefix="/tasks/{task_id}/evaluation",
    tags=["Evaluations"],
)


@router.post("/")
async def create_evaluation(
    task_id: int,
): ...
