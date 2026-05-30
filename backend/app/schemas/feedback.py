from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackEventCreate(BaseModel):
    id: str | None = None
    user_id: str
    plan_id: str
    task_id: str | None = None
    event_type: str = Field(
        pattern="^(TOO_HARD|TOO_EASY|NO_TIME|SKIP|HELPFUL|NOT_HELPFUL|UNDERSTOOD|NOT_UNDERSTOOD|BORING|WANT_MORE_PRACTICE|WANT_MORE_EXPLANATION)$"
    )
    user_comment: str | None = None
    client_created_at: datetime | None = None


class FeedbackEventRead(BaseModel):
    id: str
    user_id: str
    plan_id: str
    task_id: str | None
    event_type: str
    user_comment: str | None
    client_created_at: datetime
    server_received_at: datetime
    processed_at: datetime | None

    model_config = {"from_attributes": True}

