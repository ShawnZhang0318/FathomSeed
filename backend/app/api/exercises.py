from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.exercise_engine import ExerciseEngine
from app.db.session import get_db
from app.models.plan_task import PlanTask
from app.schemas.exercise import ExerciseResponse


router = APIRouter(prefix="/exercises", tags=["exercises"])
engine = ExerciseEngine()


@router.get("/task/{task_id}", response_model=ExerciseResponse)
def get_task_exercises(task_id: str, db: Session = Depends(get_db)) -> ExerciseResponse:
    task = db.get(PlanTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return engine.generate_for_task(task)

