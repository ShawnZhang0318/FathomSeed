import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utc_now


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"
    __table_args__ = (
        Index("ix_feedback_events_user_plan", "user_id", "plan_id"),
        Index("ix_feedback_events_processed", "processed_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_plans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("plan_tasks.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(48), index=True, nullable=False)
    user_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    server_received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("UserProfile", back_populates="feedback_events")
    plan = relationship(
        "LearningPlan",
        back_populates="feedback_events",
        foreign_keys=[plan_id],
    )
    task = relationship("PlanTask", back_populates="feedback_events")

