#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${1:-}"
if [[ -z "$MODEL_PATH" ]]; then
  echo "Usage: verify_model.sh /path/to/model.gguf"
  exit 1
fi

LLAMA_BIN="${LLAMA_CPP_BIN:-llama-cli}"
PROMPT="नमस्ते, यह एक छोटा परीक्षण है।"

"${LLAMA_BIN}" -m "${MODEL_PATH}" -p "${PROMPT}" -n 16 --mmap --use-mlock --num-gpu-layers 10
