# AI List Generate

> 面向跨境电商商品上架流程的 AI 基础项目

## 项目简介

AI List Generate 是一个面向跨境电商商品上架场景的 AI 基础项目。

本项目聚焦于将商品上架流程中高频、重复、依赖人工经验的环节进行系统化处理，包括商品信息整理、翻译、图片 OCR、类目匹配以及上架内容生成，从而降低人工操作成本，提升上架效率与结果一致性。

与传统依赖规则配置、模板填充或推荐算法辅助的商品上架方案，以及只提供单点 AI 能力的脚本式方案不同，本项目更关注“完整业务流程”的组织方式：以前后端分离架构为基础，通过统一接口、任务编排、数据库存储和缓存机制，将商品上架相关能力串联为一个可运行、可扩展的基础版本，并同时支持本地开发模式与基于 Docker Compose 的快速部署方式。

---

## 项目定位

当前文档对应分支：`v1-origin`

`v1-origin` 是本项目的基础版本，主要承担以下作用：

- 搭建跨境电商 AI 上架流程的基础工程结构
- 打通商品上架主链路与辅助能力链路
- 建立前后端分离的系统形态，便于后续业务扩展
- 为后续版本迭代提供可复用的 baseline

可以把这个版本理解为：

> 一个围绕“商品上架流程”构建的 AI 基础业务版本，而不是单独的模型调用 Demo。

---

## 与传统方案的区别

传统商品上架方案通常更多依赖以下方式：

- 基于固定字段映射进行信息填充
- 基于规则或模板生成标题与描述
- 基于传统推荐算法完成类目推荐或相似商品匹配
- 对复杂商品信息仍需较多人工介入修正

相比之下，`v1-origin` 更强调将 AI 能力嵌入完整上架流程中，使系统能够在规则处理之外，进一步结合商品文本、图片 OCR 结果以及业务上下文信息，完成更灵活的内容生成、信息补充与类目辅助判断。

也就是说，这个版本并不是简单把“传统推荐”换个接口名，而是尝试把商品上架从“规则填充”推进到“AI 辅助理解与生成”。

---

## 核心功能

### 1. 商品上架主流程
围绕跨境电商商品上架场景，提供统一业务入口，对商品原始信息进行处理，并生成适用于目标平台的上架内容。

### 2. 商品类目匹配
支持候选类目召回、匹配与排序，辅助完成商品选类目流程，减少人工筛选成本。

### 3. 文本生成能力
支持商品标题、描述等文本内容生成，用于辅助商品信息整理与优化。

### 4. 翻译能力
提供通用翻译接口，适用于跨语言商品信息处理场景。

### 5. OCR 能力
支持图片文字提取，用于商品图片中的文本识别与信息补充。

### 6. 任务化处理
项目包含任务编排与状态管理能力，适合将 AI 处理流程纳入完整业务链路，而不是只做一次性调用。

---

## 技术架构

### 后端
- FastAPI
- SQLAlchemy
- MySQL
- Redis
- OpenAI 兼容模型调用方式
- LangSmith（评测 / 观测相关能力）
- uv（Python 依赖与环境管理）

### 前端
- Vue 3
- Vue Router
- Vite

### 部署方式
- 本地开发启动
- Docker Compose 一键启动

---

## 项目结构

```text
AI_List_Generate/
├─ backend/                  # 后端工程
│  ├─ app/
│  │  ├─ models/             # ORM 数据模型
│  │  ├─ routes/             # 接口路由
│  │  │  ├─ common/          # 通用能力路由（如翻译、OCR）
│  │  │  └─ shop/            # 商品上架相关路由
│  │  ├─ schemas/            # 请求/响应结构定义
│  │  ├─ services/           # 核心业务服务层
│  │  ├─ utils/              # 通用工具、缓存、向量、模型调用等
│  │  ├─ config.py           # 配置与日志
│  │  ├─ database.py         # 数据库连接
│  │  └─ main.py             # 应用入口
│  ├─ eval/                  # 评测相关代码
│  ├─ sql/                   # 初始化 SQL
│  ├─ tests/                 # 测试代码
│  ├─ pyproject.toml         # Python 项目配置
│  └─ Dockerfile             # 后端镜像构建文件
├─ frontend/                 # 前端工程
│  ├─ src/
│  ├─ package.json
│  └─ Dockerfile
├─ files/                    # 业务或样例文件目录
├─ docker-compose.yml        # 容器编排文件
└─ README.md
```

---

## 主要模块说明

