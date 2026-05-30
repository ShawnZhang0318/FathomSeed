from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import utc_now
from app.db.session import get_db
from app.models.plan_task import PlanTask
from app.schemas.task import PlanTaskRead, TaskProgressUpdate, TaskStatusUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.patch("/{task_id}/status", response_model=PlanTaskRead)
def update_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
) -> PlanTask:
    task = db.get(PlanTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = payload.status
    if payload.status == "completed":
        task.progress_percent = 100
        task.completed_at = utc_now()
    elif payload.status == "pending":
        task.progress_percent = 0
        task.completed_at = None
    else:
        task.completed_at = None
        if payload.status == "in_progress" and task.progress_percent == 0:
            task.progress_percent = 1
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/progress", response_model=PlanTaskRead)
def update_task_progress(
    task_id: str,
    payload: TaskProgressUpdate,
    db: Session = Depends(get_db),
) -> PlanTask:
    task = db.get(PlanTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.progress_percent = payload.progress_percent
    if payload.progress_percent >= 100:
        task.status = "completed"
        task.completed_at = utc_now()
    elif payload.progress_percent > 0:
        task.status = "in_progress"
        task.completed_at = None
    else:
        task.status = "pending"
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return task
