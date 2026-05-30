from fastapi import APIRouter

from app.core.strategy_engine import StrategyEngine
from app.schemas.strategy import StrategySuggestRequest, StrategySuggestResponse


router = APIRouter(prefix="/strategies", tags=["strategies"])
engine = StrategyEngine()


@router.post("/suggest", response_model=StrategySuggestResponse)
def suggest_strategies(payload: StrategySuggestRequest) -> StrategySuggestResponse:
    return StrategySuggestResponse(
        strategies=engine.suggest(payload.goal_summary, payload.subject_area)
    )

