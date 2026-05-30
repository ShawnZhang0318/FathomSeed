from app.schemas.strategy import StrategyCard


class StrategyEngine:
    def suggest(self, goal_summary: str, subject_area: str) -> list[StrategyCard]:
        subject_label = subject_area if subject_area != "general" else "这个主题"
        return [
            StrategyCard(
                mode="exam",
                title="应试备考",
                description=f"围绕{subject_label}考点、题型和错题复盘安排节奏。",
                best_for="有明确考试、证书或测评期限",
            ),
            StrategyCard(
                mode="project",
                title="项目实战",
                description=f"用可交付的小项目串起{subject_label}的核心概念。",
                best_for="希望边做边学、形成作品集",
            ),
            StrategyCard(
                mode="job",
                title="求职能力",
                description=f"聚焦{subject_label}的岗位技能、练习和面试输出。",
                best_for="准备转岗、求职或提升工作能力",
            ),
            StrategyCard(
                mode="research",
                title="研究深入",
                description=f"强调阅读、概念框架、问题意识和阶段性综述。",
                best_for="需要理解论文、理论或复杂材料",
            ),
            StrategyCard(
                mode="overview",
                title="快速入门",
                description=f"先建立{subject_label}地图，再选择值得深入的分支。",
                best_for="还在探索方向，想快速形成全局感",
            ),
        ]

