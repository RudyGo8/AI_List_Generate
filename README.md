# AI List Generate —— 跨境电商 AI 上架基础系统(v1-origin分支)

面向跨境电商商品上架流程的 AI 基础项目，覆盖商品信息处理、翻译、图片 OCR、类目匹配、标题/描述生成与任务化处理。

> 解决痛点：传统商品上架依赖人工经验、规则模板和重复录入，类目选择、跨语言文案、图片文字提取等环节容易低效且不一致。本项目将 LLM、多模态识别、Embedding 匹配、数据库任务状态与缓存机制组织成一条可运行的业务链路，而不是单点模型调用 Demo。

---

## 技术栈

- 后端：FastAPI + SQLAlchemy + MySQL + Redis
- AI 能力：OpenAI 兼容接口、Embedding 服务、OCR、翻译、商品文案生成
- 前端：Vue 3 + Vue Router + Vite
- 依赖管理：uv
- 基础服务：Docker Compose 启动 MySQL / Redis / Embedding

---

## 更新日志

### 2026-06-07
- 重构项目整体架构，统一日志管理，统一docker精简配置

### 2025-07-03
- 实现文本翻译、图片 OCR、类目匹配与标题/描述生成
- Two-Step工作流

### v1-origin

- 打通商品上架主流程
- 支持文本翻译、图片 OCR、类目匹配与标题/描述生成
- 引入任务记录、模型配置、客户端鉴权、缓存与初始化 SQL
- 建立前后端分离的基础工程结构

---

## 核心能力

- 商品上架：接收商品源信息，生成目标平台可用的上架内容
- 类目匹配：基于候选类目、Embedding 与排序逻辑辅助选类目
- 文本生成：生成商品标题、描述等内容
- 翻译：支持单条与批量文本翻译
- OCR：识别图片中的文字信息
- 任务化处理：支持任务状态更新、结果持久化与后续查询

---

## 快速开始

```bash
# 1. 启动基础服务
docker compose up -d

# 2. 安装后端依赖
uv venv .venv
uv sync --group dev

# 3. 启动后端
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 1235

# 4. 启动前端
cd frontend
npm install
npm run dev
```

---

## License

本项目采用 Apache License 2.0 开源。详见 [LICENSE](./LICENSE)。
