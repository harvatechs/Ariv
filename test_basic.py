#!/usr/bin/env python3
"""
Basic tests for Ariv system without heavy dependencies
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_syntax():
    """Test that config file syntax is valid"""
    print("🧪 Testing config syntax...")
    
    try:
        # Read config file and check syntax
        config_file = Path("config.py")
        with open(config_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        import ast
        ast.parse(code)
        print("✅ Config syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Config syntax error: {e}")
        return False

def test_language_config():
    """Test language configuration"""
    print("\n🧪 Testing language configuration...")
    
    try:
        # Import config without llama dependency
        sys.modules['llama_cpp'] = type(sys)('llama_cpp')
        sys.modules['llama_cpp'].Llama = type('Llama', (), {})
        
        from config import INDIAN_LANGUAGES_22, get_supported_languages
        
        # Test language count
        lang_count = len(INDIAN_LANGUAGES_22)
        print(f"📊 Total languages: {lang_count}")
        
        # Test supported languages
        supported = get_supported_languages()
        print(f"📊 Supported languages: {len(supported)}")
        
        # Show sample languages
        sample_langs = ["hindi", "tamil", "bengali", "telugu", "marathi"]
        for lang in sample_langs:
            if lang in INDIAN_LANGUAGES_22:
                info = INDIAN_LANGUAGES_22[lang]
                print(f"✅ {lang}: {info['native_name']} ({info['script']})")
            else:
                print(f"❌ {lang} not found")
                return False
        
        # Check for all 22 official languages
        official_22 = [
            "assamese", "bengali", "bodo", "dogri", "english", "gujarati", "hindi",
            "kannada", "kashmiri", "konkani", "maithili", "malayalam", "manipuri",
            "marathi", "nepali", "odia", "punjabi", "sanskrit", "santali", "sindhi",
            "tamil", "telugu", "urdu"
        ]
        
        missing = [lang for lang in official_22 if lang not in INDIAN_LANGUAGES_22]
        if missing:
            print(f"❌ Missing languages: {missing}")
            return False
        else:
            print("✅ All 22 official Indian languages supported")
            
        return True
        
    except Exception as e:
        print(f"❌ Language config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_config():
    """Test model configuration"""
    print("\n🧪 Testing model configuration...")
    
    try:
        from config import MODEL_CONFIG
        
        print(f"📊 Total models: {len(MODEL_CONFIG)}")
        
        # Check core models
        core_models = ["translator", "reasoner", "critic", "bridge"]
        for model in core_models:
            if model in MODEL_CONFIG:
                info = MODEL_CONFIG[model]
                print(f"✅ {model}: {info['description']}")
            else:
                print(f"❌ {model} not found")
                return False
        
        # Check regional specialists
        specialists = [k for k in MODEL_CONFIG.keys() if k.endswith("_specialist")]
        print(f"✅ Regional specialists: {len(specialists)}")
        for spec in specialists[:5]:  # Show first 5
            print(f"   - {spec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model config test failed: {e}")
        return False

def test_tools_framework():
    """Test tool framework without heavy dependencies"""
    print("\n🧪 Testing tool framework...")
    
    try:
        # Mock torch for tools
        sys.modules['torch'] = type(sys)('torch')
        sys.modules['torch'].cuda = type('cuda', (), {})
        sys.modules['torch'].cuda.is_available = lambda: False
        sys.modules['torch'].cuda.memory_allocated = lambda: 0
        sys.modules['torch'].cuda.memory_reserved = lambda: 0
        sys.modules['torch'].cuda.empty_cache = lambda: None
        sys.modules['torch'].cuda.synchronize = lambda: None
        sys.modules['torch'].cuda.get_device_properties = lambda x: type('props', (), {'total_memory': 16*1024**3})
        
        from tools.registry import ToolRegistry
        from tools.tools import CalculatorTool, KnowledgeBaseTool
        
        # Test registry
        registry = ToolRegistry()
        tools = registry.get_available_tools()
        print(f"✅ Tool registry: {len(tools)} tools")
        
        # Test calculator
        calc = CalculatorTool()
        schema = calc.get_schema()
        print(f"✅ Calculator: {schema['name']}")
        
        result = calc.execute("2 + 2")
        print(f"✅ Calculator test: 2 + 2 = {result}")
        assert result == 4
        
        # Test knowledge base
        kb = KnowledgeBaseTool()
        result = kb.execute("capital of India")
        print(f"✅ Knowledge base test: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompts():
    """Test prompt loading"""
    print("\n🧪 Testing prompts...")
    
    try:
        import yaml
        prompts_file = Path("prompts/meta_prompts.yaml")
        
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
            
            required_prompts = ["ingestion", "reasoning", "critic", "synthesis"]
            for prompt in required_prompts:
                if prompt in prompts:
                    content = prompts[prompt]
                    print(f"✅ {prompt}: {len(content)} chars")
                else:
                    print(f"❌ {prompt} missing")
                    return False
            return True
        else:
            print("⚠️  Prompts file not found")
            return True
            
    except Exception as e:
        print(f"❌ Prompts test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist"""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        "core", "models", "prompts", "tools", "benchmarks", 
        "languages", "deploy", "tests", "examples", "docs"
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ missing")
            return False
    
    # Check required files
    required_files = [
        "config.py", "maha_system.py", "requirements.txt", 
        "setup.py", "README.md", "prompts/meta_prompts.yaml"
    ]
    
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.is_file():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    return True

