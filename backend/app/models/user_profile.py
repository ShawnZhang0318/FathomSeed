import uuid

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    time_budget_daily: Mapped[int] = mapped_column(Integer, default=45, nullable=False)
    preferred_media: Mapped[str] = mapped_column(String(64), default="mixed", nullable=False)
    difficulty_tolerance: Mapped[float] = mapped_column(Float, default=0.55, nullable=False)

    plans = relationship("LearningPlan", back_populates="user")
    feedback_events = relationship("FeedbackEvent", back_populates="user")
    method_preferences = relationship("LearningMethodPreference", back_populates="user")

