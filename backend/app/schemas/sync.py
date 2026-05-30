from pydantic import BaseModel

from app.schemas.feedback import FeedbackEventCreate, FeedbackEventRead


class FeedbackSyncRequest(BaseModel):
    events: list[FeedbackEventCreate]


class FeedbackSyncResponse(BaseModel):
    accepted: list[FeedbackEventRead]
    duplicates: list[str]

