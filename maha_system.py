#!/usr/bin/env python3
"""
Ariv: The Indian AI Orchestra - Production Ready
Main entry point for the Translate-Reason-Verify pipeline
Supports all 22 official Indian languages with advanced chain-of-thought reasoning
"""

import argparse
import logging
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths, PIPELINE_CONFIG, get_supported_languages

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ariv")

def load_prompts(prompts_file: str = "prompts/meta_prompts.yaml") -> Dict[str, str]:
    """Load meta-prompts from YAML"""
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Could not load prompts file: {e}. Using defaults.")
        return {}

def check_models(model_paths: Dict[str, str]) -> Dict[str, bool]:
    """Check which models are available"""
    status = {}
    for role, path in model_paths.items():
        model_path = Path(path)
        exists = model_path.exists()
        if exists:
            size_mb = model_path.stat().st_size / (1024 * 1024)
            status[role] = {"exists": True, "size_mb": size_mb, "path": str(model_path)}
        else:
            status[role] = {"exists": False, "path": str(model_path)}
    return status

def print_model_status(status: Dict[str, Dict[str, Any]]):
    """Print model status in a formatted way"""
    print("\n" + "=" * 60)
    print("📊 MODEL STATUS")
    print("=" * 60)
    
    available_count = 0
    total_count = len(status)
    
    for role, info in status.items():
        if info["exists"]:
            print(f"✅ {role:20s} {info['size_mb']:8.1f}MB  {info['path']}")
            available_count += 1
        else:
            print(f"❌ {role:20s}    MISSING   {info['path']}")
            
    print("-" * 60)
    print(f"📊 Available: {available_count}/{total_count} models")
    
    if available_count < total_count:
        print("\n💡 To download missing models, run:")
        print("   python models/download_models.py all")
        
    print("=" * 60)

def interactive_mode(pipeline: TRVPipeline, language: str = "hindi", show_trace: bool = False):
    """Run interactive mode"""
    print("\n" + "=" * 60)
    print("🎵 Ariv: The Indian AI Orchestra - Interactive Mode")
    print("=" * 60)
    print("Supports all 22 official Indian languages")
    print("Type 'exit' to quit, 'trace' to toggle reasoning display")
    print("Type 'lang <language>' to change language")
    print("Type 'stats' to see pipeline statistics")
    print("=" * 60)
    
    supported_langs = get_supported_languages()
    
    while True:
        try:
            prompt = f"[{language}]> "
            query = input(prompt).strip()
            
            if query.lower() == 'exit':
                break
            elif query.lower() == 'trace':
                show_trace = not show_trace
                print(f"Trace display: {'ON' if show_trace else 'OFF'}")
                continue
            elif query.lower().startswith('lang '):
                new_lang = query[5:].strip()
                if new_lang in supported_langs:
                    language = new_lang
                    print(f"Language changed to: {language}")
                else:
                    print(f"Unsupported language. Available: {', '.join(supported_langs[:10])}...")
                continue
            elif query.lower() == 'stats':
                stats = pipeline.get_stats()
                print(f"\n📊 Pipeline Statistics:")
                print(f"   Queries processed: {stats['queries_processed']}")
                print(f"   Average time: {stats['average_query_time']:.2f}s")
                print(f"   Language distribution: {stats['language_distribution']}")
                continue
            elif not query:
                continue

            print("\n🔄 Processing...")
            
            # Execute pipeline
            result = pipeline.execute(
                query=query,
                language=language,
                enable_critic=True,
                enable_deep_cot=True,
                enable_self_consistency=True
            )

            print(f"\n📝 Answer ({language}):")
            print(f"{result['final_answer']}")
            
            if show_trace:
                print(f"\n🔍 Reasoning Trace:")
                for i, step in enumerate(result['reasoning_trace'], 1):
                    phase = step['phase']
                    output = step['output']
                    print(f"  {i}. {phase.upper()}: {output[:150]}{'...' if len(output) > 150 else ''}")
                    
            print(f"\n⏱️  Time: {result['pipeline_time']:.2f}s | Iterations: {result['critic_iterations']}")
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ Error: {e}")

