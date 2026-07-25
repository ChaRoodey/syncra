from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import TaskStatus


class TaskCreateSchema(BaseModel):
    title: str = Field(max_length=128)
    description: str = Field(max_length=255)
    due_date: datetime


class TaskSchema(TaskCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    team_id: int = Field(gt=0)
    assignee_id: int = Field(gt=0)
    status: TaskStatus
    created_at: datetime


class TaskUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignee_id: int | None = Field(gt=0)
    title: str | None = Field(max_length=128)
    description: str | None = Field(max_length=255)
    due_date: datetime | None
    status: TaskStatus | None
