import logging

from fastapi import HTTPException, status

from app.models.meeting import MeetingModel
from app.repositories.meeting import MeetingRepository
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.schemas.meeting import MeetingCreateSchema, MeetingSchema, MeetingUpdateSchema
from app.schemas.user import UserReadSchema
from app.services.permissions.meeting import MeetingPermissionService
from app.services.permissions.team import TeamPermissionService

logger = logging.getLogger(__name__)


class MeetingService:
    def __init__(
        self,
        user_repo: UserRepository,
        team_repo: TeamRepository,
        meeting_repo: MeetingRepository,
        team_permission: TeamPermissionService,
        meeting_permission: MeetingPermissionService,
    ):
        self.user_repo = (user_repo,)
        self.team_repo = team_repo
        self.meeting_repo = meeting_repo
        self.team_permission = team_permission
        self.meeting_permission = meeting_permission

    async def get_all_meetings(
        self, team_id: int, curr_user_id: int
    ) -> list[MeetingSchema]:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, curr_user_id)

        meetings = await self.meeting_repo.get_all_meetings(team_id)

        return [MeetingSchema.model_validate(meeting) for meeting in meetings]

    async def get_meeting_by_id(
        self, team_id: int, meeting_id: int, curr_user_id: int
    ) -> MeetingSchema:
        await self.team_permission.require_membership(team_id, curr_user_id)
        meeting = await self.meeting_permission.require_meeting(team_id, meeting_id)

        return MeetingSchema.model_validate(meeting)

    async def create_meeting(
        self, team_id: int, curr_user_id: int, meeting: MeetingCreateSchema
    ) -> MeetingSchema:
        await self.team_permission.require_team(team_id)
        await self.team_permission.require_membership(team_id, curr_user_id)

        new_meeting = await self.meeting_repo.create_meeting(
            MeetingModel(
                author_id=curr_user_id,
                team_id=team_id,
                **meeting.model_dump(),
            )
        )

        return MeetingSchema.model_validate(new_meeting)

    async def update_meeting(
        self,
        team_id: int,
        meeting_id: int,
        curr_user_id: int,
        meeting: MeetingUpdateSchema,
    ) -> MeetingSchema:
        await self.team_permission.require_membership(team_id, curr_user_id)
        await self.meeting_permission.require_meeting(team_id, meeting_id)

        updated_meeting = await self.meeting_repo.update_meeting(
            team_id,
            meeting_id,
            meeting.model_dump(exclude_none=True),
        )

        if updated_meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="meeting not found",
            )

        return MeetingSchema.model_validate(updated_meeting)

    async def delete_meeting(
        self, team_id: int, meeting_id: int, curr_user_id: int
    ) -> None:
        await self.team_permission.require_membership(team_id, curr_user_id)
        await self.meeting_permission.require_meeting(team_id, meeting_id)

        await self.meeting_repo.delete_meeting(team_id, meeting_id)

    async def get_meeting_participants(
        self, team_id: int, meeting_id: int, curr_user_id: int
    ) -> list[UserReadSchema]:
        await self.team_permission.require_membership(team_id, curr_user_id)
        await self.meeting_permission.require_meeting(team_id, meeting_id)

        participants = await self.meeting_repo.get_participants(meeting_id)
        return [
            UserReadSchema.model_validate(participant) for participant in participants
        ]

    async def add_meeting_participant(
        self, team_id: int, meeting_id: int, manager_id: int, participant_id: int
    ) -> None:
        await self.team_permission.require_membership(team_id, manager_id)
        await self.meeting_permission.require_meeting(team_id, meeting_id)

        await self.team_permission.require_membership(team_id, participant_id)
        await self.meeting_permission.require_not_participation(
            meeting_id, participant_id
        )

        await self.meeting_repo.add_participant(meeting_id, participant_id)

    async def remove_meeting_participant(
        self, team_id: int, meeting_id: int, manager_id: int, participant_id: int
    ) -> None:
        await self.team_permission.require_membership(team_id, manager_id)
        await self.meeting_permission.require_meeting(team_id, meeting_id)

        await self.meeting_permission.require_participation(meeting_id, participant_id)

        await self.meeting_repo.remove_participant(meeting_id, participant_id)
