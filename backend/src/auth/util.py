from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from beanie import PydanticObjectId
from passlib.context import CryptContext
from fastapi import HTTPException, status

from src.config import CONFIG


CRYPT_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return CRYPT_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return CRYPT_CONTEXT.hash(password)


def create_access_token(user_id: str):
    expires = datetime.now(timezone.utc) + timedelta(
        hours=CONFIG.jwt.expires_hours_access
    )
    payload = {"sub": user_id, "exp": expires}
    return jwt.encode(
        payload, CONFIG.jwt.secret_key_access, algorithm=CONFIG.jwt.algorithm
    )


def create_refresh_token(user_id: str):
    expires = datetime.now(timezone.utc) + timedelta(
        hours=CONFIG.jwt.expires_hours_refresh
    )
    payload = {"sub": user_id, "exp": expires}
    return jwt.encode(
        payload, CONFIG.jwt.secret_key_refresh, algorithm=CONFIG.jwt.algorithm
    )


def decode_token(token: str, secret_key: str, algorithm: str) -> PydanticObjectId:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token has expired.",
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials.",
        )

    if "sub" not in payload or "exp" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials.",
        )

    try:
        user_id = PydanticObjectId(payload["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials.",
        )

    return user_id
