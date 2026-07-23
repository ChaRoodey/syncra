import logging

from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.auth.utils import (
    check_password,
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
)
from app.models.user import UserModel
from app.repositories.user import UserRepository
from app.scheams.token import TokenPair
from app.scheams.user import LoginSchema, RegisterSchema

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, data: LoginSchema) -> TokenPair:
        user = await self.user_repo.get_by_username(data.username)

        if not user or not check_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def register(self, data: RegisterSchema) -> None:
        existing = await self.user_repo.get_by_username(data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

        user = UserModel(
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        await self.user_repo.create_user(user)

    async def refresh(self, refresh_token: str) -> str:
        try:
            payload = decode_jwt(refresh_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token type",
            )

        user_id = int(payload.sub)

        user = await self.user_repo.get_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found",
            )

        return create_access_token(user.id)
