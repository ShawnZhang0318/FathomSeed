import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.llm_provider import LLMProvider
from app.core.method_engine import MethodEngine
from app.db.base import utc_now
from app.models.feedback_event import FeedbackEvent
from app.models.learning_plan import LearningPlan
from app.models.plan_task import PlanTask


class PivotEngine:
    def __init__(
        self,
        method_engine: MethodEngine | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.method_engine = method_engine or MethodEngine()
        self.llm_provider = llm_provider or LLMProvider()

    def pivot(self, db: Session, plan_id: str, event_id: str) -> LearningPlan:
        plan = db.scalar(
            select(LearningPlan)
            .options(selectinload(LearningPlan.tasks))
            .where(LearningPlan.id == plan_id)
        )
        if plan is None:
            raise ValueError("Plan not found")

        feedback = db.get(FeedbackEvent, event_id)
        if feedback is None or feedback.plan_id != plan_id:
            raise ValueError("Feedback event not found for this plan")

        existing = db.scalar(select(LearningPlan).where(LearningPlan.revision_reason_event_id == event_id))
        if existing is not None:
            return existing

        current_experience_mix = plan.experience_mix or plan.method_mix or {"drill": 0.4, "mentor": 0.3, "podcast": 0.3}
        new_experience_mix = self.method_engine.adjust_mix_for_feedback(current_experience_mix, feedback.event_type)
        new_method_mix = self.method_engine.build_method_mix(list(new_experience_mix.keys()))

        new_plan = LearningPlan(
            user_id=plan.user_id,
            plan_group_id=plan.plan_group_id,
            parent_plan_id=plan.id,
            version=plan.version + 1,
            title=plan.title,
            goal_summary=plan.goal_summary,
            goal_mode=plan.goal_mode,
            method_policy="mixed",
            method_mix=new_method_mix,
            experience_policy="mixed",
            experience_mix=new_experience_mix,
            duration_days=plan.duration_days,
            daily_minutes=plan.daily_minutes,
            status="active",
            revision_reason_event_id=feedback.id,
            source_summary=plan.source_summary,
            generation_mode="hybrid" if self.llm_provider.state.enabled else "local",
        )
        db.add(new_plan)
        db.flush()

        incomplete_tasks = [task for task in plan.tasks if task.status not in {"completed", "skipped"}]
        if not incomplete_tasks:
            incomplete_tasks = [task for task in plan.tasks[-1:]]

        day_number = 1
        position = 1
        used_minutes = 0
        for task in incomplete_tasks:
            for new_task in self._copy_or_split_task(task, feedback.event_type, new_plan.id, day_number):
                if used_minutes + new_task.estimated_minutes > new_plan.daily_minutes and used_minutes > 0:
                    day_number += 1
                    position = 1
                    used_minutes = 0
                new_task.day_number = day_number
                new_task.position = position
                title, description = self.llm_provider.polish_task(new_task.title, new_task.description)
                new_task.title = title
                new_task.description = description
                db.add(new_task)
                used_minutes += new_task.estimated_minutes
                position += 1

        plan.status = "superseded"
        feedback.processed_at = utc_now()
        db.flush()
        return new_plan

    def _copy_or_split_task(
        self,
        task: PlanTask,
        event_type: str,
        new_plan_id: str,
        day_number: int,
    ) -> list[PlanTask]:
        base_minutes = max(10, min(task.estimated_minutes, 35))
        if event_type in {"TOO_HARD", "NOT_UNDERSTOOD", "WANT_MORE_EXPLANATION"}:
            return [
                self._clone_task(
                    task,
                    new_plan_id,
                    day_number,
                    title_suffix="导师补救",
                    experience_mode="mentor",
                    exercise_type="mentor_dialogue",
                    estimated_minutes=max(10, base_minutes // 2),
                    difficulty=max(0.2, task.difficulty - 0.15),
                ),
                self._clone_task(
                    task,
                    new_plan_id,
                    day_number,
                    title_suffix="播客讲解",
                    experience_mode="podcast",
                    exercise_type="podcast_script",
                    estimated_minutes=max(10, base_minutes // 2),
                    difficulty=max(0.2, task.difficulty - 0.1),
                ),
            ]

        if event_type == "WANT_MORE_PRACTICE":
            return [
                self._clone_task(
                    task,
                    new_plan_id,
                    day_number,
                    title_suffix="题库加练",
                    experience_mode="drill",
                    exercise_type="question_set",
                    estimated_minutes=base_minutes,
                    difficulty=task.difficulty,
                )
            ]

        if event_type == "BORING":
            return [
                self._clone_task(
                    task,
                    new_plan_id,
                    day_number,
                    title_suffix="游戏化改写",
                    experience_mode="game",
                    exercise_type="game_experience",
                    estimated_minutes=base_minutes,
                    difficulty=task.difficulty,
                )
            ]

        return [
            self._clone_task(
                task,
                new_plan_id,
                day_number,
                title_suffix="调整后",
                experience_mode=task.experience_mode,
                exercise_type=task.exercise_type,
                estimated_minutes=base_minutes,
                difficulty=task.difficulty,
            )
        ]

    def _clone_task(
        self,
        task: PlanTask,
        new_plan_id: str,
        day_number: int,
        title_suffix: str,
        experience_mode: str,
        exercise_type: str,
        estimated_minutes: int,
        difficulty: float,
    ) -> PlanTask:
        method_code = self.method_engine.strategy_for_experience(experience_mode)
        return PlanTask(
            id=str(uuid.uuid4()),
            plan_id=new_plan_id,
            source_task_id=task.id,
            day_number=day_number,
            position=1,
            title=f"{task.title} - {title_suffix}",
            description=f"{task.description}\n\n调整说明：根据反馈切换体验模式或降低学习坡度。",
            method_code=method_code,
            experience_mode=experience_mode,
            skill_type=task.skill_type,
            expected_outcome=task.expected_outcome,
            exercise_type=exercise_type,
            content_format=self._content_format_for_experience(experience_mode, exercise_type),
            estimated_minutes=estimated_minutes,
            difficulty=round(difficulty, 2),
            progress_percent=0,
            status="pending",
        )

    def _content_format_for_experience(self, experience_mode: str, exercise_type: str) -> str:
        formats = {
            "drill": "question_bank",
            "game": "learning_game",
            "quest": "learning_game",
            "podcast": "audio_script",
            "video": "micro_video",
            "cinematic": "story_script",
            "project_lab": "project_brief",
            "mentor": "dialogue",
            "memory": "flashcards",
        }
        return formats.get(experience_mode, exercise_type)
