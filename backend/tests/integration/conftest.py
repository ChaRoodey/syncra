import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent

os.environ["ENV_FILE"] = str(PROJECT_ROOT / ".env.test")

from datetime import datetime, timedelta
from typing import AsyncGenerator, TypeVar

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.auth.utils import create_access_token, create_refresh_token, hash_password
from app.core.enums import MeetingStatus, TaskStatus, UserRole
from app.db.session import get_db_session
from app.main import app
from app.models.base import Base
from app.models.evaluation import EvaluationModel
from app.models.meeting import MeetingModel
from app.models.meeting_participant import MeetingParticipantModel
from app.models.task import TaskModel
from app.models.task_comment import TaskCommentModel
from app.models.team import TeamModel
from app.models.team_member import TeamMemberModel
from app.models.user import UserModel
from app.schemas.meeting import MeetingCreateSchema, MeetingUpdateSchema
from app.schemas.task import (
    EvaluationCreateSchema,
    EvaluationUpdateSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
)
from app.schemas.task_comment import TaskCommentCreateSchema, TaskCommentUpdateSchema
from app.schemas.team import TeamNameSchema

TEST_DATABASE_URL = "postgresql+asyncpg://syncra_test_user:syncra_test_password@localhost:5533/syncra_test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
SessionTest = async_sessionmaker(engine_test, expire_on_commit=False)

EntityT = TypeVar("EntityT", bound=Base)
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config(str(ALEMBIC_INI))
    db_url = "postgresql+asyncpg://syncra_test_user:syncra_test_password@localhost:5533/syncra_test_db"

    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        db_url,
    )
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with engine_test.connect() as conn:
        transaction = await conn.begin()

        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture
