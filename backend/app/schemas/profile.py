from datetime import datetime

from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    id: str | None = None
    time_budget_daily: int = Field(default=45, ge=10, le=480)
    preferred_media: str = "mixed"
    difficulty_tolerance: float = Field(default=0.55, ge=0.0, le=1.0)


class UserProfileRead(BaseModel):
    id: str
    time_budget_daily: int
    preferred_media: str
    difficulty_tolerance: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

