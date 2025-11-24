from fastapi import APIRouter, Depends, status
from typing import Annotated

from src.stu_house_market.user_service import get_userservice, UserService
from src.stu_house_market.schema.user import UserCreated, NewUser
from src.stu_house_market.utils import hash_password
from src.stu_house_market.exc import UserAlreadyExistsException


userservice = Annotated[UserService, Depends(get_userservice)]


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user(user: NewUser, userservice: userservice):
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = await userservice.insert_new_user(user.model_dump())
    if not new_user:
        raise UserAlreadyExistsException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A user already exists with this email address: {user.email}",
        )

    return {"message": "User Successfully Created", "user": new_user}
