from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.feedback import create_feedback_event_record
from app.db.session import get_db
from app.models.feedback_event import FeedbackEvent
from app.schemas.sync import FeedbackSyncRequest, FeedbackSyncResponse


router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/feedback-events", response_model=FeedbackSyncResponse)
def sync_feedback_events(
    payload: FeedbackSyncRequest,
    db: Session = Depends(get_db),
) -> FeedbackSyncResponse:
    accepted: list[FeedbackEvent] = []
    duplicates: list[str] = []
    for event_payload in payload.events:
        if event_payload.id and db.get(FeedbackEvent, event_payload.id):
            duplicates.append(event_payload.id)
            continue
        event = create_feedback_event_record(event_payload, db)
        accepted.append(event)
    db.commit()
    for event in accepted:
        db.refresh(event)
    return FeedbackSyncResponse(accepted=accepted, duplicates=duplicates)

