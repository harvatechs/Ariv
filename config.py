"""
Ariv Configuration - Production Ready
Configure model paths and system parameters for all 22 Indian languages
"""

import os
from typing import Dict, List

# All 22 Official Indian Languages (Eighth Schedule of Constitution)
# In alphabetical order
INDIAN_LANGUAGES_22 = {
    "assamese": {
        "code": "as",
        "script": "Bengali-Assamese",
        "native_name": "অসমীয়া",
        "model_specialist": None,  # Use general translator
        "family": "Indo-Aryan"
    },
    "bengali": {
        "code": "bn", 
        "script": "Bengali-Assamese",
        "native_name": "বাংলা",
        "model_specialist": "bengali_specialist",
        "family": "Indo-Aryan"
    },
    "bodo": {
        "code": "brx",
        "script": "Devanagari",
        "native_name": "बोड़ो",
        "model_specialist": None,
        "family": "Sino-Tibetan"
    },
    "dogri": {
        "code": "doi",
        "script": "Devanagari", 
        "native_name": "डोगरी",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "english": {
        "code": "en",
        "script": "Latin",
        "native_name": "English",
        "model_specialist": None,
        "family": "Germanic"
    },
    "gujarati": {
        "code": "gu",
        "script": "Gujarati",
        "native_name": "ગુજરાતી",
        "model_specialist": "gujarati_specialist",
        "family": "Indo-Aryan"
    },
    "hindi": {
        "code": "hi",
        "script": "Devanagari",
        "native_name": "हिन्दी",
        "model_specialist": "hindi_specialist", 
        "family": "Indo-Aryan"
    },
    "kannada": {
        "code": "kn",
        "script": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "model_specialist": "kannada_specialist",
        "family": "Dravidian"
    },
    "kashmiri": {
        "code": "ks",
        "script": "Perso-Arabic/Devanagari",
        "native_name": "कश्मीरी / كشميري",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "konkani": {
        "code": "kok",
        "script": "Devanagari/Kannada",
        "native_name": "कोंकणी",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "maithili": {
        "code": "mai",
        "script": "Devanagari/Tirhuta",
        "native_name": "मैथिली",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "malayalam": {
        "code": "ml",
        "script": "Malayalam",
        "native_name": "മലയാളം",
        "model_specialist": "malayalam_specialist",
        "family": "Dravidian"
    },
    "manipuri": {
        "code": "mni",
        "script": "Bengali-Assamese/Meitei Mayek",
        "native_name": "মণিপুরি / Meitei",
        "model_specialist": None,
        "family": "Sino-Tibetan"
    },
    "marathi": {
        "code": "mr",
        "script": "Devanagari",
        "native_name": "मराठी",
        "model_specialist": "marathi_specialist",
        "family": "Indo-Aryan"
    },
    "nepali": {
        "code": "ne",
        "script": "Devanagari",
        "native_name": "नेपाली",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "odia": {
        "code": "or",
        "script": "Odia",
        "native_name": "ଓଡ଼ିଆ",
        "model_specialist": "odia_specialist",
        "family": "Indo-Aryan"
    },
    "punjabi": {
        "code": "pa",
        "script": "Gurmukhi",
        "native_name": "ਪੰਜਾਬੀ",
        "model_specialist": "punjabi_specialist",
        "family": "Indo-Aryan"
    },
    "sanskrit": {
        "code": "sa",
        "script": "Devanagari",
        "native_name": "संस्कृतम्",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "santali": {
        "code": "sat",
        "script": "Ol Chiki/Devanagari",
        "native_name": "ᱥᱟᱱᱛᱟᱲᱤ",
        "model_specialist": None,
        "family": "Austroasiatic"
    },
    "sindhi": {
        "code": "sd",
        "script": "Perso-Arabic/Devanagari",
        "native_name": "सिन्धी / سنڌي",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "tamil": {
        "code": "ta",
        "script": "Tamil",
        "native_name": "தமிழ்",
        "model_specialist": "tamil_specialist",
        "family": "Dravidian"
    },
    "telugu": {
        "code": "te",
        "script": "Telugu", 
        "native_name": "తెలుగు",
        "model_specialist": "telugu_specialist",
        "family": "Dravidian"
    },
    "urdu": {
        "code": "ur",
        "script": "Perso-Arabic",
        "native_name": "اردو",
        "model_specialist": None,
        "family": "Indo-Aryan"
    },
    "hinglish": {
        "code": "hi-en",
        "script": "Latin/Devanagari",
        "native_name": "Hinglish",
        "model_specialist": "hinglish_specialist",
        "family": "Code-mixed"
    }
}

# Model Configuration for Google Colab T4 (16GB VRAM)
# All models should be in GGUF Q4_K_M format for optimal size/performance

MODEL_CONFIG = {
    # Phase 1 & 4: Translator (2B parameters, ~1.5GB VRAM)
    # Sarvam-1: Best for Indic token efficiency and cultural context
    "translator": {
        "path": "models/sarvam-1-2b-q4.gguf",
        "url": "https://huggingface.co/sarvamai/sarvam-1/resolve/main/sarvam-1-2b-q4.gguf",
        "n_ctx": 4096,
        "description": "Sarvam-1 2B: Cultural translator and contextualizer for all Indic languages"
    },

    # Phase 2: Primary Reasoner (7B parameters, ~4.5GB VRAM)
    # DeepSeek-R1-Distill: State-of-the-art reasoning
    "reasoner": {
        "path": "models/deepseek-r1-distill-llama-8b-q4.gguf", 
        "url": "https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q4_K_M.gguf",
        "n_ctx": 8192,
        "description": "DeepSeek-R1 8B: Logic engine for math/coding/reasoning"
    },

    # Alternative Phase 2: Bilingual Bridge (7B parameters, ~4.5GB VRAM)
    # OpenHathi: For Hinglish queries and moderate reasoning
    "bridge": {
        "path": "models/openhathi-7b-q4.gguf",
        "url": "https://huggingface.co/sarvamai/OpenHathi-7B-GGUF/resolve/main/openhathi-7b-q4.gguf", 
        "n_ctx": 4096,
        "description": "OpenHathi 7B: Hinglish specialist and bilingual bridge"
    },

    # Phase 3: Critic (7B parameters, ~4.5GB VRAM)
    # Airavata: Hindi instruction follower, good for verification
    "critic": {
        "path": "models/airavata-7b-q4.gguf",
        "url": "https://huggingface.co/ai4bharat/airavata/resolve/main/airavata-7b-q4.gguf",
        "n_ctx": 4096, 
        "description": "Airavata 7B: Instruction-following critic and verifier"
    },

    # Regional Specialists (dynamically loaded)
    "tamil_specialist": {
        "path": "models/tamil-llama-7b-q4.gguf",
        "url": "https://huggingface.co/abhinand/tamil-llama-7b/resolve/main/tamil-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Tamil-Llama 7B: Tamil language nuances"
    },
    
    "bengali_specialist": {
        "path": "models/bengali-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/bengali-llama-7b/resolve/main/bengali-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Bengali-Llama 7B: Bengali language specialist"
    },
    
    "gujarati_specialist": {
        "path": "models/gujarati-llama-7b-q4.gguf", 
        "url": "https://huggingface.co/l3cube-pune/gujarati-llama-7b/resolve/main/gujarati-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Gujarati-Llama 7B: Gujarati language specialist"
    },
    
    "kannada_specialist": {
        "path": "models/kannada-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/kannada-llama-7b/resolve/main/kannada-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Kannada-Llama 7B: Kannada language specialist"
    },
    
    "malayalam_specialist": {
        "path": "models/malayalam-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/malayalam-llama-7b/resolve/main/malayalam-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Malayalam-Llama 7B: Malayalam language specialist"
    },
    
    "marathi_specialist": {
        "path": "models/marathi-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/marathi-llama-7b/resolve/main/marathi-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Marathi-Llama 7B: Marathi language specialist"
    },
    
    "odia_specialist": {
        "path": "models/odia-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/odia-llama-7b/resolve/main/odia-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Odia-Llama 7B: Odia language specialist"
    },
    
    "punjabi_specialist": {
        "path": "models/punjabi-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/punjabi-llama-7b/resolve/main/punjabi-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Punjabi-Llama 7B: Punjabi language specialist"
    },
    
    "telugu_specialist": {
        "path": "models/telugu-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/telugu-llama-7b/resolve/main/telugu-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Telugu-Llama 7B: Telugu language specialist"
    },
    
    "hindi_specialist": {
        "path": "models/hindi-llama-7b-q4.gguf",
        "url": "https://huggingface.co/l3cube-pune/hindi-llama-7b/resolve/main/hindi-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Hindi-Llama 7B: Hindi language specialist"
    },
    
    "hinglish_specialist": {
        "path": "models/hinglish-llama-7b-q4.gguf",
        "url": "https://huggingface.co/openhathi/hinglish-llama-7b/resolve/main/hinglish-llama-7b-q4.gguf",
        "n_ctx": 4096,
        "description": "Hinglish-Llama 7B: Code-mixed Hinglish specialist"
    }
}

# VRAM Management Settings
VRAM_CONFIG = {
    "total_vram_gb": 16,
    "safety_margin_gb": 2,  # Keep 2GB free for overhead
    "max_concurrent_models": 1,  # Strict sequential loading
    "enable_offloading": True,  # Allow CPU offloading if needed
    "enable_memory_pooling": True,  # Keep translator loaded when possible
}

# Pipeline Settings
PIPELINE_CONFIG = {
    "default_language": "hindi",
    "enable_critic": True,
    "max_critic_iterations": 5,  # Increased for deeper reasoning
    "enable_self_consistency": True,  # Multiple reasoning paths
    "self_consistency_paths": 5,  # Number of reasoning paths to generate
    "temperature": {
        "ingestion": 0.2,    # Very faithful translation
        "reasoning": 0.6,    # Logical but controlled
        "critic": 0.4,       # Balanced skepticism
        "synthesis": 0.3     # Natural but accurate
    },
    "max_tokens": {
        "ingestion": 2048,
        "reasoning": 4096,   # Longer for complex problems
        "critic": 1024,
        "synthesis": 2048
    }
}

# Chain-of-Thought Configuration
COT_CONFIG = {
    "enable_deep_cot": True,  # Enable multi-step reasoning
    "cot_depth": 3,  # Number of reasoning depths
    "enable_program_of_thoughts": True,  # Generate code for math problems
    "enable_adversarial_cot": True,  # Devil's advocate reasoning
    "enable_reflection": True,  # Self-reflection on reasoning
}

# Tool Calling Configuration
TOOL_CONFIG = {
    "enabled": True,
    "tools": [
        "calculator",
        "code_executor", 
        "web_search",
        "knowledge_base",
        "file_system"
    ],
    "max_tool_calls": 10,
    "tool_timeout": 30
}

# ARC-AGI 2 Configuration
ARC_CONFIG = {
    "benchmark_dir": "benchmarks/arc_agi_2",
    "max_attempts": 100,
    "use_test_time_compute": True,
    "test_time_budget": 300,  # 5 minutes per problem
    "enable_ensemble": True,
    "ensemble_models": ["reasoner", "bridge"],
    "voting_strategy": "majority"  # majority, weighted, confidence
}

def get_model_paths() -> Dict[str, str]:
    """Returns simple role->path mapping for JugaadOrchestrator"""
    return {role: config["path"] for role, config in MODEL_CONFIG.items()}

def get_language_config(language: str) -> Dict:
    """Get configuration for a specific language"""
    return INDIAN_LANGUAGES_22.get(language, INDIAN_LANGUAGES_22["hindi"])

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

def get_supported_languages() -> List[str]:
    """Get list of all supported languages"""
    return list(INDIAN_LANGUAGES_22.keys())
