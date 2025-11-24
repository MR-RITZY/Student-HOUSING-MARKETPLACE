from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, Request
from typing import Annotated

from src.stu_house_market.utils import decode_jwt
from src.stu_house_market.exc import InvalidTokenException
from src.stu_house_market.user_service import UserService, get_userservice
from src.stu_house_market.redis_manager import redis_client

login_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scheme_name="auth_scheme")
refresh_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/refresh", scheme_name="refresh_scheme"
)

userservice = Annotated[UserService, Depends(get_userservice)]

CredentialException = InvalidTokenException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials --- Invalid or Expired\nLogin or Refresh for new token",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_payload(request: Request, token: Annotated[str, Depends(login_scheme)]):
    payload = getattr(request.state, "payload", None)
    if not payload:
        payload = decode_jwt(token, "access_token")
        setattr(request.state, "payload", payload)
    return payload


async def get_user_from_login(
    payload: Annotated[str, Depends(get_payload)], userservice: userservice
):
    if not payload:
        raise CredentialException
    user_id, user_email, jti = payload["sub"], payload["email"], payload["jti"]
    blacklisted_token = await redis_client.get(
        f"usr_{user_id}:blacklisted_access_token_{jti}"
    )
    if blacklisted_token or blacklisted_token=="blacklisted":
        raise CredentialException
    user = await userservice.get_user_by_id_and_email(user_id, user_email)
    if not user:
        raise CredentialException
    return user


async def get_user_from_refresh(token: Annotated[str, Depends(refresh_scheme)]):
    payload = decode_jwt(token, "refresh_token")
    if not payload:
        raise CredentialException
    user_id, user_email = payload["sub"], payload["email"]
    redis_token = await redis_client.get(f"usr_{user_id}:refresh_token")
    if not redis_token or token != redis_token:
        raise CredentialException
    user = await userservice.get_user_by_id_and_email(user_id, user_email)
    if not user:
        raise CredentialException
    return user
