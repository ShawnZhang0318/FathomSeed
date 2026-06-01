# FathomSeed

**Turn goals into daily practice.**

FathomSeed is an AI learning engine with a built-in fallback. It turns a learning goal into daily practice, flexible learning entry points, and interactive study experiences.

Instead of giving people one static study plan, FathomSeed breaks a goal into the right learning rhythm and chooses the best experience mode for each task: drills, adaptive learning games, podcasts, flashcards, project labs, mentor dialogue, short video or microfilm experiences, and cinematic stories.

It works without an API key. LLMs are optional upgrades for better content, richer exercises, grading, explanations, and personalized rewrites.

## Why It Exists

Most learning tools still look like a calendar, a course list, or a pile of notes.

FathomSeed is built around a different idea:

> Learning content should adapt into the right experience for the learner and the task.

A concept-heavy topic may become a podcast or mentor dialogue.  
A skill that needs fluency may become drills and flashcards.  
A complex applied topic may become a learning game or project lab.  
Feedback changes the next version of the plan instead of rewriting the past.

## Core Ideas

- **LLM enhanced:** connect providers later for smarter generation and feedback.
- **Rhythm-aware planning:** choose J Mode, P Mode, or Adaptive Mode before generating the learning system.
- **Multi-mode learning:** tasks can become drills, learning games, podcasts, flashcards, videos, stories, projects, or dialogue.
- **Daily or flexible planning:** goals can become a clear daily roadmap, a free-choice task pool, or a hybrid of both.
- **Adaptive method mix:** feedback and performance can shift future learning methods.
- **Versioned plans:** pivots create V2, V3, and later versions instead of overwriting history.
- **Offline-friendly UX:** the PWA can view plans and queue feedback offline.

## Current Features

- Goal clarification
- Strategy selection
- J Mode, P Mode, and Adaptive Mode
- Learning method selection
- No-provider fallback for the basic flow
- Multi-mode task planning
- Local template exercises
- Dedicated activity pages for different experience modes
- SQLite-backed state
- Feedback events
- Plan pivoting
- Optional model routing for LLM-enhanced tasks

## Experience Modes

FathomSeed can plan with these learning experiences:

- **Drill:** focused question practice
- **Game:** adaptive learning games, such as simulation labs, scenario choices, roleplay, strategy simulations, and debugging puzzles
- **Podcast:** listenable explanations with transcripts
- **Video:** short video or microfilm scripts for history, biography, poetry, and case-based memory
- **Cinematic:** story-like explanations
- **Project Lab:** small buildable projects
- **Mentor:** guided dialogue and reflection
- **Memory:** flashcards and spaced review
- **Mixed:** lets the task scoring engine choose from all modes

Mixed mode does not force every mode to appear. It only makes every mode available. The task itself still decides what fits best.

## Learning Rhythm Modes

FathomSeed separates "what to learn" from "how tightly the day is planned."

- **J Mode:** clear day-by-day tasks. Best for learners who want structure, deadlines, and a concrete daily checklist.
- **P Mode:** a flexible task pool. Best for learners who want to choose from today's drills, games, podcasts, projects, dialogue, flashcards, or short-video experiences based on energy and curiosity.
- **Adaptive Mode:** a main route with flexible entry points. The system protects the learning direction, while the learner chooses how to enter today's work.

Internally, these modes are stored as `j_mode`, `p_mode`, and `adaptive`.

## Tech Stack

**Frontend**

- Vue 3
- Vite
- Tailwind CSS
- PWA support

