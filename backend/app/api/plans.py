import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.llm_provider import LLMProvider
from app.core.method_engine import MethodEngine
from app.core.pivot_engine import PivotEngine
from app.core.plan_generator import PlanGenerator
from app.db.session import get_db
from app.models.learning_plan import LearningPlan
from app.models.plan_task import PlanTask
from app.models.user_profile import UserProfile
from app.schemas.plan import (
    LearningPlanRead,
    PlanGenerateRequest,
    PlanHistoryResponse,
    PlanPivotRequest,
)


router = APIRouter(prefix="/plans", tags=["plans"])
method_engine = MethodEngine()
plan_generator = PlanGenerator(method_engine=method_engine)
pivot_engine = PivotEngine(method_engine=method_engine)
llm_provider = LLMProvider()


@router.post("/generate", response_model=LearningPlanRead)
def generate_plan(payload: PlanGenerateRequest, db: Session = Depends(get_db)) -> LearningPlan:
    profile = _get_or_create_profile(db, payload.user_id, payload.daily_minutes)
    selected_experiences = payload.selected_experiences or payload.selected_methods
    method_mix = method_engine.build_method_mix(selected_experiences)
    method_policy = method_engine.method_policy(selected_experiences)
    experience_mix = method_engine.build_experience_mix(selected_experiences)
    experience_policy = method_engine.experience_policy(selected_experiences)
    plan_group_id = str(uuid.uuid4())
    plan = LearningPlan(
        user_id=profile.id,
        plan_group_id=plan_group_id,
        parent_plan_id=None,
        version=1,
        title=payload.title or payload.goal_summary[:80],
        goal_summary=payload.goal_summary,
        goal_mode=payload.goal_mode,
        method_policy=method_policy,
        method_mix=method_mix,
        experience_policy=experience_policy,
        experience_mix=experience_mix,
        duration_days=payload.duration_days,
        daily_minutes=payload.daily_minutes,
        status="active",
        source_summary=payload.source_summary,
        generation_mode="hybrid" if llm_provider.state.enabled else "local",
    )
    db.add(plan)
    db.flush()

    for draft in plan_generator.create_task_drafts(
        goal_summary=payload.goal_summary,
        selected_methods=selected_experiences,
        duration_days=payload.duration_days,
        daily_minutes=payload.daily_minutes,
        goal_mode=payload.goal_mode,
    ):
        db.add(
            PlanTask(
                plan_id=plan.id,
                day_number=draft.day_number,
                position=draft.position,
                title=draft.title,
                description=draft.description,
                method_code=draft.method_code,
                experience_mode=draft.experience_mode,
                skill_type=draft.skill_type,
                expected_outcome=draft.expected_outcome,
                exercise_type=draft.exercise_type,
                content_format=draft.content_format,
                estimated_minutes=draft.estimated_minutes,
                difficulty=draft.difficulty,
                progress_percent=0,
                status="pending",
            )
        )

    db.commit()
    return _load_plan(db, plan.id)


@router.get("/group/{plan_group_id}", response_model=PlanHistoryResponse)
def get_plan_history(plan_group_id: str, db: Session = Depends(get_db)) -> PlanHistoryResponse:
    plans = list(
        db.scalars(
            select(LearningPlan)
            .options(selectinload(LearningPlan.tasks))
            .where(LearningPlan.plan_group_id == plan_group_id)
            .order_by(LearningPlan.version)
        )
    )
    return PlanHistoryResponse(plans=plans)


@router.get("/{plan_id}", response_model=LearningPlanRead)
def get_plan(plan_id: str, db: Session = Depends(get_db)) -> LearningPlan:
    return _load_plan(db, plan_id)


@router.post("/{plan_id}/pivot", response_model=LearningPlanRead)
def pivot_plan(
    plan_id: str,
    payload: PlanPivotRequest,
    db: Session = Depends(get_db),
) -> LearningPlan:
    try:
        new_plan = pivot_engine.pivot(db, plan_id=plan_id, event_id=payload.event_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return _load_plan(db, new_plan.id)


def _get_or_create_profile(db: Session, user_id: str | None, daily_minutes: int) -> UserProfile:
    if user_id:
        profile = db.get(UserProfile, user_id)
        if profile:
            return profile
    profile = UserProfile(time_budget_daily=daily_minutes)
    db.add(profile)
    db.flush()
    return profile


def _load_plan(db: Session, plan_id: str) -> LearningPlan:
    plan = db.scalar(
        select(LearningPlan)
        .options(selectinload(LearningPlan.tasks))
        .where(LearningPlan.id == plan_id)
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
