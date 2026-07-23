from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from starlette import status

from app.api.v1.deps import get_auth_service
from app.scheams.user import LoginSchema, RegisterSchema
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(
    user: RegisterSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.register(user)


@router.post("/login/")
async def login(
    user: LoginSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.login(user)

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
    )

    return {
        "token": tokens.access_token,
        "token_type": tokens.token_type,
    }


@router.post("/refresh/")
async def refresh(
    refresh_token: str | None = Cookie(
        default=None,
    ),
    auth_service: AuthService = Depends(get_auth_service),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing",
        )

    access_token = await auth_service.refresh(refresh_token)

    return {
        "token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
):
    response.delete_cookie(
        key="refresh_token",
    )
