import asyncio

from sqlalchemy import select

from app.core.enums import UserRole
from app.db.session import Session
from app.models.user import UserModel
from app.auth.utils import hash_password


async def create_demo_user():
    async with Session() as session:
        user = await session.scalar(
            select(UserModel)
            .where(UserModel.username == UserRole.MANAGER)
        )

        if user:
            print("Demo user already exists")
            return

        user = UserModel(
            username="manager",
            email="manager@example.com",
            first_name="Demo",
            last_name="Manager",
            password_hash=hash_password("manager123"),
            role=UserRole.MANAGER,
            is_active=True,
        )

        session.add(user)

        await session.commit()

        print("Demo manager created")


if __name__ == "__main__":
    asyncio.run(create_demo_user())
