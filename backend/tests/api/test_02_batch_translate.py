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
    response = requests.post(url, headers=headers, json=data, timeout=60)

    print(f"状态码: {response.status_code}")
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type.lower():
        body = response.json()
        print(f"响应: {json.dumps(body, ensure_ascii=False, indent=2)}")
    else:
        body = None
        print(f"非JSON响应: {response.text}")

    assert response.status_code == 200, f"batchtranslate failed: {response.status_code}, body={response.text}"
    assert body is not None and body.get("success") is True, f"unexpected response body: {body}"


if __name__ == "__main__":
    print("测试批量翻译接口...")
    test_batch_translate()
