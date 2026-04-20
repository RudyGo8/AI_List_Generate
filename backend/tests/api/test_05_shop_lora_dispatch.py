"""
Shop LoRA dispatch smoke test (scene -> shop_desc model routing).

Usage:
    python backend/tests/api/test_05_shop_lora_dispatch.py

Optional envs:
    TEST_BASE_URL=http://127.0.0.1:8000
    TEST_ACCESS_KEY=test_key
    TEST_ACCESS_SECRET=test_secret
    TEST_SHOP_IMAGE_URL=https://.../demo.jpg
    TEST_TASK_TIMEOUT_SEC=240
    TEST_POLL_INTERVAL_SEC=2
    TEST_SCENE_MODEL_MAP='{"shopee":"shopee","tiktok":"tiktok","amazon":"amazon"}'
"""

from __future__ import annotations

import json
import os
import time
from typing import Dict

import requests


DEFAULT_SCENE_MODEL_MAP: Dict[str, str] = {
    "shopee": "shopee",
    "tiktok": "tiktok",
    "amazon": "amazon",
}

DEFAULT_IMAGE_URL = (
    "https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true"
)


def _get_scene_model_map() -> Dict[str, str]:
    raw = os.getenv("TEST_SCENE_MODEL_MAP", "").strip()
    if not raw:
        return DEFAULT_SCENE_MODEL_MAP
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and data:
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    print("[WARN] TEST_SCENE_MODEL_MAP invalid, fallback to defaults.")
    return DEFAULT_SCENE_MODEL_MAP


def _create_task(base_url: str, access_key: str, access_secret: str, scene: str, image_url: str) -> int:
    url = f"{base_url}/api/r1/shop/ailist"
    headers = {
        "Content-Type": "application/json",
        "accesskey": access_key,
        "accesssecret": access_secret,
        "x-ai-scene": scene,
    }
    payload = {
        "site": scene,
        "spu_image_url": image_url,
        "product_title": "垃圾桶 两侧 - 功能清晰款",
        "category_name": "",
        "attributes": [],
        "des_lang_type": "中文",
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()
    if not body.get("success"):
        raise RuntimeError(f"create task failed: {body}")

    task_id = body.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"missing task_id in response: {body}")
    return int(task_id)


def _poll_task(
    base_url: str,
    access_key: str,
    access_secret: str,
    task_id: int,
    timeout_sec: int,
    poll_interval_sec: int,
) -> dict:
    url = f"{base_url}/api/r1/shop/ailist/task/{task_id}"
    headers = {
        "accesskey": access_key,
        "accesssecret": access_secret,
    }

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        body = response.json()
        status = str(body.get("data", {}).get("status", ""))
        if status in ("00", "01"):
            return body
        time.sleep(poll_interval_sec)

    raise TimeoutError(f"poll task timeout after {timeout_sec}s, task_id={task_id}")


def run_shop_lora_dispatch_smoke() -> int:
    base_url = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    access_key = os.getenv("TEST_ACCESS_KEY", "test_key")
    access_secret = os.getenv("TEST_ACCESS_SECRET", "test_secret")
    image_url = os.getenv("TEST_SHOP_IMAGE_URL", DEFAULT_IMAGE_URL)
    timeout_sec = int(os.getenv("TEST_TASK_TIMEOUT_SEC", "240"))
    poll_interval_sec = int(os.getenv("TEST_POLL_INTERVAL_SEC", "2"))
    scene_model_map = _get_scene_model_map()

    print(f"[INFO] base_url={base_url}")
    print(f"[INFO] scenes={scene_model_map}")

    failed = []
    for scene, expected_model in scene_model_map.items():
        print(f"\n[CASE] scene={scene}, expected_model={expected_model}")
        try:
            task_id = _create_task(
                base_url=base_url,
                access_key=access_key,
                access_secret=access_secret,
                scene=scene,
                image_url=image_url,
            )
            print(f"[INFO] created task_id={task_id}")
            task_result = _poll_task(
                base_url=base_url,
                access_key=access_key,
                access_secret=access_secret,
                task_id=task_id,
                timeout_sec=timeout_sec,
                poll_interval_sec=poll_interval_sec,
            )

            data = task_result.get("data", {})
            status = str(data.get("status", ""))
            actual_model = str(data.get("model_name", ""))
            ok = status == "00" and actual_model == expected_model

            print(
                f"[RESULT] status={status}, model_name={actual_model}, "
                f"expected={expected_model}, pass={ok}"
            )
            if not ok:
                failed.append(
                    {
                        "scene": scene,
                        "expected_model": expected_model,
                        "actual_model": actual_model,
                        "status": status,
                        "task_id": task_id,
                    }
                )
        except Exception as error:
            print(f"[ERROR] scene={scene} failed: {error}")
            failed.append(
                {
                    "scene": scene,
                    "expected_model": expected_model,
                    "actual_model": "",
                    "status": "EXCEPTION",
                    "task_id": None,
                }
            )

    print("\n" + "=" * 70)
    if failed:
        print("[FAIL] shop LoRA dispatch smoke test failed")
        print(json.dumps(failed, ensure_ascii=False, indent=2))
        return 1

    print("[PASS] shop LoRA dispatch smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_shop_lora_dispatch_smoke())

