from sqlalchemy.orm import mapped_column, Mapped, Relationship
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID as PQ_UUID, ENUM as PQ_ENUM
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey, UniqueConstraint
from uuid import UUID, uuid4
from datetime import datetime

from src.stu_house_market.model.base import Base


class Role(str, Enum):
    seeker = "seeker"
    owner = "owner"


class AuthProvider(str, Enum):
    local = "local"
    google = "google"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    role: Mapped[Role] = mapped_column(PQ_ENUM(Role, name="role_enum"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    houses = Relationship(
        "House", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )

    user_providers = Relationship(
        "UserProvider",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class UserProvider(Base):
    __tablename__ = "auth_provider"

    id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        PQ_UUID(as_uuid=True),
        ForeignKey("users.id", name="user_id", ondelete="CASCADE"),
        nullable=False,
    )

    provider: Mapped[AuthProvider] = mapped_column(
        PQ_ENUM(AuthProvider, name="auth_provider_enum"),
        nullable=False,
        default=AuthProvider.local,
    )

    user = Relationship("Users", back_populates="user_providers", lazy="selectin")

    __table_args__ = (UniqueConstraint(
        "user_id", "provider", name="user_provider_constraint"
    ),)
