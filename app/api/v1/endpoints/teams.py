from fastapi import APIRouter

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post("/")
async def create_team(): ...


@router.post("/{id}/join")
async def join_team(
    team_id: int,
): ...


@router.get("/{id}/members")
async def get_team_members(
    team_id: int,
): ...


@router.get("/{id}/tasks")
async def get_tasks(
    team_id: int,
): ...


@router.post("/{id}/tasks")
async def create_tasks(
    team_id: int,
): ...


@router.patch("/{id}/tasks")
async def update_tasks(
    team_id: int,
): ...


@router.delete("/{id}/tasks")
async def delete_tasks(
    team_id: int,
): ...


@router.get("/{id}/meetings")
async def get_meetings(
    team_id: int,
): ...


@router.post("/{id}/meetings")
async def create_meetings(
    team_id: int,
): ...


@router.patch("/{id}/meetings")
async def update_meetings(
    team_id: int,
): ...


@router.delete("/{id}/meetings")
async def delete_meetings(
    team_id: int,
): ...
