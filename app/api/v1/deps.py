from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import decode_jwt
from app.core.enums import UserRole
from app.db.session import get_db_session
from app.models.user import UserModel
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.schemas.token import TokenPayload
from app.services.auth import AuthService
from app.services.team import TeamService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(session)


async def get_team_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TeamRepository:
    return TeamRepository(session)


async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_team_service(
    repo: TeamRepository = Depends(get_team_repository),
) -> TeamService:
    return TeamService(repo)


async def get_current_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserModel:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials

    try:
        payload: TokenPayload = decode_jwt(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
        )

    user_id = int(payload.sub)

    user = await user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or not found",
        )

    return user


async def require_manager(
    user: UserModel = Depends(get_current_auth_user),
) -> UserModel:
    if user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin role required",
        )

    return user
