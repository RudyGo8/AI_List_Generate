"""
测试接口：POST /api/v1/c/translate
功能：文本翻译

业务流程：
    1. 验证API密钥 (accesskey + accesssecret)
    2. 获取请求参数 (des_lang_type, content)
    3. 从数据库获取提示词模板 (sys_ai_prompt表)
    4. 填充模板参数
    5. 调用AI翻译 (根据sys_conf表选择qwen或gemini)
    6. 返回翻译结果和token使用量
"""

import requests
import json

base_url = "http://localhost:1235"
headers = {
    "Content-Type": "application/json",
    "accesskey": "test_key",
    "accesssecret": "test_secret"
}


def test_translate() -> None:
    url = f"{base_url}/api/r1/c/translate"
    data = {
        "des_lang_type": "English",
        "content": "你好，AI应用工程师"
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    print("测试翻译接口...")
    test_translate()