from pydantic import BaseModel

from src.users.models import User


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokensWithUser(Tokens):
    user: User


class LoginBody(BaseModel):
    email: str
    password: str
