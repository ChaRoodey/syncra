from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import get_calendar_service, get_current_auth_user
from app.models.user import UserModel
from app.services.calendar import CalendarService

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.get("")
async def get_calendar(
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    service: CalendarService = Depends(get_calendar_service),
    user: UserModel = Depends(get_current_auth_user),
):
    return await service.get_calendar(user.id, from_, to)
