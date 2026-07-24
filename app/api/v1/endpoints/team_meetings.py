from fastapi import APIRouter

router = APIRouter(
    prefix="/teams/{team_id}/meetings",
    tags=["Tasks"],
)


@router.get("/")
async def get_meetings(
    team_id: int,
): ...


@router.post("/")
async def create_meetings(
    team_id: int,
): ...


@router.patch("/")
async def update_meetings(
    team_id: int,
): ...


@router.delete("/")
async def delete_meetings(
    team_id: int,
): ...
