from fastapi import Depends, status, Request, Cookie
from typing import Annotated

from src.stu_house_market.core.jwt_utils import decode_jwt
from src.stu_house_market.core.exc import InvalidTokenException
from src.stu_house_market.services.user_service import UserService, get_userservice
from src.stu_house_market.db.redis_manager import redis_client
from src.stu_house_market.core.config import settings


userservice = Annotated[UserService, Depends(get_userservice)]

CredentialException = InvalidTokenException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials --- Invalid or Expired\nLogin or Refresh for new token",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_payload(request: Request):
    payload = getattr(request.state, "payload", None)
    if not payload:
        token = request.cookies.get(f"_{settings.APP_NAME}_api_auth")
        if not token:
            raise CredentialException

        payload = decode_jwt(token, "access_token")
        setattr(request.state, "payload", payload)
    return payload


async def get_current_user(
    payload: Annotated[str, Depends(get_payload)], userservice: userservice
):
    if not payload:
        raise CredentialException
    user_id, user_email, jti = payload["sub"], payload["email"], payload["jti"]
    blacklisted_token = await redis_client.get(
        f"usr_{user_id}:blacklisted_access_token_{jti}"
    )
    if blacklisted_token or blacklisted_token == "blacklisted":
        raise CredentialException
    user = await userservice.get_user_by_id_and_email(user_id, user_email)
    if not user:
        raise CredentialException
    return user


async def get_user_from_refresh(
    userservice: userservice,
    refresh_token: str | None = Cookie(
        default=None, alias=f"_{settings.APP_NAME}_api_refresh"
    ),
):
    if not refresh_token:
        raise CredentialException
    payload = decode_jwt(refresh_token, "refresh_token")
    if not payload:
        raise CredentialException
    user_id, user_email = payload["sub"], payload["email"]
    redis_key = f"usr_{user_id}:refresh_token"
    redis_token = await redis_client.get(redis_key)
    if not redis_token or refresh_token != redis_token:
        raise CredentialException
    user = await userservice.get_user_by_id_and_email(user_id, user_email)
    if not user:
        raise CredentialException
    return user
