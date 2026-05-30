# Security Policy

FathomSeed is an early open-source project. Please report security problems responsibly.

## What to Report

Please report:

- API key leaks
- Unsafe file handling
- Path traversal
- Authentication or authorization issues
- SQLite/database corruption risks
- Cross-site scripting
- Dependency vulnerabilities with a real exploit path
- Anything that could expose user learning data

## How to Report

Please do not open a public issue for a sensitive vulnerability.

Use GitHub Security Advisories if enabled for the repository. If it is not enabled yet, contact the maintainer through the GitHub repository owner profile and include:

- What the issue is
- How to reproduce it
- What data or system access may be affected
- Suggested fix, if you have one

## Supported Versions

Only the latest `main` branch is supported while the project is in early development.

## Security Principles

- When no model provider is configured, user content should not be sent to any model provider.
- LLM mode should make provider use explicit.
- Secrets must stay in local `.env` files and never be committed.
- User-generated files must be parsed defensively.
- Offline feedback queues should not store secrets.

---

# 安全策略

FathomSeed 仍处在早期开源阶段。请负责任地报告安全问题。

## 应该报告什么

请报告：

- API Key 泄漏
- 不安全的文件处理
- 路径穿越
- 认证或权限问题
- SQLite / 数据库损坏风险
- 跨站脚本
- 有实际利用路径的依赖漏洞
- 任何可能暴露用户学习数据的问题

## 如何报告

请不要用公开 issue 报告敏感漏洞。

如果仓库开启了 GitHub Security Advisories，请优先使用它。否则可以通过仓库 owner 的 GitHub 主页联系维护者，并说明：

- 问题是什么
- 如何复现
- 可能影响哪些数据或系统权限
- 如果你有建议修复方式，也请一起附上

## 支持版本

项目早期只支持最新的 `main` 分支。

## 安全原则

- 没有配置模型 provider 时，不应该把用户内容发送给任何模型服务。
- 大模型模式应该明确告知 provider 使用。
- 密钥只应该保存在本地 `.env` 文件中，不能提交到仓库。
- 用户上传文件必须防御式解析。
- 离线反馈队列不应保存密钥。
