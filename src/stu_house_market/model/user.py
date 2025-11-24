from sqlalchemy.orm import mapped_column, Mapped
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID as PQ_UUID, ENUM as PQ_ENUM
from sqlalchemy import String, DateTime, func
from uuid import UUID, uuid4
from datetime import datetime

from src.stu_house_market.model.base import Base




class Role(str, Enum):
    seeker = "seeker"
    owner = "owner"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(PQ_ENUM(Role, name="role_enum"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
