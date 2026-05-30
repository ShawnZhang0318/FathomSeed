from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning_method_preference import LearningMethodPreference
from app.models.method_effectiveness_event import MethodEffectivenessEvent
from app.models.plan_task import PlanTask
from app.schemas.method import MethodOption


EXPERIENCE_OPTIONS = [
    MethodOption(
        code="drill",
        title="刷题模式",
        description="把知识点拆成 L1 基础题、L2 变式题、L3 综合题和错题卡。",
    ),
    MethodOption(
        code="game",
        title="互动游戏",
        description="根据知识类型生成不同游戏：模拟实验、情景选择、策略解谜、角色扮演或挑战任务。",
    ),
    MethodOption(
        code="podcast",
        title="播客讲解",
        description="生成口语化播客脚本，用故事、类比和问答帮你听懂。",
    ),
    MethodOption(
        code="video",
        title="短视频剧场",
        description="把历史故事、人物生平、古诗词意象或案例做成短视频/微电影，用场景和画面帮助理解记忆。",
    ),
    MethodOption(
        code="cinematic",
        title="电影故事",
        description="用角色、冲突、误解和反转讲清抽象知识点。",
    ),
    MethodOption(
        code="project_lab",
        title="项目实验室",
        description="把知识点转成小项目、验收标准、调试记录和迭代任务。",
    ),
    MethodOption(
        code="mentor",
        title="导师对话",
        description="用苏格拉底追问、误区识别和解释重写来逼近理解。",
    ),
    MethodOption(
        code="memory",
        title="记忆卡片",
        description="生成闪卡、主动回忆、间隔复习和遗忘补救队列。",
    ),
    MethodOption(
        code="mixed",
        title="系统混合",
        description="先混合多种体验，再根据表现自动调整比例。",
    ),
]


EXPERIENCE_TO_STRATEGY = {
    "drill": "practice_heavy",
    "game": "practice_heavy",
    "quest": "practice_heavy",
    "podcast": "concept_first",
    "video": "concept_first",
    "cinematic": "concept_first",
    "project_lab": "project_based",
    "mentor": "teach_back",
    "memory": "spaced_review",
    "mixed": "mixed",
}

DEFAULT_MIXED_EXPERIENCE_MIX = {
    "drill": 0.16,
    "game": 0.14,
    "podcast": 0.13,
    "video": 0.1,
    "cinematic": 0.1,
    "project_lab": 0.16,
    "mentor": 0.11,
    "memory": 0.1,
}


