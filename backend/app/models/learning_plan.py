import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class LearningPlan(TimestampMixin, Base):
    __tablename__ = "learning_plans"
    __table_args__ = (
        Index("ix_learning_plans_user_status", "user_id", "status"),
        Index("ix_learning_plans_group_version", "plan_group_id", "version"),
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
    plan_group_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    parent_plan_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("learning_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    goal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    goal_mode: Mapped[str] = mapped_column(String(48), default="overview", nullable=False)
    planning_mode: Mapped[str] = mapped_column(String(32), default="adaptive", nullable=False)
    method_policy: Mapped[str] = mapped_column(String(48), default="mixed", nullable=False)
    method_mix: Mapped[dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    experience_policy: Mapped[str] = mapped_column(String(48), default="mixed", nullable=False)
    experience_mix: Mapped[dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    daily_minutes: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True, nullable=False)
    revision_reason_event_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("feedback_events.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_mode: Mapped[str] = mapped_column(String(24), default="local", nullable=False)

    user = relationship("UserProfile", back_populates="plans")
    parent_plan = relationship("LearningPlan", remote_side=[id])
    tasks = relationship(
        "PlanTask",
        back_populates="plan",
        cascade="all, delete-orphan",
        foreign_keys="PlanTask.plan_id",
        order_by="PlanTask.day_number, PlanTask.position",
    )
    feedback_events = relationship(
        "FeedbackEvent",
        back_populates="plan",
        foreign_keys="FeedbackEvent.plan_id",
    )
