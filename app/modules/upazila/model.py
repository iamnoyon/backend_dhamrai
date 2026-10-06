from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer


class Upazila(Base):
    __tablename__ = "upazilas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)

    unions: Mapped[list["Union"]] = relationship(back_populates="upazila", cascade="all, delete-orphan", passive_deletes=True)
