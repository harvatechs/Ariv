#!/usr/bin/env python3
"""
Maha-System: The Indian AI Orchestra
Main entry point for the Translate-Reason-Verify pipeline
"""

import argparse
import logging
import yaml
from pathlib import Path
from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths, PIPELINE_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MahaSystem")

def load_prompts(prompts_file: str = "prompts/meta_prompts.yaml"):
    """Load meta-prompts from YAML"""
    try:
        with open(prompts_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Could not load prompts file: {e}. Using defaults.")
        return {}

def main():
    parser = argparse.ArgumentParser(
        description="Maha-System: Orchestrate Indian AI models for SOTA reasoning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hindi riddle solving
  python maha_system.py --query "एक रस्सी की दो टूकड़े, दोनों के दोनों रूखे" --lang hindi

  # Tamil math problem with critic disabled
  python maha_system.py --query "12 ஆப்பிள்கள் இருந்தால்..." --lang tamil --no-critic

  # Interactive mode
  python maha_system.py --interactive
        """
    )

    parser.add_argument("--query", "-q", help="Input query in vernacular language")
    parser.add_argument("--lang", "-l", default="hindi", 
                       choices=["hindi", "tamil", "telugu", "marathi", "bengali", "hinglish"],
                       help="Input language (default: hindi)")
    parser.add_argument("--no-critic", action="store_true",
                       help="Disable critic phase (faster but less accurate)")
    parser.add_argument("--reasoner", default="reasoner", 
                       choices=["reasoner", "bridge"],
                       help="Reasoning model to use (default: deepseek-r1)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Interactive mode for continuous queries")
    parser.add_argument("--show-trace", action="store_true",
                       help="Show full reasoning trace")

    args = parser.parse_args()

    # Initialize system
    logger.info("🚀 Initializing Maha-System...")
    model_paths = get_model_paths()
    prompts = load_prompts()

    # Check if models exist
    missing = [role for role, path in model_paths.items() if not Path(path).exists()]
    if missing:
        logger.error(f"❌ Missing models: {missing}")
        logger.info("Run: python models/download_models.py all")
        return

    # Initialize orchestrator and pipeline
    orchestrator = JugaadOrchestrator(model_paths)
    pipeline = TRVPipeline(orchestrator, prompts)

    try:
        if args.interactive:
            print("\n🎵 Maha-System Interactive Mode")
            print("Type 'exit' to quit, 'trace' to toggle reasoning display\n")
            show_trace = args.show_trace

            while True:
                try:
                    query = input(f"[{args.lang}]> ").strip()
                    if query.lower() == 'exit':
                        break
                    if query.lower() == 'trace':
                        show_trace = not show_trace
                        print(f"Trace display: {'ON' if show_trace else 'OFF'}")
                        continue
                    if not query:
                        continue

                    result = pipeline.execute(
                        query=query,
                        language=args.lang,
                        enable_critic=not args.no_critic,
                        reasoning_model=args.reasoner
                    )

                    print(f"\n📝 Answer: {result['final_answer']}")
                    if show_trace:
                        print(f"\n🔍 Reasoning Trace:")
                        for step in result['reasoning_trace']:
                            print(f"  {step['phase']}: {step['output'][:100]}...")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error: {e}")

        else:
            if not args.query:
                parser.error("--query required unless using --interactive")

            logger.info(f"📝 Processing query: {args.query}")
            result = pipeline.execute(
                query=args.query,
                language=args.lang,
                enable_critic=not args.no_critic,
                reasoning_model=args.reasoner
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
                    print(f"\nStep {i}: {step['phase'].upper()}")
                    print(f"{step['output']}")

    finally:
        orchestrator.unload_model()
        logger.info("👋 Maha-System shutdown complete")

if __name__ == "__main__":
    main()
