from app.models.plan_task import PlanTask
from app.providers.exercises.hybrid_provider import HybridExerciseProvider
from app.providers.exercises.question_bank_provider import LocalQuestionBankProvider
from app.providers.exercises.template_provider import TemplateExerciseProvider
from app.schemas.exercise import ExerciseResponse


class ExerciseEngine:
    def __init__(self) -> None:
        self.template_provider = TemplateExerciseProvider()
        self.question_bank_provider = LocalQuestionBankProvider()
        self.hybrid_provider = HybridExerciseProvider(template_provider=self.template_provider)

    def generate_for_task(self, task: PlanTask) -> ExerciseResponse:
        question_bank_items = self.question_bank_provider.generate(task)
        template_items = self.template_provider.generate(task)
        hybrid_items = self.hybrid_provider.generate(task)
        if question_bank_items:
            return ExerciseResponse(
                task_id=task.id,
                provider="local_experience_bank+template",
                exercises=question_bank_items + template_items,
            )
        return ExerciseResponse(
            task_id=task.id,
            provider=self.hybrid_provider.name,
            exercises=hybrid_items,
        )
