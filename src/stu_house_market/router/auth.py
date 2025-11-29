from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from uuid import uuid4
import time

from src.stu_house_market.user_service import get_userservice, UserService
from src.stu_house_market.exc import InvalidCredentialsException, UnverifiedUserException
from src.stu_house_market.utils import verify_password, create_jwt, get_sefe_token
from src.stu_house_market.schema.user import UserLogin
from src.stu_house_market.oauth import get_user_from_refresh, get_user_from_login
from src.stu_house_market.model.user import Users
from src.stu_house_market.redis_manager import redis_client
from src.stu_house_market.config import settings
from src.stu_house_market.background_tasks.celery_task import send_email



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
    if not user.is_verified:
        token_code = str(uuid4())
        safe_token_data = {"code": token_code, "user_id": str(user.id)}
        token = get_sefe_token(safe_token_data)
        verification_link = f"{settings.BASE_URL}/users/verify/your-new-account?token={token}"
        mail_template_data = {
            "firstname": user.firstname,
            "verification_link": verification_link,
        }
        send_email.delay(
            recipients=[user.email],
            subject="User Verification Email",
            template_rel_path="verify-new-account.html",
            template_data=mail_template_data,
        )
        await redis_client.setex(
            f"usr_{user.id}:email_verification_code", 24 * 3600, token_code
        )
        raise UnverifiedUserException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not A Verified User --- User Verification Required\nCheck Your Email for Verification Link",
        )
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


    return {
        "message": "Login Successful",
        "user": user,
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

    return {"message": "Logged out"}
