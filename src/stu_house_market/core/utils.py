from passlib.context import CryptContext
from password_validator import PasswordValidator
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4
from itsdangerous import URLSafeTimedSerializer



from src.stu_house_market.core.config import settings


pwd_context = CryptContext("bcrypt")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


schema = PasswordValidator()
schema.has(r"[a-z]+").has(r"[A-Z]+").has(r"\d+").has(r"\S").has().symbols().min(8)


def validate_password(password: str):
    return schema.validate(password)


def create_jwt(data: dict, token_type: Literal["access_token", "refresh_token"]):
    now = datetime.now(tz=timezone.utc)
    jti = str(uuid4())
    payload = data.copy()
    exp_interval = (
        {"days": settings.JWT_REFRESH_TOKEN_EXP}
        if token_type == "refresh_token"
        else {"minutes": settings.JWT_ACCESS_TOKEN_EXP}
    )
    exp = now + timedelta(**exp_interval)
    payload.update(
        {
            "jti": jti,
            "token_type": token_type,
            "exp": exp,
            "iat": now,
            "nbf": now,
            "iss": settings.BASE_URL,
            "aud": f"{settings.BASE_URL}/api",
        }
    )
    encoded = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    return encoded


def decode_jwt(token: str, expected_type: Literal["access_token", "refresh_token"]):
    options = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_nbf": True,
        "verify_iat": True,
        "verify_aud": True,
        "verify_iss": True,
        "require": [
            "exp",
            "iat",
            "nbf",
            "iss",
            "aud",
            "sub",
            "email",
            "jti",
            "token_type",
        ],
    }
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options=options,
            audience=f"{settings.BASE_URL}/api",
            issuer=settings.BASE_URL,
        )
    except JWTError as e:
        return None
    if payload.get("token_type") != expected_type:
        return None
    return payload


serializer = URLSafeTimedSerializer(
    settings.SAFE_URL_SECRET, salt="Student Housing Marketplace Safe URL"
)


def get_sefe_token(code: str | dict):
    return serializer.dumps(code)


def decode_safe_token(token: str):
    try:
        return serializer.loads(token, max_age=24 * 3600)
    except Exception:
        return None

