from typing import Any, Optional
from datetime import datetime
from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import JSONB


class DurgaPuja(Base):
    __tablename__ = "durga_pujas"
    __table_args__ = (
        UniqueConstraint("feature_id", "union_id", "ward_code", name="durga_pujas_feature_id_union_id_ward_code_key", postgresql_nulls_not_distinct=True),
        Index("idx_durga_pujas_feature_id", "feature_id"),
        Index("idx_durga_pujas_union_id", "union_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature_id: Mapped[int] = mapped_column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    union_id: Mapped[int] = mapped_column(Integer, ForeignKey("unions.id", ondelete="CASCADE"), nullable=False)
    ward_code: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("wards.code", ondelete="CASCADE"), nullable=True)  # null for a union without wards (paurashava)
    villages: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)  # [{village_name, mondir_name, phone}]

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())
