from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# =========================================================
# KNOWLEDGE POST
# Articles, Questions and Solutions
# =========================================================

class KnowledgePost(Base):

    __tablename__ = "knowledge_posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # article / question / solution
    content_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # AWS / Azure / GCP / Security / etc.
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    # Stored as JSON string
    # Example:
    # ["AWS", "EC2", "Cost Optimization"]
    tags: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]"
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
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


# =========================================================
# KNOWLEDGE COMMENT
# Comments / Answers
# =========================================================

class KnowledgeComment(Base):

    __tablename__ = "knowledge_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # True when the comment is an answer
    # to a question
    is_answer: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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


# =========================================================
# KNOWLEDGE RATING
# One user can rate a post only once
# =========================================================

class KnowledgeRating(Base):

    __tablename__ = "knowledge_ratings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    rating: Mapped[int] = mapped_column(
        Integer,
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

    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_knowledge_post_user_rating"
        ),
    )