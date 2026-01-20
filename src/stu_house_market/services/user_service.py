from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional
from uuid import UUID

from src.stu_house_market.model.user import Users, UserProvider, AuthProvider
from src.stu_house_market.db.db import get_db



class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_new_user(self, user_data: dict, provider:AuthProvider):
        try:
            user = Users(**user_data)
            user_provider = UserProvider(user_id = user.id, provider=provider)
            self.db.add_all(user, user_provider)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()

    async def get_user_by_id(self, id: str):
        result = await self.db.get(Users, UUID(id))
        return result

    async def get_user_by_email(self, email: str):
        result = await self.db.scalars(select(Users).where(Users.email == email))
        return result.first()

    async def get_user_by_id_and_email(self, id: str, email: str):
        result = await self.db.scalars(
            select(Users).where(Users.id == UUID(id), Users.email == email)
        )
        return result.first()

    async def update_user_data(
        self, user_data: dict, id: Optional[str] = None, user: Optional[Users] = None
    ):
        if not user:
            user = await self.db.get(Users, UUID(id))
        if not user:
            return None
        protected_field = {"id", "created_at"}
        for key, value in user_data.items():
            if key not in protected_field:
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user


def get_userservice(db: Annotated[AsyncSession, Depends(get_db)]):
    return UserService(db)
