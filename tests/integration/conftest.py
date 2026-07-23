import os

os.environ["ENV_FILE"] = ".env.test"

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.auth.utils import create_refresh_token, hash_password
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
async def user(db_session: AsyncSession) -> UserModel:
    user = UserModel(
        username="string",
        email="user@example.com",
        first_name="John",
        last_name="Doe",
        password_hash=hash_password("string"),
        role_id=1,
        is_active=True,
    )

    db_session.add(user)
    await db_session.flush()

    return user


@pytest.fixture
def refresh_token(user: UserModel) -> str:
    return create_refresh_token(user.id)
