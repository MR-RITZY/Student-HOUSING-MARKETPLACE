from fastapi import status, Depends, Response
from typing import Annotated

from src.stu_house_market.model.user import Users
from src.stu_house_market.core.exc import UnverifiedUserException
from src.stu_house_market.core.jwt_utils import create_jwt
from src.stu_house_market.db.redis_manager import redis_client
from src.stu_house_market.core.config import settings
from src.stu_house_market.services.user_service import get_userservice, UserService

userservice = Annotated[UserService, Depends(get_userservice)]


async def create_login_session(user:Users , response: Response):
    access_token = create_jwt(
        {"sub": str(user.user_id), "role": user.role},
        "access_token",
    )
    refresh_token = create_jwt(
        {"sub": str(user.user_id), "role": user.role},
        "refresh_token",
    )

    ttl = settings.JWT_REFRESH_TOKEN_EXP * 24 * 3600
    await redis_client.setex(
        f"usr_{user.user_id}:refresh_token",
        ttl,
        refresh_token,
    )

    response.set_cookie(
        f"_{settings.APP_NAME}_api_auth",
        value=access_token,
        max_age=settings.JWT_ACCESS_TOKEN_EXP * 60,
        path="/",
        secure=True,
        httponly=True,
        samesite="strict",
    )

    response.set_cookie(
        f"_{settings.APP_NAME}_api_refresh",
        value=refresh_token,
        max_age=settings.JWT_REFRESH_TOKEN_EXP * 24 * 3600,
        path="/",
        secure=True,
        httponly=True,
        samesite="strict",
    )

    return {
        "message": "Login Successful",
        "user": user,
    }
