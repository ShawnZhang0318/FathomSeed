from pydantic import BaseModel


class ExerciseItem(BaseModel):
    type: str
    prompt: str
    expected_output: str
    hints: list[str] = []


class ExerciseResponse(BaseModel):
    task_id: str
    provider: str
    exercises: list[ExerciseItem]

