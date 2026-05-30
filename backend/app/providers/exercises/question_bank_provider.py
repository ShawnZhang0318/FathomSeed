from app.models.plan_task import PlanTask
from app.schemas.exercise import ExerciseItem


class LocalQuestionBankProvider:
    name = "local_experience_bank"

    def generate(self, task: PlanTask) -> list[ExerciseItem]:
        banks = {
            "drill": self._drill_bank,
            "game": self._game_bank,
            "quest": self._game_bank,
            "project_lab": self._project_bank,
            "podcast": self._podcast_bank,
            "video": self._video_bank,
            "cinematic": self._cinematic_bank,
            "mentor": self._mentor_bank,
            "memory": self._memory_bank,
            "mixed": self._mixed_bank,
        }
        builder = banks.get(task.experience_mode)
        return builder(task) if builder else []

    def _drill_bank(self, task: PlanTask) -> list[ExerciseItem]:
        if "python" in f"{task.title} {task.description}".lower():
            return [
                ExerciseItem(
                    type="bank_l1",
                    prompt="【单选】你要保存用户输入的项目名称，最合适的 Python 写法是哪一个？\nA. project-name = input()\nB. project_name = input('项目名：')\nC. input = project_name()\nD. print(project_name)",
                    expected_output="参考答案：B。变量名不能包含连字符，input(...) 用来接收用户输入并返回字符串。",
                    hints=["先判断哪一项真的把输入值保存到了变量里。"],
                ),
                ExerciseItem(
                    type="bank_l1",
                    prompt="【填空】补全函数，让它接收一个任务列表 tasks，并返回任务数量：\n\ndef count_tasks(tasks):\n    return ____",
                    expected_output="参考答案：len(tasks)。len 可以返回列表、字符串等容器的长度。",
                    hints=["这个题考察列表长度，不需要循环。"],
                ),
                ExerciseItem(
                    type="bank_l2",
                    prompt="【代码阅读】下面代码会输出什么？为什么？\n\ntasks = ['read', 'code']\ntasks.append('review')\nprint(tasks[-1])",
                    expected_output="参考答案：输出 review。append 会把元素加入列表末尾，tasks[-1] 读取最后一个元素。",
                    hints=["负数索引从列表末尾开始数。"],
                ),
                ExerciseItem(
                    type="bank_l2",
                    prompt="【改错】下面代码想逐行打印任务，但会报错。请写出修正后的代码：\n\ntasks = ['read', 'code']\nfor task in tasks\n    print(task)",
                    expected_output="参考答案：for task in tasks: 后面缺少冒号。修正为：\nfor task in tasks:\n    print(task)",
                    hints=["Python 的代码块通常由冒号和缩进一起标记。"],
                ),
                ExerciseItem(
                    type="bank_l3",
                    prompt="【小综合】写一个函数 done_ratio(tasks)，tasks 是由 True/False 组成的列表，返回完成百分比。比如 [True, False, True] 返回 67。",
                    expected_output="参考答案：\ndef done_ratio(tasks):\n    if not tasks:\n        return 0\n    return round(sum(tasks) / len(tasks) * 100)\n\nTrue 在求和时按 1 计算，False 按 0 计算。",
                    hints=["先处理空列表，再计算 True 的数量占比。"],
                ),
            ]

        return [
            ExerciseItem(
                type="bank_l1",
                prompt=f"【概念题】用一句话解释「{task.title}」要解决什么问题，并举一个最小例子。",
                expected_output="参考答案应包含：问题场景、核心概念、一个具体例子。",
                hints=["不要写定义堆砌，先写它帮你解决什么。"],
            ),
            ExerciseItem(
                type="bank_l2",
                prompt="【变式题】把刚才的例子改一个条件，说明解法哪一步需要变化，哪一步不变。",
                expected_output="参考答案应包含：变化条件、不变结构、调整后的解法。",
                hints=["迁移能力来自识别“哪些没变”。"],
            ),
            ExerciseItem(
                type="bank_l3",
                prompt="【综合题】设计一道需要组合两个知识点才能完成的题，并写出分步解法。",
                expected_output="参考答案应包含：题面、分步路径、关键转折、答案。",
                hints=["先拆路径，再算答案。"],
            ),
        ]

    def _game_bank(self, task: PlanTask) -> list[ExerciseItem]:
        text = f"{task.title} {task.description}".lower()
        if any(token in text for token in ("物理", "实验", "力学", "电路", "physics", "lab", "simulation")):
            return [
                ExerciseItem(
                    type="simulation_lab",
                    prompt="模拟实验：设置一个可调变量、一个观察指标和一个固定条件，先预测结果，再改变变量观察变化。",
                    expected_output="变量表、预测、观察结果、规律解释。",
                    hints=["一次只改一个变量，才能看清因果。"],
                ),
                ExerciseItem(
                    type="lab_report",
                    prompt="实验复盘：如果观察结果和预测不同，写出 2 个可能原因，并说明下一轮如何验证。",
                    expected_output="偏差原因、验证方案、修正后的理解。",
                    hints=["把失败当成反馈，不要直接跳到答案。"],
                ),
            ]
        if any(token in text for token in ("化学", "反应", "方程", "配平", "元素", "chemistry", "formula")):
            return [
                ExerciseItem(
                    type="scenario_choice",
                    prompt="情景选择：你是实验室助手，需要根据条件选择下一步操作。给出 3 个选项，并解释每个选项会导致什么结果。",
                    expected_output="选项、选择结果、知识点解释。",
                    hints=["选项必须能暴露一个常见误解。"],
                ),
                ExerciseItem(
                    type="reaction_dialogue",
                    prompt="对话游戏：设计一段师生对话，让用户通过选择判断反应条件或公式变化是否合理。",
                    expected_output="对话节点、正确选择、错误反馈。",
                    hints=["错误反馈要告诉用户为什么错。"],
                ),
            ]
        if any(token in text for token in ("python", "代码", "编程", "函数", "算法", "debug", "code")):
            return [
                ExerciseItem(
                    type="debug_puzzle",
                    prompt="调试解谜：给出一段有 1 个隐藏错误的代码，让用户根据输入输出定位错误并修复。",
                    expected_output="错误位置、修复代码、定位过程。",
                    hints=["先看输出和预期差异，再查代码。"],
                ),
                ExerciseItem(
                    type="system_choice",
                    prompt="系统选择：给出 3 种实现方案，让用户选择最适合当前目标的一种，并说明取舍。",
                    expected_output="选择、理由、可能风险。",
                    hints=["好方案不是最复杂，而是最贴目标。"],
                ),
            ]
        return [
            ExerciseItem(
                type="game_design",
                prompt="游戏设计：根据今天内容选择一种玩法：模拟实验、情景选择、角色扮演、策略推演或解谜挑战。",
                expected_output="玩法类型、学习目标、操作规则、失败反馈、完成条件。",
                hints=["玩法要服务知识点，不要为了游戏而游戏。"],
            ),
            ExerciseItem(
                type="game_feedback",
                prompt="反馈规则：设计用户做错时的提示，不直接给答案，而是引导他发现误区。",
                expected_output="错误类型、提示语、补救动作。",
                hints=["好的反馈会让用户知道下一步该试什么。"],
            ),
        ]

    def _project_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="project_seed",
                prompt="项目库 Seed：把今天知识做成一个最小工具，例如 CLI 小工具、表格分析器、学习卡片生成器或 Todo 列表。",
                expected_output="项目名称、用户故事、输入输出。",
                hints=["项目越小，越容易形成正反馈。"],
            ),
            ExerciseItem(
                type="project_acceptance",
                prompt="项目验收：写 5 条验收标准，其中至少 2 条是异常场景。",
                expected_output="5 条验收标准。",
                hints=["异常场景能逼你真正理解边界。"],
            ),
        ]

    def _podcast_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="podcast_opening",
                prompt=f"【开场】想象你正在做「{task.title}」，卡住的不是努力程度，而是不知道从哪里下手。今天这段播客会把它拆成一个能听懂的故事。",
                expected_output="开场要让用户知道：为什么今天的知识值得学、它解决什么痛点。",
                hints=["语气要像真人讲给朋友听。"],
            ),
            ExerciseItem(
                type="podcast_script",
                prompt="【正文文字稿】第一段：先用生活类比解释核心概念。第二段：用一个最小例子演示。第三段：指出最常见误区。第四段：给出今天结束前要完成的一个动作。",
                expected_output="完整文字稿应包含：类比、例子、误区、行动问题。",
                hints=["每段控制在 80-140 字，适合朗读。"],
            ),
            ExerciseItem(
                type="podcast_recap",
                prompt="【听后回顾】回答 3 个问题：它解决什么问题？最小例子是什么？我最容易错在哪里？",
                expected_output="3 个回顾答案，用来判断是否真的听懂。",
                hints=["听完后不要立刻划走，先复述。"],
            ),
        ]

    def _mixed_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            *self._drill_bank(task)[:2],
            *self._game_bank(task)[:1],
            *self._podcast_bank(task)[:2],
            *self._video_bank(task)[:1],
            *self._cinematic_bank(task)[:1],
            *self._mentor_bank(task)[:1],
            *self._memory_bank(task)[:1],
            *self._project_bank(task)[:1],
        ]

    def _video_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="micro_video_script",
                prompt="短视频脚本：设计 5 个镜头，分别是开场画面、人物/场景、关键冲突、记忆锚点、结尾回望。",
                expected_output="镜头表：画面、旁白、情绪、知识点映射。",
                hints=["不要写成老师讲课，先让画面把情绪和关系立起来。"],
            ),
            ExerciseItem(
                type="memory_anchor",
                prompt="记忆锚点：为这支短视频设计 2 个能帮助记忆的画面符号或台词。",
                expected_output="画面符号/台词 + 对应知识点。",
                hints=["锚点要一想起来就能带出知识点。"],
            )
        ]

    def _cinematic_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="cinematic_template",
                prompt="电影模板：角色误解一个知识点，引发冲突，最后通过正确理解解决问题。",
                expected_output="故事梗概 + 知识点映射。",
                hints=["故事必须落回现实练习。"],
            )
        ]

    def _mentor_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="mentor_template",
                prompt="导师模板：解释 -> 追问 -> 找漏洞 -> 重写解释 -> 举例验证。",
                expected_output="一轮导师对话记录。",
                hints=["追问要让用户发现自己哪里没懂。"],
            )
        ]

    def _memory_bank(self, task: PlanTask) -> list[ExerciseItem]:
        return [
            ExerciseItem(
                type="memory_template",
                prompt="记忆模板：5 张闪卡 + 3 个主动回忆问题 + 1/3/7 天复习队列。",
                expected_output="闪卡和复习安排。",
                hints=["每张卡只测一个最小知识点。"],
            )
        ]
