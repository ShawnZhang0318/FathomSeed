from dataclasses import dataclass

from app.core.method_engine import MethodEngine

CORE_EXPERIENCE_ORDER = [
    "drill",
    "game",
    "podcast",
    "video",
    "cinematic",
    "project_lab",
    "mentor",
    "memory",
]


@dataclass(frozen=True)
class TaskDraft:
    day_number: int
    position: int
    title: str
    description: str
    method_code: str
    experience_mode: str
    skill_type: str
    expected_outcome: str
    exercise_type: str
    content_format: str
    estimated_minutes: int
    difficulty: float


class PlanGenerator:
    """Experience generator with a no-provider fallback.

    Goal mode answers "why learn"; experience mode answers "how should this feel".
    Cognitive strategy is still stored in method_code, but the user-facing choice is
    now experience_mode: drill, game, podcast, video, cinematic, project_lab,
    mentor, memory.
    """

    def __init__(self, method_engine: MethodEngine | None = None) -> None:
        self.method_engine = method_engine or MethodEngine()

    def create_task_drafts(
        self,
        goal_summary: str,
        selected_methods: list[str],
        duration_days: int,
        daily_minutes: int,
        goal_mode: str,
        planning_mode: str = "adaptive",
    ) -> list[TaskDraft]:
        planning_mode = self._normalize_planning_mode(planning_mode)
        experience_mix = self.method_engine.build_experience_mix(selected_methods)
        tasks: list[TaskDraft] = []
        total_units = min(duration_days, 8) if planning_mode == "p_mode" else duration_days

        for day in range(1, total_units + 1):
            phase = self._phase_for_day(day, total_units)
            knowledge_focus = self._knowledge_focus(day, phase, goal_mode)
            day_experiences = self._day_experiences(
                day=day,
                phase=phase,
                goal_mode=goal_mode,
                goal_summary=goal_summary,
                knowledge_focus=knowledge_focus,
                experience_mix=experience_mix,
                daily_minutes=daily_minutes,
                planning_mode=planning_mode,
            )
            difficulty = self._difficulty_for_day(day, total_units)

            for position, experience_mode in enumerate(day_experiences, start=1):
                tasks.append(
                    self._draft_for_experience(
                        day_number=day,
                        position=position,
                        experience_mode=experience_mode,
                        goal_summary=goal_summary,
                        knowledge_focus=knowledge_focus,
                        phase=phase,
                        daily_minutes=daily_minutes,
                        task_count=len(day_experiences),
                        difficulty=difficulty,
                        planning_mode=planning_mode,
                    )
                )
        return tasks

    def _normalize_planning_mode(self, planning_mode: str) -> str:
        aliases = {"roadmap": "j_mode", "flow": "p_mode", "hybrid": "adaptive"}
        return aliases.get(planning_mode, planning_mode)

    def _phase_for_day(self, day: int, duration_days: int) -> str:
        progress = day / max(1, duration_days)
        if progress <= 0.28:
            return "foundation"
        if progress <= 0.68:
            return "practice"
        return "integration"

    def _knowledge_focus(self, day: int, phase: str, goal_mode: str) -> str:
        if phase == "foundation":
            focuses = ["概念地图", "核心术语", "最小例子", "常见误区"]
        elif phase == "practice":
            focuses = ["分层练习", "变式迁移", "错因定位", "速度与准确率"]
        else:
            focuses = ["综合输出", "小项目交付", "模拟检验", "复盘迭代"]

        if goal_mode == "project" and phase != "foundation":
            focuses = ["项目功能切片", "验收标准", "调试记录", "交付演示"]
        if goal_mode == "exam" and phase != "foundation":
            focuses = ["高频题型", "限时训练", "错题复盘", "考点串联"]
        return focuses[(day - 1) % len(focuses)]

    def _day_experiences(
        self,
        day: int,
        phase: str,
        goal_mode: str,
        goal_summary: str,
        knowledge_focus: str,
        experience_mix: dict[str, float],
        daily_minutes: int,
        planning_mode: str,
    ) -> list[str]:
        available = [experience for experience in CORE_EXPERIENCE_ORDER if experience in experience_mix]
        if not available:
            available = ["drill", "game", "podcast", "project_lab"]

        if planning_mode == "p_mode":
            max_tasks = 3 if daily_minutes < 50 else 4
        elif planning_mode == "adaptive":
            max_tasks = 2 if daily_minutes < 35 else 3
        else:
            max_tasks = 1 if daily_minutes < 25 else 2 if daily_minutes < 55 else 3
        scores = self._score_experiences(
            goal_summary=goal_summary,
            knowledge_focus=knowledge_focus,
            phase=phase,
            goal_mode=goal_mode,
            daily_minutes=daily_minutes,
            available=available,
            experience_mix=experience_mix,
        )
        ranked = sorted(available, key=lambda item: scores[item], reverse=True)
        if planning_mode == "p_mode":
            return self._balanced_pool_slice(ranked, day, max_tasks)
        return ranked[:max_tasks]

    def _balanced_pool_slice(self, ranked: list[str], day: int, max_tasks: int) -> list[str]:
        if len(ranked) <= max_tasks:
            return ranked
        # P mode is a choice pool: keep the strongest fit first, then expose a few
        # nearby alternatives so the user can enter learning from today's state.
        start = (day - 1) % len(ranked)
        rotated = ranked[start:] + ranked[:start]
        strongest = ranked[0]
        result = [strongest]
        for item in rotated:
            if item not in result:
                result.append(item)
            if len(result) >= max_tasks:
                break
        return result

    def _score_experiences(
        self,
        goal_summary: str,
        knowledge_focus: str,
        phase: str,
        goal_mode: str,
        daily_minutes: int,
        available: list[str],
        experience_mix: dict[str, float],
    ) -> dict[str, float]:
        dimensions = self._learning_dimensions(
            goal_summary=goal_summary,
            knowledge_focus=knowledge_focus,
            phase=phase,
            goal_mode=goal_mode,
            daily_minutes=daily_minutes,
        )
        profiles = {
            "drill": {
                "practice": 1.0,
                "memory": 0.36,
                "understanding": -0.18,
                "execution": 0.1,
                "short_time": 0.22,
            },
            "game": {
                "practice": 0.78,
                "execution": 0.35,
                "motivation": 0.85,
                "understanding": 0.08,
                "short_time": 0.12,
                "simulation": 0.86,
                "decision": 0.74,
            },
            "podcast": {
                "understanding": 0.9,
                "narrative": 0.7,
                "visual": -0.15,
                "practice": -0.2,
                "short_time": 0.08,
            },
            "video": {
                "visual": 0.9,
                "understanding": 0.28,
                "narrative": 0.82,
                "memory": 0.48,
                "motivation": 0.34,
                "short_time": 0.1,
            },
            "cinematic": {
                "narrative": 0.95,
                "understanding": 0.45,
                "motivation": 0.55,
                "memory": 0.18,
                "practice": -0.18,
            },
            "project_lab": {
                "execution": 1.0,
                "practice": 0.38,
                "understanding": 0.18,
                "long_time": 0.45,
                "short_time": -0.42,
            },
            "mentor": {
                "understanding": 0.86,
                "expression": 0.85,
                "diagnostic": 0.72,
                "practice": -0.05,
                "short_time": 0.06,
            },
            "memory": {
                "memory": 1.0,
                "practice": 0.2,
                "short_time": 0.3,
                "understanding": 0.08,
            },
        }
        phase_bonus = {
            "foundation": {
                "podcast": 0.28,
                "mentor": 0.2,
                "video": 0.18,
                "cinematic": 0.1,
                "memory": 0.1,
            },
            "practice": {
                "drill": 0.3,
                "game": 0.24,
                "mentor": 0.12,
                "memory": 0.14,
            },
            "integration": {
                "project_lab": 0.34,
                "cinematic": 0.18,
                "video": 0.16,
                "game": 0.12,
            },
        }
        goal_bonus = self._goal_bonus(goal_mode=goal_mode, phase=phase)
        scores: dict[str, float] = {}
        for experience in available:
            score = experience_mix.get(experience, 0.0) * 0.8
            for dimension, value in dimensions.items():
                score += profiles.get(experience, {}).get(dimension, 0.0) * value
            score += phase_bonus.get(phase, {}).get(experience, 0.0)
            score += goal_bonus.get(experience, 0.0)
            if phase == "foundation" and experience == "project_lab":
                score -= 0.22
            scores[experience] = round(score, 4)
        return scores

    def _goal_bonus(self, goal_mode: str, phase: str) -> dict[str, float]:
        if goal_mode == "exam":
            return {"drill": 0.38, "memory": 0.26, "mentor": 0.14, "game": 0.12}
        if goal_mode == "job":
            return {"project_lab": 0.28, "drill": 0.18, "mentor": 0.12, "game": 0.12}
        if goal_mode == "project":
            if phase == "foundation":
                return {"podcast": 0.18, "video": 0.16, "mentor": 0.16, "memory": 0.1, "game": 0.08}
            return {"project_lab": 0.36, "game": 0.18, "video": 0.12, "mentor": 0.1, "drill": 0.08}
        if goal_mode == "research":
            return {"mentor": 0.28, "podcast": 0.2, "memory": 0.12, "video": 0.08}
        return {"podcast": 0.18, "video": 0.16, "cinematic": 0.14, "memory": 0.1}

    def _learning_dimensions(
        self,
        goal_summary: str,
        knowledge_focus: str,
        phase: str,
        goal_mode: str,
        daily_minutes: int,
    ) -> dict[str, float]:
        text = f"{goal_summary} {knowledge_focus} {goal_mode}".lower()
        dimensions = {
            "understanding": 0.35,
            "practice": 0.35,
            "execution": 0.25,
            "memory": 0.25,
            "expression": 0.22,
            "visual": 0.18,
            "narrative": 0.16,
            "diagnostic": 0.24,
            "motivation": 0.24,
            "simulation": 0.12,
            "decision": 0.12,
            "short_time": 1.0 if daily_minutes <= 35 else 0.35 if daily_minutes <= 60 else 0.0,
            "long_time": 1.0 if daily_minutes >= 75 else 0.35 if daily_minutes >= 50 else 0.0,
        }

        if phase == "foundation":
            self._boost(dimensions, {"understanding": 0.35, "expression": 0.2, "visual": 0.16, "memory": 0.12})
        elif phase == "practice":
            self._boost(dimensions, {"practice": 0.42, "diagnostic": 0.18, "memory": 0.12})
        else:
            self._boost(dimensions, {"execution": 0.42, "expression": 0.18, "practice": 0.12})

        if goal_mode == "exam":
            self._boost(dimensions, {"practice": 0.38, "memory": 0.32, "diagnostic": 0.22})
        elif goal_mode in {"job", "project"}:
            self._boost(dimensions, {"execution": 0.45, "practice": 0.18, "expression": 0.16})
        elif goal_mode == "research":
            self._boost(dimensions, {"understanding": 0.32, "expression": 0.24, "memory": 0.14})

        keyword_boosts = {
            "understanding": ["why", "principle", "theory", "concept", "understand", "原理", "概念", "理解", "证明", "理论"],
            "practice": ["exercise", "quiz", "problem", "exam", "test", "刷题", "题", "考试", "练习", "算法"],
            "execution": ["project", "build", "code", "portfolio", "deliver", "项目", "实战", "代码", "作品", "开发"],
            "memory": ["remember", "vocabulary", "formula", "recite", "记忆", "背", "单词", "公式", "术语"],
            "visual": ["geometry", "visual", "diagram", "空间", "几何", "图像", "可视化", "结构"],
            "narrative": ["history", "story", "case", "movie", "biography", "poem", "poetry", "故事", "历史", "人物", "生平", "案例", "电影", "诗词", "古诗", "文学", "传记"],
            "simulation": ["physics", "experiment", "lab", "simulation", "物理", "实验", "仿真", "模拟", "力学", "电路"],
            "decision": ["chemistry", "formula", "reaction", "choice", "dialogue", "化学", "公式", "反应", "配平", "情景", "选择", "对话"],
        }
        for dimension, keywords in keyword_boosts.items():
            if any(keyword in text for keyword in keywords):
                dimensions[dimension] = min(1.0, dimensions[dimension] + 0.28)

        return {key: min(1.0, max(0.0, value)) for key, value in dimensions.items()}

    def _boost(self, dimensions: dict[str, float], boosts: dict[str, float]) -> None:
        for key, amount in boosts.items():
            dimensions[key] = min(1.0, dimensions.get(key, 0.0) + amount)

    def _game_format_for_goal(self, goal_summary: str, knowledge_focus: str) -> dict[str, str]:
        text = f"{goal_summary} {knowledge_focus}".lower()
        if any(token in text for token in ("physics", "物理", "实验", "力学", "电路", "光学", "仿真", "模拟")):
            return {
                "label": "模拟实验游戏",
                "title_suffix": "模拟实验",
                "description": "让用户调节变量、观察结果、记录规律，再解释现象背后的原理",
                "outcome": "完成一次变量控制实验，写出观察结果和规律解释",
                "content_format": "simulation_lab",
            }
        if any(token in text for token in ("chemistry", "化学", "公式", "方程", "反应", "配平", "元素", "酸碱")):
            return {
                "label": "情景选择游戏",
                "title_suffix": "情景选择",
                "description": "把反应条件、公式变化或概念判断放进情境对话，让用户通过选择推动结果",
                "outcome": "完成情景选择并解释每个关键选择对应的知识点",
                "content_format": "scenario_choice",
            }
        if any(token in text for token in ("history", "case", "故事", "历史", "政治", "经济", "案例")):
            return {
                "label": "策略推演游戏",
                "title_suffix": "策略推演",
                "description": "让用户在历史或案例情境中做决策，比较不同选择带来的后果",
                "outcome": "完成一次决策推演，复盘选择、后果和知识映射",
                "content_format": "strategy_simulation",
            }
        if any(token in text for token in ("language", "speaking", "英语", "日语", "口语", "写作", "表达")):
            return {
                "label": "角色扮演游戏",
                "title_suffix": "角色扮演",
                "description": "把知识点放进对话角色和真实任务，让用户用语言完成沟通目标",
                "outcome": "完成一轮角色对话，并标记表达错误和可替换说法",
                "content_format": "roleplay_game",
            }
        if any(token in text for token in ("code", "python", "编程", "代码", "算法", "debug", "函数")):
            return {
                "label": "调试解谜游戏",
                "title_suffix": "调试解谜",
                "description": "把代码错误、输入输出和隐藏条件做成解谜任务，让用户逐步定位问题",
                "outcome": "找出关键错误，修复代码，并说明定位路径",
                "content_format": "debug_puzzle",
            }
        return {
            "label": "互动任务游戏",
            "title_suffix": "互动挑战",
            "description": "根据今天的知识点生成操作目标、选择节点、反馈结果和完成条件",
            "outcome": "完成一局互动学习任务，并复盘关键知识点",
            "content_format": "learning_game",
        }

    def _video_format_for_goal(self, goal_summary: str, knowledge_focus: str) -> dict[str, str]:
        text = f"{goal_summary} {knowledge_focus}".lower()
        if any(token in text for token in ("history", "历史", "朝代", "战争", "事件", "制度", "政治")):
            return {
                "label": "历史微电影",
                "title_suffix": "历史微电影",
                "description": "用时代背景、人物选择、关键冲突和后果反转串起知识点",
                "outcome": "产出一支历史微电影脚本，包含场景、人物、冲突、旁白和记忆锚点",
                "content_format": "history_microfilm",
            }
        if any(token in text for token in ("biography", "人物", "生平", "传记", "作者", "科学家", "诗人")):
            return {
                "label": "人物小传短片",
                "title_suffix": "人物小传",
                "description": "用一个人物的选择、挫折、转折和代表作品建立长期记忆",
                "outcome": "产出一支人物小传短片脚本，包含人生节点和知识映射",
                "content_format": "biography_short",
            }
        if any(token in text for token in ("poem", "poetry", "古诗", "诗词", "意象", "文学", "散文", "文言")):
            return {
                "label": "诗词意象短片",
                "title_suffix": "意象短片",
                "description": "把意象、情绪、场景和句子节奏转成可视化镜头",
                "outcome": "产出一支诗词意象短片脚本，包含画面、旁白、情绪和背诵锚点",
                "content_format": "poetry_visual_short",
            }
        if any(token in text for token in ("case", "案例", "商业", "法律", "心理", "社会", "经济")):
            return {
                "label": "案例短视频",
                "title_suffix": "案例短片",
                "description": "用真实情境、问题升级、选择后果和复盘结论呈现知识点",
                "outcome": "产出一支案例短视频脚本，包含情境、冲突、选择和复盘",
                "content_format": "case_short_video",
            }
        return {
            "label": "短视频学习片",
            "title_suffix": "短视频",
            "description": "用场景、人物、视觉隐喻和结尾复盘把知识点拍成一支短片",
            "outcome": "产出一支短视频脚本，包含镜头、旁白、关键画面和记忆锚点",
            "content_format": "micro_video",
        }

    def _difficulty_for_day(self, day: int, duration_days: int) -> float:
        if duration_days <= 1:
            return 0.45
        progress = (day - 1) / max(1, duration_days - 1)
        return round(min(0.86, 0.32 + progress * 0.46), 2)

    def _minutes_for_task(self, daily_minutes: int, task_count: int, position: int) -> int:
        if task_count <= 1:
            return daily_minutes
        weights = [0.5, 0.32, 0.18]
        return max(8, int(daily_minutes * weights[min(position - 1, len(weights) - 1)]))

    def _draft_for_experience(
        self,
        day_number: int,
        position: int,
        experience_mode: str,
        goal_summary: str,
        knowledge_focus: str,
        phase: str,
        daily_minutes: int,
        task_count: int,
        difficulty: float,
        planning_mode: str,
    ) -> TaskDraft:
        minutes = self._minutes_for_task(daily_minutes, task_count, position)
        phase_label = {"foundation": "地基", "practice": "训练", "integration": "整合"}[phase]
        method_code = self.method_engine.strategy_for_experience(experience_mode)
        game_format = self._game_format_for_goal(goal_summary, knowledge_focus)
        video_format = self._video_format_for_goal(goal_summary, knowledge_focus)

        templates = {
            "drill": (
                f"{phase_label}刷题：{knowledge_focus}分层题组",
                f"围绕「{goal_summary}」做一组 L1 基础题、L2 变式题、L3 综合题，并记录每题的错因和识别信号。",
                "practice",
                "完成一组题库练习、正确率记录和错因卡",
                "question_set",
                "question_bank",
            ),
            "game": (
                f"{phase_label}游戏：{knowledge_focus}{game_format['title_suffix']}",
                f"把「{goal_summary}」转成一个{game_format['label']}：{game_format['description']}。保留明确目标、操作步骤、失败反馈和完成条件。",
                "game",
                game_format["outcome"],
                "game_experience",
                game_format["content_format"],
            ),
            "podcast": (
                f"{phase_label}播客：听懂{knowledge_focus}",
                f"生成一段 5-8 分钟播客脚本：开场故事、口语化解释、类比、常见误解、结尾复盘问题。",
                "audio",
                "产出一份可朗读的播客讲稿和 3 个回顾问题",
                "podcast_script",
                "audio_script",
            ),
            "video": (
                f"{phase_label}视频：{knowledge_focus}{video_format['title_suffix']}",
                f"把「{goal_summary}」做成一个{video_format['label']}：{video_format['description']}。重点是场景、人物、画面、旁白和记忆锚点，而不是课堂讲解。",
                "visual",
                video_format["outcome"],
                "short_video",
                video_format["content_format"],
            ),
            "cinematic": (
                f"{phase_label}电影故事：让{knowledge_focus}发生冲突",
                f"用角色、冲突、误解、反转讲清「{goal_summary}」。最后把故事转成一个现实练习。",
                "story",
                "产出一段电影化故事和一个迁移练习",
                "cinematic_story",
                "story_script",
            ),
            "project_lab": (
                f"{phase_label}项目实验室：交付{knowledge_focus}",
                f"把「{goal_summary}」落成一个小项目切片：用户故事、输入输出、验收标准、异常场景、下一步扩展。",
                "project",
                "交付一个可验收的小项目切片",
                "mini_project",
                "project_brief",
            ),
            "mentor": (
                f"{phase_label}导师对话：追问{knowledge_focus}",
                f"用导师对话检查理解：先解释，再追问，再指出漏洞，最后把解释重写得更清楚。",
                "reflection",
                "完成一轮追问、漏洞定位和解释重写",
                "mentor_dialogue",
                "dialogue",
            ),
            "memory": (
                f"{phase_label}记忆卡：巩固{knowledge_focus}",
                f"把今天内容做成闪卡、主动回忆题和 1/3/7 天复习队列，防止学完就忘。",
                "review",
                "生成闪卡、回忆题和间隔复习安排",
                "memory_cards",
                "flashcards",
            ),
        }
        title, description, skill_type, outcome, exercise_type, content_format = templates.get(
            experience_mode,
            templates["drill"],
        )
        title_prefix = {
            "j_mode": f"Day {day_number}",
            "p_mode": f"入口 {((day_number - 1) * task_count) + position}",
            "adaptive": f"Day {day_number} 可选入口",
        }.get(planning_mode, f"Day {day_number}")
        return TaskDraft(
            day_number=day_number,
            position=position,
            title=f"{title_prefix} · {title}",
            description=description,
            method_code=method_code,
            experience_mode=experience_mode,
            skill_type=skill_type,
            expected_outcome=outcome,
            exercise_type=exercise_type,
            content_format=content_format,
            estimated_minutes=minutes,
            difficulty=difficulty,
        )
