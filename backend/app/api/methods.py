from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.method_engine import MethodEngine
from app.db.session import get_db
from app.schemas.method import (
    MethodOptionsResponse,
    MethodPreferenceRead,
    MethodPreferenceUpsert,
)


router = APIRouter(prefix="/methods", tags=["methods"])
engine = MethodEngine()


@router.get("", response_model=MethodOptionsResponse)
def list_methods() -> MethodOptionsResponse:
    return MethodOptionsResponse(methods=engine.list_methods())


@router.post("/preferences", response_model=MethodPreferenceRead)
def upsert_preference(
    payload: MethodPreferenceUpsert,
    db: Session = Depends(get_db),
) -> MethodPreferenceRead:
    preference = engine.upsert_preference(
        db=db,
        user_id=payload.user_id,
        subject_area=payload.subject_area,
        method_code=payload.method_code,
        score=payload.explicit_preference_score,
    )
    db.commit()
    db.refresh(preference)
    return preference

