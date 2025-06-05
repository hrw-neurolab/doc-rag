from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from beanie import Document, Indexed, PydanticObjectId


class User(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    email: EmailStr
    first_name: str
    last_name: str


class UserDB(Document, User):
    """User DB representation."""

    email: Annotated[str, Indexed(EmailStr, unique=True)]
    hashed_password: str

    class Settings:
        name = "users"
        keep_nulls = False


class CreateUserBody(BaseModel):
    """Request body for creating a new user."""

    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UpdateUserBody(BaseModel):
    """Request body for updating user fields."""

    first_name: str = None
    last_name: str = None
