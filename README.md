# AI 商品列表生成服务

## 项目介绍

本项目是一个基于 FastAPI 的 AI 辅助电商商品上架接口服务，旨在帮助卖家在多平台上架商品时，自动生成符合各平台要求的商品信息。

### 核心功能

1. **AI 商品列表生成** (`/api/r1/shop/ailist`)
   - 基于图片+标题进行类目推理，并通过 hybrid（向量+关键词）匹配站点类目
   - AI 生成商品标题（多语言支持）
   - AI 生成商品描述（多语言支持）
   - AI 生成商品属性

2. **文本翻译** (`/api/r1/c/translate`, `/api/r1/c/batchtranslate`)
   - 单文本翻译
   - 批量文本翻译
   - 多语言支持

3. **图片 OCR 识别** (`/api/r1/c/ocr`)
   - 从商品图片中提取文字信息

### 技术栈

- **Web 框架**: FastAPI
- **数据库**: MySQL (SQLAlchemy ORM)
- **AI 模型**:
  - **Embedding 模型（可选）** - 用于类目语义匹配（未配置时自动降级到关键词匹配）
  - Qwen (通义千问) - 用于商品标题、描述、属性生成
  - Gemini - 备用 LLM
- **API 调用**: OpenAI SDK (兼容 OpenAI 格式)


---

## 项目流程思维导图（场景化）

### 1) 流程梳理（文字版）

- 项目名称：`ai_list_generate`
- 项目目标：面向电商上架场景，提供 AI 商品信息生成、文本翻译、图片 OCR，并对商品生成任务做状态追踪与结果落库。
- 参与角色：用户/调用方、前端、FastAPI 后端、MySQL、LLM/多模态第三方接口、可选回调服务。
- 流程范围：从用户提交请求到同步返回结果或异步回调完成。

主流程步骤：

1. 客户端发起 API 请求（翻译/批量翻译/OCR/商品生成）。
2. 后端进行鉴权与参数校验，不通过则直接返回错误。
3. 根据接口类型进入对应业务流程。
4. 翻译与 OCR：调用模型后直接返回结果与 usage。
5. 商品生成：先写源商品与任务，再执行类目识别、标题生成、描述生成、属性生成。
6. 类目识别优先走 embedding + 关键词混合匹配；embedding 不可用时自动降级关键词匹配。
7. 保存生成结果并更新任务状态（SUCCESS/FAIL）。
8. 有 `notice_url` 时异步回调，无 `notice_url` 时同步返回最终生成内容。

### 2) 标准流程图（Mermaid）

```mermaid
flowchart TD
    A([开始]) --> B[客户端调用 API]
    B --> C{鉴权是否通过?}
    C -- 否 --> C1[返回 401/失败响应] --> Z([结束])
    C -- 是 --> D{参数是否有效?}
    D -- 否 --> D1[返回 4xx/失败响应] --> Z
    D -- 是 --> E{接口类型?}

    E -- translate --> T1[读取提示词并调用 LLM 翻译]
    T1 --> T2[返回 translated_content + usage]
    T2 --> Z

    E -- batchtranslate --> BT1[批量翻译并组装列表结果]
    BT1 --> BT2[返回 translated_content_list + usage]
    BT2 --> Z

    E -- ocr --> O1[调用多模态 OCR 识别图片文字]
    O1 --> O2[返回 word_list + usage]
    O2 --> Z

    E -- shop/ailist --> S1[写入源商品数据与任务记录]
    S1 --> S2{任务创建成功?}
    S2 -- 否 --> S2N[返回 task create fail] --> Z
    S2 -- 是 --> S3[任务置为 PROCESSING]

    S3 --> S4[类目阶段-第1轮: LLM 产出类目文本]
    S4 --> S5{第1轮 Embedding 可用?}
    S5 -- 是 --> S6[第1轮 Hybrid 匹配: 向量+关键词, 召回 Top3]
    S5 -- 否 --> S7[第1轮降级: 仅关键词匹配, 召回 Top3]
    S6 --> S8
    S7 --> S8

    S8[类目阶段-第2轮: LLM 基于 Top3 再推理类目文本] --> S9{第2轮 Embedding 可用?}
    S9 -- 是 --> S10[第2轮 Hybrid 匹配并排序, 取 Top1 作为最终类目]
    S9 -- 否 --> S11[第2轮降级: 仅关键词匹配并排序, 取 Top1]
    S10 --> S12
    S11 --> S12

    S12[生成阶段: 标题/描述/属性] --> S13[写入生成结果表]
    S13 --> S14{保存是否成功?}
    S14 -- 否 --> S14N[任务置 FAIL, 返回 fail] --> Z
    S14 -- 是 --> S15[任务置 SUCCESS]

    S15 --> S16{是否有 notice_url?}
    S16 -- 是 --> S17[异步回调通知结果] --> S18[返回 task_id/成功]
    S16 -- 否 --> S19[同步返回生成结果 + usage]
    S17 --> Z
    S18 --> Z
    S19 --> Z
```

