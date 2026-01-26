#!/usr/bin/env python3
"""
Model Downloader for Ariv - All 22 Indian Languages Support
Downloads Indian AI models from HuggingFace
"""

import os
import sys
import argparse
from pathlib import Path
from huggingface_hub import hf_hub_download, snapshot_download
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelDownloader")

# Model configurations for all 22 Indian languages
MODELS = {
    # Core models
    "translator": {
        "repo_id": "sarvamai/sarvam-1",
        "filename": "sarvam-1-2b-q4.gguf",
        "description": "Sarvam-1 2B: Cultural translator for all Indic languages"
    },
    "reasoner": {
        "repo_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B-GGUF",
        "filename": "DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "description": "DeepSeek-R1 8B: Logic engine for reasoning"
    },
    "bridge": {
        "repo_id": "sarvamai/OpenHathi-7B-GGUF",
        "filename": "openhathi-7b-q4.gguf",
        "description": "OpenHathi 7B: Hinglish specialist"
    },
    "critic": {
        "repo_id": "ai4bharat/airavata",
        "filename": "airavata-7b-q4.gguf",
        "description": "Airavata 7B: Hindi instruction follower"
    },
    
    # Regional specialists - Dravidian languages
    "tamil_specialist": {
        "repo_id": "abhinand/tamil-llama-7b",
        "filename": "tamil-llama-7b-q4.gguf",
        "description": "Tamil-Llama 7B: Tamil language specialist"
    },
    "telugu_specialist": {
        "repo_id": "l3cube-pune/telugu-llama-7b",
        "filename": "telugu-llama-7b-q4.gguf",
        "description": "Telugu-Llama 7B: Telugu language specialist"
    },
    "kannada_specialist": {
        "repo_id": "l3cube-pune/kannada-llama-7b",
        "filename": "kannada-llama-7b-q4.gguf",
        "description": "Kannada-Llama 7B: Kannada language specialist"
    },
    "malayalam_specialist": {
        "repo_id": "l3cube-pune/malayalam-llama-7b",
        "filename": "malayalam-llama-7b-q4.gguf",
        "description": "Malayalam-Llama 7B: Malayalam language specialist"
    },
    
    # Regional specialists - Indo-Aryan languages
    "bengali_specialist": {
        "repo_id": "l3cube-pune/bengali-llama-7b",
        "filename": "bengali-llama-7b-q4.gguf",
        "description": "Bengali-Llama 7B: Bengali language specialist"
    },
    "gujarati_specialist": {
        "repo_id": "l3cube-pune/gujarati-llama-7b",
        "filename": "gujarati-llama-7b-q4.gguf",
        "description": "Gujarati-Llama 7B: Gujarati language specialist"
    },
    "marathi_specialist": {
        "repo_id": "l3cube-pune/marathi-llama-7b",
        "filename": "marathi-llama-7b-q4.gguf",
        "description": "Marathi-Llama 7B: Marathi language specialist"
    },
    "odia_specialist": {
        "repo_id": "l3cube-pune/odia-llama-7b",
        "filename": "odia-llama-7b-q4.gguf",
        "description": "Odia-Llama 7B: Odia language specialist"
    },
    "punjabi_specialist": {
        "repo_id": "l3cube-pune/punjabi-llama-7b",
        "filename": "punjabi-llama-7b-q4.gguf",
        "description": "Punjabi-Llama 7B: Punjabi language specialist"
    },
    "hindi_specialist": {
        "repo_id": "l3cube-pune/hindi-llama-7b",
        "filename": "hindi-llama-7b-q4.gguf",
        "description": "Hindi-Llama 7B: Hindi language specialist"
    },
    "hinglish_specialist": {
        "repo_id": "openhathi/hinglish-llama-7b",
        "filename": "hinglish-llama-7b-q4.gguf",
        "description": "Hinglish-Llama 7B: Code-mixed Hinglish specialist"
    }
}

