from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: Literal["access", "refresh"]
    exp: datetime
    iat: datetime
