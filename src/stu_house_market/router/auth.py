from fastapi import APIRouter, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import time

from src.stu_house_market.services.user_service import get_userservice, UserService
from src.stu_house_market.core.exc import (
    InvalidCredentialsException,
    UnverifiedUserException,
)
from src.stu_house_market.core.jwt_utils import create_jwt
from src.stu_house_market.schema.user import UserLogin
from src.stu_house_market.core.auth import get_user_from_refresh, get_current_user
from src.stu_house_market.model.user import Users
from src.stu_house_market.db.redis_manager import redis_client
from src.stu_house_market.core.config import settings
from src.stu_house_market.core.rate_limiter import standalone_rate_limiter
from src.stu_house_market.core.auth_session import create_login_session
from src.stu_house_market.background_tasks.email_handler import verification_mail_sender
from src.stu_house_market.core.password_utils import verify_password



router = APIRouter(prefix="/auth", tags=["Authentication and Session Refresh"])
userservice = Annotated[UserService, Depends(get_userservice)]


@router.post("/login", response_model=UserLogin)
async def login(
    user_cred: Annotated[OAuth2PasswordRequestForm, Depends()],
    rate_limit: Annotated[None, Depends(standalone_rate_limiter(3))],
    userservice: userservice,
):
    email, password = user_cred.username, user_cred.password
    user = await userservice.get_user_by_email(email)

    if not user or not verify_password(password, user.password):
        raise InvalidCredentialsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials --- wrong email or password",
        )

    if not user.is_verified:
        verification_mail_sender(
            {"user_id": user.id, "email": user.email, "firstname": user.firstname}
        )
        raise UnverifiedUserException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified -- Verification mail has been sent to your email, check email to verify your account",
        )

   
    return await create_login_session(user)


@router.get("/refresh")
async def refresh(
    user: Annotated[Users, Depends(get_user_from_refresh)], response: Response
):
    access_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "access_token"
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


@router.post("/logout")
async def logout(
    user: Annotated[Users, Depends(get_current_user)],
    request: Request,
    response: Response,
):
    payload = getattr(request.state, "payload")

    ttl = payload["exp"] - int(time.time())
    if ttl > 0:
        await redis_client.setex(
            f"usr_{user.id}:blacklisted_access_token_{payload['jti']}",
            ttl,
            "blacklisted",
        )

    await redis_client.delete(f"usr_{user.id}:refresh_token")

    response.delete_cookie(f"_{settings.APP_NAME}_api_auth", path="/")
    response.delete_cookie(f"_{settings.APP_NAME}_api_refresh", path="/")

    return {"message": "Logged out"}
