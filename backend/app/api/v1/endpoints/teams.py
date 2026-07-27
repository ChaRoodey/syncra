from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_auth_user, get_team_service, require_manager
from app.models.user import UserModel
from app.schemas.team import TeamNameSchema, TeamSchema, TeamInviteCodeSchema
from app.services.team import TeamService

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.get("")
async def get_my_teams(
        service: TeamService = Depends(get_team_service),
        user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_all_by_user_id(user.id)


@router.get("/{team_id}")
async def get_team_by_id(
        team_id: int,
        service: TeamService = Depends(get_team_service),
        user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_by_id(team_id, user.id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TeamSchema)
async def create_team(
        data: TeamNameSchema,
        service: TeamService = Depends(get_team_service),
        user: UserModel = Depends(require_manager),
):
    return await service.create(data, user.id)


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_team(
        data: TeamInviteCodeSchema,
        service: TeamService = Depends(get_team_service),
        user: UserModel = Depends(get_current_auth_user),
):
    await service.join(user.id, data)


@router.get("/{team_id}/members")
async def get_team_members(
        team_id: int,
        service: TeamService = Depends(get_team_service),
        user: UserModel = Depends(get_current_auth_user),
):
    members = await service.get_all_members(team_id, user.id)
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
