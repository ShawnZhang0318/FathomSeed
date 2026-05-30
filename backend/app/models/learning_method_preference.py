import uuid

from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class LearningMethodPreference(TimestampMixin, Base):
    __tablename__ = "learning_method_preferences"
    __table_args__ = (
        Index(
            "uq_method_preference_user_subject_method",
            "user_id",
            "subject_area",
            "method_code",
            unique=True,
        ),
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
    subject_area: Mapped[str] = mapped_column(String(120), default="general", nullable=False)
    method_code: Mapped[str] = mapped_column(String(48), nullable=False)
    explicit_preference_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    observed_effectiveness_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user = relationship("UserProfile", back_populates="method_preferences")

