from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from stu_house_market.model.user import Users
from src.stu_house_market.db import get_db
from uuid import UUID


db = Annotated[AsyncSession, Depends(get_db)]


class UserService:
    def __init__(self, db: db):
        self.db = db

    async def insert_new_user(self, user_data: dict):
        try:
            user = Users(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except:
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


def get_userservice():
    return UserService()
