import os

from app.core.enums import UserRole
from app.models.team import TeamModel
from app.models.team_member import TeamMemberModel
from app.schemas.team import TeamNameSchema

os.environ["ENV_FILE"] = ".env.test"

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.auth.utils import create_access_token, create_refresh_token, hash_password
from app.db.session import get_db_session
from app.main import app
from app.models.user import UserModel

TEST_DATABASE_URL = "postgresql+asyncpg://syncra_test_user:syncra_test_password@localhost:5533/syncra_test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
SessionTest = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")

    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        "postgresql+asyncpg://syncra_test_user:syncra_test_password@localhost:5533/syncra_test_db",
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


@pytest_asyncio.fixture
async def user_factory(db_session: AsyncSession):
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

        db_session.add(user)
        await db_session.flush()

        access_token = create_access_token(user.id)

        return user, password, access_token

    return create_user


@pytest_asyncio.fixture
async def team_factory(db_session: AsyncSession):
    async def create_team(
        name: str = "team",
        invite_code: str = "aaaaaaaaaaaaaaaaaaaaaa",
    ) -> TeamModel:
        team = TeamModel(name=name, invite_code=invite_code)

        db_session.add(team)
        await db_session.flush()
        return team

    return create_team


@pytest_asyncio.fixture
async def team_member_factory(db_session: AsyncSession):
    async def create_team_member(
        team_id: int,
        user_id: int,
    ) -> TeamMemberModel:
        team_member = TeamMemberModel(team_id=team_id, user_id=user_id)

        db_session.add(team_member)
        await db_session.flush()
        return team_member

    return create_team_member


@pytest_asyncio.fixture
async def user(db_session: AsyncSession) -> UserModel:
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
def refresh_token(user: UserModel) -> str:
    return create_refresh_token(user.id)


@pytest.fixture
def team_name_payload() -> TeamNameSchema:
    return TeamNameSchema(name="team")
