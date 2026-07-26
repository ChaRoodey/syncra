from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TaskStatus
from app.models.base import Base


class TaskModel(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignee_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False), default=TaskStatus.OPEN, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    evaluation: Mapped["EvaluationModel | None"] = relationship(
        back_populates="task",
        uselist=False,
        lazy="selectin",
    )
