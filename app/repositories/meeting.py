import logging
from datetime import datetime

from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import MeetingModel
from app.models.meeting_participant import MeetingParticipantModel
from app.models.user import UserModel

logger = logging.getLogger(__name__)


class MeetingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_meeting(self, meeting: MeetingModel) -> MeetingModel:
        self.session.add(meeting)
        await self.session.flush()
        return meeting

    async def get_meeting_by_id(
        self, team_id: int, meeting_id: int
    ) -> MeetingModel | None:
        stmt = select(MeetingModel).where(
            MeetingModel.id == meeting_id,
            MeetingModel.team_id == team_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_meetings(self, team_id: int) -> list[MeetingModel] | None:
        stmt = select(MeetingModel).where(MeetingModel.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_all_meetings_by_participant_id(
        self, participant_id: int, start: datetime, end: datetime
    ) -> list[MeetingModel] | None:
        stmt = (
            select(MeetingModel)
            .join(MeetingParticipantModel)
            .where(
                MeetingParticipantModel.user_id == participant_id,
                MeetingModel.starts_at <= end,
                MeetingModel.ends_at >= start,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def update_meeting(
        self, team_id: int, meeting_id: int, data: dict
    ) -> MeetingModel | None:
        stmt = (
            update(MeetingModel)
            .where(
                MeetingModel.id == meeting_id,
                MeetingModel.team_id == team_id,
            )
            .values(**data)
            .returning(MeetingModel)
        )

        updated_meeting = await self.session.execute(stmt)
        await self.session.flush()

        return updated_meeting.scalar_one_or_none()

    async def delete_meeting(self, team_id: int, meeting_id: int) -> None:
        stmt = delete(MeetingModel).where(
            MeetingModel.id == meeting_id,
            MeetingModel.team_id == team_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()

    async def get_participants(self, meeting_id: int) -> list[UserModel]:
        stmt = (
            select(UserModel)
            .join(MeetingParticipantModel)
            .where(MeetingParticipantModel.meeting_id == meeting_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def add_participant(
        self, meeting_id: int, user_id: int
    ) -> MeetingParticipantModel:
        meeting_participant = MeetingParticipantModel(
            meeting_id=meeting_id, user_id=user_id
        )

        self.session.add(meeting_participant)
        await self.session.flush()
        return meeting_participant

    async def remove_participant(self, meeting_id: int, user_id: int) -> None:
        stmt = delete(MeetingParticipantModel).where(
            MeetingParticipantModel.meeting_id == meeting_id,
            MeetingParticipantModel.user_id == user_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()

    async def is_participant(self, meeting_id: int, user_id: int) -> bool:
        stmt = select(
            exists().where(
                MeetingParticipantModel.user_id == user_id,
                MeetingParticipantModel.meeting_id == meeting_id,
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar()