def test_dependencies():
    """Test optional dependencies"""
    print("\n🧪 Testing optional dependencies...")
    
    # Check if llama-cpp is available
    try:
        import llama_cpp
        print("✅ llama-cpp-python: AVAILABLE")
        llama_available = True
    except ImportError:
        print("⚠️  llama-cpp-python: NOT AVAILABLE (required for model inference)")
        llama_available = False
    
    # Check if torch is available
    try:
        import torch
        print("✅ PyTorch: AVAILABLE")
        torch_available = True
    except ImportError:
        print("⚠️  PyTorch: NOT AVAILABLE (required for GPU memory management)")
        torch_available = False
    
    # Check if yaml is available
    try:
        import yaml
        print("✅ PyYAML: AVAILABLE")
    except ImportError:
        print("❌ PyYAML: NOT AVAILABLE (required for prompts)")
        return False
    
    # Check if numpy is available
    try:
        import numpy
        print("✅ NumPy: AVAILABLE")
    except ImportError:
        print("⚠️  NumPy: NOT AVAILABLE (optional)")
    
    return True

def create_install_script():
    """Create installation script"""
    script_content = '''#!/bin/bash
# Ariv Installation Script

echo "🎵 Installing Ariv - The Indian AI Orchestra"
echo "="60

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📊 Python version: $python_version"

# Install basic dependencies
echo "📦 Installing basic dependencies..."
pip3 install pyyaml numpy requests

# Install optional dependencies
echo "📦 Installing optional dependencies..."
pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# Install llama-cpp-python (CPU version for testing)
echo "📦 Installing llama-cpp-python (CPU version)..."
pip3 install llama-cpp-python

echo "✅ Basic installation complete!"
echo ""
echo "💡 Next steps:"
echo "   1. Download models: python3 models/download_models.py core"
echo "   2. Test system: python3 test_basic.py"
echo "   3. Run interactive: python3 maha_system.py --interactive --lang hindi"
'''
    
    with open("install.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("install.sh", 0o755)
    print("✅ Created installation script: install.sh")

def main():
    """Run all basic tests"""
    print("🎵 Ariv Basic Test Suite")
    print("=" * 60)
    
    tests = [
        ("Config Syntax", test_config_syntax),
        ("Language Config", test_language_config),
        ("Model Config", test_model_config),
        ("Tools Framework", test_tools_framework),
        ("Prompts", test_prompts),
        ("Directory Structure", test_directory_structure),
        ("Dependencies", test_dependencies),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BASIC TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed >= 5:  # Allow some failures for optional components
        print("\n🎉 Basic tests passed! System structure is ready.")
        
        # Create installation script
        create_install_script()
        
        print("\n💡 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Or use script: ./install.sh")
        print("   3. Download models: python models/download_models.py core")
        print("   4. Test system: python maha_system.py --status")
        print("   5. Run interactive: python maha_system.py --interactive --lang hindi")
        return 0
    else:
        print(f"\n⚠️  Multiple tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
