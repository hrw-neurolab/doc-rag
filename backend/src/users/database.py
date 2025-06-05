from src.users.models import UpdateUserBody, UserDB


async def update(body: UpdateUserBody, user: UserDB) -> UserDB:
    return await user.set(body.model_dump(exclude_unset=True))
