from pydantic import BaseModel, Field


class LLMTaskDescriptorRequest(BaseModel):
    task_type: str = Field(default="exercise_generation")
    output_type: str = "text"
    subject_area: str = "general"
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    language: str = "zh"
    needs_reasoning: bool = False
    needs_creativity: bool = False
    needs_code: bool = False
    needs_image: bool = False
    needs_structured_output: bool = False
    latency_priority: str = "medium"
    cost_priority: str = "medium"


class LLMModelProfileRead(BaseModel):
    id: str
    provider: str
    model: str
    display_name: str
    capabilities: dict
    task_quality: dict[str, float]
    cost_level: str
    latency_level: str
    reliability: float
    verified: bool
    source: str


class LLMRouteCandidateRead(BaseModel):
    model: LLMModelProfileRead
    score: float
    reasons: list[str]


class LLMRouteResponse(BaseModel):
    selected: LLMModelProfileRead | None
    candidates: list[LLMRouteCandidateRead]


class LLMModelsResponse(BaseModel):
    enabled: bool
    providers: list[str]
    models: list[LLMModelProfileRead]