class MethodEngine:
    def list_methods(self) -> list[MethodOption]:
        return EXPERIENCE_OPTIONS

    def build_method_mix(self, selected_methods: list[str]) -> dict[str, float]:
        strategy_mix: dict[str, float] = {}
        for experience, weight in self.build_experience_mix(selected_methods).items():
            strategy = EXPERIENCE_TO_STRATEGY.get(experience, "concept_first")
            if strategy == "mixed":
                continue
            strategy_mix[strategy] = strategy_mix.get(strategy, 0) + weight
        return self._normalize(strategy_mix)

    def build_experience_mix(self, selected_experiences: list[str]) -> dict[str, float]:
        experiences = [
            self._canonical_experience(item)
            for item in selected_experiences
            if item and item != "mixed" and self._canonical_experience(item) in EXPERIENCE_TO_STRATEGY
        ]
        if not experiences:
            return self._normalize(DEFAULT_MIXED_EXPERIENCE_MIX)
        weight = round(1 / len(experiences), 3)
        return self._normalize({experience: weight for experience in experiences})

    def method_policy(self, selected_methods: list[str]) -> str:
        experiences = [self._canonical_experience(item) for item in selected_methods if item and item != "mixed"]
        if len(experiences) == 1:
            return EXPERIENCE_TO_STRATEGY.get(experiences[0], experiences[0])
        return "mixed"

    def experience_policy(self, selected_experiences: list[str]) -> str:
        experiences = [self._canonical_experience(item) for item in selected_experiences if item and item != "mixed"]
        if len(experiences) == 1:
            return experiences[0]
        return "mixed"

    def strategy_for_experience(self, experience_mode: str) -> str:
        return EXPERIENCE_TO_STRATEGY.get(self._canonical_experience(experience_mode), "concept_first")

    def upsert_preference(
        self,
        db: Session,
        user_id: str,
        subject_area: str,
        method_code: str,
        score: float,
    ) -> LearningMethodPreference:
        existing = db.scalar(
            select(LearningMethodPreference).where(
                LearningMethodPreference.user_id == user_id,
                LearningMethodPreference.subject_area == subject_area,
                LearningMethodPreference.method_code == method_code,
            )
        )
        if existing:
            existing.explicit_preference_score = score
            existing.confidence = min(1.0, existing.confidence + 0.1)
            return existing

        preference = LearningMethodPreference(
            user_id=user_id,
            subject_area=subject_area,
            method_code=method_code,
            explicit_preference_score=score,
            observed_effectiveness_score=0.5,
            confidence=0.1,
        )
        db.add(preference)
        return preference

    def adjust_mix_for_feedback(self, current_mix: dict[str, float], event_type: str) -> dict[str, float]:
        mix = self._normalize_aliases(current_mix)
        if event_type in {"TOO_HARD", "NOT_UNDERSTOOD", "WANT_MORE_EXPLANATION"}:
            mix["mentor"] = mix.get("mentor", 0) + 0.1
            mix["podcast"] = mix.get("podcast", 0) + 0.08
            mix["drill"] = max(0, mix.get("drill", 0) - 0.06)
        elif event_type == "WANT_MORE_PRACTICE":
            mix["drill"] = mix.get("drill", 0) + 0.12
            mix["game"] = mix.get("game", 0) + 0.06
        elif event_type == "BORING":
            mix["game"] = mix.get("game", 0) + 0.12
            mix["cinematic"] = mix.get("cinematic", 0) + 0.08
            mix["project_lab"] = mix.get("project_lab", 0) + 0.06
        elif event_type in {"HELPFUL", "UNDERSTOOD"}:
            best = max(mix, key=mix.get) if mix else "drill"
            mix[best] = mix.get(best, 0) + 0.05
        return self._normalize(mix)

    def record_feedback_effect(
        self,
        db: Session,
        task: PlanTask | None,
        user_id: str,
        plan_id: str,
        event_type: str,
        user_comment: str | None = None,
    ) -> None:
        if task is None:
            return
        understanding = 0.25 if event_type == "NOT_UNDERSTOOD" else 0.75 if event_type == "UNDERSTOOD" else None
        difficulty = 0.85 if event_type == "TOO_HARD" else 0.2 if event_type == "TOO_EASY" else None
        event = MethodEffectivenessEvent(
            user_id=user_id,
            plan_id=plan_id,
            task_id=task.id,
            method_code=task.experience_mode,
            completion_status=task.status,
            understanding_score=understanding,
            difficulty_score=difficulty,
            user_feedback=user_comment,
        )
        db.add(event)

    def _normalize(self, mix: dict[str, float]) -> dict[str, float]:
        canonical_mix = self._normalize_aliases(mix)
        positive = {key: max(0.0, value) for key, value in canonical_mix.items() if value > 0.001}
        total = sum(positive.values())
        if total <= 0:
            return DEFAULT_MIXED_EXPERIENCE_MIX.copy()
        normalized = {key: round(value / total, 3) for key, value in positive.items()}
        drift = round(1.0 - sum(normalized.values()), 3)
        if normalized and drift:
            first_key = next(iter(normalized))
            normalized[first_key] = round(normalized[first_key] + drift, 3)
        return normalized

    def _canonical_experience(self, experience_mode: str) -> str:
        return "game" if experience_mode == "quest" else experience_mode

    def _normalize_aliases(self, mix: dict[str, float]) -> dict[str, float]:
        normalized: dict[str, float] = {}
        for key, value in mix.items():
            canonical = self._canonical_experience(key)
            normalized[canonical] = normalized.get(canonical, 0.0) + value
        return normalized
