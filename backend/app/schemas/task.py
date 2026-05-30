from datetime import datetime

from pydantic import BaseModel, Field


class PlanTaskRead(BaseModel):
    id: str
    plan_id: str
    source_task_id: str | None
    day_number: int
    position: int
    title: str
    description: str
    method_code: str
    experience_mode: str = "drill"
    skill_type: str
    expected_outcome: str
    exercise_type: str
    content_format: str = "exercise"
    estimated_minutes: int
    difficulty: float
    progress_percent: int = 0
    status: str
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|in_progress|completed|skipped|deferred)$")


class TaskProgressUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
