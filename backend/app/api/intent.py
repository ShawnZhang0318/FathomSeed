from fastapi import APIRouter

from app.core.intent_engine import IntentEngine
from app.schemas.intent import IntentClarifyRequest, IntentClarifyResponse


router = APIRouter(prefix="/intent", tags=["intent"])
engine = IntentEngine()


@router.post("/clarify", response_model=IntentClarifyResponse)
def clarify_intent(payload: IntentClarifyRequest) -> IntentClarifyResponse:
    return engine.clarify(payload.text)

