# AI Listing Generate API 接口文档（企业级）

## 1. 通用约定
### 1.1 Base URL
`http://{host}:1235`

### 1.2 请求头
1. `Content-Type: application/json`
2. `accesskey: <client_api_key>`（必填）
3. `accesssecret: <client_api_secret>`（必填）
4. `x-ai-scene: <scene>`（可选，默认 `default`）

### 1.3 通用响应结构
```json
{
  "success": true,
  "msg": "success",
  "data": {},
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### 1.4 状态码
1. `200`：请求已处理（业务成功/失败由 `success` 判断）
2. `401`：鉴权失败
3. `422`：请求体校验失败
4. `5xx`：服务异常

## 2. 文本翻译
### 2.1 POST `/api/r1/c/translate`
请求体：
```json
{
  "des_lang_type": "English",
  "content": "你好，AI应用工程师"
}
```

成功响应示例：
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "translated_content": "Hello, AI application engineer"
  },
  "usage": {
    "prompt_tokens": 44,
    "completion_tokens": 9,
    "total_tokens": 53
  }
}
```

失败响应示例：
```json
{
  "success": false,
  "msg": "Translation failed",
  "data": {},
  "usage": null
}
```

## 3. 批量翻译
### 3.1 POST `/api/r1/c/batchtranslate`
请求体：
```json
{
  "des_lang_type": "English",
  "content_list": ["我爱AI", "我爱大模型"]
}
```

成功响应示例：
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "translated_content_list": [
      {"content": "我爱AI", "translated": "I love AI"},
      {"content": "我爱大模型", "translated": "I love large models"}
    ]
  },
  "usage": {
    "total_tokens": 100
  }
}
```

## 4. 图片 OCR
### 4.1 POST `/api/r1/c/ocr`
请求体：
```json
{
  "image_url_list": ["https://example.com/image.png"]
}
```

成功响应示例：
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "word_list": "识别出的文本内容"
  },
  "usage": {
    "total_tokens": 1273
  }
}
```

## 5. 商品异步生成
### 5.1 POST `/api/r1/shop/ailist`
说明：
1. `site` 必填。
2. `product_url` 与 `spu_image_url` 至少传一个。
3. 创建成功返回任务信息，由客户端轮询结果。

请求体（手动输入模式）：
```json
{
  "site": "shop",
  "platform_id": -1,
  "des_lang_type": "English",
  "spu_image_url": "https://example.com/spu.png",
  "sku_image_url_list": ["https://example.com/sku1.png"],
  "product_title": "Apple iPhone smartphone 128GB unlocked",
  "category_name": "Electronics > Mobile Phones",
  "category_id": 10001,
  "attributes": [{"attributeName": "Color", "value": "Black"}],
  "custom_data": "{\"bizOrderId\":\"A001\"}",
  "tag_type": "0001",
  "notice_url": "https://your.callback/notify"
}
```

成功响应示例：
```json
{
  "success": true,
  "msg": "task created success",
  "data": {
    "task_id": 12345,
    "status": "02",
    "polling_url": "/api/r1/shop/ailist/task/12345"
  },
  "usage": null
}
```

失败响应示例：
```json
{
  "success": false,
  "msg": "task create fail",
  "data": null,
  "usage": null
}
```

### 5.2 GET `/api/r1/shop/ailist/task/{task_id}`
状态枚举：
1. `02`：READY
2. `03`：PROCESSING
3. `00`：SUCCESS
4. `01`：FAIL

处理中响应：
```json
{
  "success": true,
  "msg": "task processing",
  "data": {
    "task_id": 12345,
    "status": "03",
    "model_name": "qwen-vl-max-latest"
  },
  "usage": null
}
```

成功响应：
```json
{
  "success": true,
  "msg": "success",
  "data": {
    "task_id": 12345,
    "status": "00",
    "model_name": "qwen-vl-max-latest",
    "product_title": "Generated Title",
    "product_desc": "Generated Description",
    "category_name": "Electronics > Phones",
    "category_id": "123456",
    "attr_value_list": "{\"Color\":\"Black\"}"
  },
  "usage": {
    "prompt_tokens": 1000,
    "completion_tokens": 500,
    "total_tokens": 1500
  }
}
```

失败响应：
```json
{
  "success": false,
  "msg": "task failed",
  "data": {
    "task_id": 12345,
    "status": "01",
    "model_name": "qwen-vl-max-latest"
  },
  "usage": null
}
```

## 6. 回调通知契约（notice_url）
1. 触发时机：商品生成成功落库后。
2. 请求方法：`POST`
3. 请求体：生成结果字段 + `task_id` + `custom_data`。
4. 失败重试：指数退避，达到阈值后标记通知失败。

## 7. 企业化增强建议
1. 增加业务错误码（如 `BIZ_XXXX`）与错误字典。
2. 增加请求幂等键（`X-Idempotency-Key`）。
3. 回调增加签名字段与重放保护。
4. 输出 OpenAPI 示例与字段长度/枚举约束。

