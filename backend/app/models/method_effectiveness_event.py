import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utc_now


class MethodEffectivenessEvent(Base):
    __tablename__ = "method_effectiveness_events"

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
    method_code: Mapped[str] = mapped_column(String(48), index=True, nullable=False)
    completion_status: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    understanding_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quiz_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_spent_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

