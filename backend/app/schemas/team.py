from pydantic import BaseModel, Field, ConfigDict


class TeamNameSchema(BaseModel):
    name: str = Field(max_length=255)


class TeamInviteCodeSchema(BaseModel):
    invite_code: str = Field(min_length=22, max_length=22)


class TeamSchema(TeamNameSchema, TeamInviteCodeSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
