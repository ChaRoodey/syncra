from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import MeetingStatus


class MeetingCreateSchema(BaseModel):
    title: str = Field(max_length=128)
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def validate_time(self):
        if self.starts_at >= self.ends_at:
            raise ValueError("starts_at must be earlier than ends_at")

        return self


class MeetingSchema(MeetingCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    author_id: int = Field(gt=0)
    status: MeetingStatus


class MeetingUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None = Field(max_length=128)
    status: MeetingStatus | None
    starts_at: datetime | None
    ends_at: datetime | None
