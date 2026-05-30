from app.models.plan_task import PlanTask
from app.schemas.exercise import ExerciseItem


class TemplateExerciseProvider:
    name = "template"

    def generate(self, task: PlanTask) -> list[ExerciseItem]:
        builders = {
            "concept_check": self._concept_items,
            "question_set": self._question_items,
            "mini_project": self._project_items,
            "teach_back": self._teach_back_items,
            "recall": self._recall_items,
            "game_experience": self._game_items,
            "quest_level": self._game_items,
            "short_video": self._video_items,
            "podcast_script": self._podcast_items,
            "video_storyboard": self._video_items,
            "cinematic_story": self._cinematic_items,
            "mentor_dialogue": self._mentor_items,
            "memory_cards": self._memory_items,
        }
        builder = builders.get(task.exercise_type, self._concept_items)
        return builder(task)

    def _concept_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="concept_card",
                prompt=f"为「{task.title}」制作一张概念卡：定义、用途、最小例子、反例各写一条。",
                expected_output="一张结构化概念卡，能直接放进复习库。",
                hints=["不要只写定义，必须写例子。", "反例可以暴露边界。"],
            ),
            ExerciseItem(
                type="micro_quiz",
                prompt="不看资料，回答 3 个问题：它是什么？什么时候用？不用它会怎样？",
                expected_output="3 个短答案，以及一个仍不确定的问题。",
                hints=["答案越短越好，短说明你更可能真的懂。"],
            ),
        ]

    def _question_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="foundation_set",
                prompt="完成 5 道基础题：先限时独立做，再对照答案记录错因。",
                expected_output="正确率、错题编号、错因一句话。",
                hints=["错因只能选一个主因：概念不清、步骤遗漏、场景识别失败。"],
            ),
            ExerciseItem(
                type="transfer_set",
                prompt="完成 2 道变式题：每题只改变一个条件，写出解法哪里需要调整。",
                expected_output="2 道变式题的思路、关键条件和结论。",
                hints=["不要同时改变多个条件，否则很难定位迁移能力。"],
            ),
        ]

    def _project_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="mini_project_brief",
                prompt="写一个 30-60 分钟能完成的小项目 brief：目标、输入、输出、验收标准。",
                expected_output="项目 brief + 3 条可观察验收标准。",
                hints=["验收标准必须能被别人检查。"],
            ),
            ExerciseItem(
                type="implementation_slice",
                prompt="只完成最核心的一条功能链路，不做美化和扩展。",
                expected_output="一个可运行或可演示的最小切片。",
                hints=["先让它跑起来，再考虑优雅。"],
            ),
        ]

    def _teach_back_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="teach_back",
                prompt="用 5 句话向零基础朋友讲清今天的内容。",
                expected_output="5 句话讲解 + 2 个讲不顺的地方。",
                hints=["不许照抄资料。", "讲不顺的点就是下一轮补救入口。"],
            )
        ]

    def _recall_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="active_recall",
                prompt="合上资料，写出 7 个你还记得的关键词，再回去核对。",
                expected_output="关键词列表、遗漏项、下一次复习时间。",
                hints=["先回忆，再查资料。"],
            )
        ]

    def _game_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="game_setup",
                prompt="选择今天最适合的游戏形态：模拟实验、情景选择、角色扮演、策略推演或解谜挑战。说明为什么这个形态适合当前知识点。",
                expected_output="游戏形态 + 选择理由 + 学习目标。",
                hints=["先看知识点需要观察、判断、操作、记忆还是表达。"],
            ),
            ExerciseItem(
                type="game_loop",
                prompt="设计一轮 5-10 分钟的核心玩法：用户做什么、系统给什么反馈、错误时如何引导。",
                expected_output="操作步骤、反馈规则、失败补救。",
                hints=["反馈要帮助理解，不只是显示对错。"],
            ),
            ExerciseItem(
                type="game_win_condition",
                prompt="写出完成条件：用户做到什么才算真正掌握？再写一个可选的高阶挑战。",
                expected_output="完成条件 + 高阶挑战 + 复盘问题。",
                hints=["完成条件必须能观察，不能只写“理解了”。"],
            ),
        ]

    def _podcast_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="podcast_opening",
                prompt="写一个 60 秒播客开场故事，把今天的知识点放进一个生活场景。",
                expected_output="开场故事 + 今天要解决的问题。",
                hints=["开场要像说给朋友听，不像教材。"],
            ),
            ExerciseItem(
                type="podcast_explainer",
                prompt="写 3 段口语化讲解：直觉解释、类比、常见误解。",
                expected_output="可朗读的播客讲解稿。",
                hints=["每段不超过 120 字。"],
            ),
            ExerciseItem(
                type="podcast_recap",
                prompt="设计 3 个听完后的回顾问题。",
                expected_output="3 个回顾问题 + 参考答案。",
                hints=["问题要能检验是否真的听懂。"],
            ),
        ]

    def _video_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="opening_scene",
                prompt="写一个 15 秒开场画面：地点、人物/物件、情绪、第一句旁白。它要让人想继续看下去。",
                expected_output="开场画面 + 旁白 + 对应知识点。",
                hints=["开场不是讲定义，而是制造画面和问题。"],
            ),
            ExerciseItem(
                type="microfilm_beats",
                prompt="写 4 个短视频段落：背景、冲突、转折、回望。每段都要标出画面、旁白和记忆锚点。",
                expected_output="4 段微电影脚本 + 知识点映射。",
                hints=["适合历史、人物、古诗词和案例的内容，要优先用情境承载记忆。"],
            ),
            ExerciseItem(
                type="closing_recall",
                prompt="写一个结尾复盘：用 3 个问题帮学习者回忆这支短片里的知识线索。",
                expected_output="3 个回忆问题 + 参考答案。",
                hints=["问题要能把画面拉回知识点。"],
            ),
        ]

    def _cinematic_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="story_arc",
                prompt="写一个电影化小故事：主角、冲突、误解、反转、解决。",
                expected_output="一段故事梗概 + 对应知识点。",
                hints=["冲突必须来自知识误解。"],
            ),
            ExerciseItem(
                type="transfer_scene",
                prompt="把故事里的解决办法迁移到一个真实练习场景。",
                expected_output="真实场景 + 练习任务。",
                hints=["故事最后必须落回行动。"],
            ),
        ]

    def _mentor_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="mentor_question",
                prompt="导师追问 1：如果你必须用一句话解释它，你会怎么说？",
                expected_output="一句话解释。",
                hints=["不要超过 30 字。"],
            ),
            ExerciseItem(
                type="mentor_probe",
                prompt="导师追问 2：你的解释在哪个场景下会失效？",
                expected_output="失效场景 + 修正后的解释。",
                hints=["找不到失效场景，通常说明理解还太抽象。"],
            ),
            ExerciseItem(
                type="rewrite",
                prompt="把解释重写成更适合初学者听懂的版本。",
                expected_output="重写版解释 + 一个例子。",
                hints=["重写不是变长，是变清楚。"],
            ),
        ]

    def _memory_items(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="flashcards",
                prompt="生成 5 张闪卡：正面是问题，背面是简短答案。",
                expected_output="5 张 Q/A 闪卡。",
                hints=["每张卡只测一个点。"],
            ),
            ExerciseItem(
                type="review_queue",
                prompt="把今天内容排进 1 天后、3 天后、7 天后的复习队列。",
                expected_output="三次复习安排。",
                hints=["复习任务要短，可以在 5 分钟内完成。"],
            ),
        ]
