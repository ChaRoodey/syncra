import logging
import secrets

from fastapi import HTTPException
from starlette import status

from app.models.team import TeamModel
from app.repositories.team import TeamRepository
from app.schemas.team import TeamNameSchema, TeamSchema, TeamInviteCodeSchema
from app.schemas.user import UserReadSchema
from app.services.permissions.team import TeamPermissionService

logger = logging.getLogger(__name__)


class TeamService:
    def __init__(
            self, team_repo: TeamRepository, team_permission: TeamPermissionService
    ):
        self.team_repo = team_repo
        self.team_permission = team_permission

    async def generate_invite_code(self) -> str:
        while True:
            invite_code = secrets.token_urlsafe(16)
            if await self.team_repo.get_by_invite_code(invite_code) is None:
                return invite_code

    async def get_all_by_user_id(self, user_id: int) -> list[TeamSchema]:
        teams = await self.team_repo.get_all_by_participant_id(user_id)

        return [TeamSchema.model_validate(team) for team in teams]

    async def get_by_id(self, team_id: int, user_id: int) -> TeamSchema:
        await self.team_permission.require_membership(team_id, user_id)
        team = await self.team_permission.require_team(team_id)

        return TeamSchema.model_validate(team)

    async def create(self, data: TeamNameSchema, user_id: int) -> TeamModel:
        if await self.team_repo.get_by_name(data.name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team already exists",
            )

        invite_code = await self.generate_invite_code()
        team = TeamModel(
            **data.model_dump(),
            invite_code=invite_code,
        )

        await self.team_repo.create(team)
        await self.team_repo.add_member(team.id, user_id)

        return team

    async def join(self, user_id: int, data: TeamInviteCodeSchema) -> None:
        team = await self.team_repo.get_by_invite_code(data.invite_code)

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team does not exist",
            )

        if await self.team_repo.is_member(team.id, user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already in this team",
            )

        await self.team_repo.add_member(team.id, user_id)

    async def get_all_members(
            self, team_id: int, user_id: int
    ) -> list[UserReadSchema]:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, user_id)

        members = await self.team_repo.get_members(team_id)
        return [UserReadSchema.model_validate(member) for member in members]

    async def remove_member(self, team_id: int, user_id: int) -> None:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, user_id)
        await self.team_repo.remove_member(team_id, user_id)
