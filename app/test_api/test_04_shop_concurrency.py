import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


SUCCESS_STATUS = "00"
FAIL_STATUS = "01"


@dataclass
class SubmitResult:
    ok: bool
    status_code: int
    latency_ms: float
    task_id: Optional[int]
    error: Optional[str] = None


@dataclass
class TaskResult:
    task_id: int
    completed: bool
    success: bool
    status: Optional[str]
    latency_ms: float
    error: Optional[str] = None


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = min(len(sorted_values) - 1, int((len(sorted_values) - 1) * p))
    return round(sorted_values[idx], 2)


def classify_submit_error(status_code: int, error: Optional[str]) -> str:
    if error:
        low = error.lower()
        if "timed out" in low:
            return "submit_timeout"
        if "connection" in low:
            return "submit_connection_error"
        return "submit_request_error"
    if status_code == 401:
        return "submit_auth_error"
    if status_code == 422:
        return "submit_validation_error"
    if status_code >= 500:
        return "submit_server_error"
    if status_code >= 400:
        return "submit_client_error"
    return "submit_unknown_error"


def classify_task_error(task_result: TaskResult) -> str:
    if task_result.error:
        low = task_result.error.lower()
        if "timed out" in low:
            return "poll_timeout"
        if "connection" in low:
            return "poll_connection_error"
        return "poll_request_error"
    if not task_result.completed:
        return "task_not_completed"
    if task_result.status == FAIL_STATUS:
        return "task_failed_status"
    return "task_unknown_error"


def post_json(url: str, headers: Dict[str, str], payload: Dict, timeout_sec: int) -> Tuple[int, Dict, Optional[str], float]:
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_sec)
        latency_ms = (time.time() - start) * 1000
        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text}
        return resp.status_code, body, None, latency_ms
    except requests.RequestException as exc:
        latency_ms = (time.time() - start) * 1000
        return 0, {}, str(exc), latency_ms


def get_json(url: str, headers: Dict[str, str], timeout_sec: int) -> Tuple[int, Dict, Optional[str]]:
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_sec)
        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text}
        return resp.status_code, body, None
    except requests.RequestException as exc:
        return 0, {}, str(exc)


def submit_one(base_url: str, headers: Dict[str, str], payload: Dict, timeout_sec: int) -> SubmitResult:
    status_code, body, error, latency_ms = post_json(
        url=f"{base_url}/api/r1/shop/ailist",
        headers=headers,
        payload=payload,
        timeout_sec=timeout_sec,
    )

    if error:
        return SubmitResult(ok=False, status_code=status_code, latency_ms=latency_ms, task_id=None, error=error)

    success = status_code == 200 and isinstance(body, dict) and body.get("success") is True
    task_id = body.get("data", {}).get("task_id") if isinstance(body, dict) else None
    if success and task_id:
        return SubmitResult(ok=True, status_code=status_code, latency_ms=latency_ms, task_id=int(task_id))

    msg = body.get("msg") if isinstance(body, dict) else None
    return SubmitResult(ok=False, status_code=status_code, latency_ms=latency_ms, task_id=None, error=str(msg) if msg else None)


def poll_task(
    base_url: str,
    headers: Dict[str, str],
    task_id: int,
    poll_timeout_sec: int,
    poll_interval_sec: float,
    request_timeout_sec: int,
) -> TaskResult:
    start = time.time()
    deadline = start + poll_timeout_sec

    while time.time() < deadline:
        status_code, body, error = get_json(
            url=f"{base_url}/api/r1/shop/ailist/task/{task_id}",
            headers=headers,
            timeout_sec=request_timeout_sec,
        )

        if error:
            return TaskResult(
                task_id=task_id,
                completed=False,
                success=False,
                status=None,
                latency_ms=(time.time() - start) * 1000,
                error=error,
            )

        if status_code != 200 or not isinstance(body, dict):
            return TaskResult(
                task_id=task_id,
                completed=False,
                success=False,
                status=None,
                latency_ms=(time.time() - start) * 1000,
                error=f"poll_http_{status_code}",
            )

        data = body.get("data") or {}
        task_status = data.get("status")

        if task_status in (SUCCESS_STATUS, FAIL_STATUS):
            return TaskResult(
                task_id=task_id,
                completed=True,
                success=task_status == SUCCESS_STATUS,
                status=task_status,
                latency_ms=(time.time() - start) * 1000,
                error=None,
            )

        time.sleep(poll_interval_sec)

    return TaskResult(
        task_id=task_id,
        completed=False,
        success=False,
        status=None,
        latency_ms=(time.time() - start) * 1000,
        error=f"poll_timeout_{poll_timeout_sec}s",
    )