class ModelDownloader:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def download_model(self, model_key: str, force: bool = False) -> bool:
        """Download a single model"""
        if model_key not in MODELS:
            logger.error(f"❌ Unknown model: {model_key}")
            return False
            
        model_info = MODELS[model_key]
        repo_id = model_info["repo_id"]
        filename = model_info["filename"]
        description = model_info["description"]
        
        output_path = self.models_dir / filename
        
        # Check if already exists
        if output_path.exists() and not force:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ {model_key} already exists ({size_mb:.1f}MB): {filename}")
            return True
            
        logger.info(f"⬇️  Downloading {model_key}: {description}")
        logger.info(f"   Repository: {repo_id}")
        logger.info(f"   File: {filename}")
        
        try:
            # Download file
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=str(self.models_dir),
                local_dir_use_symlinks=False
            )
            
            # Verify download
            final_path = self.models_dir / filename
            if final_path.exists():
                size_mb = final_path.stat().st_size / (1024 * 1024)
                logger.info(f"✅ Downloaded {model_key} ({size_mb:.1f}MB): {filename}")
                return True
            else:
                logger.error(f"❌ Download failed for {model_key}: File not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Download failed for {model_key}: {e}")
            return False
            
    def download_all(self, force: bool = False) -> Dict[str, bool]:
        """Download all models"""
        results = {}
        
        logger.info("=" * 60)
        logger.info("🎵 Ariv Model Downloader - All 22 Indian Languages")
        logger.info("=" * 60)
        logger.info(f"📁 Models directory: {self.models_dir}")
        logger.info(f"📊 Total models to download: {len(MODELS)}")
        logger.info("=" * 60)
        
        success_count = 0
        
        for model_key in MODELS.keys():
            logger.info("")
            success = self.download_model(model_key, force=force)
            results[model_key] = success
            
            if success:
                success_count += 1
                
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 DOWNLOAD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Successful: {success_count}/{len(MODELS)}")
        logger.info(f"❌ Failed: {len(MODELS) - success_count}")
        
        if success_count == len(MODELS):
            logger.info("🎉 All models downloaded successfully!")
        else:
            logger.warning("⚠️  Some models failed to download")
            
        # List downloaded models
        logger.info("")
        logger.info("📁 Downloaded models:")
        for model_file in self.models_dir.glob("*.gguf"):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            logger.info(f"   {model_file.name} ({size_mb:.1f}MB)")
            
        return results
        
    def verify_models(self) -> Dict[str, bool]:
        """Verify which models are available"""
        results = {}
        
        for model_key, model_info in MODELS.items():
            filename = model_info["filename"]
            model_path = self.models_dir / filename
            
            if model_path.exists():
                size_mb = model_path.stat().st_size / (1024 * 1024)
                logger.info(f"✅ {model_key}: {filename} ({size_mb:.1f}MB)")
                results[model_key] = True
            else:
                logger.info(f"❌ {model_key}: {filename} (missing)")
                results[model_key] = False
                
        return results
        
    def get_total_size(self) -> float:
        """Get total size of all downloaded models in GB"""
        total_bytes = 0
        for model_file in self.models_dir.glob("*.gguf"):
            total_bytes += model_file.stat().st_size
            
        return total_bytes / (1024**3)

def main():
    parser = argparse.ArgumentParser(
        description="Download models for Ariv - Indian AI Orchestra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all models
  python download_models.py all
  
  # Download specific model
  python download_models.py translator
  
  # Download core models only
  python download_models.py core
  
  # Verify existing models
  python download_models.py --verify
  
  # Force re-download
  python download_models.py all --force
        """
    )
    
    parser.add_argument("models", nargs="*", help="Models to download (all, core, or specific model names)")
    parser.add_argument("--models-dir", default="models", help="Directory to save models (default: models)")
    parser.add_argument("--verify", action="store_true", help="Verify existing models instead of downloading")
    parser.add_argument("--force", action="store_true", help="Force re-download even if models exist")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(models_dir=args.models_dir)
    
    if args.list:
        logger.info("📋 Available models:")
        for key, info in MODELS.items():
            logger.info(f"   {key}: {info['description']}")
        return
        
    if args.verify:
        logger.info("🔍 Verifying existing models...")
        downloader.verify_models()
        total_size = downloader.get_total_size()
        logger.info(f"💾 Total size: {total_size:.2f}GB")
        return
        
    # Determine which models to download
    if "all" in args.models:
        models_to_download = list(MODELS.keys())
    elif "core" in args.models:
        models_to_download = ["translator", "reasoner", "critic", "bridge"]
    elif args.models:
        models_to_download = args.models
    else:
        # Default: download core models
        models_to_download = ["translator", "reasoner", "critic"]
        
    # Validate model names
    invalid_models = [m for m in models_to_download if m not in MODELS]
    if invalid_models:
        logger.error(f"❌ Invalid model names: {invalid_models}")
        logger.info("Use --list to see available models")
        sys.exit(1)
        
    # Download models
    if "all" in args.models or "core" in args.models:
        # Download all or core in batch
        downloader.download_all(force=args.force)
    else:
        # Download specific models
        for model_key in models_to_download:
            downloader.download_model(model_key, force=args.force)
            
    # Show final status
    logger.info("")
    logger.info("🎵 Ariv Model Downloader Complete!")
    logger.info(f"💾 Total disk usage: {downloader.get_total_size():.2f}GB")

if __name__ == "__main__":
    main()
