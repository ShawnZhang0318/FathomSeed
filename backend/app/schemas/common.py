from enum import StrEnum


class GoalMode(StrEnum):
    EXAM = "exam"
    RESEARCH = "research"
    JOB = "job"
    PROJECT = "project"
    OVERVIEW = "overview"


class GenerationMode(StrEnum):
    LOCAL = "local"
    LLM = "llm"
    HYBRID = "hybrid"


class PlanStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    DEFERRED = "deferred"


class LearningMethod(StrEnum):
    PRACTICE_HEAVY = "practice_heavy"
    CONCEPT_FIRST = "concept_first"
    PROJECT_BASED = "project_based"
    TEACH_BACK = "teach_back"
    SPACED_REVIEW = "spaced_review"
    MIXED = "mixed"


class ExperienceMode(StrEnum):
    DRILL = "drill"
    GAME = "game"
    QUEST = "quest"
    PODCAST = "podcast"
    VIDEO = "video"
    CINEMATIC = "cinematic"
    PROJECT_LAB = "project_lab"
    MENTOR = "mentor"
    MEMORY = "memory"
    MIXED = "mixed"


class FeedbackType(StrEnum):
    TOO_HARD = "TOO_HARD"
    TOO_EASY = "TOO_EASY"
    NO_TIME = "NO_TIME"
    SKIP = "SKIP"
    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    UNDERSTOOD = "UNDERSTOOD"
    NOT_UNDERSTOOD = "NOT_UNDERSTOOD"
    BORING = "BORING"
    WANT_MORE_PRACTICE = "WANT_MORE_PRACTICE"
    WANT_MORE_EXPLANATION = "WANT_MORE_EXPLANATION"
