from typing import Annotated

from beanie import PydanticObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.auth.util import decode_token
from src.config import CONFIG
from src.users.models import UserDB


OAUTH2 = OAuth2PasswordBearer(tokenUrl="auth/login")


async def current_user(token: Annotated[str, Depends(OAUTH2)]) -> UserDB:
    """Validates and decodes a users access token.

    Args:
        token (str): The access token to validate.

    Returns:
        UserDB: The authenticated raw user object.

    Raises:
        HTTPException: If the user is not authenticated or the token is invalid.
    """
    user_id = decode_token(token, CONFIG.jwt.secret_key_access, CONFIG.jwt.algorithm)
    user = await UserDB.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def current_user_id(user: Annotated[UserDB, Depends(current_user)]) -> PydanticObjectId:
    """Returns the ID of the currently authenticated user.

    Args:
        user (UserDB): The authenticated user object.

    Returns:
        PydanticObjectId: The ID of the authenticated user.
    """
    return user.id
