# AI 商品列表生成服务

## 项目介绍

本项目是一个基于 FastAPI 的 AI 辅助电商商品上架接口服务，旨在帮助卖家在多平台上架商品时，自动生成符合各平台要求的商品信息。

### 核心功能

1. **AI 商品列表生成** (`/api/r1/shop/ailist`)
   - 通过商品图片识别商品类目（基于 BGE-M3 多语言嵌入向量相似度匹配）
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
  - **BGE-M3** (BAAI General Embedding M3) - 用于商品类目多语言嵌入匹配
  - Qwen (通义千问) - 用于商品标题、描述、属性生成
  - Gemini - 备用 LLM
- **API 调用**: OpenAI SDK (兼容 OpenAI 格式)


**---**

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

    API->>DB: 3. 创建生成任务(status=processing)
    activate DB
    DB-->>API: 3.1 返回 task_id
    deactivate DB

    API-->>Client: 4. 返回任务受理结果(task_id)

    API->>LLM: 5. 识别候选类目(图片+标题)
    activate LLM
    LLM-->>API: 5.1 返回候选类目
    deactivate LLM

    API->>Embedding: 6. 生成候选类目嵌入向量
    activate Embedding
    Embedding-->>API: 6.1 返回候选类目向量
    deactivate Embedding

    API->>DB: 7. 查询站点类目列表
    activate DB
    DB-->>API: 7.1 返回 category_list
    deactivate DB

    API->>Embedding: 8. 批量生成站点类目嵌入向量
    activate Embedding
    Embedding-->>API: 8.1 返回类目向量列表
    deactivate Embedding

    API->>API: 9. 计算余弦相似度并筛选 Top-K

    API->>LLM: 10. 选择最佳类目(图片+Top-K类目)
    activate LLM
    LLM-->>API: 10.1 返回最终类目
    deactivate LLM

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

本项目使用 **BGE-M3 (BAAI General Embedding M3)** 多语言嵌入模型进行商品类目匹配，通过嵌入向量相似度计算，将 AI 识别的类目路径与数据库中的目标站点类目进行智能匹配。

> **BGE-M3** 特点：支持超过100种语言的稠密嵌入、稀疏嵌入和混合检索，是当前性能最优的开源嵌入模型之一。

### 部署方式

BGE 模型通过 **Docker** 部署为 API 服务，使用 [FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) 项目提供的服务化脚本。

### 1. 启动 BGE-M3 服务

```bash
docker run --gpus all -p 8000:80 -v "%cd%\data:/data" ghcr.io/huggingface/text-embeddings-inference:cuda-1.8.1 --model-id BAAI/bge-m3
```

### 2. 配置存储在数据库

所有配置存储在 MySQL 数据库的 `sys_conf` 表中，系统启动时自动读取：

| key | 说明 | 示例值 |
|-----|------|--------|
| EMBEDDING_API_KEY | API 认证密钥 | dummy |
| EMBEDDING_BASE_URL | BGE 服务 API 地址 | http://bge-container-ip:8000/v1 |
| EMBEDDING_MODEL | BGE 模型名称 | BAAI/bge-m3 |

配置示例（插入数据库）：

```sql
INSERT INTO sys_conf (`key`, `value`, `enable`) VALUES 
('EMBEDDING_API_KEY', 'dummy', 1),
('EMBEDDING_BASE_URL', 'http://192.168.1.100:8080/v1', 1),
('EMBEDDING_MODEL', 'BAAI/bge-m3', 1);
```

> 应用会在调用嵌入服务时从数据库动态读取这些配置，修改配置后无需重启服务。


```

配置数据库（sys_conf 表）：
| key | value |
|-----|-------|
| EMBEDDING_BASE_URL | http://localhost:11434/v1 |
| EMBEDDING_API_KEY | ollama |
| EMBEDDING_MODEL | BAAI/bge-m3 |

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_HOST | MySQL 主机 | localhost |
| MYSQL_PORT | MySQL 端口 | 3306 |
| MYSQL_USERNAME | MySQL 用户名 | xx |
| MYSQL_PASSWORD | MySQL 密码 | xx |
| MYSQL_DATABASE | 数据库名 | xx |

---

## 快速启动

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置数据库连接（修改 `app/config.py`）

3. 启动服务：
```bash
python -m app.main
```

服务将在 `http://localhost:1235` 启动

