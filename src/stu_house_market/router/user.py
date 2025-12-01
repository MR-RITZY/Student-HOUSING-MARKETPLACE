from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from typing import Annotated
from uuid import uuid4

from src.stu_house_market.services.user_service import get_userservice, UserService
from src.stu_house_market.schema.user import UserCreated, NewUser
from src.stu_house_market.core.utils import hash_password, get_sefe_token, decode_safe_token
from src.stu_house_market.core.exc import UserAlreadyExistsException, InvalidTokenException
from src.stu_house_market.db.redis_manager import redis_client
from src.stu_house_market.background_tasks.celery_task import send_email
from src.stu_house_market.core.config import settings


userservice = Annotated[UserService, Depends(get_userservice)]


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register", response_model=UserCreated, status_code=status.HTTP_201_CREATED
)
async def create_user(user: NewUser, userservice: userservice):
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = await userservice.insert_new_user(user.model_dump())
    if not new_user:
        raise UserAlreadyExistsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A user already exists with this email address: {user.email}",
        )
    token_code = str(uuid4())
    safe_token_data = {"code": token_code, "user_id": str(new_user.id)}
    token = get_sefe_token(safe_token_data)
    verification_link = f"{settings.BASE_URL}/users/verify/your-new-account?token={token}"
    mail_template_data = {
        "firstname": new_user.firstname,
        "verification_link": verification_link,
    }
    send_email.delay(
        recipients=[new_user.email],
        subject="User Verification Email",
        template_rel_path="verify-new-account.html",
        template_data=mail_template_data,
    )
    await redis_client.setex(
        f"usr_{new_user.id}:email_verification_code", 24 * 3600, token_code
    )
    return {"message": "User Successfully Created", "user": new_user}


@router.get("/verify/your-new-account")
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
        return RedirectResponse(settings.FRONTEND_HOST, status_code=status.HTTP_302_FOUND)
    redis_code = await redis_client.get(f"usr_{user_id}:email_verification_code")
    if not redis_code or code != redis_code:
        raise InvalidTokenException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or Expired Token from the Verification Link\nRe-verify",
        )
    await userservice.update_user_data({"is_verified": True}, user=user)
    await redis_client.delete(f"usr_{user_id}:email_verification_code")

    return RedirectResponse(f"{settings.FRONTEND_HOST}/login", status_code=status.HTTP_302_FOUND)
