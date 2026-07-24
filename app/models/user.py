from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UserRole
from app.models.base import Base


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
