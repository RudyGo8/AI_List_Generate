
import requests
import json

base_url = "http://localhost:1235"
headers = {
    "Content-Type": "application/json",
    "accesskey": "test_key",
    "accesssecret": "test_secret"
}


def test_batch_translate():
    url = f"{base_url}/api/r1/c/batchtranslate"
    data = {
        "des_lang_type": "English",
        "content_list": ["我爱AI", "我爱大模型", "我爱人工智能"]
    }
    response = requests.post(url, headers=headers, json=data)

    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    print("测试批量翻译接口...")
    test_batch_translate()