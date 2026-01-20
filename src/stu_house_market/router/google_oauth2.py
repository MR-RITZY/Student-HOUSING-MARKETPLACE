from fastapi import APIRouter, Depends, status, Request
from typing import Annotated


from src.stu_house_market.services.user_service import get_userservice, UserService
from src.stu_house_market.core.exc import (
    UserNotAuthenticatedByGoogleException,
    UnexpectedError,
)
from src.stu_house_market.core.google_oauth2 import google_redirect, google_callback
from src.stu_house_market.core.rate_limiter import standalone_rate_limiter
from src.stu_house_market.core.auth_session import create_login_session
from src.stu_house_market.background_tasks.celery_task import background_task_sender
from src.stu_house_market.schema.user import UserLogin


router = APIRouter(prefix="/auth/google", tags=["Google OAuth 2.0 Authentication"])
userservice = Annotated[UserService, Depends(get_userservice)]


@router.get("/redirect")
async def redirect_to_google(request: Request):
    return await google_redirect(request)


@router.get("/callback", response_model=UserLogin)
async def google_oauth_callback(
    rate_limit: Annotated[None, Depends(standalone_rate_limiter(3))],
    userservice: userservice,
    user_data: Annotated[dict, Depends(google_callback)],
):
    if not user_data:
        raise UserNotAuthenticatedByGoogleException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed",
        )

    user = await userservice.get_user_by_email(user_data["email"])

    if not user:
        user = await userservice.create_new_user(user_data,  provider="google")

        if not user:
            raise UnexpectedError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed",
            )

        background_task_sender(
            "email_sender",
            {
                "recipients": [user.email],
                "subject": f"Welcome {user.firstname}",
                "template_path": "welcome-new-user.html",
                "template_data": {"user_firstname": user.firstname},
            },
        )

    return await create_login_session(user)
