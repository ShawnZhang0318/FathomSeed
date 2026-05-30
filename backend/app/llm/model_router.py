from dataclasses import dataclass

from app.llm.model_registry import LEVEL_SCORES, ModelProfile, ModelRegistry
from app.llm.task_descriptor import LLMTaskDescriptor


COST_PENALTY = {
    "free": 0.0,
    "low": 0.04,
    "medium": 0.1,
    "high": 0.18,
}

LATENCY_PENALTY = {
    "fast": 0.0,
    "medium": 0.05,
    "slow": 0.13,
}


@dataclass(frozen=True)
class ModelCandidateScore:
    profile: ModelProfile
    score: float
    reasons: list[str]


@dataclass(frozen=True)
class ModelRouteResult:
    selected: ModelProfile | None
    candidates: list[ModelCandidateScore]
    task: LLMTaskDescriptor


class ModelRouter:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    def route(self, task: LLMTaskDescriptor) -> ModelRouteResult:
        candidates: list[ModelCandidateScore] = []
        for profile in self.registry.list_models():
            if not self._passes_hard_filters(profile, task):
                continue
            score, reasons = self._score(profile, task)
            candidates.append(ModelCandidateScore(profile=profile, score=round(score, 4), reasons=reasons))
        candidates.sort(key=lambda item: item.score, reverse=True)
        selected = candidates[0].profile if candidates else None
        return ModelRouteResult(selected=selected, candidates=candidates, task=task)

    def _passes_hard_filters(self, profile: ModelProfile, task: LLMTaskDescriptor) -> bool:
        if task.needs_image or task.task_type in {"image_generation", "visual_asset_generation"}:
            return profile.supports("image_generation")
        if not profile.supports("text"):
            return False
        if task.needs_structured_output and not profile.supports("structured_json"):
            return False
        return True

    def _score(self, profile: ModelProfile, task: LLMTaskDescriptor) -> tuple[float, list[str]]:
        reasons: list[str] = []
        score = 0.0

        task_quality = profile.task_quality.get(task.task_type, 0.55)
        score += task_quality * 45
        reasons.append(f"task_quality={task_quality:.2f}")

        if task.needs_reasoning:
            value = profile.capability_score("reasoning")
            score += value * 18
            reasons.append(f"reasoning={value:.2f}")
        if task.needs_code:
            value = profile.capability_score("code")
            score += value * 14
            reasons.append(f"code={value:.2f}")
        if task.needs_creativity:
            value = profile.capability_score("creativity")
            score += value * 12
            reasons.append(f"creativity={value:.2f}")
        if task.language == "zh":
            value = profile.capability_score("chinese")
            score += value * 10
            reasons.append(f"zh={value:.2f}")
        if task.needs_structured_output or task.output_type == "json":
            value = profile.capability_score("structured_json")
            score += value * 10
            reasons.append(f"json={value:.2f}")
        if task.output_type in {"long_text", "script"}:
            value = profile.capability_score("long_text")
            score += value * 8
            reasons.append(f"long_text={value:.2f}")
        if task.needs_image:
            value = profile.capability_score("image_generation")
            score += value * 35
            reasons.append(f"image={value:.2f}")

        difficulty_target = self._difficulty_target(task.difficulty)
        difficulty_gap = abs(profile.capability_score("reasoning") - difficulty_target)
        score += max(0.0, 1 - difficulty_gap) * 6
        reasons.append(f"difficulty_fit={1 - difficulty_gap:.2f}")

        cost_penalty = COST_PENALTY.get(profile.cost_level, 0.1) * self._priority_weight(task.cost_priority) * 20
        latency_penalty = LATENCY_PENALTY.get(profile.latency_level, 0.05) * self._priority_weight(task.latency_priority) * 18
        score -= cost_penalty
        score -= latency_penalty
        if cost_penalty:
            reasons.append(f"cost_penalty={cost_penalty:.2f}")
        if latency_penalty:
            reasons.append(f"latency_penalty={latency_penalty:.2f}")

        score += profile.reliability * 8
        if profile.verified:
            score += 2
            reasons.append("verified")
        else:
            score -= 2
            reasons.append("unverified")
        return score, reasons

    def _difficulty_target(self, difficulty: float) -> float:
        if difficulty >= 0.75:
            return LEVEL_SCORES["very_high"]
        if difficulty >= 0.55:
            return LEVEL_SCORES["high"]
        if difficulty >= 0.3:
            return LEVEL_SCORES["medium"]
        return LEVEL_SCORES["low"]

    def _priority_weight(self, priority: str) -> float:
        return {"low": 0.5, "medium": 1.0, "high": 1.5}.get(priority, 1.0)

