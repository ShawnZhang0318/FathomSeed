# Deployment Notes

FathomSeed is a Vue frontend plus a FastAPI backend.

For the first public web version, the simplest production shape is:

```text
Browser
  -> CDN / static hosting for frontend
  -> FastAPI backend
  -> SQLite for early MVP state
```

For a very small launch, you can also run everything on one VPS:

```text
Nginx
  -> frontend static files
  -> FastAPI on localhost:8010
  -> SQLite file on persistent disk
```

## Recommended Paths

### Railway Single-Service Setup

This repository includes a root `Dockerfile` and `railway.toml` for Railway.
The container builds the Vue app first, copies the generated static files into
the FastAPI app, and serves both the web UI and API from one Railway service.

Use this for the first public web version because it avoids frontend/backend
domain wiring.

Railway settings:

```text
Service source: GitHub repository
Builder: Dockerfile
Dockerfile path: Dockerfile
Health check path: /health
```

Add a Railway Volume:

```text
Mount path: /app/backend/storage
```

Recommended variables:

```env
LLM_PROVIDER=none
FULLMIND_STORAGE_DIR=storage
FULLMIND_DB_FILENAME=fullmind_app.db
FULLMIND_SQLITE_JOURNAL_MODE=WAL
```

If you enable model providers later, add the real keys in Railway variables,
not in Git:

```env
LLM_PROVIDER=auto
DEEPSEEK_API_KEY=...
OPENAI_API_KEY=...
DOUBAO_API_KEY=...
```

For the single-service Docker deployment, do not set `VITE_API_BASE`. The
frontend calls the API on the same domain.

SQLite is fine for an early MVP, but keep the Railway service at one replica
while using SQLite. Move to Postgres before serious multi-user production.

### Easiest Overseas Setup

- Frontend: Cloudflare Pages or Vercel
- Backend: Render, Railway, Fly.io, DigitalOcean Droplet, or Hetzner Cloud

Use this if you want quick deployment and Git-based CI.

### Cheapest Stable Overseas Setup

- One VPS
- Nginx
- FastAPI with `uvicorn` or `gunicorn`
- SQLite on disk

Use this if you want predictable cost and do not mind basic server maintenance.

### Mainland China Setup

- Tencent Cloud Lighthouse, Alibaba Cloud Simple Application Server, or Huawei Cloud Flexus
- Nginx
- FastAPI service
- SQLite on persistent disk

Use this if your main users are in Mainland China. Mainland-hosted public websites usually need ICP filing.

## Production Checklist

- Add a real `LICENSE` file.
- Do not commit `.env`, local SQLite files, or `node_modules`.
- Build frontend with `npm run build`.
- Run backend behind a reverse proxy.
- Enable HTTPS.
- Set `VITE_API_BASE` only if frontend and backend are deployed separately.
- Decide whether LLM mode is disabled, BYOK, or centrally hosted.
- Back up the SQLite database if real users are using it.

---

# 部署说明

FathomSeed 是一个 Vue 前端加 FastAPI 后端的项目。

第一个公开网页版，最简单的生产形态是：

```text
浏览器
  -> CDN / 静态托管前端
  -> FastAPI 后端
  -> SQLite 保存早期 MVP 状态
```

如果只是小规模上线，也可以把所有东西都放在一台 VPS 上：

```text
Nginx
  -> 前端静态文件
  -> localhost:8010 上的 FastAPI
  -> 持久化磁盘里的 SQLite 文件
```

## 推荐路径

### Railway 单服务部署

仓库根目录已经包含 `Dockerfile` 和 `railway.toml`，可以直接给 Railway 用。
这个容器会先构建 Vue 前端，再把构建产物复制到 FastAPI，由同一个服务同时提供网页和 API。

第一个公开网页版建议先用这个方案，因为不用处理前后端两个域名和跨域配置。

Railway 设置：

```text
Service source: GitHub repository
Builder: Dockerfile
Dockerfile path: Dockerfile
Health check path: /health
```

添加 Railway Volume：

```text
Mount path: /app/backend/storage
```

推荐环境变量：

```env
LLM_PROVIDER=none
FULLMIND_STORAGE_DIR=storage
FULLMIND_DB_FILENAME=fullmind_app.db
FULLMIND_SQLITE_JOURNAL_MODE=WAL
```

如果后续启用大模型，把真实 Key 放在 Railway 变量里，不要写进 Git：

```env
LLM_PROVIDER=auto
DEEPSEEK_API_KEY=...
OPENAI_API_KEY=...
DOUBAO_API_KEY=...
```

单服务 Docker 部署时，不需要设置 `VITE_API_BASE`。前端会直接调用同域名 API。

SQLite 适合早期 MVP，但使用 SQLite 时 Railway 服务先保持单副本。真实多用户生产环境建议迁移到 Postgres。

### 海外最省心方案

- 前端：Cloudflare Pages 或 Vercel
- 后端：Render、Railway、Fly.io、DigitalOcean Droplet 或 Hetzner Cloud

适合想快速上线、用 Git 自动部署的人。

### 海外最稳低成本方案

- 一台 VPS
- Nginx
- FastAPI，使用 `uvicorn` 或 `gunicorn`
- SQLite 放在磁盘上

适合想要成本稳定，并且能接受基础服务器维护的人。

### 中国大陆方案

- 腾讯云轻量应用服务器、阿里云轻量应用服务器或华为云 Flexus
- Nginx
- FastAPI 服务
- SQLite 放在持久化磁盘上

适合主要用户在中国大陆的情况。中国大陆服务器公开提供网站通常需要 ICP 备案。

## 上线前检查

- 添加正式 `LICENSE` 文件。
- 不要提交 `.env`、本地 SQLite 文件或 `node_modules`。
- 前端使用 `npm run build` 构建。
- 后端放在反向代理后面。
- 启用 HTTPS。
- 只有前后端分开部署时才需要设置 `VITE_API_BASE`。
- 决定大模型模式是关闭、用户自带 Key，还是平台统一提供。
- 如果有真实用户，记得备份 SQLite 数据库。
