from pydantic import BaseModel, Field


class StrategySuggestRequest(BaseModel):
    goal_summary: str = Field(min_length=1)
    subject_area: str = "general"


class StrategyCard(BaseModel):
    mode: str
    title: str
    description: str
    best_for: str


class StrategySuggestResponse(BaseModel):
    strategies: list[StrategyCard]

