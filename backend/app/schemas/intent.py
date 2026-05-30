from pydantic import BaseModel, Field


class IntentClarifyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class IntentClarifyResponse(BaseModel):
    needs_clarification: bool
    goal_summary: str
    subject_area: str
    questions: list[str] = []

