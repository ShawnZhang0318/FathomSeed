from app.schemas.intent import IntentClarifyResponse


AMBIGUOUS_TERMS = {"数学", "英语", "编程", "天文", "物理", "历史", "哲学", "ai", "机器学习"}


class IntentEngine:
    def clarify(self, text: str) -> IntentClarifyResponse:
        normalized = text.strip()
        subject = self._infer_subject(normalized)
        too_broad = len(normalized) < 12 or normalized.lower() in AMBIGUOUS_TERMS
        questions = []
        if too_broad:
            questions = [
                "你学习这个主题主要是为了考试、工作、项目、研究，还是兴趣了解？",
                "你希望多久看到一个可验证的成果？",
                "你现在的基础更接近零基础、学过一点，还是已经能独立实践？",
            ]

        summary = normalized if not too_broad else f"用户想学习{subject}，但目标、周期和当前基础还需要澄清。"
        return IntentClarifyResponse(
            needs_clarification=too_broad,
            goal_summary=summary,
            subject_area=subject,
            questions=questions,
        )

    def _infer_subject(self, text: str) -> str:
        lowered = text.lower()
        for keyword in AMBIGUOUS_TERMS:
            if keyword.lower() in lowered:
                return keyword
        if "python" in lowered:
            return "Python"
        if "数学" in text or "代数" in text or "微积分" in text:
            return "数学"
        if "代码" in text or "编程" in text or "开发" in text:
            return "编程"
        return "general"

