from fastapi import HTTPException, status

from app.models.meeting import MeetingModel
from app.repositories.meeting import MeetingRepository


class MeetingPermissionService:
    def __init__(self, meeting_repo: MeetingRepository):
        self.meeting_repo = meeting_repo

    async def require_meeting(self, team_id: int, meeting_id: int) -> MeetingModel:
        meeting = await self.meeting_repo.get_meeting_by_id(team_id, meeting_id)

        if meeting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found",
            )

        return meeting

    async def require_participation(self, meeting_id: int, user_id: int) -> None:
        if not await self.meeting_repo.is_participant(meeting_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a participant",
            )

    async def require_not_participation(self, meeting_id: int, user_id: int) -> None:
        if await self.meeting_repo.is_participant(meeting_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a participant",
            )
