from pydantic import BaseModel, Field


class MethodOption(BaseModel):
    code: str
    title: str
    description: str


class MethodOptionsResponse(BaseModel):
    methods: list[MethodOption]


class MethodPreferenceUpsert(BaseModel):
    user_id: str
    subject_area: str = "general"
    method_code: str
    explicit_preference_score: float = Field(ge=0.0, le=1.0)


class MethodPreferenceRead(BaseModel):
    id: str
    user_id: str
    subject_area: str
    method_code: str
    explicit_preference_score: float
    observed_effectiveness_score: float
    confidence: float

    model_config = {"from_attributes": True}

