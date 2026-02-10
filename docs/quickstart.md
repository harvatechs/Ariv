# ARIV Low-VRAM Quickstart

## 1) Hardware probe
```bash
python ariv/scripts/probe_hw.py
```

## 2) Download models
```bash
bash ariv/scripts/download_models.sh
```

## 3) Start server
```bash
arivctl start --host 0.0.0.0 --port 8000
```

## 4) Chat
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo", "text": "नमस्ते", "preferred_lang": "hi"}'
```

## 5) CLI status
```bash
arivctl status
```

## 6) Run benchmark
```bash
python benchmarks/run_bench.py --models tests/fixtures/tiny.gguf --lang hi --subset dev
```
