import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PlanTask(TimestampMixin, Base):
    __tablename__ = "plan_tasks"
    __table_args__ = (
        Index("ix_plan_tasks_plan_day_position", "plan_id", "day_number", "position"),
        Index("ix_plan_tasks_status", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_plans.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("plan_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    method_code: Mapped[str] = mapped_column(String(48), index=True, nullable=False)
    experience_mode: Mapped[str] = mapped_column(String(48), default="drill", index=True, nullable=False)
    skill_type: Mapped[str] = mapped_column(String(48), default="general", nullable=False)
    expected_outcome: Mapped[str] = mapped_column(String(240), default="", nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(48), default="reflection", nullable=False)
    content_format: Mapped[str] = mapped_column(String(48), default="exercise", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    plan = relationship("LearningPlan", back_populates="tasks", foreign_keys=[plan_id])
    source_task = relationship("PlanTask", remote_side=[id])
    feedback_events = relationship("FeedbackEvent", back_populates="task")
