from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.deps import get_current_auth_user, get_team_service, require_manager
from app.models.user import UserModel
from app.schemas.team import TeamNameSchema, TeamSchema
from app.services.team import TeamService

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TeamSchema)
async def create_team(
    data: TeamNameSchema,
    service: TeamService = Depends(get_team_service),
    user: UserModel = Depends(require_manager),
):
    return await service.create(data, user)


@router.post("/{team_id}/join", status_code=status.HTTP_201_CREATED)
async def join_team(
    team_id: int,
    service: TeamService = Depends(get_team_service),
    user: UserModel = Depends(get_current_auth_user),
):
    await service.join(team_id, user)


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: int,
    service: TeamService = Depends(get_team_service),
    user: UserModel = Depends(get_current_auth_user),
):
    members = await service.get_all_members(team_id, user)
    return members


@router.delete(
    "/{team_id}/remove_member/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_team_member(
    team_id: int,
    user_id: int,
    service: TeamService = Depends(get_team_service),
    user: UserModel = Depends(require_manager),
):
    return await service.remove_member(team_id, user_id)
