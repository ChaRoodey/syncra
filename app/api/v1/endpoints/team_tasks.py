from fastapi import APIRouter

router = APIRouter(
    prefix="/teams/{team_id}/tasks",
    tags=["Tasks"],
)


@router.get("/")
async def get_tasks(
    team_id: int,
): ...


@router.post("/")
async def create_tasks(
    team_id: int,
): ...


@router.patch("/")
async def update_tasks(
    team_id: int,
): ...


@router.delete("/")
async def delete_tasks(
    team_id: int,
): ...
