from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class UserCloudProfile(Base):
    __tablename__ = "user_cloud_profiles"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    organization_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    organization_size: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    cloud_platforms: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    cloud_usage: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    goals: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )