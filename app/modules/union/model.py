from typing import Any, Optional
from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint, Index, false
from sqlalchemy.dialects.postgresql import JSONB


class Union(Base):
    __tablename__ = "unions"
    __table_args__ = (
        UniqueConstraint("upazila_id", "name", name="unions_upazila_id_name_key"),
        Index("idx_unions_upazila_id", "upazila_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upazila_id: Mapped[int] = mapped_column(Integer, ForeignKey("upazilas.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    is_paurashava: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    geometry: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
