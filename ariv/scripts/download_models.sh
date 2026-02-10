#!/usr/bin/env bash
set -euo pipefail

DRY_RUN="false"
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="true"
fi

mkdir -p ariv/models/gguf

do_download() {
  local url="$1"
  local out="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] wget -c -O ${out} ${url}"
    return 0
  fi
  wget -c -O "${out}" "${url}"
}

# Sarvam 2B
SARVAM_URL="https://huggingface.co/rachittshah/sarvam-2b-v0.5-Q4_K_M-GGUF/resolve/main/sarvam-2b-v0.5-q4_k_m.gguf"
do_download "${SARVAM_URL}" "ariv/models/gguf/sarvam-2b-q4_k_m.gguf"

# Qwen 2.5 3B
QWEN_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
do_download "${QWEN_URL}" "ariv/models/gguf/qwen-2.5-3b-q4_k_m.gguf"

echo "Download complete. Verify with ariv/scripts/verify_model.sh"
