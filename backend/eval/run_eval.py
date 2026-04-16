import argparse
import json
import statistics
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

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


def classify_error(status_code: int, err: str) -> str:
    if err:
        if 'timed out' in err.lower():
            return 'timeout'
        if 'connection' in err.lower():
            return 'connection_error'
        return 'request_error'
    if status_code in (401, 403):
        return 'auth_error'
    if status_code == 422:
        return 'validation_error'
    if status_code >= 500:
        return 'server_error'
    if status_code >= 400:
        return 'client_error'
    return 'unknown'


def call_api_with_retry(url: str, headers: dict, payload: dict, timeout_sec: int = 90, retries: int = 1):
    last_error = None
    for i in range(retries + 1):
        try:
            start = time.time()
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_sec)
            latency_ms = (time.time() - start) * 1000
            body = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {'raw': resp.text}
            return resp.status_code, body, latency_ms, None, i
        except requests.RequestException as e:
            last_error = str(e)
    return 0, {}, 0.0, last_error, retries


def is_valid_output(task_name: str, body: dict) -> bool:
    if not isinstance(body, dict) or not body.get('success'):
        return False

    data = body.get('data') or {}
    if task_name == 'translate':
        return bool((data.get('translated_content') or '').strip())
    if task_name == 'ocr':
        return data.get('word_list') is not None
    if task_name == 'shop':
        return bool(data.get('task_id')) or bool(data.get('status'))
    return False


def extract_tokens(body: dict) -> int:
    usage = body.get('usage') if isinstance(body, dict) else None
    if isinstance(usage, dict):
        return int(usage.get('total_tokens') or 0)
    return 0


def run_task_eval(task_name: str, endpoint: str, dataset_rows: List[dict], base_url: str, headers: dict,
                  scene: str, timeout_sec: int, retries: int):
    records = []
    for row in dataset_rows:
        req_headers = dict(headers)
        req_headers['x-ai-scene'] = scene

        status_code, body, latency_ms, err, retry_count = call_api_with_retry(
            url=f"{base_url}{endpoint}",
            headers=req_headers,
            payload=row,
            timeout_sec=timeout_sec,
            retries=retries,
        )

        ok = status_code == 200 and isinstance(body, dict) and body.get('success') is True
        valid = is_valid_output(task_name, body)
        token_total = extract_tokens(body if isinstance(body, dict) else {})
        err_type = classify_error(status_code, err) if not ok else None

        records.append({
            'ok': ok,
            'valid_output': valid,
            'latency_ms': round(latency_ms, 2),
            'status_code': status_code,
            'token_total': token_total,
            'retry_count': retry_count,
            'error_type': err_type,
            'error': err,
            'response': body,
        })

    return records


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    idx = min(len(arr) - 1, int((len(arr) - 1) * p))
    return round(arr[idx], 2)


def summarize(records: List[dict], min_success_rate: float, max_p95_ms: float):
    if not records:
        return {
            'count': 0,
            'success_rate': 0.0,
            'valid_output_rate': 0.0,
            'avg_ms': 0.0,
            'p50_ms': 0.0,
            'p95_ms': 0.0,
            'p99_ms': 0.0,
            'token_total': 0,
            'avg_tokens': 0.0,
            'avg_retries': 0.0,
            'error_breakdown': {},
            'slo_pass': False,
        }

    latencies = [r['latency_ms'] for r in records]
    success_rate = sum(1 for r in records if r['ok']) / len(records)
    valid_rate = sum(1 for r in records if r['valid_output']) / len(records)
    token_total = sum(r['token_total'] for r in records)
    avg_retries = statistics.mean([r['retry_count'] for r in records])
    error_counter = Counter(r['error_type'] for r in records if r['error_type'])

    p95 = percentile(latencies, 0.95)
    slo_pass = success_rate >= min_success_rate and (p95 <= max_p95_ms if max_p95_ms > 0 else True)

    return {
        'count': len(records),
        'success_rate': round(success_rate, 4),
        'valid_output_rate': round(valid_rate, 4),
        'avg_ms': round(statistics.mean(latencies), 2),
        'p50_ms': percentile(latencies, 0.50),
        'p95_ms': p95,
        'p99_ms': percentile(latencies, 0.99),
        'token_total': int(token_total),
        'avg_tokens': round(token_total / len(records), 2),
        'avg_retries': round(avg_retries, 2),
        'error_breakdown': dict(error_counter),
        'slo_pass': slo_pass,
    }