### 路由层
- `common/translate`：翻译相关接口
- `common/ocr`：OCR 相关接口
- `shop/ailist`：商品上架主流程接口

### 服务层
- `shop.py`：商品上架主业务流程
- `tasks.py`：任务编排与状态处理
- `category_matcher.py`：类目匹配与候选处理
- `text_generator.py`：文本生成相关能力
- `multimodel_generator.py`：多模态生成相关能力
- `llm.py`：模型调用封装
- `embedding_generator.py`：向量生成相关处理

### 模型层
项目中包含商品源数据、生成结果、任务记录、类目数据、提示词配置、客户端配置等数据模型，说明该版本已经具备较完整的业务数据承载能力。

---

## 适用场景

本项目适用于以下类型场景：

- 跨境电商商品上架流程自动化
- 商品标题、描述等内容的 AI 辅助生成
- 多语言商品信息处理
- 图片文字提取与结构化补充
- 商品类目推荐与匹配
- AI 能力在业务系统中的接口化集成

---

## 快速启动

本项目支持两种启动方式：

- **方式一：本地开发启动**
- **方式二：Docker Compose 一键启动**

### 方式一：本地开发启动

#### 1. 克隆项目并切换到基础版本分支

```bash
git clone https://github.com/RudyGo8/AI_List_Generate.git
cd AI_List_Generate
git checkout v1-origin
```

#### 2. 启动后端

```bash
cd backend
uv venv .venv
uv sync --group dev
uv run uvicorn app.main:app --reload
```

#### 3. 配置后端环境变量

```env
MYSQL_USERNAME=root
MYSQL_PASSWORD=123456
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=ai_list

LOG_PATH=./logs
REDIS_URL=redis://localhost:6379/0
CATEGORY_CACHE_TTL_SECONDS=21600
EMBEDDING_CACHE_TTL_SECONDS=86400
```

#### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

---

### 方式二：Docker Compose 一键启动

项目根目录已提供完整的容器编排文件与镜像构建文件，可直接拉起 MySQL、Redis、Embedding、Backend 和 Frontend 服务。

#### 1. 克隆项目并切换到基础版本分支

```bash
git clone https://github.com/RudyGo8/AI_List_Generate.git
cd AI_List_Generate
git checkout v1-origin
```

#### 2. 复制环境变量文件

```bash
cp .env.compose.example .env.compose
cp backend/.env.compose.example backend/.env.compose
```

#### 3. 按需修改配置

根据本地环境或部署环境，修改：

- `.env.compose`
- `backend/.env.compose`

例如数据库密码、端口、缓存配置、Embedding 模型等参数。

#### 4. 启动全部服务

```bash
docker compose --env-file .env.compose up -d
```

#### 5. 查看运行状态

```bash
docker compose ps
```

#### 6. 查看日志

```bash
docker compose logs -f
```

#### 7. 停止服务

```bash
docker compose down
```

---

## 项目特点

- 面向真实业务流程，而非单点 AI Demo
- 区别于传统规则填充、模板生成与推荐算法辅助方案
- 前后端分离，结构清晰，便于扩展
- 具备商品上架、翻译、OCR、类目匹配等基础能力
- 已引入任务、模型配置、缓存、测试、评测等工程化模块
- 同时支持本地开发模式与 Docker Compose 一键启动
- 可作为后续业务版本演进的基础版本

---

## 版本说明

本仓库包含两个主要版本，分别对应项目从基础方案到迭代方案的演进过程：

### `v1-origin`
项目基础版本。  
该版本主要实现通用跨境电商商品上架流程的 AI 化，包括商品信息处理、翻译、OCR、类目匹配以及上架文案生成等核心能力。

### `v2-iteration`
项目当前迭代版本。  
该版本基于 `v1-origin` 进一步演进，围绕新的业务适配需求与技术迭代方向，对原有流程进行了扩展和增强，用于支撑后续能力升级与方案持续优化。

可以简单理解为：

- `v1-origin`：基础流程版
- `v2-iteration`：增强迭代版

---

## 分支策略

- `v1-origin`：基础版本分支，用于保留第一阶段实现与 baseline 能力
- `v2-iteration`：迭代版本分支，用于承接后续增强开发与方案演进

这种分支保留方式便于进行功能对比、问题回溯以及版本演进说明。

---

## License

本项目采用 Apache License 2.0 开源。  
你可以在遵守许可证条款的前提下使用、修改和分发本项目。  
具体请参见仓库根目录下的 [LICENSE](./LICENSE) 文件。