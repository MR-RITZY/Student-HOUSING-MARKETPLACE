from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from typing import Annotated

from src.stu_house_market.services.user_service import get_userservice, UserService
from src.stu_house_market.schema.user import UserCreated, NewUser
from src.stu_house_market.utils.safe_token import decode_safe_token
from src.stu_house_market.core.password_utils import hash_password
from src.stu_house_market.core.exc import (
    UserAlreadyExistsException,
    InvalidTokenException,
)
from src.stu_house_market.core.config import settings
from src.stu_house_market.background_tasks.email_handler import verification_mail_sender
from src.stu_house_market.background_tasks.celery_task import background_task_sender

userservice = Annotated[UserService, Depends(get_userservice)]


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserCreated, status_code=status.HTTP_201_CREATED
)
async def create_user(new_user: NewUser, userservice: userservice):
    hashed_password = hash_password(new_user.password)
    new_user.password = hashed_password
    new_user_created = await userservice.create_new_user(new_user.model_dump(), "local")
    if not new_user_created:
        raise UserAlreadyExistsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A user already exists with this email address: {new_user.email}",
        )
    
    verification_mail_sender(
            {
                "user_id": new_user_created.id,
                "email": new_user_created.email,
                "firstname": new_user_created.firstname,
            }
        )
    mail_data = {
            "recipients": [new_user_created.email],
            "subject": f"Welcome {new_user_created.firstname}",
            "template_path": "welcome-new-user.html",
            "template_data": {"user_firstname": new_user_created.firstname},
        }
    background_task_sender("email_sender", mail_data)
    
    return {"message": "User Successfully Created", "user": new_user_created}


@router.get("/verify")
async def verify_new_account(token: str, userservice: userservice):
    payload = decode_safe_token(token)
    if not payload or not isinstance(payload, dict):
        raise InvalidTokenException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or Expired Token from the Verification Link\nRe-verify",
        )
    code, user_id = payload.get("code"), payload.get("user_id")
    if not code or not user_id:
        raise InvalidTokenException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or Expired Token from the Verification Link\nRe-verify",
        )
    user = await userservice.get_user_by_id(user_id)
    if not user:
        raise InvalidTokenException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or Expired Token from the Verification Link\nRe-verify",
        )
    if user.is_verified:
        return RedirectResponse(
            settings.FRONTEND_HOST, status_code=status.HTTP_302_FOUND
        )
    await userservice.update_user_data({"is_verified": True}, user=user)

    return RedirectResponse(
        f"{settings.FRONTEND_HOST}/login", status_code=status.HTTP_302_FOUND
    )
