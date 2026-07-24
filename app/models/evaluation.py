from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EvaluationModel(Base):
    __tablename__ = "evaluation"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    manager_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"), unique=True
    )
    score: Mapped[int]
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
