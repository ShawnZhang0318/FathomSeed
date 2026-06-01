from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.task import PlanTaskRead


class PlanGenerateRequest(BaseModel):
    user_id: str | None = None
    goal_summary: str = Field(min_length=1)
    title: str | None = None
    subject_area: str = "general"
    goal_mode: str = "overview"
    planning_mode: str = Field(default="adaptive", pattern="^(j_mode|p_mode|adaptive|roadmap|flow|hybrid)$")
    selected_methods: list[str] = Field(default_factory=lambda: ["mixed"])
    selected_experiences: list[str] | None = None
    duration_days: int = Field(default=14, ge=1, le=180)
    daily_minutes: int = Field(default=45, ge=10, le=480)
    source_summary: str | None = None


class LearningPlanRead(BaseModel):
    id: str
    user_id: str
    plan_group_id: str
    parent_plan_id: str | None
    version: int
    title: str
    goal_summary: str
    goal_mode: str
    planning_mode: str = "adaptive"
    method_policy: str
    method_mix: dict[str, float]
    experience_policy: str = "mixed"
    experience_mix: dict[str, float] = Field(default_factory=dict)
    duration_days: int
    daily_minutes: int
    status: str
    revision_reason_event_id: str | None
    source_summary: str | None
    generation_mode: str
    created_at: datetime
    updated_at: datetime
    tasks: list[PlanTaskRead] = []

    model_config = {"from_attributes": True}


class PlanPivotRequest(BaseModel):
    event_id: str


class PlanHistoryResponse(BaseModel):
    plans: list[LearningPlanRead]