---

## API 时序图

### 商品列表生成流程 (ailist)

#### 异步模式（有回调地址）

```mermaid
%%{init: {'sequence': {'mirrorActors': false}} }%%
sequenceDiagram
    participant Client as 客户端
    participant API as AI商品生成服务
    participant DB as MySQL数据库
    participant LLM as Qwen LLM
    participant Embedding as 嵌入模型
    participant Notice as 回调服务

    Client->>API: 1. 发起商品生成请求(图片、站点、notice_url)
    activate API

    alt 1.1 存在 product_url
        API->>API: 获取商品基础信息
        API-->>API: 返回商品标题/图片/详情
    end

    API->>DB: 2. 写入源商品数据
    activate DB
    DB-->>API: 2.1 返回 src_id
    deactivate DB

    API->>DB: 3. 创建生成任务(status=ready)
    activate DB
    DB-->>API: 3.1 返回 task_id
    deactivate DB

    API-->>Client: 4. 返回任务受理结果(task_id)

    API->>LLM: 5. 识别候选类目(图片+标题)
    activate LLM
    LLM-->>API: 5.1 返回候选类目
    deactivate LLM

    alt 6. Embedding 可用
        API->>Embedding: 6.1 生成候选类目嵌入向量
        activate Embedding
        Embedding-->>API: 6.2 返回候选类目向量
        deactivate Embedding
    else 6. Embedding 不可用
        API->>API: 6.1 降级为关键词匹配
    end

    API->>DB: 7. 查询站点类目列表
    activate DB
    DB-->>API: 7.1 返回 category_list
    deactivate DB

    alt 8. Embedding 可用
        API->>Embedding: 8.1 批量生成站点类目嵌入向量
        activate Embedding
        Embedding-->>API: 8.2 返回类目向量列表
        deactivate Embedding
    else 8. Embedding 不可用
        API->>API: 8.1 保持关键词匹配路径
    end

    API->>API: 9. 计算余弦相似度并筛选 Top-K

    API->>LLM: 10. 选择最佳类目(图片+Top-K类目)
    activate LLM
    LLM-->>API: 10.1 返回最终类目
    deactivate LLM

    alt 10.2 Embedding 可用
        API->>Embedding: 10.2.1 最终类目向量匹配并取 Top1
        activate Embedding
        Embedding-->>API: 10.2.2 返回最终类目
        deactivate Embedding
    else 10.2 Embedding 不可用
        API->>API: 10.2.1 关键词匹配并取 Top1
    end

    API->>LLM: 11. 生成商品标题
    activate LLM
    LLM-->>API: 11.1 返回商品标题
    deactivate LLM

    API->>LLM: 12. 生成商品描述
    activate LLM
    LLM-->>API: 12.1 返回商品描述
    deactivate LLM

    API->>LLM: 13. 生成商品属性
    activate LLM
    LLM-->>API: 13.1 返回商品属性
    deactivate LLM

    API->>DB: 14. 保存生成结果
    activate DB
    DB-->>API: 14.1 保存成功
    deactivate DB

    API->>DB: 15. 更新任务状态(status=success)
    activate DB
    DB-->>API: 15.1 更新成功
    deactivate DB

    alt 16. 存在 notice_url
        API->>Notice: 16.1 发送回调通知
        activate Notice
        Notice-->>API: 16.2 返回回调结果
        deactivate Notice
    end

    deactivate API
```

