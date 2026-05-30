from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.method_engine import MethodEngine
from app.db.base import utc_now
from app.db.session import get_db
from app.models.feedback_event import FeedbackEvent
from app.models.plan_task import PlanTask
from app.schemas.feedback import FeedbackEventCreate, FeedbackEventRead


router = APIRouter(prefix="/feedback-events", tags=["feedback"])
method_engine = MethodEngine()


@router.post("", response_model=FeedbackEventRead)
def create_feedback_event(
    payload: FeedbackEventCreate,
    db: Session = Depends(get_db),
) -> FeedbackEvent:
    event = create_feedback_event_record(payload, db)
    db.commit()
    db.refresh(event)
    return event


def create_feedback_event_record(payload: FeedbackEventCreate, db: Session) -> FeedbackEvent:
    if payload.id:
        existing = db.get(FeedbackEvent, payload.id)
        if existing:
            return existing

    task = db.get(PlanTask, payload.task_id) if payload.task_id else None
    if payload.task_id and task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    event_kwargs = {
        "user_id": payload.user_id,
        "plan_id": payload.plan_id,
        "task_id": payload.task_id,
        "event_type": payload.event_type,
        "user_comment": payload.user_comment,
        "client_created_at": payload.client_created_at or utc_now(),
        "server_received_at": utc_now(),
    }
    if payload.id:
        event_kwargs["id"] = payload.id
    event = FeedbackEvent(**event_kwargs)
    db.add(event)
    method_engine.record_feedback_effect(
        db=db,
        task=task,
        user_id=payload.user_id,
        plan_id=payload.plan_id,
        event_type=payload.event_type,
        user_comment=payload.user_comment,
    )
    return event
