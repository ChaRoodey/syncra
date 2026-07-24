from pydantic import BaseModel, ConfigDict, EmailStr


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(LoginSchema):
    email: EmailStr
    first_name: str
    last_name: str


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    # is_active: bool
