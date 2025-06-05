from typing import Annotated

from fastapi import APIRouter, Depends, status

import src.users.database as users_db
from src.auth.dependencies import current_user
from src.users.models import UpdateUserBody, User, UserDB


router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def get_user(user: Annotated[UserDB, Depends(current_user)]) -> User:
    """Return the current user.

    Args:
        user (UserDB): The current user obtained from the dependency.

    Returns:
        User: The current user.

    Raises:
        HTTPException: If the user is not found.
    """
    return user


@router.patch("")
async def update_user(
    body: UpdateUserBody, user: Annotated[UserDB, Depends(current_user)]
) -> User:
    """Update allowed user fields.

    Args:
        body (UpdateUserBody): User update fields.
        user (UserDB): The current user obtained from the dependency.

    Returns:
        User: The updated user.

    Raises:
        HTTPException: If the user is not found.
    """
    return await users_db.update(body, user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: Annotated[UserDB, Depends(current_user)]) -> None:
    """Delete current user.

    Args:
        user (UserDB): The current user obtained from the dependency.

    Raises:
        HTTPException: If the user is not found.
    """
    await user.delete()
