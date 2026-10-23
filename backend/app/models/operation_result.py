from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class CloudOperationResult(Base):
    __tablename__ = "cloud_operation_results"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    operation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    result: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    __table_args__ = (
        Index(
            "ix_cloud_operation_user_type_created",
            "user_id",
            "operation_type",
            "created_at"
        ),
    )