---

## BGE 模型 Docker 部署

本项目可使用 embedding 模型进行商品类目语义匹配；若 embedding 未配置或不可用，系统会自动降级为关键词匹配，不阻断主流程。

> 说明：当前代码通过 `db_sys_conf` 读取 `EMBEDDING_*` 配置。

### 部署方式

BGE 模型通过 **Docker** 部署为 API 服务，使用 [FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) 项目提供的服务化脚本。

### 1. 启动 BGE-M3 服务

```bash
docker run --gpus all -p 8000:80 -v "%cd%\data:/data" ghcr.io/huggingface/text-embeddings-inference:cuda-1.8.1 --model-id BAAI/bge-m3
```

### 2. 配置存储在数据库

所有配置存储在 MySQL 数据库的 `db_sys_conf` 表中，系统启动时自动读取：

| key | 说明 | 示例值 |
|-----|------|--------|
| EMBEDDING_API_KEY | API 认证密钥 | dummy |
| EMBEDDING_BASE_URL | BGE 服务 API 地址 | http://bge-container-ip:8000/v1 |
| EMBEDDING_MODEL | BGE 模型名称 | BAAI/bge-m3 |

配置示例（插入数据库）：

```sql
INSERT INTO db_sys_conf (`key`, `value`, `enable`) VALUES
('EMBEDDING_API_KEY', 'dummy', 1),
('EMBEDDING_BASE_URL', 'http://192.168.1.100:8080/v1', 1),
('EMBEDDING_MODEL', 'BAAI/bge-m3', 1);
```

> 应用会在调用嵌入服务时从数据库动态读取这些配置，修改配置后无需重启服务。

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_HOST | MySQL 主机 | localhost |
| MYSQL_PORT | MySQL 端口 | 3306 |
| MYSQL_USERNAME | MySQL 用户名 | root |
| MYSQL_PASSWORD | MySQL 密码 | 123456 |
| MYSQL_DATABASE | 数据库名 | ai_list |

---

## 快速启动

1. 安装依赖：
```bash
uv venv .venv
uv sync
```

2. 配置数据库连接（推荐使用环境变量）

3. 启动服务：
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 1235 --reload
```

服务将在 `http://localhost:1235` 启动


## AI 路由与评测（新增）

### 1. 按任务路由模型

系统支持通过 `db_ai_model_route` 按 `task_type + scene` 选择模型。请求可通过 Header 传入：

- `x-ai-scene: default`（默认）

已接入任务类型：

- `shop_category`
- `shop_title`
- `shop_desc`
- `shop_attribute`
- `translate`
- `batch_translate`
- `ocr`

### 2. 离线评测脚手架

评测脚本：`app/eval/run_eval.py`

示例：

```bash
uv run python app/eval/run_eval.py --base-url http://localhost:1235 --scene default
```

评测数据：

- `app/eval/datasets/translate_eval.jsonl`
- `app/eval/datasets/ocr_eval.jsonl`

### 企业评测命令（推荐）

```bash
uv run python app/eval/run_eval.py --base-url http://localhost:1235 --scene default --compare-scene promo --min-success-rate 0.95 --out app/eval/reports/report_ab.json
```

输出包含：
- success_rate / valid_output_rate
- avg/p50/p95/p99 延迟
- token 统计
- 错误分类（auth/validation/server/timeout/connection）
- 双场景差异（delta）
