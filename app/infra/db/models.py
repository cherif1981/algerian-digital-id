from sqlalchemy import String, Date, DateTime, Enum, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, date
import enum


class Base(DeclarativeBase):
    pass


class IdentityORM(Base):
    __tablename__ = "identities"

    identity_id: Mapped[str] = mapped_column(String(26), primary_key=True)
    nin: Mapped[str | None] = mapped_column(String(18), unique=True, index=True)
    first_name_ar: Mapped[str] = mapped_column(String(100))
    last_name_ar: Mapped[str] = mapped_column(String(100))
    first_name_fr: Mapped[str] = mapped_column(String(100))
    last_name_fr: Mapped[str] = mapped_column(String(100))
    date_of_birth: Mapped[date] = mapped_column(Date)
    place_of_birth: Mapped[str] = mapped_column(String(200))
    gender: Mapped[str] = mapped_column(String(1))
    status: Mapped[str] = mapped_column(String(20), index=True)
    verification_level: Mapped[str] = mapped_column(String(20))
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_identities_status_level", "status", "verification_level"),
    )