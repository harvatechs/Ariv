# Deployment Guide (Production)

This guide defines a production-grade deployment baseline for Ariv, including environment hardening, runtime configuration, observability, and benchmark sign-off.

## 1) Deployment architecture

Recommended minimal production stack:

- **Ariv API** (`deploy/api_wrapper.py`) as ASGI app.
- **Reverse proxy** (Nginx/Caddy) for TLS termination and request limits.
- **Process supervisor** (systemd/supervisord) with automatic restarts.
- **Metrics + logs** pipeline (Prometheus/Grafana + centralized logs).
- **Model cache volume** mounted on fast local SSD.

## 2) Environment baseline

- Python 3.10+ recommended.
- Dedicated service user (no root execution).
- `ulimit` tuned for concurrent clients.
- GPU drivers pinned and validated (if GPU inference is enabled).

### Example bootstrap

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Security hardening checklist

- [ ] Run behind HTTPS only.
- [ ] Restrict CORS to trusted origins.
- [ ] Add API authentication/authorization.
- [ ] Set request body size and rate limits at reverse proxy.
- [ ] Disable debug mode in production.
- [ ] Rotate secrets via environment variables or secret manager.
- [ ] Enable audit logging for admin operations.

## 4) Runtime configuration

Set explicit runtime values instead of relying on defaults:

- model path(s)
- max tokens
- temperature
- GPU layer offload
- timeout budgets
- concurrency limits

Use environment-specific `.env` files and avoid committing secrets.

## 5) Operations and observability

Track, at minimum:

- Request count / error rate
- p50 / p95 / p99 latency
- Throughput (tokens per second)
- GPU utilization, VRAM usage, CPU, memory
- Queue depth / active sessions

Define SLOs before launch (example):

- Availability: 99.5% monthly
- p95 latency: < 2.5s on standard prompt class
- Error rate: < 1%

## 6) Release gates

A release is production-ready only if all are true:

1. Security checklist complete.
2. Smoke tests pass.
3. Benchmark report generated and reviewed.
4. Rollback plan documented.
5. On-call and alert routing configured.

## 7) Benchmark sign-off workflow

Run benchmark:

```bash
python benchmarks/run_bench.py --models tests/fixtures/tiny.gguf --lang hi --subset dev
```

Generate a production-friendly report from CSV:

```bash
python benchmarks/generate_report.py --csv benchmarks/results/tiny.gguf-hi-dev.csv --output benchmarks/results/PRODUCTION_BENCHMARK_REPORT.md
```

Commit benchmark artifacts for traceability.

## 8) Suggested deployment command

```bash
python deploy/api_wrapper.py
```

For internet-facing services, prefer running with a production ASGI server and proxy (e.g., gunicorn/uvicorn workers + Nginx).
