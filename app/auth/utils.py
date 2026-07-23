from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.scheams.token import TokenPayload


def encode_jwt(
    payload: dict,
    expire_minutes: int,
    private_key: str = settings.auth_jwt.private_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )

    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def create_access_token(user_id: int, **kwargs) -> str:
    return encode_jwt(
        {
            "sub": str(user_id),
            "type": "access",
        },
        settings.auth_jwt.access_token_expire_minutes,
        **kwargs,
    )


def create_refresh_token(user_id: int, **kwargs) -> str:
    return encode_jwt(
        {
            "sub": str(user_id),
            "type": "refresh",
        },
        settings.auth_jwt.refresh_token_expire_minutes,
        **kwargs,
    )


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key,
    algorithm: str = settings.auth_jwt.algorithm,
) -> TokenPayload:
    try:
        payload = jwt.decode(token, public_key, algorithms=[algorithm])
        return TokenPayload.model_validate(payload)
    except (InvalidTokenError, ValidationError):
        raise InvalidTokenError


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
