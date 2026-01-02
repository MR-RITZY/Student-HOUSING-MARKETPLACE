from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import time

from src.stu_house_market.services.user_service import get_userservice, UserService
from src.stu_house_market.core.exc import (
    InvalidCredentialsException,
    UnverifiedUserException,
    UserNotAuthenticatedByGoogleException,
    UnexpectedError,
)
from src.stu_house_market.core.utils import verify_password, create_jwt
from src.stu_house_market.schema.user import UserLogin
from src.stu_house_market.core.auth import get_user_from_refresh, get_user_from_login
from src.stu_house_market.model.user import Users
from src.stu_house_market.db.redis_manager import redis_client
from src.stu_house_market.core.config import settings
from src.stu_house_market.core.oauth2 import google_redirect, google_callback
"""from src.stu_house_market.core.utils import verification_mail_handler, mail_sender"""


router = APIRouter(prefix="/auth", tags=["Authentication and Refresh Session"])
userservice = Annotated[UserService, Depends(get_userservice)]


@router.post("/login", response_model=UserLogin)
async def login(
    user_cred: Annotated[OAuth2PasswordRequestForm, Depends()], userservice: userservice
):
    email, password = user_cred.username, user_cred.password
    user = await userservice.get_user_by_email(email)
    if not user:
        raise InvalidCredentialsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Credentials\nIncorrect email or password",
        )
    """if not user.is_verified:
        verification_mail_handler(user)
        raise UnverifiedUserException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not A Verified User -- User Verification Required\nCheck Your Email for Verification Link",
        )"""
    is_correct_password = verify_password(password, user.password)
    if not is_correct_password:
        raise InvalidCredentialsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Credentials\nIncorrect email or password",
        )
    access_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "access_token"
    )
    refresh_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "refresh_token"
    )
    ttl = settings.JWT_REFRESH_TOKEN_EXP * 24 * 3600

    await redis_client.setex(f"usr_{user.id}:refresh_token", ttl, refresh_token)

    logged_in_user = await userservice.update_user_data({"is_active": True}, user=user)

    return {
        "message": "Login Successful",
        "user": logged_in_user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh")
async def refresh(user: Annotated[Users, Depends(get_user_from_refresh)]):
    access_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "access_token"
    )

    return {
        "message": "Refresh Successful",
        "user": user,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/logout")
async def logout(
    user: Annotated[Users, Depends(get_user_from_login)], request: Request
):
    payload = getattr(request.state, "payload")
    ttl = payload["exp"] - int(time.time())
    await redis_client.setex(
        f"usr_{str(user.id)}:blacklisted_access_token_{payload["jti"]}",
        ttl,
        "blacklisted",
    )
    await redis_client.delete(f"usr_{str(user.id)}:refresh_token")

    userservice.update_user_data({"is_active": False}, user=user)

    return {"message": "Logged out"}


@router.get("/google/redirect")
async def redirect_to_google(request: Request):
    return await google_redirect(request)


@router.get("/google/callback")
async def validate_callback(
    request: Request,
    userservice: userservice,
    oauth_user: Annotated[dict, Depends(google_callback)],
):
    if not oauth_user:
        raise UserNotAuthenticatedByGoogleException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not Authenticated By Google",
        )
    user = await userservice.get_user_by_email(user["email"])
    if not user:
        user = await userservice.create_new_user(oauth_user)
        if not user:
            raise UnexpectedError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Something Wrong with Google Account",
            )
        """mail_sender(
            user,
            f"Welcome {user.firstname}",
            template_path="welcome-new-user.html",
            template_data={"firstname": user.firstname},
        )"""
    access_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "access_token"
    )
    refresh_token = create_jwt(
        {"sub": str(user.id), "email": user.email, "role": user.role}, "refresh_token"
    )
    ttl = settings.JWT_REFRESH_TOKEN_EXP * 24 * 3600

    await redis_client.setex(f"usr_{user.id}:refresh_token", ttl, refresh_token)

    logged_in_user = userservice.update_user_data({"is_active": True}, user=user)

    return {
        "message": "Login Successful",
        "user": logged_in_user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
