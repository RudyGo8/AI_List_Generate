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

### 1. 商品列表生成流程 (ailist)

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as FastAPI<br/>/api/r1/shop/ailist
    participant DB as MySQL数据库
    participant Embedding as BGE嵌入服务<br/>(Docker)
    participant LLM as Qwen LLM<br/>(通义千问)
    participant Notice as 回调通知

    Note over Client,Notice: 1. 接收商品信息
    Client->>API: POST /api/r1/shop/ailist<br/>(商品图片/URL, 站点, 语言等)
    
    Note over API,DB: 2. 存储原始商品数据
    API->>DB: 创建 ProductSrcDetail 记录
    API->>DB: 创建 DbProductTaskDetail 任务记录
    
    Note over API,Embedding: 3. AI 识别商品类目
    API->>Embedding: 请求类目嵌入向量
    Embedding-->>API: 返回嵌入向量
    
    Note over API,DB: 4. 从数据库获取候选类目
    API->>DB: 查询站点类目列表
    
    Note over API,Embedding: 5. 类目相似度匹配
    API->>Embedding: 批量获取类目嵌入向量
    API->>Embedding: 计算余弦相似度
    Embedding-->>API: 返回最相似的类目
    
    Note over API,LLM: 6. AI 生成商品标题
    API->>LLM: 发送商品图片+提示词
    LLM-->>API: 返回生成的标题
    
    Note over API,LLM: 7. AI 生成商品描述
    API->>LLM: 发送商品图片+标题+类目
    LLM-->>API: 返回生成的描述
    
    Note over API,LLM: 8. AI 生成商品属性
    API->>LLM: 发送商品图片+描述+类目
    LLM-->>API: 返回生成的属性
    
    Note over API,DB: 9. 存储生成结果
    API->>DB: 创建 ProductDesDetail 记录
    API->>DB: 更新任务状态为成功
    
    alt 有回调地址
        Note over API,Notice: 10. 发送回调通知
        API->>Notice: POST notice_url<br/>(生成的商品信息)
        Notice-->>API: 回调响应
    end
    
    API-->>Client: 返回生成的商品信息
```

### 2. 文本翻译流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as FastAPI<br/>/api/r1/c/translate
    participant DB as MySQL数据库
    participant LLM as Qwen LLM<br/>(通义千问)

    Client->>API: POST /api/r1/c/translate<br/>(原文, 目标语言)
    
    API->>DB: 获取 LLM 配置
    API->>LLM: 发送翻译请求
    
    LLM-->>API: 返回翻译结果
    
    API-->>Client: 返回翻译内容
```

### 3. OCR 图片识别流程

```mermaid
sequenceDiagram
    participant Client as 客户端
    participant API as FastAPI<br/>/api/r1/c/ocr
    participant LLM as Qwen VL<br/>(多模态模型)

    Client->>API: POST /api/r1/c/ocr<br/>(图片URL列表)
    
    API->>LLM: 发送图片+OCR提示词
    
    LLM-->>API: 返回识别的文字
    
    API-->>Client: 返回文字列表
```

### 4. BGE 类目匹配详细流程

```mermaid
sequenceDiagram
    participant Service as 商品生成服务
    participant DB as MySQL数据库
    participant BGE as BGE嵌入服务<br/>(Docker)
    
    Note over Service,DB: 获取查询文本的嵌入向量
    Service->>BGE: get_embedding(query_text)
    BGE-->>Service: query_embedding [1536维]
    
    Note over Service,DB: 获取候选类目列表
    Service->>DB: SELECT category_path, category_id<br/>FROM category<br/>WHERE site=? AND enable=1
    DB-->>Service: category_list
    
    Note over Service,BGE: 批量获取类目嵌入
    Service->>BGE: batch_get_embeddings(category_paths)
    BGE-->>Service: category_embeddings []
    
    Note over Service,Service: 计算余弦相似度
    Service->>Service: for each category:<br/>similarity = cosine(query_emb, cat_emb)
    Service->>Service: sort by similarity DESC
    
    Service-->>Service: 返回 top_k 相似类目
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


