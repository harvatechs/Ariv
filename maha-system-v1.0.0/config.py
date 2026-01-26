"""
Maha-System Configuration
Configure model paths and system parameters here
"""

import os
from typing import Dict

# Model Configuration for Google Colab T4 (16GB VRAM)
# All models should be in GGUF Q4_K_M format for optimal size/performance

MODEL_CONFIG = {
    # Phase 1 & 4: Translator (2B parameters, ~1.5GB VRAM)
    # Sarvam-1: Best for Indic token efficiency and cultural context
    "translator": {
        "path": "/content/models/sarvam-1-2b-q4.gguf",
        "url": "https://huggingface.co/sarvamai/sarvam-1/resolve/main/sarvam-1-2b-q4.gguf",
        "n_ctx": 4096,
        "description": "Sarvam-1 2B: Cultural translator and contextualizer"
    },

    # Phase 2: Primary Reasoner (7B parameters, ~4.5GB VRAM)
    # DeepSeek-R1-Distill: State-of-the-art reasoning
    "reasoner": {
        "path": "/content/models/deepseek-r1-distill-llama-8b-q4.gguf", 
        "url": "https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "n_ctx": 8192,
        "description": "DeepSeek-R1 8B: Logic engine for math/coding/reasoning"
    },

    # Alternative Phase 2: Bilingual Bridge (7B parameters, ~4.5GB VRAM)
    # OpenHathi: For Hinglish queries and moderate reasoning
    "bridge": {
        "path": "/content/models/openhathi-7b-q4.gguf",
        "url": "https://huggingface.co/sarvamai/OpenHathi-7B-GGUF/resolve/main/openhathi-7b-q4.gguf", 
        "n_ctx": 4096,
        "description": "OpenHathi 7B: Hinglish specialist and bilingual bridge"
    },

    # Phase 3: Critic (7B parameters, ~4.5GB VRAM)
    # Airavata: Hindi instruction follower, good for verification
    "critic": {
        "path": "/content/models/airavata-7b-q4.gguf",
        "url": "https://huggingface.co/ai4bharat/airavata/resolve/main/airavata-7b-q4.gguf",
        "n_ctx": 4096, 
        "description": "Airavata 7B: Instruction-following critic and verifier"
    },

    # Regional Specialist: Tamil (7B parameters, ~4.5GB VRAM)
    # Loaded dynamically only for Tamil queries
    "tamil_specialist": {
        "path": "/content/models/tamil-llama-7b-q4.gguf",
        "url": "https://huggingface.co/abhinand/tamil-llama-7b/resolve/main/tamil-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Tamil-Llama 7B: Tamil language nuances"
    }
}

# VRAM Management Settings
VRAM_CONFIG = {
    "total_vram_gb": 16,
    "safety_margin_gb": 2,  # Keep 2GB free for overhead
    "max_concurrent_models": 1,  # Strict sequential loading
    "enable_offloading": True,  # Allow CPU offloading if needed
}

# Pipeline Settings
PIPELINE_CONFIG = {
    "default_language": "hindi",
    "enable_critic": True,
    "max_critic_iterations": 3,
    "temperature": {
        "ingestion": 0.3,    # Faithful translation
        "reasoning": 0.7,    # Creative but logical
        "critic": 0.5,       # Balanced skepticism
        "synthesis": 0.4     # Natural but accurate
    }
}

# Language Code Mapping
LANGUAGE_CODES = {
    "hindi": "hi",
    "tamil": "ta", 
    "telugu": "te",
    "marathi": "mr",
    "bengali": "bn",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    "hinglish": "hi-en"
}

def get_model_paths() -> Dict[str, str]:
    """Returns simple role->path mapping for JugaadOrchestrator"""
    return {role: config["path"] for role, config in MODEL_CONFIG.items()}

def verify_models():
    """Check which models are downloaded"""
    status = {}
    for role, config in MODEL_CONFIG.items():
        exists = os.path.exists(config["path"])
        size = os.path.getsize(config["path"]) / (1024**3) if exists else 0
        status[role] = {
            "exists": exists,
            "size_gb": round(size, 2),
            "path": config["path"]
        }
    return status
