import json
import os
import re
from dataclasses import dataclass

from app.llm.model_router import ModelRouteResult, ModelRouter
from app.llm.providers import ChatMessage
from app.llm.task_descriptor import LLMTaskDescriptor
from app.models.plan_task import PlanTask
from app.schemas.exercise import ExerciseItem


@dataclass(frozen=True)
class LLMState:
    provider: str
    enabled: bool
    models: int = 0


class LLMProvider:
    """Compatibility facade over the model pool and router."""

    def __init__(self, router: ModelRouter | None = None) -> None:
        self.router = router or ModelRouter()

    @property
    def state(self) -> LLMState:
        models = self.router.registry.list_models()
        provider = os.getenv("LLM_PROVIDER", "none").strip().lower() or "none"
        return LLMState(provider=provider, enabled=bool(models), models=len(models))

    def route(self, task: LLMTaskDescriptor) -> ModelRouteResult:
        return self.router.route(task)

    def complete(
        self,
        *,
        task: LLMTaskDescriptor,
        messages: list[ChatMessage],
        temperature: float = 0.3,
        response_format: str | None = None,
    ) -> str | None:
        route = self.router.route(task)
        if route.selected is None:
            return None
        adapter = self.router.registry.adapter_for(route.selected.provider)
        if adapter is None:
            return None
        result = adapter.complete(
            model=route.selected.model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        return result.text

    def generate_exercises_for_task(self, task: PlanTask) -> list[ExerciseItem]:
        descriptor = LLMTaskDescriptor(
            task_type="exercise_generation",
            output_type="json",
            subject_area=task.skill_type or "general",
            difficulty=float(task.difficulty or 0.5),
            language="zh",
            needs_reasoning=True,
            needs_code=_looks_like_code_task(task),
            needs_structured_output=True,
            cost_priority="medium",
            latency_priority="medium",
        )
        messages = [
            ChatMessage(
                role="system",
                content=(
                    "You generate learning exercises for FathomSeed. "
                    "Return strict JSON only. The JSON object must have an `exercises` array. "
                    "Each item must include: type, prompt, expected_output, hints."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    f"Task title: {task.title}\n"
                    f"Task description: {task.description}\n"
                    f"Experience mode: {task.experience_mode}\n"
                    f"Exercise type: {task.exercise_type}\n"
                    f"Difficulty: {task.difficulty}\n"
                    f"Expected outcome: {task.expected_outcome}\n\n"
                    "Generate 3 to 6 concrete exercises in Chinese. "
                    "For drill mode, include answerable questions and reference answers. "
                    "For podcast mode, include readable transcript sections. "
                    "For video mode, create short-video or microfilm-style scenes with visuals, narration, "
                    "characters or objects, emotional beats, and memory anchors. Do not make it a classroom lecture outline. "
                    "For game mode, choose a suitable game format first, such as simulation lab, "
                    "scenario choices, roleplay, strategy simulation, or debugging puzzle. "
                    "Then include rules, actions, feedback, and completion conditions."
                ),
            ),
        ]
        try:
            text = self.complete(task=descriptor, messages=messages, temperature=0.35, response_format="json")
        except Exception:
            return []
        if not text:
            return []
        return _parse_exercise_items(text)

    def polish_task(self, title: str, description: str) -> tuple[str, str]:
        if not self.state.enabled:
            return title, description
        descriptor = LLMTaskDescriptor(
            task_type="structured_rewrite",
            output_type="json",
            language="zh",
            needs_structured_output=True,
            needs_creativity=False,
            cost_priority="low",
            latency_priority="medium",
        )
        messages = [
            ChatMessage(role="system", content="Return strict JSON with `title` and `description` fields."),
            ChatMessage(role="user", content=f"Polish this learning task in Chinese.\nTitle: {title}\nDescription: {description}"),
        ]
        try:
            text = self.complete(task=descriptor, messages=messages, temperature=0.2, response_format="json")
        except Exception:
            return title, description
        if not text:
            return title, description
        try:
            payload = _extract_json_object(text)
        except ValueError:
            return title, description
        next_title = payload.get("title")
        next_description = payload.get("description")
        if isinstance(next_title, str) and isinstance(next_description, str):
            return next_title, next_description
        return title, description


def _parse_exercise_items(text: str) -> list[ExerciseItem]:
    try:
        payload = _extract_json_object(text)
    except ValueError:
        return []
    raw_items = payload.get("exercises")
    if not isinstance(raw_items, list):
        return []
    items: list[ExerciseItem] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        prompt = raw.get("prompt")
        expected_output = raw.get("expected_output")
        if not isinstance(prompt, str) or not isinstance(expected_output, str):
            continue
        hints = raw.get("hints", [])
        if not isinstance(hints, list):
            hints = []
        items.append(
            ExerciseItem(
                type=str(raw.get("type") or "llm_generated"),
                prompt=prompt,
                expected_output=expected_output,
                hints=[str(hint) for hint in hints],
            )
        )
    return items


def _extract_json_object(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("No JSON object found")
        payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("JSON payload is not an object")
    return payload


def _looks_like_code_task(task: PlanTask) -> bool:
    text = f"{task.title} {task.description} {task.expected_outcome}".lower()
    return any(token in text for token in ("python", "code", "代码", "编程", "函数", "算法"))
