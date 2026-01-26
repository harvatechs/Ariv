#!/usr/bin/env python3
"""
Test script for Ariv system
Tests basic functionality without requiring models
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from core.orchestrator import JugaadOrchestrator
        from core.trv_pipeline import TRVPipeline
        from core.vram_manager import VRAMManager, MemoryStats
        from tools.registry import ToolRegistry
        from config import get_model_paths, get_supported_languages, INDIAN_LANGUAGES_22
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import INDIAN_LANGUAGES_22, MODEL_CONFIG, PIPELINE_CONFIG
        
        # Test language count
        lang_count = len(INDIAN_LANGUAGES_22)
        print(f"📊 Loaded {lang_count} languages")
        
        # Test model config
        model_count = len(MODEL_CONFIG)
        print(f"📊 Loaded {model_count} model configurations")
        
        # Test pipeline config
        assert "max_critic_iterations" in PIPELINE_CONFIG
        print(f"✅ Pipeline config loaded (max iterations: {PIPELINE_CONFIG['max_critic_iterations']})")
        
        # Test specific languages
        test_langs = ["hindi", "tamil", "bengali", "telugu"]
        for lang in test_langs:
            if lang in INDIAN_LANGUAGES_22:
                info = INDIAN_LANGUAGES_22[lang]
                print(f"✅ {lang}: {info['native_name']} ({info['script']})")
            else:
                print(f"❌ {lang} not found")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_paths():
    """Test model path configuration"""
    print("\n🧪 Testing model paths...")
    
    try:
        from config import get_model_paths
        
        paths = get_model_paths()
        print(f"📊 Found {len(paths)} model roles")
        
        for role, path in list(paths.items())[:3]:  # Show first 3
            print(f"   {role}: {path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Model paths test failed: {e}")
        return False

def test_tools():
    """Test tool framework"""
    print("\n🧪 Testing tool framework...")
    
    try:
        from tools.registry import ToolRegistry
        from tools.tools import CalculatorTool, KnowledgeBaseTool
        
        # Test registry
        registry = ToolRegistry()
        tools = registry.get_available_tools()
        print(f"✅ Tool registry loaded with {len(tools)} tools: {', '.join(tools)}")
        
        # Test calculator
        calc = CalculatorTool()
        schema = calc.get_schema()
        print(f"✅ Calculator schema: {schema['name']}")
        
        result = calc.execute("2 + 2")
        print(f"✅ Calculator test: 2 + 2 = {result}")
        assert result == 4
        
        # Test knowledge base
        kb = KnowledgeBaseTool()
        result = kb.execute("capital of India")
        print(f"✅ Knowledge base test: capital of India = {result}")
        
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
                    print(f"✅ {prompt} prompt loaded ({len(prompts[prompt])} chars)")
                else:
                    print(f"❌ {prompt} prompt missing")
                    return False
            return True
        else:
            print("⚠️  Prompts file not found, using defaults")
            return True
            
    except Exception as e:
        print(f"❌ Prompts test failed: {e}")
        return False

def test_vram_manager():
    """Test VRAM manager"""
    print("\n🧪 Testing VRAM manager...")
    
    try:
        from core.vram_manager import VRAMManager, MemoryProfiler
        
        manager = VRAMManager()
        
        # Test memory stats
        stats = manager.get_memory_stats()
        print(f"✅ VRAM stats: {stats.total_gb:.1f}GB total")
        
        # Test flush
        flush_result = manager.flush()
        print(f"✅ Flush completed, freed: {flush_result['freed_gb']:.2f}GB")
        
        # Test optimization
        opt = manager.optimize_for_model(5.0)  # 5GB model
        print(f"✅ Optimization recommendation: {opt['recommended_gpu_layers']} GPU layers")
        
        return True
        
    except Exception as e:
        print(f"❌ VRAM manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dummy_orchestrator():
    """Test orchestrator initialization without models"""
    print("\n🧪 Testing orchestrator (dummy)...")
    
    try:
        from core.orchestrator import JugaadOrchestrator
        
        # Create dummy model config
        dummy_models = {
            "translator": "/tmp/dummy_translator.gguf",
            "reasoner": "/tmp/dummy_reasoner.gguf", 
            "critic": "/tmp/dummy_critic.gguf"
        }
        
        # Test initialization
        orch = JugaadOrchestrator(dummy_models)
        print("✅ Orchestrator initialized")
        
        # Test stats
        stats = orch.get_stats()
        print(f"✅ Stats: {stats['models_loaded']} models loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🎵 Ariv System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Model Paths", test_model_paths),
        ("Tools", test_tools),
        ("Prompts", test_prompts),
        ("VRAM Manager", test_vram_manager),
        ("Orchestrator", test_dummy_orchestrator),
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
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\n💡 Next steps:")
        print("   1. Download models: python models/download_models.py core")
        print("   2. Test with: python maha_system.py --status")
        print("   3. Run interactive: python maha_system.py --interactive --lang hindi")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
