from app.models.plan_task import PlanTask
from app.providers.exercises.llm_provider import LLMExerciseProvider
from app.providers.exercises.template_provider import TemplateExerciseProvider
from app.schemas.exercise import ExerciseItem


class HybridExerciseProvider:
    name = "hybrid"

    def __init__(
        self,
        template_provider: TemplateExerciseProvider | None = None,
        llm_provider: LLMExerciseProvider | None = None,
    ) -> None:
        self.template_provider = template_provider or TemplateExerciseProvider()
        self.llm_provider = llm_provider or LLMExerciseProvider()

    def generate(self, task: PlanTask) -> list[ExerciseItem]:
        base = self.template_provider.generate(task)
        llm_items = self.llm_provider.generate(task)
        return llm_items or base

