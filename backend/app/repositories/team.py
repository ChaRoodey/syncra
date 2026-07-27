import logging

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import TeamModel
from app.models.team_member import TeamMemberModel
from app.models.user import UserModel

logger = logging.getLogger(__name__)


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, team: TeamModel) -> TeamModel:
        self.session.add(team)
        await self.session.flush()
        return team

    async def get_by_id(self, team_id: int) -> TeamModel | None:
        stmt = select(TeamModel).where(TeamModel.id == team_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> TeamModel | None:
        stmt = select(TeamModel).where(TeamModel.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_invite_code(self, invite_code: str) -> TeamModel | None:
        stmt = select(TeamModel).where(TeamModel.invite_code == invite_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_member(self, team_id: int, user_id: int) -> TeamMemberModel:
        team_member = TeamMemberModel(team_id=team_id, user_id=user_id)

        self.session.add(team_member)
        await self.session.flush()
        return team_member

    async def remove_member(self, team_id: int, user_id: int) -> None:
        stmt = delete(TeamMemberModel).where(
            TeamMemberModel.team_id == team_id,
            TeamMemberModel.user_id == user_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()

    async def get_members(self, team_id: int) -> list[UserModel]:
        stmt = (
            select(UserModel)
            .join(TeamMemberModel)
            .join(TeamModel)
            .where(TeamModel.id == team_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def is_member(self, team_id: int, user_id: int) -> bool:
        stmt = select(
            exists().where(
                TeamMemberModel.user_id == user_id,
                TeamMemberModel.team_id == team_id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_all_by_participant_id(self, participant_id: int) -> list[TeamModel]:
        stmt = (
            select(TeamModel)
            .join(TeamMemberModel)
            .where(TeamMemberModel.user_id == participant_id)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
