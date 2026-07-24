from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TeamModel(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    invite_code: Mapped[str] = mapped_column(unique=True, index=True)
