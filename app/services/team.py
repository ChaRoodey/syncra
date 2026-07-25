import logging
import secrets

from fastapi import HTTPException
from starlette import status

from app.models.team import TeamModel
from app.models.user import UserModel
from app.repositories.team import TeamRepository
from app.schemas.team import TeamNameSchema
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

    async def create(self, data: TeamNameSchema, user: UserModel) -> TeamModel:
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
        await self.team_repo.add_member(team.id, user.id)

        return team

    async def join(self, team_id: int, user: UserModel) -> None:
        await self.team_permission.require_team(team_id)

        if await self.team_repo.is_member(team_id, user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already in this team",
            )

        await self.team_repo.add_member(team_id, user.id)

    async def get_all_members(
        self, team_id: int, user: UserModel
    ) -> list[UserReadSchema]:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, user.id)

        members = await self.team_repo.get_members(team_id)
        return [UserReadSchema.model_validate(member) for member in members]

    async def remove_member(self, team_id: int, user_id: int) -> None:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, user_id)
        await self.team_repo.remove_member(team_id, user_id)
