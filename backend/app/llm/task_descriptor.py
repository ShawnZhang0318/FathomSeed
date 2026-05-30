from dataclasses import dataclass


@dataclass(frozen=True)
class LLMTaskDescriptor:
    task_type: str
    output_type: str = "text"
    subject_area: str = "general"
    difficulty: float = 0.5
    language: str = "zh"
    needs_reasoning: bool = False
    needs_creativity: bool = False
    needs_code: bool = False
    needs_image: bool = False
    needs_structured_output: bool = False
    latency_priority: str = "medium"
    cost_priority: str = "medium"

