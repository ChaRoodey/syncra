from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import TaskStatus


class EvaluationCreateSchema(BaseModel):
    score: int = Field(gt=0, le=5)
    comment: str | None = None


class EvaluationUpdateSchema(BaseModel):
    score: int | None = Field(gt=0, le=5, default=None)
    comment: str | None = None


class EvaluationSchema(EvaluationCreateSchema):
    model_config = ConfigDict(from_attributes=True)

    manager_id: int
    task_id: int
    created_at: datetime


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
    evaluation: EvaluationSchema | None = None


class TaskUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignee_id: int | None = Field(gt=0, default=None)
    title: str | None = Field(max_length=128, default=None)
    description: str | None = Field(max_length=255, default=None)
    due_date: datetime | None = None
    status: TaskStatus | None = None
