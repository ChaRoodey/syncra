from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import MeetingStatus
from app.models.base import Base


class MeetingModel(Base):
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    title: Mapped[str]
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(MeetingStatus, native_enum=False),
        default=MeetingStatus.SCHEDULED,
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