def run_one_round(
    concurrency: int,
    base_url: str,
    headers: Dict[str, str],
    payload: Dict,
    submit_timeout_sec: int,
    poll_timeout_sec: int,
    poll_interval_sec: float,
    poll_request_timeout_sec: int,
) -> Dict:
    submit_results: List[SubmitResult] = []
    task_results: List[TaskResult] = []

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [
            pool.submit(submit_one, base_url, headers, payload, submit_timeout_sec)
            for _ in range(concurrency)
        ]
        for fut in as_completed(futures):
            submit_results.append(fut.result())

    success_submits = [x for x in submit_results if x.ok and x.task_id is not None]
    failed_submits = [x for x in submit_results if not x.ok]

    poll_workers = min(max(1, len(success_submits)), max(8, concurrency))
    if success_submits:
        with ThreadPoolExecutor(max_workers=poll_workers) as pool:
            futures = [
                pool.submit(
                    poll_task,
                    base_url,
                    headers,
                    x.task_id,
                    poll_timeout_sec,
                    poll_interval_sec,
                    poll_request_timeout_sec,
                )
                for x in success_submits
            ]
            for fut in as_completed(futures):
                task_results.append(fut.result())

    completed_tasks = [x for x in task_results if x.completed]
    successful_tasks = [x for x in task_results if x.success]
    failed_tasks = [x for x in task_results if not x.success]

    submit_latencies = [x.latency_ms for x in submit_results]
    task_latencies = [x.latency_ms for x in task_results if x.completed or x.error]

    error_breakdown: Dict[str, int] = {}

    for item in failed_submits:
        key = classify_submit_error(item.status_code, item.error)
        error_breakdown[key] = error_breakdown.get(key, 0) + 1

    for item in failed_tasks:
        key = classify_task_error(item)
        error_breakdown[key] = error_breakdown.get(key, 0) + 1

    task_success_rate = round((len(successful_tasks) / len(task_results)) * 100, 2) if task_results else 0.0

    return {
        "concurrency": concurrency,
        "submit_success": f"{len(success_submits)}/{concurrency}",
        "task_completed": len(completed_tasks),
        "task_success": len(successful_tasks),
        "task_success_rate": task_success_rate,
        "submit_avg_ms": round(statistics.mean(submit_latencies), 2) if submit_latencies else 0.0,
        "task_avg_ms": round(statistics.mean(task_latencies), 2) if task_latencies else 0.0,
        "p50_ms": percentile(task_latencies, 0.50),
        "p95_ms": percentile(task_latencies, 0.95),
        "p99_ms": percentile(task_latencies, 0.99),
        "error_breakdown": error_breakdown,
    }


