from enum import Enum
from typing import Any, Optional
from datetime import datetime
from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, false, func, text
from sqlalchemy.dialects.postgresql import JSONB


class FeatureStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Feature(Base):
    __tablename__ = "features"
    __table_args__ = (
        Index("uq_features_title_lower", func.lower(text("title")), unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_union_based: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    union_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("unions.id", ondelete="SET NULL"), nullable=True)
    wards: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)  # [{ward_id, code, union_id, ward_no, total_voter}], ward_id/code/ward_no are null for a union without wards (paurashava)
    candidates: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)  # [{id, name, image}]
    status: Mapped[FeatureStatus] = mapped_column(String(10), nullable=False, default=FeatureStatus.ACTIVE, server_default=FeatureStatus.ACTIVE.value)  # active, inactive

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now())


class FeatureResult(Base):
    __tablename__ = "feature_results"
    __table_args__ = (
        UniqueConstraint("feature_id", "union_id", "ward_id", "candidate_id", name="feature_results_feature_union_ward_candidate_key", postgresql_nulls_not_distinct=True),
        Index("idx_feature_results_feature_id", "feature_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feature_id: Mapped[int] = mapped_column(Integer, ForeignKey("features.id", ondelete="CASCADE"), nullable=False)
    union_id: Mapped[int] = mapped_column(Integer, ForeignKey("unions.id", ondelete="CASCADE"), nullable=False)
    ward_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("wards.id", ondelete="CASCADE"), nullable=True)  # null for a union without wards (paurashava)
    candidate_id: Mapped[str] = mapped_column(String(10), nullable=False)  # candidate key from features.candidates, e.g. "a"
    value: Mapped[int] = mapped_column(Integer, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
