# AI Listing 并发压测报告（2026-04-16）

## 1. 测试配置
- base_url: `http://localhost:1235`
- 并发档位: `20, 50, 100`
- submit timeout: `30s`
- poll timeout: `300s`
- poll interval: `2.0s`

## 2. 结果汇总

| 并发 | 提交成功 | 任务完成 | 任务成功 | 成功率 | submit_avg_ms | task_avg_ms | p50_ms | p95_ms | p99_ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 20/20 | 0 | 0 | 0.00% | 2702.85 | 22054.55 | 22056.2 | 22062.31 | 22062.31 |
| 50 | 0/50 | 0 | 0 | 0.00% | 32047.21 | 0.0 | 0.0 | 0.0 | 0.0 |
| 100 | 0/100 | 0 | 0 | 0.00% | 32067.65 | 0.0 | 0.0 | 0.0 | 0.0 |

## 3. 错误分布

### concurrency=20
- poll_timeout: 20

### concurrency=50
- submit_timeout: 50

### concurrency=100
- submit_timeout: 100
