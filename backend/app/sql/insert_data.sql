USE ai_list;

-- =====================================================
-- 1. AI模型配置
-- =====================================================
INSERT IGNORE INTO db_sys_conf (`key`, `value`, enable, remark) VALUES
('LLM_TYPE', 'QWEN', 1, '当前使用的AI模型: QWEN或GEMINI'),
('AI_MODEL_QWEN', 'qwen-vl-max-latest', 1, '通义千问模型名称'),
('AI_BASE_URL_QWEN', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 1, '通义千问API地址'),
('AI_APIKEY_QWEN', 'YOUR_QWEN_API_KEY_HERE', 1, '通义千问API密钥，请替换为真实密钥');

-- =====================================================
-- 2. 客户端配置（API密钥）
-- =====================================================
INSERT IGNORE INTO db_sys_client_conf (client_name, api_key, api_secret, enable, remark) VALUES
('test_client', 'test_key', 'test_secret', 1, '测试客户端'),
('batch', 'batch', 'test_secret', 1, '批量任务客户端（有执行任务权限）');

-- =====================================================
-- 3. 提示词模板配置
-- =====================================================
INSERT IGNORE INTO db_sys_ai_prompt (prompt_key, prompt_value, enable, remark) VALUES

-- 翻译接口 (/api/r1/c/translate)
('SYSTEM_TEXT_TRANSLATE', '你是一个专业的翻译专家，精通多国语言翻译。请将用户提供的文本翻译成指定语言，保持原文的语气和风格。', 1, '文本翻译系统提示词'),
('USER_TEXT_TRANSLATE', '请将以下文本翻译成%s语言，只返回翻译结果，不要添加任何解释：\n%s', 1, '文本翻译用户提示词'),

-- 批量翻译接口 (/api/r1/c/batchtranslate)
('SYSTEM_BATCH_TEXT_TRANSLATE', '你是一个专业的翻译专家，精通多国语言翻译。请将用户提供的文本列表翻译成指定语言，返回JSON格式的翻译结果列表。', 1, '批量翻译系统提示词'),
('USER_BATCH_TEXT_TRANSLATE', '请将以下文本列表翻译成%s语言，返回JSON数组格式，保持原文的语气和风格：\n%s', 1, '批量翻译用户提示词'),

-- OCR识别接口 (/api/r1/c/ocr)
('SYSTEM_IMAGE_OCR', '你是一个专业的OCR文字识别专家。请识别图片中的所有文字内容，按顺序输出文字，保持原有格式。', 1, 'OCR系统提示词'),
('USER_IMAGE_OCR', 'Please recognize all text in this image.', 1, 'OCR用户提示词'),

-- 商品生成类目
('SYSTEM_COMMON_CATEGORY_STEP_ONE', '你是一个电商类目分析专家。根据商品图片和标题，分析商品类型并给出合适的类目路径。', 1, '类目分析第一步系统提示词'),
('USER_COMMON_CATEGORY_STEP_ONE', '商品标题：%s\n原始类目：%s\n\n请根据图片和标题分析商品类型，给出最合适的类目路径。', 1, '类目分析第一步用户提示词'),
('SYSTEM_COMMON_CATEGORY_STEP_TWO', '你是一个电商类目分析专家。从候选类目列表中选择最合适的类目。', 1, '类目分析第二步系统提示词'),
('USER_COMMON_CATEGORY_STEP_TWO', '商品标题：%s\n候选类目列表：%s\n\n请从以上候选类目中选择最合适的类目。', 1, '类目分析第二步用户提示词'),

-- 商品标题/描述
('SYSTEM_TIKTOKSHOP_PRODUCT_TITLE', '你是一个TikTokShop商品标题优化专家。根据商品图片和信息，生成符合TikTokShop平台规范的优质商品标题。标题应该简洁、有吸引力，包含关键词。', 1, 'TikTokShop标题生成系统提示词'),
('USER_TIKTOKSHOP_PRODUCT_TITLE', '商品原标题：%s\n商品类目：%s\n目标语言：%s\n\n请根据图片和商品信息生成TikTokShop商品标题。', 1, 'TikTokShop标题生成用户提示词'),
('SYSTEM_TIKTOKSHOP_PRODUCT_DESC', '你是一个TikTokShop商品描述撰写专家。根据商品图片和信息，生成详细、吸引人的商品描述，突出产品特点和卖点。', 1, 'TikTokShop描述生成系统提示词'),
('USER_TIKTOKSHOP_PRODUCT_DESC', '商品标题：%s\n商品类目：%s\n目标语言：%s\n\n请根据图片和商品信息生成TikTokShop商品描述。', 1, 'TikTokShop描述生成用户提示词');

-- =====================================================
-- 4. AI模型路由配置（按任务类型）
-- =====================================================
INSERT IGNORE INTO db_ai_model_route (task_type, scene, model_name, llm_type, enable, remark) VALUES
('shop_category', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '商品类目识别模型'),
('shop_title', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '商品标题生成模型'),
('shop_desc', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '商品描述生成模型'),
('shop_attribute', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '商品属性生成模型'),
('translate', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '翻译模型'),
('batch_translate', 'default', 'qwen-vl-max-latest', 'QWEN', 1, '批量翻译模型'),
('ocr', 'default', 'qwen-vl-max-latest', 'QWEN', 1, 'OCR模型');

SELECT '基础配置初始化完成，请继续将 AI_APIKEY_QWEN 更新为真实密钥。' AS message;
