from sqlalchemy import select, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated
from uuid import UUID

from src.stu_house_market.model.house import (
    House,
    PowerStability,
    WaterAccessibility,
    EnvironmentSecurity,
)
from src.stu_house_market.db.db import get_db


RANGE_FILTERS = {
    "max_price": lambda v: House.price <= v,
    "min_price": lambda v: House.price >= v,
    "max_bedroom_count": lambda v: House.bedroom_count <= v,
    "min_bedroom_count": lambda v: House.bedroom_count >= v,
}

ENUM_FIELDS = {
    "power": PowerStability,
    "water": WaterAccessibility,
    "security": EnvironmentSecurity,
}

POWER_ORDER = {
    "very stable": 1,
    "stable to some extent": 2,
    "not that stable": 3,
}

SECURITY_ORDER = {
    "highly secured environment": 1,
    "secured to some extent": 2,
    "not that secured": 3,
}

WATER_ORDER = {
    "tap inside the apartment": 1,
    "tap outside the apartment": 2,
    "tap nearby": 3,
    "well outside": 4,
    "well nearby": 5,
    "water source not that close": 6,
}

BOOL_ORDER = {
    True: 1,
    False: 2,
}


def _bool_sort(field):
    return case(*[(field == k, v) for k, v in BOOL_ORDER.items()], else_=999)


power_sort = case(*[(House.power == k, v) for k, v in POWER_ORDER.items()], else_=999)
water_sort = case(*[(House.water == k, v) for k, v in WATER_ORDER.items()], else_=999)
security_sort = case(*[(House.security == k, v) for k, v in SECURITY_ORDER.items()], else_=999)
wifi_sort = _bool_sort(House.wifi)
parking_sort = _bool_sort(House.parking_space)
ac_sort = _bool_sort(House.ac)
kitchen_sort = _bool_sort(House.kitchen)
gym_sort = _bool_sort(House.gym)
tv_sort = _bool_sort(House.tv)


fallback_sorting = [
    water_sort,
    power_sort,
    security_sort,
    House.price.asc(),
    House.bedroom_count.desc(),
    House.location.asc(),
    wifi_sort,
    parking_sort,
    ac_sort,
    kitchen_sort,
    gym_sort,
    tv_sort,
    func.jsonb_array_length(House.images).desc(),
]


class HouseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_house(self, user_id: UUID, house_data: dict):
        try:
            house = House(user_id=user_id, **house_data)
            self.db.add(house)
            await self.db.commit()
            await self.db.refresh(house)
            return house
        except Exception as e:
            await self.db.rollback()
            print(f"Error saving house: {e}")
            return None

    async def search_house(self, house_data: dict):
        filters = self.filter_house(house_data)
        query = select(House).order_by(*fallback_sorting).limit(30)
        if filters:
            query = query.where(*filters)
        result = await self.db.scalars(query)
        return result.all()

    @classmethod
    def filter_house(house_data: dict):
        filters = []

        for key, value in house_data.items():
            if value is not None:
                if key == "location":
                    filters.append(House.location.ilike(value))

                elif key in RANGE_FILTERS:
                    filters.append(RANGE_FILTERS[key](value))

                elif key in ENUM_FIELDS:
                    filters.append(getattr(House, key) == ENUM_FIELDS[key](value))

                elif hasattr(House, key):
                    filters.append(getattr(House, key) == value)

            return filters


def get_house_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return HouseService(db)