**Backend**

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Optional OpenAI-compatible LLM providers

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev:preview
```

Open:

```text
http://127.0.0.1:5183
```

The frontend calls the backend on port `8010` by default. You can override it with:

```env
VITE_API_BASE=http://127.0.0.1:8010
```

## Railway Deployment

The repository includes a root `Dockerfile` and `railway.toml`.

The Railway deployment builds the Vue frontend, copies it into the FastAPI
backend, and serves the web UI and API from one service.

Recommended Railway setup:

```text
Create Project -> Deploy from GitHub repo
Builder: Dockerfile
Health check path: /health
Volume mount path: /app/backend/storage
```

Recommended variables:

```env
LLM_PROVIDER=none
FULLMIND_STORAGE_DIR=storage
FULLMIND_DB_FILENAME=fullmind_app.db
FULLMIND_SQLITE_JOURNAL_MODE=WAL
```

Do not commit real API keys. Add model keys in Railway variables when needed.

For this single-service deployment, leave `VITE_API_BASE` unset.

## LLM Mode

By default, FathomSeed can run without a model provider:

```env
LLM_PROVIDER=none
```

To enable model-enhanced behavior, copy `backend/.env.example` to `backend/.env` and configure one or more providers:

```env
LLM_PROVIDER=auto
# or
LLM_PROVIDER=openai,deepseek,doubao,ollama
```

The model router can choose a model based on task type, output format, difficulty, and provider capability. If no provider is configured, the built-in fallback still handles basic planning and template exercises.

## Project Structure

```text
backend/
  app/
    api/          API routes
    core/         intent, method, plan, exercise, and pivot engines
    db/           SQLite session setup
    llm/          model registry and routing
    models/       SQLAlchemy models
    providers/    exercise and LLM providers
    schemas/      Pydantic schemas
  main.py

frontend/
  src/
    components/   learning and activity UI
    services/     API and offline queue
    stores/       frontend state
    views/        onboarding, plan, exercise, history
```

## Roadmap

- Better local question banks
- More polished activity pages for every experience mode
- LLM-generated exercises and grading
- Document and webpage ingestion
- RAG for long documents and codebases
- Knowledge graph exploration
- Production deployment guides
- Mobile app and mini-program versions

## Repository Description

Suggested GitHub description:

> Turn learning goals into daily multi-mode experiences: drills, learning games, podcasts, flashcards, projects, and adaptive feedback loops.

## License

FathomSeed is licensed under the GNU Affero General Public License v3.0.

You may use, modify, deploy, and commercially use the AGPL version, as long as
you comply with AGPL-3.0. If you distribute a modified version or provide it to
users over a network, you must provide the corresponding source code under
AGPL-3.0.

Closed-source commercial use requires a separate commercial license from the
author. See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md).

---

# FathomSeed / 悟道星火

**把目标变成每日可执行的练习。**

FathomSeed 是一个带基础托底能力的 AI 学习引擎。它会把一个学习目标变成每日练习、自由学习入口和不同的互动学习体验。

它不只是生成一张计划表，而是先判断更适合的学习节奏，再根据任务特点选择合适的体验模式：刷题、学习游戏、播客、闪卡、项目实验室、导师对话、短视频/微电影、故事化理解。

默认不需要 API Key，也不需要接入大模型。接入 LLM 后，可以获得更好的内容生成、练习题、批改、解释和个性化重写。

## 为什么做它

很多学习工具仍然停留在课程列表、笔记、日历和打卡表。

FathomSeed 想做的是另一件事：

> 让学习内容根据学习者和任务本身，自动变成更合适的学习体验。

适合理解的内容，可以变成播客或导师对话。  
需要熟练度的内容，可以变成刷题和闪卡。  
偏应用的内容，可以变成学习游戏或项目实验室。  
用户反馈不会覆盖旧计划，而是生成新的计划版本。

## 核心理念

- 模型增强：接入大模型后升级为智能模式。
- 学习节奏：支持 J人模式、P人模式和自适应模式。
- 多体验学习：任务可以变成刷题、学习游戏、播客、闪卡、视频、故事、项目或对话。
- 灵活规划：可以生成按天路线，也可以生成自由任务池。
- 自适应方法：根据反馈和表现调整后续学习方式。
- 计划版本化：调整计划时生成 V2/V3，不覆盖历史。
- 离线友好：PWA可以离线查看计划并缓存反馈。

## 当前功能

- 目标澄清
- 方案选择
- J人模式、P人模式、自适应模式
- 学习方法选择
- 没有配置模型时的基础托底流程
- 多体验任务规划
- 本地模板练习
- 不同体验模式的专用学习页面
- SQLite 本地状态
- 反馈事件
- 计划动态调整
- 可选的大模型路由能力

## 体验模式

FathomSeed 当前支持这些学习体验：

- 刷题：集中练习题目
- 游戏：根据知识点生成模拟实验、情景选择、角色扮演、策略推演或解谜挑战
- 播客：可听讲解和文字稿
- 视频：短视频/微电影脚本，适合历史故事、人物生平、古诗词意象和案例记忆
- 故事：故事化理解知识
- 项目实验室：做一个小项目来掌握能力
- 导师：对话式引导和反思
- 闪卡：记忆卡片和间隔复习
- 混合：让系统根据任务评分自动选择

混合模式不会强行让所有模式都出现。它只是把所有模式放进候选池，最终仍然由任务本身决定。

## 学习节奏模式

FathomSeed 会把“学什么”和“每天被安排得多紧”分开。

- J人模式：清晰的按天任务。适合喜欢计划、截止日期和每日清单的人。
- P人模式：自由任务池。适合想根据当天状态，从刷题、游戏、播客、项目、对话、闪卡或短视频里自由选择入口的人。
- 自适应模式：有主线，也有选择权。系统守住阶段目标，用户选择今天怎么进入学习。

系统内部对应为 `j_mode`、`p_mode` 和 `adaptive`。

## 快速启动

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev:preview
```

