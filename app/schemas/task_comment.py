from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCommentCreateSchema(BaseModel):
    text: str = Field(max_length=255)


class TaskCommentSchema(TaskCommentCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    task_id: int = Field(gt=0)
    author_id: int = Field(gt=0)
    created_at: datetime


class TaskCommentUpdateSchema(BaseModel):
    text: str | None = Field(max_length=255)
