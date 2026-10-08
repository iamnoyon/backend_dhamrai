from enum import Enum
from app.core.db import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    dob: Mapped[str] = mapped_column(String(10), nullable=False)  # Format: YYYY-MM-DD
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.USER, server_default=UserRole.USER.value)  # superadmin, admin, user
    status: Mapped[UserStatus] = mapped_column(String(10), nullable=False, default=UserStatus.ACTIVE)  # active, inactive, banned

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    updated_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")