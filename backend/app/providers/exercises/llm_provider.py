from app.core.llm_provider import LLMProvider
from app.models.plan_task import PlanTask
from app.schemas.exercise import ExerciseItem


class LLMExerciseProvider:
    name = "llm"

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or LLMProvider()

    def generate(self, task: PlanTask) -> list[ExerciseItem]:
        if not self.llm_provider.state.enabled:
            return []
        return self.llm_provider.generate_exercises_for_task(task)

