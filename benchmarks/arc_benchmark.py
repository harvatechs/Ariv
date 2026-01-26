#!/usr/bin/env python3
"""
ARC-AGI 2 Benchmark Runner for Ariv
Tests abstract reasoning capabilities
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ARC-Benchmark")

class ARCBenchmark:
    """ARC-AGI 2 Benchmark Runner"""
    
    def __init__(self, pipeline: TRVPipeline):
        self.pipeline = pipeline
        self.results = {
            "benchmark_name": "ARC-AGI 2",
            "timestamp": datetime.now().isoformat(),
            "system": "Ariv",
            "total_problems": 0,
            "solved": 0,
            "failed": 0,
            "timeout": 0,
            "total_time": 0.0,
            "problems": []
        }
        
    def load_problems(self, problem_file: str) -> List[Dict[str, Any]]:
        """Load ARC-AGI problems from file"""
        try:
            with open(problem_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("problems", [])
        except Exception as e:
            logger.error(f"Failed to load problems: {e}")
            return []
            
    def evaluate_problem(self, problem: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """Evaluate a single problem"""
        problem_id = problem.get("id", "unknown")
        query = problem.get("query", "")
        expected = problem.get("expected", "")
        language = problem.get("language", "english")
        problem_type = problem.get("type", "abstract")
        
        logger.info(f"🧪 Evaluating {problem_id}: {query[:50]}...")
        
        start_time = time.time()
        
        try:
            # Execute pipeline with ARC-AGI optimized settings
            result = self.pipeline.execute(
                query=query,
                language=language,
                enable_critic=True,
                enable_deep_cot=True,
                enable_self_consistency=True,
                reasoning_model="reasoner"
            )
            
            elapsed = time.time() - start_time
            
            # Check if solution is correct
            is_correct = self._check_solution(
                result["final_answer"], 
                expected, 
                problem_type
            )
            
            problem_result = {
                "id": problem_id,
                "query": query,
                "expected": expected,
                "generated": result["final_answer"],
                "language": language,
                "type": problem_type,
                "solved": is_correct,
                "time": elapsed,
                "critic_iterations": result["critic_iterations"],
                "trace": result["reasoning_trace"][:3]  # First 3 steps
            }
            
            if is_correct:
                logger.info(f"✅ {problem_id}: SOLVED in {elapsed:.1f}s")
                self.results["solved"] += 1
            else:
                logger.info(f"❌ {problem_id}: FAILED in {elapsed:.1f}s")
                self.results["failed"] += 1
                
            return problem_result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ {problem_id}: ERROR in {elapsed:.1f}s - {e}")
            self.results["failed"] += 1
            
            return {
                "id": problem_id,
                "query": query,
                "error": str(e),
                "solved": False,
                "time": elapsed
            }
            
    def evaluate(self, problem_file: str, max_problems: Optional[int] = None) -> Dict[str, Any]:
        """Evaluate all problems"""
        problems = self.load_problems(problem_file)
        
        if not problems:
            logger.error("No problems to evaluate")
            return self.results
            
        if max_problems:
            problems = problems[:max_problems]
            
        self.results["total_problems"] = len(problems)
        
        logger.info("=" * 60)
        logger.info(f"🧪 Starting ARC-AGI 2 Benchmark")
        logger.info(f"📊 Total problems: {len(problems)}")
        logger.info(f"🎯 Max problems: {max_problems or 'all'}")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        for i, problem in enumerate(problems, 1):
            logger.info("")
            logger.info(f"Problem {i}/{len(problems)}")
            logger.info("-" * 40)
            
            result = self.evaluate_problem(problem)
            self.results["problems"].append(result)
            
        total_time = time.time() - start_time
        self.results["total_time"] = total_time
        
        # Calculate summary statistics
        self.results["accuracy"] = self.results["solved"] / len(problems) if problems else 0
        self.results["average_time"] = total_time / len(problems) if problems else 0
        
        # Print summary
        self._print_summary()
        
        return self.results
        
    def _check_solution(self, generated: str, expected: str, problem_type: str) -> bool:
        """Check if solution is correct"""
        if not expected:
            return True  # No expected answer
            
        gen_normalized = generated.strip().lower()
        exp_normalized = expected.strip().lower()
        
        # Exact match
        if gen_normalized == exp_normalized:
            return True
            
        # Containment check
        if exp_normalized in gen_normalized or gen_normalized in exp_normalized:
            return True
            
        # For numerical answers, extract numbers
        if problem_type in ["numerical", "math"]:
            import re
            gen_numbers = re.findall(r'\d+(?:\.\d+)?', gen_normalized)
            exp_numbers = re.findall(r'\d+(?:\.\d+)?', exp_normalized)
            
            if gen_numbers and exp_numbers:
                return gen_numbers[0] == exp_numbers[0]
                
        return False
        
    def _print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 60)
        print("📊 ARC-AGI 2 BENCHMARK RESULTS")
        print("=" * 60)
        print(f"🎯 Accuracy: {self.results['accuracy']*100:.1f}% ({self.results['solved']}/{self.results['total_problems']})")
        print(f"⏱️  Total time: {self.results['total_time']:.1f}s")
        print(f"📈 Average time: {self.results['average_time']:.1f}s")
        print(f"✅ Solved: {self.results['solved']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏰ Timeout: {self.results['timeout']}")
        print("=" * 60)
        
    def save_results(self, output_file: str):
        """Save results to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def create_sample_problems():
    """Create sample ARC-AGI problems for testing"""
    problems = {
        "problems": [
            {
                "id": "pattern_001",
                "query": "What comes next in the sequence: 2, 4, 8, 16, ?",
                "expected": "32",
                "language": "english",
                "type": "numerical",
                "category": "pattern_recognition"
            },
            {
                "id": "logic_001", 
                "query": "All roses are flowers. Some flowers fade quickly. Therefore, some roses fade quickly. Is this reasoning correct?",
                "expected": "No, this reasoning is not necessarily correct",
                "language": "english",
                "type": "logical",
                "category": "syllogism"
            },
            {
                "id": "math_001",
                "query": "यदि एक ट्रेन 120 किमी दूरी 2 घंटे में तय करती है, तो इसकी औसत गति कितनी है?",
                "expected": "60 किमी प्रति घंटा",
                "language": "hindi",
                "type": "math",
                "category": "word_problem"
            },
            {
                "id": "tamil_001",
                "query": "12 ஆப்பிள்கள் உள்ளன, அவற்றில் 4 சாப்பிடப்பட்டன. எத்தனை ஆப்பிள்கள் மீதமுள்ளன?",
                "expected": "8 ஆப்பிள்கள்",
                "language": "tamil",
                "type": "math",
                "category": "subtraction"
            },
            {
                "id": "pattern_002",
                "query": "Find the next term: A, C, E, G, ?",
                "expected": "I",
                "language": "english",
                "type": "pattern",
                "category": "alphabet_sequence"
            },
            {
                "id": "spatial_001",
                "query": "If you rotate a square 90 degrees clockwise, what shape do you get?",
                "expected": "A square",
                "language": "english", 
                "type": "spatial",
                "category": "rotation"
            },
            {
                "id": "bengali_001",
                "query": "একটি আয়তক্ষেত্রের দৈর্ঘ্য 8 মিটার এবং প্রস্থ 5 মিটার। এর ক্ষেত্রফল কত?",
                "expected": "40 বর্গমিটার",
                "language": "bengali",
                "type": "math",
                "category": "area"
            }
        ]
    }
    
    return problems

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ARC-AGI 2 Benchmark for Ariv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run benchmark with sample problems
  python arc_benchmark.py --sample
  
  # Run benchmark with custom problems
  python arc_benchmark.py --problems my_problems.json
  
  # Run limited number of problems
  python arc_benchmark.py --problems problems.json --max 10
  
  # Create sample problems file
  python arc_benchmark.py --create-sample
        """
    )
    
    parser.add_argument("--problems", help="JSON file containing problems")
    parser.add_argument("--sample", action="store_true", help="Use sample problems")
    parser.add_argument("--max", type=int, help="Maximum number of problems to run")
    parser.add_argument("--create-sample", action="store_true", help="Create sample problems file")
    parser.add_argument("--output", default="arc_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Handle create sample
    if args.create_sample:
        problems = create_sample_problems()
        with open("sample_problems.json", 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        print("✅ Sample problems created: sample_problems.json")
        return
    
    # Determine problem file
    problem_file = None
    if args.sample:
        problems = create_sample_problems()
        # Save temporarily
        with open("temp_problems.json", 'w', encoding='utf-8') as f:
            json.dump(problems, f, ensure_ascii=False, indent=2)
        problem_file = "temp_problems.json"
    elif args.problems:
        problem_file = args.problems
    else:
        print("❌ Please specify --problems, --sample, or --create-sample")
        return
    
    # Check if file exists
    if not Path(problem_file).exists():
        print(f"❌ Problem file not found: {problem_file}")
        return
    
    # Initialize system
    print("🚀 Initializing Ariv system...")
    try:
        model_paths = get_model_paths()
        orchestrator = JugaadOrchestrator(model_paths)
        
        # Load prompts
        prompts_file = Path(__file__).parent.parent / "prompts" / "meta_prompts.yaml"
        if prompts_file.exists():
            import yaml
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = yaml.safe_load(f)
        else:
            prompts = {}
            
        pipeline = TRVPipeline(orchestrator, prompts)
        print("✅ System initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return
    
    # Run benchmark
    try:
        benchmark = ARCBenchmark(pipeline)
        results = benchmark.evaluate(problem_file, max_problems=args.max)
        benchmark.save_results(args.output)
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        
    finally:
        # Cleanup temp file
        if args.sample and Path("temp_problems.json").exists():
            Path("temp_problems.json").unlink()

if __name__ == "__main__":
    main()
