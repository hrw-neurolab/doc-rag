from beanie import PydanticObjectId
from fastapi import HTTPException, status

from src.users.models import UpdateUserBody, User, UserDB


async def get_by_id(user_id: PydanticObjectId) -> User:
    user = await UserDB.find_one(UserDB.id == user_id).project(User)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    return user


async def get_by_email(email: str) -> UserDB:
    user = await UserDB.find_one(UserDB.email == email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with E-Mail {email} not found.",
        )

    return user


async def update(body: UpdateUserBody, user: UserDB) -> User:
    return await user.set(body.model_dump(exclude_unset=True))
