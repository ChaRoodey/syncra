from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(LoginSchema):
    email: EmailStr
    first_name: str
    last_name: str


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
