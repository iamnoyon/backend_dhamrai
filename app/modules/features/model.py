from typing import Any, Optional
from datetime import datetime
from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, false
from sqlalchemy.dialects.postgresql import JSONB


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_union_based: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    union_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("unions.id", ondelete="SET NULL"), nullable=True)
    wards: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)  # [{ward_id, code, union_id, ward_no, total_voter}]
    candidates: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)  # [{id, name, image}]

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
