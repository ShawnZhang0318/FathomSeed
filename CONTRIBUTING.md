# Contributing to FathomSeed

Thanks for wanting to help.

FathomSeed is still early, so the best contributions are clear, focused, and easy to review.

## What Helps Most

- Better local question banks
- Better activity pages for drills, learning games, podcasts, flashcards, projects, and dialogue
- Cleaner learning method scoring
- Bug fixes
- Small UX improvements
- Documentation that explains the product in plain language
- LLM provider adapters that preserve the no-provider fallback

## Product Rules

Please keep these ideas intact:

- The app must work without an LLM.
- SQLite is the MVP source of truth.
- LLMs should enhance the product, not become a startup requirement.
- A plan change should create a new version instead of overwriting history.
- Mixed mode should make multiple experiences available, not force every mode into every plan.
- UX should feel like a learning product, not an admin dashboard.

## Local Setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev:preview
```

## Before Opening a Pull Request

- Keep the change small and focused.
- Do not commit local databases, `node_modules`, build output, or API keys.
- Test the no-provider fallback.
- If you add LLM behavior, make sure the same flow still has a fallback path.
- Explain what changed and how you tested it.

## Contributor License

By submitting a contribution, you agree that the maintainer may use, modify,
distribute, and sublicense your contribution as part of FathomSeed, including
under AGPL-3.0 and under separate commercial licenses.

This matters because FathomSeed uses AGPL-3.0 publicly while also keeping a
separate commercial licensing path for closed-source commercial use.

## Commit Style

Use short, plain commit messages:

```text
Add local drill question bank
Improve podcast activity transcript
Fix plan pivot duplicate event handling
```

---

# 参与贡献

谢谢你愿意参与 FathomSeed。

项目还在早期阶段，所以最好的贡献是清晰、聚焦、容易 review 的改动。

## 最需要的贡献

- 更好的本地题库
- 更完整的刷题、学习游戏、播客、闪卡、项目、对话体验页
- 更合理的学习方式评分逻辑
- Bug 修复
- 小而有效的 UX 改进
- 用人话写清楚的文档
- 保持无模型托底能力的大模型 provider

## 产品原则

请尽量保持这些原则：

- 项目必须在没有大模型时也能使用。
- SQLite 是 MVP 的权威状态源。
- 大模型是增强能力，不是启动前提。
- 调整计划时生成新版本，不覆盖历史。
- 混合模式是让多种体验进入候选池，不是强迫每个计划都出现所有模式。
- 界面应该像学习产品，不要像后台管理系统。

## 本地启动

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

前端：

```bash
cd frontend
npm install
npm run dev:preview
```

## 提交 PR 前

- 保持改动小而聚焦。
- 不要提交本地数据库、`node_modules`、构建产物或 API Key。
- 先测试没有大模型时的托底流程。
- 如果新增大模型能力，必须保留 fallback。
- 说明你改了什么，以及怎么测试的。

## 贡献者授权

提交贡献即表示你同意维护者可以把你的贡献作为 FathomSeed 的一部分使用、修改、分发和再授权，包括用于 AGPL-3.0 版本以及维护者单独授予的商业许可证。

这一点很重要，因为 FathomSeed 公开版本使用 AGPL-3.0，同时保留闭源商业使用的单独授权路径。

## Commit 建议

使用简短、清楚的提交信息：

```text
Add local drill question bank
Improve podcast activity transcript
Fix plan pivot duplicate event handling
```
