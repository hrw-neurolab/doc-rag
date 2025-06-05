from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.config import CONFIG
from src.auth.dependencies import OAUTH2
from src.auth.models import LoginBody, Tokens, TokensWithUser
from src.auth.util import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from src.users.models import CreateUserBody, User, UserDB


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(body: CreateUserBody) -> TokensWithUser:
    existing_user = await UserDB.find_one(UserDB.email == body.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(body.password)
    user = await UserDB(
        email=body.email,
        hashed_password=hashed_password,
        first_name=body.first_name,
        last_name=body.last_name,
    ).insert()

    user = User(**user.model_dump(by_alias=True))

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return TokensWithUser(
        access_token=access_token, refresh_token=refresh_token, user=user
    )


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokensWithUser:
    user = await UserDB.find_one(UserDB.email == form_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return TokensWithUser(
        access_token=access_token, refresh_token=refresh_token, user=user
    )


@router.get("/refresh")
async def refresh_token(token: Annotated[str, Depends(OAUTH2)]) -> Tokens:
    user_id = decode_token(token, CONFIG.jwt.secret_key_refresh, CONFIG.jwt.algorithm)

    user = await UserDB.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(str(user.id))

    return Tokens(access_token=access_token, refresh_token=token)
