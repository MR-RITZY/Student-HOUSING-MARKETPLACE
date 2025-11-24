from sqlalchemy.orm import mapped_column, Mapped
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID as PQ_UUID, ENUM as PQ_ENUM
from sqlalchemy import String, Integer, DateTime, Boolean, func
from uuid import UUID, uuid4
from datetime import datetime
from typing import Literal

from src.stu_house_market.model.base import Base


class House(Base):
    id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4()
    )
    uni: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    loc: Mapped[str] = mapped_column(String(256), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    bedroom: Mapped[int] = mapped_column(Integer, nullable=False)
    water: Mapped[
        Literal[
            "running tap inside", "well outside", "running tap nearby", "well nearby"
        ]
    ] = mapped_column(String(25), nullable=False)
    power: Mapped[
        Literal["very stable", "stable to some extent", "not that stable"]
    ] = mapped_column(String(25), nullable=False)
    wifi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    park: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ac: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    kitchen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gym: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
