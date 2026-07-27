from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_auth_user
from app.models.user import UserModel
from app.schemas.user import UserReadSchema

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserReadSchema)
async def get_curr_user(user: UserModel = Depends(get_current_auth_user)):
    return user