def batch_mode(pipeline: TRVPipeline, input_file: str, output_file: str, language: str):
    """Process queries from file in batch mode"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip()]
            
        results = []
        
        print(f"🔄 Processing {len(queries)} queries...")
        
        for i, query in enumerate(queries, 1):
            print(f"Query {i}/{len(queries)}: {query[:50]}...")
            
            result = pipeline.execute(
                query=query,
                language=language,
                enable_critic=True,
                enable_deep_cot=True
            )
            
            results.append({
                "query": query,
                "result": result
            })
            
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Batch mode failed: {e}")
        print(f"❌ Batch mode failed: {e}")

def benchmark_mode(pipeline: TRVPipeline, benchmark_file: str):
    """Run benchmark mode"""
    try:
        with open(benchmark_file, 'r', encoding='utf-8') as f:
            benchmark_data = json.load(f)
            
        problems = benchmark_data.get("problems", [])
        
        if not problems:
            print("❌ No problems found in benchmark file")
            return
            
        print(f"🧪 Running benchmark with {len(problems)} problems...")
        
        results = pipeline.benchmark_arc_agi_2(problems)
        
        # Save benchmark results
        output_file = benchmark_file.replace('.json', '_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Benchmark results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Benchmark mode failed: {e}")
        print(f"❌ Benchmark mode failed: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Ariv: The Indian AI Orchestra - Production Ready",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎵 Ariv: Orchestrating India's AI models for state-of-the-art reasoning

Examples:
  # Interactive mode (Hindi)
  python maha_system.py --interactive --lang hindi
  
  # Single query (Tamil)
  python maha_system.py --query "12 ஆப்பிள்கள் இருந்தால்..." --lang tamil
  
  # Batch processing
  python maha_system.py --batch input.txt --output results.json --lang bengali
  
  # Benchmark mode
  python maha_system.py --benchmark arc_agi_problems.json
  
  # With reasoning trace
  python maha_system.py --query "एक रस्सी की दो टुकड़े..." --lang hindi --show-trace
  
  # Quick model status check
  python maha_system.py --status

Supported Languages (22 official Indian languages):
  assamese, bengali, bodo, dogri, english, gujarati, hindi, kannada,
  kashmiri, konkani, maithili, malayalam, manipuri, marathi, nepali,
  odia, punjabi, sanskrit, santali, sindhi, tamil, telugu, urdu, hinglish
        """
    )

    # Input options
    parser.add_argument("--query", "-q", help="Input query in vernacular language")
    parser.add_argument("--lang", "-l", default="hindi", 
                       choices=get_supported_languages(),
                       help="Input language (default: hindi)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Interactive mode for continuous queries")
    parser.add_argument("--batch", help="Input file for batch processing")
    parser.add_argument("--output", help="Output file for batch results")
    parser.add_argument("--benchmark", help="Run benchmark with given problem file")

    # Pipeline options
    parser.add_argument("--no-critic", action="store_true",
                       help="Disable critic phase (faster but less accurate)")
    parser.add_argument("--reasoner", default="reasoner", 
                       choices=["reasoner", "bridge"],
                       help="Reasoning model to use (default: deepseek-r1)")
    parser.add_argument("--show-trace", action="store_true",
                       help="Show full reasoning trace")
    parser.add_argument("--no-deep-cot", action="store_true",
                       help="Disable deep chain-of-thought (faster)")
    parser.add_argument("--no-self-consistency", action="store_true",
                       help="Disable self-consistency voting (faster)")

    # System options
    parser.add_argument("--status", action="store_true",
                       help="Show model status and exit")
    parser.add_argument("--prompts", default="prompts/meta_prompts.yaml",
                       help="Path to prompts configuration file")
    parser.add_argument("--models-dir", default="models",
                       help="Directory containing model files")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")

    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Get model paths
    model_paths = get_model_paths()
    
    # Update model paths to use specified models directory
    if args.models_dir != "models":
        for role, path in model_paths.items():
            model_paths[role] = path.replace("models/", f"{args.models_dir}/")
    
    # Check model status
    status = check_models(model_paths)
    
    if args.status:
        print_model_status(status)
        return
        
    # Check if required models are available
    available_models = sum(1 for info in status.values() if info["exists"])
    if available_models == 0:
        print("\n❌ No models found!")
        print("\n💡 To download models, run:")
        print("   python models/download_models.py all")
        sys.exit(1)
    elif available_models < len(status):
        print(f"\n⚠️  Only {available_models}/{len(status)} models available")
        print("Some features may be limited.")
        print("\n💡 To download missing models, run:")
        print("   python models/download_models.py all")

    # Initialize system
    logger.info("🚀 Initializing Ariv System...")
    
    try:
        orchestrator = JugaadOrchestrator(model_paths, enable_tools=True)
        prompts = load_prompts(args.prompts)
        pipeline = TRVPipeline(orchestrator, prompts)
        
        logger.info("✅ Ariv system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        print(f"\n❌ Initialization failed: {e}")
        print("\n💡 Make sure models are downloaded:")
        print("   python models/download_models.py core")
        sys.exit(1)

    try:
        # Interactive mode
        if args.interactive:
            interactive_mode(pipeline, args.lang, args.show_trace)
            
        # Batch mode
        elif args.batch:
            if not args.output:
                print("❌ --output required for batch mode")
                sys.exit(1)
            batch_mode(pipeline, args.batch, args.output, args.lang)
            
        # Benchmark mode
        elif args.benchmark:
            benchmark_mode(pipeline, args.benchmark)
            
        # Single query mode
        else:
            if not args.query:
                parser.error("--query required unless using --interactive, --batch, or --benchmark")

            logger.info(f"📝 Processing query: {args.query}")
            
            result = pipeline.execute(
                query=args.query,
                language=args.lang,
                enable_critic=not args.no_critic,
                reasoning_model=args.reasoner,
                enable_deep_cot=not args.no_deep_cot,
                enable_self_consistency=not args.no_self_consistency
            )

            print(f"\n{'='*60}")
            print(f"🎯 FINAL ANSWER ({args.lang}):")
            print(f"{'='*60}")
            print(result['final_answer'])

            if args.show_trace:
                print(f"\n{'='*60}")
                print("🔍 REASONING TRACE:")
                print(f"{'='*60}")
                for i, step in enumerate(result['reasoning_trace'], 1):
                    phase = step['phase']
                    output = step['output']
                    print(f"\nStep {i}: {phase.upper()}")
                    print(f"{output}")

            print(f"\n⏱️  Pipeline time: {result['pipeline_time']:.2f}s")
            print(f"🔄 Critic iterations: {result['critic_iterations']}")

    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        logger.error(f"Runtime error: {e}")
        print(f"\n❌ Runtime error: {e}")
    finally:
        if 'orchestrator' in locals():
            orchestrator.unload_model()
        logger.info("👋 Ariv system shutdown complete")

if __name__ == "__main__":
    import sys
    main()
