from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TeamMemberModel(Base):
    __tablename__ = "team_member"

    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
