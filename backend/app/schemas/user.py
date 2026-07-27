from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import UserRole


class LoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str


class RegisterSchema(LoginSchema):
    email: EmailStr
    first_name: str = Field(max_length=50, default='')
    last_name: str = Field(max_length=50, default='')


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: UserRole
    # is_active: bool
