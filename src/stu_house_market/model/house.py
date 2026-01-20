from sqlalchemy import String, Integer, DateTime, Boolean, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PQ_UUID, ENUM as PQ_ENUM, JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Dict, Literal
from enum import Enum

from src.stu_house_market.model.base import Base


class PowerStability(str, Enum):
    very_stable = "very stable"
    stable = "stable to some extent"
    not_stable = "not that stable"


class WaterAccessibility(str, Enum):
    tap_inside = "tap inside the apartment"
    tap_outside = "tap outside the apartment"
    tap_nearby = "tap nearby"
    well_outside = "well outside"
    well_nearby = "well nearby"
    no_nearby_water_source = "water source not that close"


class EnvironmentSecurity(str, Enum):
    highly_secured = "highly secured environment"
    secured_to_some_extent = "secured to some extent"
    not_secured = "not that secured"


class PaymentDuration(str, Enum):
    monthly = "monthly"
    anually = "anually"


class House(Base):
    __tablename__ = "houses"

    id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    owner_id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True),
        ForeignKey("users.id", name="user_id", ondelete="CASCADE"),
        nullable=False,
    )
    house_title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    institution: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_duration: Mapped[PaymentDuration] = mapped_column(
        PQ_ENUM(PaymentDuration, name="payment_duration"), nullable=False
    )
    bedroom_count: Mapped[int] = mapped_column(Integer, nullable=False)
    security: Mapped[EnvironmentSecurity] = mapped_column(
        PQ_ENUM(EnvironmentSecurity, name="environment_security"),
        nullable=False,
        default=EnvironmentSecurity.not_secured,
    )
    water: Mapped[WaterAccessibility] = mapped_column(
        PQ_ENUM(WaterAccessibility, name="water_accessibility"),
        nullable=False,
        default=WaterAccessibility.no_nearby_water_source,
    )
    power: Mapped[PowerStability] = mapped_column(
        PQ_ENUM(PowerStability, name="power_stability"),
        nullable=False,
        default=PowerStability.not_stable,
    )

    wifi: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parking_space: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ac: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    kitchen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gym: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tv: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    images: Mapped[List[Dict[Literal["file_key"], str]]] = mapped_column(
        JSONB, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    user = relationship("Users", lazy="selectin", back_populates="houses")
