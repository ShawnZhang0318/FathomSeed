from dataclasses import asdict

from fastapi import APIRouter

from app.llm.model_registry import ModelProfile, ModelRegistry
from app.llm.model_router import ModelCandidateScore, ModelRouter
from app.llm.task_descriptor import LLMTaskDescriptor
from app.schemas.llm import (
    LLMModelProfileRead,
    LLMModelsResponse,
    LLMRouteCandidateRead,
    LLMRouteResponse,
    LLMTaskDescriptorRequest,
)


router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/models", response_model=LLMModelsResponse)
def list_models() -> LLMModelsResponse:
    registry = ModelRegistry()
    return LLMModelsResponse(
        enabled=registry.enabled,
        providers=registry.providers(),
        models=[_profile_read(profile) for profile in registry.list_models()],
    )


@router.post("/route", response_model=LLMRouteResponse)
def route_model(payload: LLMTaskDescriptorRequest) -> LLMRouteResponse:
    descriptor = LLMTaskDescriptor(**payload.model_dump())
    result = ModelRouter().route(descriptor)
    return LLMRouteResponse(
        selected=_profile_read(result.selected) if result.selected else None,
        candidates=[_candidate_read(candidate) for candidate in result.candidates],
    )


def _candidate_read(candidate: ModelCandidateScore) -> LLMRouteCandidateRead:
    return LLMRouteCandidateRead(
        model=_profile_read(candidate.profile),
        score=candidate.score,
        reasons=candidate.reasons,
    )


def _profile_read(profile: ModelProfile) -> LLMModelProfileRead:
    return LLMModelProfileRead(**asdict(profile))