def run_scene(scene: str, args, headers: dict):
    datasets = {
        'translate': (args.translate_dataset, '/api/r1/c/translate', args.timeout_sec),
        'ocr': (args.ocr_dataset, '/api/r1/c/ocr', args.timeout_sec),
        'shop': (args.shop_dataset, '/api/r1/shop/ailist', args.timeout_sec_shop),
    }

    raw = {}
    summary = {}
    for task_name, (dataset_path, endpoint, timeout_sec) in datasets.items():
        path = Path(dataset_path)
        rows = load_jsonl(path) if path.exists() else []
        records = run_task_eval(
            task_name=task_name,
            endpoint=endpoint,
            dataset_rows=rows,
            base_url=args.base_url,
            headers=headers,
            scene=scene,
            timeout_sec=timeout_sec,
            retries=args.retries,
        )
        raw[task_name] = records
        summary[task_name] = summarize(
            records,
            min_success_rate=args.min_success_rate,
            max_p95_ms=args.max_p95_ms,
        )

    return {
        'scene': scene,
        'summary': summary,
        'raw': raw,
    }


def build_comparison(primary: dict, secondary: dict):
    compare = {}
    for task in primary['summary'].keys():
        a = primary['summary'][task]
        b = secondary['summary'].get(task, {})
        compare[task] = {
            'success_rate_delta': round((b.get('success_rate', 0) - a.get('success_rate', 0)), 4),
            'valid_output_rate_delta': round((b.get('valid_output_rate', 0) - a.get('valid_output_rate', 0)), 4),
            'p95_ms_delta': round((b.get('p95_ms', 0) - a.get('p95_ms', 0)), 2),
            'avg_tokens_delta': round((b.get('avg_tokens', 0) - a.get('avg_tokens', 0)), 2),
        }
    return compare


def main():
    parser = argparse.ArgumentParser(description='评估')
    parser.add_argument('--base-url', default='http://localhost:1235')
    parser.add_argument('--accesskey', default='test_key')
    parser.add_argument('--accesssecret', default='test_secret')

    parser.add_argument('--scene', default='default', help='primary scene')
    parser.add_argument('--compare-scene', default='', help='optional secondary scene for A/B compare')

    parser.add_argument('--translate-dataset', default='eval/datasets/translate_eval.jsonl')
    parser.add_argument('--ocr-dataset', default='eval/datasets/ocr_eval.jsonl')
    parser.add_argument('--shop-dataset', default='eval/datasets/shop_eval.jsonl')

    parser.add_argument('--timeout-sec', type=int, default=90)
    parser.add_argument('--timeout-sec-shop', type=int, default=180)
    parser.add_argument('--retries', type=int, default=1)

    parser.add_argument('--min-success-rate', type=float, default=0.95)
    parser.add_argument('--max-p95-ms', type=float, default=0)

    parser.add_argument('--out', default='eval/reports/latest_report.json')
    args = parser.parse_args()

    headers = {
        'Content-Type': 'application/json',
        'accesskey': args.accesskey,
        'accesssecret': args.accesssecret,
    }

    primary = run_scene(args.scene, args, headers)
    result = {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'base_url': args.base_url,
        'slo': {
            'min_success_rate': args.min_success_rate,
            'max_p95_ms': args.max_p95_ms,
        },
        'primary': primary,
    }

    if args.compare_scene:
        secondary = run_scene(args.compare_scene, args, headers)
        result['secondary'] = secondary
        result['comparison'] = build_comparison(primary, secondary)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
