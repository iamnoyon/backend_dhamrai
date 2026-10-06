from typing import Any
from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB


class Ward(Base):
    __tablename__ = "wards"
    __table_args__ = (
        UniqueConstraint("union_id", "ward_no", name="wards_union_id_ward_no_key"),
        Index("idx_wards_union_id", "union_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    union_id: Mapped[int] = mapped_column(Integer, ForeignKey("unions.id", ondelete="CASCADE"), nullable=False)
    ward_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    geometry: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    union: Mapped["Union"] = relationship(back_populates="wards")
