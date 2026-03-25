项目架构与需求文档
一、项目背景与目标
解决的问题: 跨境电商卖家在多平台上架商品时面临的痛点：
- 商品信息需要多语言翻译
- 不同平台有不同格式要求
- 大量商品需要批量处理
- 图片信息需要自动化提取
- 目标: 构建AI辅助电商商品上架系统，自动化生成符合各平台要求的商品信息
---
二、技术架构
技术栈:
├── 框架: FastAPI (Python)
├── 数据库: MySQL + SQLAlchemy ORM
├── AI模型: Google Gemini / 阿里通义千问
├── 日志: JSON格式，按天轮转
└── 部署: Uvicorn (端口)
---
三、项目目录结构
copylisting_ai_base/
├── app/
│   ├── main.py                 # 应用入口，注册路由
│   ├── config.py               # 配置(数据库、日志)
│   ├── database.py             # SQLAlchemy连接配置
│   ├── routes/                 # API路由层
│   │   ├── common/             # 通用功能
│   │   │   ├── translate.py    # 翻译接口
│   │   │   ├── ocr.py          # OCR识别接口
│   │   │   └── tasks.py        # 任务管理接口
│   │   ├── tiktokshop/         # TikTok Shop平台
│   │   ├── fruugo/             # Fruugo平台
│   │   ├── shopee/             # Shopee平台
│   │   └── customize/          # 自定义平台
│   ├── services/               # 业务逻辑层
│   │   ├── llm.py              # LLM统一调用入口
│   │   ├── tasks.py            # 任务处理核心逻辑
│   │   ├── tiktokshop.py       # TikTok平台业务
│   │   ├── fruugo.py           # Fruugo平台业务
│   │   ├── text_generator.py   # 文本生成/翻译
│   │   └── multimodal_generator.py # 多模态处理
│   ├── models/                 # 数据模型层
│   │   ├── constants.py        # 枚举常量
│   │   ├── db_product_src_detail.py   # 原始商品表
│   │   ├── db_product_des_detail.py   # 目标商品表
│   │   ├── db_product_task_detail.py  # 任务表
│   │   ├── db_notice_detail.py        # 通知表
│   │   ├── db_sys_ai_prompt.py        # AI提示词配置
│   │   └── db_sys_conf.py             # 系统配置
│   ├── schemas/                # Pydantic数据验证
│   │   ├── common.py           # 通用响应模型
│   │   ├── listings.py         # 商品请求模型
│   │   ├── translate.py        # 翻译请求模型
│   │   └── ocr.py              # OCR请求模型
│   └── utils/                  # 工具类
│       ├── gemini_utils.py     # Gemini API调用
│       ├── qwen_utils.py       # 通义千问API调用
│       ├── image_utils.py      # 图片处理
│       ├── similar_utils.py    # 类目匹配
│       └── dependencies.py     # 依赖注入(鉴权)
---
四、核心业务流程
用户请求 → API路由 → 参数验证 → 存储原始数据 → AI处理(多步骤) → 存储结果 → 返回/通知
商品生成流程(TikTok为例):
1. 类目匹配: AI分析图片+标题 → 匹配平台类目
2. 标题生成: 基于图片+类目 → 生成目标语言标题
3. 描述生成: 基于图片+标题+类目 → 生成目标语言描述
4. 属性填充: 基于类目要求 → 生成/翻译商品属性
5. 标签生成: 可选，基于商品信息 → 生成标签
---
五、API接口设计
接口路径
/api/v1/tk/listing
/api/v1/fruugo/listing
/api/v1/c/translate
/api/v1/c/batchtranslate
/api/v1/c/ocr
/api/v1/c/tasks
---
六、数据库设计(核心表)
1. db_product_src_detail - 原始商品数据
存储用户提交的原始商品信息(图片URL、标题、属性等)
2. db_product_des_detail - 生成商品数据
存储AI生成的目标平台商品信息
3. db_product_task_detail - 任务记录
关联原始数据和生成数据，记录任务状态、耗时、Token消耗
状态: READY(02) → PROCESSING(03) → SUCCESS(00)/FAIL(01)
4. db_sys_ai_prompt - AI提示词配置
存储各场景的System/User Prompt，支持动态调整
5. db_notice_detail - 回调通知
任务完成后通知调用方，支持失败重试(指数退避)
---
### 七、关键设计模式
1. **提示词数据库化**: 所有AI提示词存在数据库，无需改代码即可调整
2. **异步任务机制**: 支持notice_url回调，适合大批量处理
3. **多LLM支持**: 通过配置切换Gemini/通义千问
4. **平台策略模式**: 每个平台独立service，便于扩展
5. **批量任务**: 线程池并发处理，可配置并发数
---
八、仿写建议
最小可行版本(MVP):
1. 先实现单平台(如Fruugo)的商品生成
2. 实现翻译和OCR通用功能
3. 添加任务管理和回调通知
4. 最后扩展多平台支持
需要准备的:
- MySQL数据库
- AI模型API密钥(Gemini或通义千问)
- 各平台类目数据(可从Excel导入)