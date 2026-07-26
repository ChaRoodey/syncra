from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import decode_jwt
from app.core.enums import UserRole
from app.db.session import get_db_session
from app.models.user import UserModel
from app.repositories.meeting import MeetingRepository
from app.repositories.task import TaskRepository
from app.repositories.task_comment import TaskCommentRepository
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.schemas.token import TokenPayload
from app.services.auth import AuthService
from app.services.meeting import MeetingService
from app.services.permissions.meeting import MeetingPermissionService
from app.services.permissions.task import TaskPermissionService
from app.services.permissions.task_comment import TaskCommentPermissionService
from app.services.permissions.team import TeamPermissionService
from app.services.task import TaskService
from app.services.task_comment import TaskCommentService
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


async def get_task_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TaskRepository:
    return TaskRepository(session)


async def get_meeting_repository(
    session: AsyncSession = Depends(get_db_session),
) -> MeetingRepository:
    return MeetingRepository(session)


async def get_task_comment_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TaskCommentRepository:
    return TaskCommentRepository(session)


async def get_task_permission_service(
    task_repo: TaskRepository = Depends(get_task_repository),
) -> TaskPermissionService:
    return TaskPermissionService(task_repo)


async def get_team_permission_service(
    team_repo: TeamRepository = Depends(get_team_repository),
) -> TeamPermissionService:
    return TeamPermissionService(team_repo)


async def get_meeting_permission_service(
    meeting_repo: MeetingRepository = Depends(get_meeting_repository),
) -> MeetingPermissionService:
    return MeetingPermissionService(meeting_repo)


async def get_task_comment_permission_service(
    task_comment_repo: TaskCommentRepository = Depends(get_task_comment_repository),
) -> TaskCommentPermissionService:
    return TaskCommentPermissionService(task_comment_repo)


async def get_auth_service(
    repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


async def get_team_service(
    team_repo: TeamRepository = Depends(get_team_repository),
    team_permission: TeamPermissionService = Depends(get_team_permission_service),
) -> TeamService:
    return TeamService(team_repo, team_permission)


async def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    team_repo: TeamRepository = Depends(get_team_repository),
    team_permission: TeamPermissionService = Depends(get_team_permission_service),
    task_permission: TaskPermissionService = Depends(get_task_permission_service),
) -> TaskService:
    return TaskService(
        task_repo,
        team_repo,
        team_permission,
        task_permission,
    )


async def get_meeting_service(
    user_repo: UserRepository = Depends(get_user_repository),
    team_repo: TeamRepository = Depends(get_team_repository),
    meeting_repo: MeetingRepository = Depends(get_meeting_repository),
    team_permission: TeamPermissionService = Depends(get_team_permission_service),
    meeting_permission: MeetingPermissionService = Depends(
        get_meeting_permission_service
    ),
) -> MeetingService:
    return MeetingService(
        user_repo,
        team_repo,
        meeting_repo,
        team_permission,
        meeting_permission,
    )


async def get_task_comment_service(
    task_comment_repo: TaskCommentRepository = Depends(get_task_comment_repository),
    team_permission: TeamPermissionService = Depends(get_team_permission_service),
    task_permission: TaskPermissionService = Depends(get_task_permission_service),
    task_comment_permission: TaskCommentPermissionService = Depends(
        get_task_comment_permission_service
    ),
) -> TaskCommentService:
    return TaskCommentService(
        task_comment_repo,
        team_permission,
        task_permission,
        task_comment_permission,
    )


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
