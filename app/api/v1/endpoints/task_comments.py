from fastapi import APIRouter

router = APIRouter(
    prefix="/tasks/{task_id}/comments",
    tags=["Comments"],
)


@router.post("/")
async def create_comment(
    task_id: int,
): ...
