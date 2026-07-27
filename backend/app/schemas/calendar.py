from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CalendarSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    type: Literal["task", "meeting"]
    title: str
    starts_at: datetime | None
    ends_at: datetime
