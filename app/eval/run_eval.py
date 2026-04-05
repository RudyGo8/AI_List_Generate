import argparse
import json
import statistics
import time
from pathlib import Path

import requests


def load_jsonl(path: Path):
    rows = []
    with path.open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def evaluate_translate(base_url: str, headers: dict, sample: dict, scene: str):
    payload = {
        'des_lang_type': sample.get('des_lang_type', 'English'),
        'content': sample.get('content', ''),
    }
    req_headers = dict(headers)
    req_headers['x-ai-scene'] = scene

    start = time.time()
    resp = requests.post(f"{base_url}/api/r1/c/translate", headers=req_headers, json=payload, timeout=90)
    elapsed = (time.time() - start) * 1000

    ok = resp.status_code == 200 and resp.json().get('success')
    return {
        'ok': ok,
        'latency_ms': elapsed,
        'status_code': resp.status_code,
        'response': resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text,
    }


def evaluate_ocr(base_url: str, headers: dict, sample: dict, scene: str):
    payload = {
        'image_url_list': sample.get('image_url_list', []),
    }
    req_headers = dict(headers)
    req_headers['x-ai-scene'] = scene

    start = time.time()
    resp = requests.post(f"{base_url}/api/r1/c/ocr", headers=req_headers, json=payload, timeout=120)
    elapsed = (time.time() - start) * 1000

    ok = resp.status_code == 200 and resp.json().get('success')
    return {
        'ok': ok,
        'latency_ms': elapsed,
        'status_code': resp.status_code,
        'response': resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text,
    }


def main():
    parser = argparse.ArgumentParser(description='Offline AI API evaluator')
    parser.add_argument('--base-url', default='http://localhost:1235')
    parser.add_argument('--accesskey', default='test_key')
    parser.add_argument('--accesssecret', default='test_secret')
    parser.add_argument('--scene', default='default')
    parser.add_argument('--translate-dataset', default='app/eval/datasets/translate_eval.jsonl')
    parser.add_argument('--ocr-dataset', default='app/eval/datasets/ocr_eval.jsonl')
    args = parser.parse_args()

    headers = {
        'Content-Type': 'application/json',
        'accesskey': args.accesskey,
        'accesssecret': args.accesssecret,
    }

    report = {
        'translate': [],
        'ocr': [],
    }

    translate_path = Path(args.translate_dataset)
    if translate_path.exists():
        for row in load_jsonl(translate_path):
            result = evaluate_translate(args.base_url, headers, row, args.scene)
            report['translate'].append(result)

    ocr_path = Path(args.ocr_dataset)
    if ocr_path.exists():
        for row in load_jsonl(ocr_path):
            result = evaluate_ocr(args.base_url, headers, row, args.scene)
            report['ocr'].append(result)

    def summary(items):
        if not items:
            return {'count': 0, 'success_rate': 0.0, 'p95_ms': 0.0}
        latencies = sorted([i['latency_ms'] for i in items])
        p95_index = min(len(latencies) - 1, int(len(latencies) * 0.95))
        success_rate = sum(1 for i in items if i['ok']) / len(items)
        return {
            'count': len(items),
            'success_rate': round(success_rate, 4),
            'p95_ms': round(latencies[p95_index], 2),
            'avg_ms': round(statistics.mean(latencies), 2),
        }

    result = {
        'scene': args.scene,
        'translate_summary': summary(report['translate']),
        'ocr_summary': summary(report['ocr']),
        'raw': report,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
