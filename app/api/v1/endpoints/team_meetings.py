from fastapi import APIRouter, Depends, status

from app.api.v1.deps import get_current_auth_user, get_meeting_service, require_manager
from app.models.user import UserModel
from app.schemas.meeting import MeetingCreateSchema, MeetingUpdateSchema
from app.services.meeting import MeetingService

router_meeting = APIRouter(
    prefix="/teams/{team_id}/meetings",
    tags=["Meetings"],
)

router_meeting_id = APIRouter(
    prefix="/{meeting_id}",
    tags=["Meetings"],
)

router_meeting_members = APIRouter(
    prefix="/members",
    tags=["Meeting Participants"],
)

router_meeting.include_router(router_meeting_id)
router_meeting_id.include_router(router_meeting_members)


@router_meeting.get("")
async def get_all_meetings(
    team_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    return await service.get_all_meetings(team_id, user.id)


@router_meeting.post("", status_code=status.HTTP_201_CREATED)
async def create_meetings(
    team_id: int,
    data: MeetingCreateSchema,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    return await service.create_meeting(team_id, user.id, data)


@router_meeting_id.get("")
async def get_meeting_by_id(
    team_id: int,
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_meeting_by_id(team_id, meeting_id, user.id)


@router_meeting_id.patch("")
async def update_meetings(
    team_id: int,
    meeting_id: int,
    data: MeetingUpdateSchema,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    return await service.update_meeting(team_id, meeting_id, user.id, data)


@router_meeting_id.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meetings(
    team_id: int,
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    await service.delete_meeting(team_id, meeting_id, user.id)


@router_meeting_members.get("")
async def get_meeting_participants(
    team_id: int,
    meeting_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_meeting_participants(team_id, meeting_id, user.id)


@router_meeting_members.post("/{participant_id}", status_code=status.HTTP_201_CREATED)
async def add_meeting_participant(
    team_id: int,
    meeting_id: int,
    participant_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    await service.add_meeting_participant(team_id, meeting_id, user.id, participant_id)


@router_meeting_members.delete(
    "/{participant_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_meeting_participant(
    team_id: int,
    meeting_id: int,
    participant_id: int,
    service: MeetingService = Depends(get_meeting_service),
    user: UserModel = Depends(require_manager),
):
    await service.remove_meeting_participant(
        team_id, meeting_id, user.id, participant_id
    )
