from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str


class RegisterSchema(LoginSchema):
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    # is_active: bool
