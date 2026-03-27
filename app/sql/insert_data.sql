USE ai_base;

-- =====================================================
-- 1. AI模型配置
-- =====================================================
INSERT INTO db_sys_conf (`key`, `value`, enable, remark) VALUES
('LLM_TYPE', 'QWEN', 1, '当前使用的AI模型: QWEN或GEMINI'),
('AI_MODEL_QWEN', 'qwen-vl-max-latest', 1, '通义千问模型名称'),
('AI_BASE_URL_QWEN', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 1, '通义千问API地址'),
('AI_APIKEY_QWEN', 'YOUR_QWEN_API_KEY_HERE', 1, '通义千问API密钥，请替换为真实密钥');

-- =====================================================
-- 2. 客户端配置（API密钥）
-- =====================================================
INSERT INTO db_sys_client_conf (client_name, api_key, api_secret, enable, remark) VALUES
('test_client', 'test_key', 'test_secret', 1, '测试客户端'),
('batch', 'batch', 'test_secret', 1, '批量任务客户端（有执行任务权限）');

-- =====================================================
-- 3. 提示词模板配置
-- =====================================================
INSERT INTO db_sys_ai_prompt (prompt_key, prompt_value, enable, remark) VALUES

-- 翻译接口 (/api/v1/c/translate)
('SYSTEM_TEXT_TRANSLATE', 'You are a translation expert. Translate text to specified language. Return only the translated text.', 1, '翻译系统提示词'),
('USER_TEXT_TRANSLATE', 'Translate to %s: %s', 1, '翻译用户提示词'),

-- 批量翻译接口 (/api/v1/c/batchtranslate)
('SYSTEM_BATCH_TEXT_TRANSLATE', 'You are a translation expert. Translate each item in the list to the specified language. Return ONLY a JSON array of translated strings, no other text.', 1, '批量翻译系统提示词'),
('USER_BATCH_TEXT_TRANSLATE', 'Translate each item in the following list to %s: %s', 1, '批量翻译用户提示词'),

-- OCR识别接口 (/api/v1/c/ocr)
('SYSTEM_IMAGE_OCR', 'You are an expert in image text recognition. Recognize and extract all text from the image. Return only the text content, no other explanation.', 1, 'OCR系统提示词'),
('USER_IMAGE_OCR', 'Please recognize all text in this image.', 1, 'OCR用户提示词');

SELECT 'All data inserted successfully!' AS message;