#!/usr/bin/env python3
"""
Model Downloader for Maha-System
Downloads GGUF models from HuggingFace to Google Drive/Colab
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files
import argparse

# Map friendly names to HF repo details
MODEL_REPOS = {
    "sarvam-1": {
        "repo_id": "sarvamai/sarvam-1",
        "filename": "sarvam-1-2b-q4.gguf",
        "revision": "main"
    },
    "deepseek-r1": {
        "repo_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B-GGUF",
        "filename": "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "revision": "main"
    },
    "openhathi": {
        "repo_id": "sarvamai/OpenHathi-7B-GGUF", 
        "filename": "openhathi-7b-q4.gguf",
        "revision": "main"
    },
    "airavata": {
        "repo_id": "ai4bharat/airavata",
        "filename": "airavata-7b-q4.gguf",
        "revision": "main"
    }
}

def download_model(model_name: str, cache_dir: str = "/content/models"):
    """Download a specific model"""
    if model_name not in MODEL_REPOS:
        print(f"❌ Unknown model: {model_name}")
        print(f"Available: {list(MODEL_REPOS.keys())}")
        return False

    info = MODEL_REPOS[model_name]
    os.makedirs(cache_dir, exist_ok=True)

    print(f"⬇️ Downloading {model_name} from {info['repo_id']}...")
    print(f"   File: {info['filename']}")

    try:
        local_path = hf_hub_download(
            repo_id=info["repo_id"],
            filename=info["filename"],
            cache_dir=cache_dir,
            local_dir=cache_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )

        size_gb = os.path.getsize(local_path) / (1024**3)
        print(f"✅ Downloaded: {local_path} ({size_gb:.2f} GB)")
        return True

    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def download_all(cache_dir: str = "/content/models"):
    """Download all orchestra models"""
    print("🎵 Downloading full Maha-System Orchestra...")
    success_count = 0

    for model_name in MODEL_REPOS:
        if download_model(model_name, cache_dir):
            success_count += 1
        print()

    print(f"✅ Downloaded {success_count}/{len(MODEL_REPOS)} models")

    # Check VRAM math
    total_size = sum([
        1.5,  # Sarvam-1 (2B)
        5.0,  # DeepSeek (8B) 
        4.5,  # OpenHathi (7B)
        4.5   # Airavata (7B)
    ])
    print(f"📊 Total VRAM required for orchestra: ~{total_size}GB (sequential loading)")
    print(f"📊 T4 GPU has 16GB VRAM - {'SUFFICIENT' if total_size < 16 else 'INSUFFICIENT'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Maha-System models")
    parser.add_argument("model", nargs="?", help="Model name to download (or 'all')")
    parser.add_argument("--dir", default="/content/models", help="Download directory")

    args = parser.parse_args()

    if args.model == "all" or args.model is None:
        download_all(args.dir)
    else:
        download_model(args.model, args.dir)