def to_markdown(results: List[Dict], args: argparse.Namespace) -> str:
    lines = []
    lines.append(f"# AI Listing 并发压测报告（{datetime.now().strftime('%Y-%m-%d')}）")
    lines.append("")
    lines.append("## 1. 测试配置")
    lines.append(f"- base_url: `{args.base_url}`")
    lines.append(f"- 并发档位: `{', '.join(str(x) for x in args.concurrency_levels)}`")
    lines.append(f"- submit timeout: `{args.submit_timeout_sec}s`")
    lines.append(f"- poll timeout: `{args.poll_timeout_sec}s`")
    lines.append(f"- poll interval: `{args.poll_interval_sec}s`")
    lines.append("")
    lines.append("## 2. 结果汇总")
    lines.append("")
    lines.append("| 并发 | 提交成功 | 任务完成 | 任务成功 | 成功率 | submit_avg_ms | task_avg_ms | p50_ms | p95_ms | p99_ms |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for row in results:
        lines.append(
            "| {concurrency} | {submit_success} | {task_completed} | {task_success} | {task_success_rate:.2f}% | {submit_avg_ms} | {task_avg_ms} | {p50_ms} | {p95_ms} | {p99_ms} |".format(
                **row
            )
        )

    lines.append("")
    lines.append("## 3. 错误分布")
    lines.append("")
    for row in results:
        lines.append(f"### concurrency={row['concurrency']}")
        if row["error_breakdown"]:
            for key, value in sorted(row["error_breakdown"].items()):
                lines.append(f"- {key}: {value}")
        else:
            lines.append("- 无")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_levels(raw: str) -> List[int]:
    levels: List[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        levels.append(int(part))

    cleaned = sorted(set(levels))
    if not cleaned:
        raise ValueError("concurrency-levels cannot be empty")
    if any(x <= 0 for x in cleaned):
        raise ValueError("concurrency level must be positive")
    return cleaned


def main():
    parser = argparse.ArgumentParser(description="Shop API concurrency test")
    parser.add_argument("--base-url", default="http://localhost:1235")
    parser.add_argument("--accesskey", default="test_key")
    parser.add_argument("--accesssecret", default="test_secret")
    parser.add_argument("--scene", default="default")

    parser.add_argument("--site", default="shop")
    parser.add_argument("--spu-image-url", default="https://github.com/RudyGo8/AI_List_Generate/blob/master/datasets/iphone.png?raw=true")
    parser.add_argument("--product-title", default="Apple iPhone smartphone 128GB unlocked")
    parser.add_argument("--des-lang-type", default="English")

    parser.add_argument("--concurrency-levels", default="20,50,100", help="comma-separated, e.g. 20,50,100")
    parser.add_argument("--submit-timeout-sec", type=int, default=30)
    parser.add_argument("--poll-timeout-sec", type=int, default=300)
    parser.add_argument("--poll-interval-sec", type=float, default=2.0)
    parser.add_argument("--poll-request-timeout-sec", type=int, default=20)

    parser.add_argument("--report-out", default="")
    parser.add_argument("--json-out", default="")

    args = parser.parse_args()
    args.concurrency_levels = parse_levels(args.concurrency_levels)

    headers = {
        "Content-Type": "application/json",
        "accesskey": args.accesskey,
        "accesssecret": args.accesssecret,
        "x-ai-scene": args.scene,
    }
    payload = {
        "site": args.site,
        "spu_image_url": args.spu_image_url,
        "product_title": args.product_title,
        "des_lang_type": args.des_lang_type,
    }

    all_results: List[Dict] = []
    for level in args.concurrency_levels:
        print(f"[RUN] concurrency={level}")
        result = run_one_round(
            concurrency=level,
            base_url=args.base_url,
            headers=headers,
            payload=payload,
            submit_timeout_sec=args.submit_timeout_sec,
            poll_timeout_sec=args.poll_timeout_sec,
            poll_interval_sec=args.poll_interval_sec,
            poll_request_timeout_sec=args.poll_request_timeout_sec,
        )
        all_results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[SAVE] json report -> {json_path}")

    report_path = args.report_out
    if report_path:
        out_path = Path(report_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path("app/test_api") / f"concurrency_test_report_{timestamp}.md"

    markdown = to_markdown(all_results, args)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"[SAVE] markdown report -> {out_path}")


if __name__ == "__main__":
    main()
