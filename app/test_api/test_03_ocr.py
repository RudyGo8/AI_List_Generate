"""
测试接口：POST /api/r1/c/ocr
功能：图片OCR文字识别

业务流程：
    1. 验证API密钥 (accesskey + accesssecret)
    2. 获取请求参数 (image_url_list)
    3. 调用AI识别图片中的文字 (multimodal_generator.py)
    4. 返回识别出的文字列表和token使用量
"""

import requests
import json

base_url = "http://localhost:1235"
headers = {
    "Content-Type": "application/json",
    "accesskey": "test_key",
    "accesssecret": "test_secret"
}


def test_ocr():
    url = f"{base_url}/api/r1/c/ocr"
    data = {
        "image_url_list": ["https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true"]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    print("测试OCR识别接口...")
    test_ocr()