打开：

```text
http://127.0.0.1:5183
```

前端默认调用 `8010` 端口的后端。也可以通过下面的环境变量覆盖：

```env
VITE_API_BASE=http://127.0.0.1:8010
```

## Railway 部署

仓库根目录已经包含 `Dockerfile` 和 `railway.toml`。

Railway 部署时会先构建 Vue 前端，再把静态文件复制进 FastAPI 后端，最终由一个服务同时提供网页和 API。

推荐 Railway 设置：

```text
Create Project -> Deploy from GitHub repo
Builder: Dockerfile
Health check path: /health
Volume mount path: /app/backend/storage
```

推荐环境变量：

```env
LLM_PROVIDER=none
FULLMIND_STORAGE_DIR=storage
FULLMIND_DB_FILENAME=fullmind_app.db
FULLMIND_SQLITE_JOURNAL_MODE=WAL
```

不要提交真实 API Key。后续需要接入模型时，把 Key 放到 Railway Variables 里。

这个单服务部署方案不需要设置 `VITE_API_BASE`。

## 大模型模式

默认可以不配置模型 provider：

```env
LLM_PROVIDER=none
```

如果要启用模型增强，把 `backend/.env.example` 复制为 `backend/.env`，再配置一个或多个 provider：

```env
LLM_PROVIDER=auto
# 或
LLM_PROVIDER=openai,deepseek,doubao,ollama
```

模型路由会根据任务类型、输出格式、难度和模型能力自动选择合适的模型。没有配置模型时，本地托底仍然可以完成基础规划和模板练习。

## 路线图

- 更丰富的本地题库
- 每种体验模式的高完成度专用页面
- LLM 生成练习和批改
- 网页、文档、笔记导入
- 面向长文档和代码库的 RAG
- 知识图谱探索
- 生产部署指南
- 小程序和 App 版本

## License

FathomSeed 使用 GNU Affero General Public License v3.0，即 AGPL-3.0。

你可以使用、修改、部署，甚至商用 AGPL 版本，但必须遵守 AGPL-3.0。
如果你分发修改版，或通过网络服务向用户提供修改版，需要按 AGPL-3.0
提供对应源码。

闭源商业使用需要获得作者单独授予的商业许可证。详见
[COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md)。