async def client(
        db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


def entity_factory(db_session: AsyncSession):
    async def add_entity_to_db(entity: EntityT) -> EntityT:
        db_session.add(entity)
        await db_session.flush()

        return entity

    return add_entity_to_db


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_user(
            role: UserRole = UserRole.USER,
            username: str = "user",
            password: str = "password",
            is_active: bool = True,
    ) -> (UserModel, str, str):
        user = UserModel(
            username=username,
            email=f"{username}@example.com",
            first_name="Test",
            last_name="User",
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )

        user = await add_entity(user)

        access_token = create_access_token(user.id)

        return user, password, access_token

    return create_user


@pytest_asyncio.fixture
async def team_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_team(
            name: str = "team",
            invite_code: str = "aaaaaaaaaaaaaaaaaaaaaa",
    ) -> TeamModel:
        team = TeamModel(name=name, invite_code=invite_code)

        return await add_entity(team)

    return create_team


@pytest_asyncio.fixture
async def team_member_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_team_member(
            team_id: int,
            user_id: int,
    ) -> TeamMemberModel:
        team_member = TeamMemberModel(team_id=team_id, user_id=user_id)

        return await add_entity(team_member)

    return create_team_member


@pytest_asyncio.fixture
async def task_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_task(
            title: str = "task",
            description: str = "description",
            assignee_id: int = 1,
            team_id: int = 1,
            status: TaskStatus = TaskStatus.OPEN,
            due_date: datetime = datetime.now() + timedelta(days=1),
    ) -> TaskModel:
        task = TaskModel(
            title=title,
            description=description,
            assignee_id=assignee_id,
            team_id=team_id,
            status=status,
            due_date=due_date,
        )

        return await add_entity(task)

    return create_task


@pytest_asyncio.fixture
async def meeting_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_meeting(
            team_id: int = 1,
            author_id: int = 1,
            title: str = "meeting",
            starts_at: datetime = datetime.now() + timedelta(days=1),
            ends_at: datetime = datetime.now() + timedelta(days=1, hours=1),
    ) -> MeetingModel:
        meeting = MeetingModel(
            team_id=team_id,
            author_id=author_id,
            title=title,
            starts_at=starts_at,
            ends_at=ends_at,
        )

        return await add_entity(meeting)

    return create_meeting


@pytest_asyncio.fixture
async def meeting_participant_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_meeting_participant(
            meeting_id: int,
            user_id: int,
    ) -> MeetingParticipantModel:
        meeting_participant = MeetingParticipantModel(
            meeting_id=meeting_id, user_id=user_id
        )

        return await add_entity(meeting_participant)

    return create_meeting_participant


@pytest_asyncio.fixture
async def comment_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_task_comment(
            task_id: int,
            author_id: int,
            text: str = "comment",
    ) -> TaskCommentModel:
        task_comment = TaskCommentModel(
            task_id=task_id,
            author_id=author_id,
            text=text,
        )

        return await add_entity(task_comment)

    return create_task_comment


@pytest_asyncio.fixture
async def evaluation_factory(db_session: AsyncSession):
    add_entity = entity_factory(db_session)

    async def create_evaluation(
            manager_id: int = 1,
            task_id: int = 1,
    ) -> EvaluationModel:
        evaluation = EvaluationModel(
            manager_id=manager_id,
            task_id=task_id,
            score=4,
            comment="comment",
        )

        return await add_entity(evaluation)

    return create_evaluation


@pytest_asyncio.fixture
async def factory(
        user_factory,
        team_factory,
        team_member_factory,
        task_factory,
        meeting_factory,
        meeting_participant_factory,
        comment_factory,
        evaluation_factory,
):
    class Factory:
        def __init__(self):
            self.user = user_factory
            self.team = team_factory
            self.team_member = team_member_factory
            self.task = task_factory
            self.meeting = meeting_factory
            self.meeting_participant = meeting_participant_factory
            self.comment = comment_factory
            self.evaluation = evaluation_factory

        async def user_team_membership(
                self,
                curr_user_role: UserRole = UserRole.USER,
        ):
            user, _, token = await self.user(role=curr_user_role)
            team = await self.team()
            await self.team_member(team.id, user.id)
            return user, team, token

        async def user_team_membership_task(self, *args, **kwargs):
            user, team, token = await self.user_team_membership(*args, **kwargs)

            task = await self.task(
                team_id=team.id,
                assignee_id=user.id,
            )

            return user, team, token, task

        async def manager_team_member(self):
            curr_user, _, token = await self.user(role=UserRole.MANAGER)
            member, _, _ = await self.user(
                username="user1",
                role=UserRole.USER,
            )

            team = await self.team()

            await self.team_member(team.id, curr_user.id)
            await self.team_member(team.id, member.id)

            return curr_user, member, team, token

        async def manager_team_member_task(self):
            curr_user, member, team, token = await self.manager_team_member()

            task = await self.task(
                team_id=team.id,
                assignee_id=curr_user.id,
            )

            return curr_user, member, team, token, task

    return Factory()


@pytest_asyncio.fixture
async def user_model(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        username="string",
        email="user@example.com",
        first_name="John",
        last_name="Doe",
        password_hash=hash_password("string"),
        role=UserRole.USER,
        is_active=True,
    )

    db_session.add(user)
    await db_session.flush()

    return user


@pytest.fixture
def refresh_token(user_model: UserModel) -> str:
    return create_refresh_token(user_model.id)


@pytest.fixture
def team_name_payload() -> TeamNameSchema:
    return TeamNameSchema(name="team")


@pytest.fixture
def task_create_payload() -> TaskCreateSchema:
    return TaskCreateSchema(
        title="task",
        description="description",
        due_date=datetime.now() + timedelta(days=1),
    )


@pytest.fixture
def task_update_payload() -> TaskUpdateSchema:
    return TaskUpdateSchema(
        title="task1",
        description="description1",
        due_date=datetime.now() + timedelta(days=1),
        assignee_id=2,
        status=TaskStatus.IN_PROGRESS,
    )


@pytest.fixture
def meeting_create_payload() -> MeetingCreateSchema:
    return MeetingCreateSchema(
        title="task",
        starts_at=datetime.now() + timedelta(days=1),
        ends_at=datetime.now() + timedelta(days=1, hours=1),
    )


@pytest.fixture
def meeting_update_payload() -> MeetingUpdateSchema:
    return MeetingUpdateSchema(
        title="task",
        status=MeetingStatus.SCHEDULED,
        starts_at=datetime.now() + timedelta(days=1),
        ends_at=datetime.now() + timedelta(days=1, hours=1),
    )


@pytest.fixture
def task_comment_create_payload() -> TaskCommentCreateSchema:
    return TaskCommentCreateSchema(text="comment")


@pytest.fixture
def task_comment_update_payload() -> TaskCommentUpdateSchema:
    return TaskCommentUpdateSchema(text="comment")


@pytest.fixture
def evaluation_create_payload() -> EvaluationCreateSchema:
    return EvaluationCreateSchema(
        score=5,
        comment="comment",
    )


@pytest.fixture
def evaluation_update_payload() -> EvaluationUpdateSchema:
    return EvaluationUpdateSchema(
        score=2,
        comment="comment",
    )
