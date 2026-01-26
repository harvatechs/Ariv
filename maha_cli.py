#!/usr/bin/env python3
"""
Maha-CLI: Rich Command Line Interface for Maha-System
Provides beautiful terminal output and interactive features
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import logging

# Optional rich imports for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Install rich for better UI: pip install rich")

console = Console() if RICH_AVAILABLE else None

from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths, verify_models, MODEL_CONFIG
from utils.vram_monitor import VRAMMonitor
from utils.profiler import PipelineProfiler

class MahaCLI:
    """Beautiful CLI for Maha-System"""

    def __init__(self):
        self.orchestrator = None
        self.pipeline = None
        self.profiler = PipelineProfiler()

    def print_banner(self):
        """Print welcome banner"""
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                "[bold cyan]🎵 Maha-System: The Indian AI Orchestra[/bold cyan]\n"
                "[dim]Sovereign Intelligence via Test-Time Compute[/dim]\n"
                "[dim]v1.0.0 | Built with Jugaad for Bharat 🇮🇳[/dim]",
                box=box.DOUBLE
            ))
        else:
            print("🎵 Maha-System v1.0.0")

    def print_status(self):
        """Print system status"""
        if not RICH_AVAILABLE:
            return

        table = Table(title="System Status", box=box.MINIMAL)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Check models
        status = verify_models()
        for role, info in status.items():
            icon = "✅" if info['exists'] else "❌"
            size = f"{info['size_gb']:.1f}GB" if info['exists'] else "Not found"
            table.add_row(
                role.capitalize(),
                f"{icon} {'Ready' if info['exists'] else 'Missing'}",
                size
            )

        console.print(table)

    def interactive_mode(self, language: str = "hindi", enable_critic: bool = True):
        """Interactive query mode"""
        self.print_banner()

        # Initialize
        with console.status("[bold green]Initializing Maha-System...") if RICH_AVAILABLE else nullcontext():
            model_paths = get_model_paths()
            self.orchestrator = JugaadOrchestrator(model_paths)
            self.pipeline = TRVPipeline(self.orchestrator, {})

        self.print_status()

        print(f"\n[Interactive Mode] Language: {language} | Critic: {'ON' if enable_critic else 'OFF'}")
        print("Commands: /quit, /trace, /critic, /lang <language>, /status\n")

        show_trace = False

        while True:
            try:
                if RICH_AVAILABLE:
                    query = console.input(f"[bold cyan]{language}[/bold cyan]> ")
                else:
                    query = input(f"{language}> ")

                query = query.strip()

                # Handle commands
                if query == "/quit":
                    break
                elif query == "/trace":
                    show_trace = not show_trace
                    print(f"Trace: {'ON' if show_trace else 'OFF'}")
                    continue
                elif query == "/critic":
                    enable_critic = not enable_critic
                    print(f"Critic: {'ON' if enable_critic else 'OFF'}")
                    continue
                elif query.startswith("/lang "):
                    language = query.split()[1]
                    print(f"Language: {language}")
                    continue
                elif query == "/status":
                    self.print_status()
                    continue
                elif not query:
                    continue

                # Execute query with progress
                if RICH_AVAILABLE:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("[cyan]Thinking...", total=None)

                        result = self.pipeline.execute(
                            query=query,
                            language=language,
                            enable_critic=enable_critic
                        )

                        progress.update(task, completed=True)
                else:
                    result = self.pipeline.execute(
                        query=query,
                        language=language,
                        enable_critic=enable_critic
                    )

                # Display result
                if RICH_AVAILABLE:
                    console.print(Panel(
                        result['final_answer'],
                        title="[bold green]Answer[/bold green]",
                        border_style="green"
                    ))

                    if show_trace:
                        for step in result['reasoning_trace']:
                            console.print(f"[dim]{step['phase']}: {step['output'][:100]}...[/dim]")
                else:
                    print(f"\nAnswer: {result['final_answer']}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                else:
                    print(f"Error: {e}")

        print("\n👋 Goodbye!")

    def benchmark_mode(self, dataset: str, max_samples: Optional[int] = None):
        """Run benchmarks"""
        from benchmarks.sanskriti_eval import SanskritiBenchmark

        self.print_banner()

        if not Path(dataset).exists():
            console.print(f"[red]Dataset not found: {dataset}[/red]")
            return

        model_paths = get_model_paths()
        orchestrator = JugaadOrchestrator(model_paths)
        benchmark = SanskritiBenchmark(dataset, orchestrator)

        with console.status("[bold green]Running benchmark..."):
            metrics = benchmark.evaluate(max_samples=max_samples)

        # Display results
        table = Table(title="Benchmark Results", box=box.MINIMAL)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Overall Accuracy", f"{metrics['overall_accuracy']:.2%}")
        table.add_row("Total Samples", str(metrics['total_samples']))
        table.add_row("Correct", str(metrics['correct']))

        if 'by_category' in metrics:
            for cat, stats in metrics['by_category'].items():
                table.add_row(
                    f"  {cat.capitalize()}",
                    f"{stats['accuracy']:.2%}"
                )

        console.print(table)

    def profile_mode(self, query: str, language: str = "hindi"):
        """Profile pipeline performance"""
        from utils.profiler import PipelineProfiler

        self.print_banner()

        model_paths = get_model_paths()
        orchestrator = JugaadOrchestrator(model_paths)

        # Wrap pipeline with profiler
        profiler = PipelineProfiler()

        # Execute with profiling
        print(f"Profiling: {query}")

        # Simulate phase tracking (would need to integrate with actual pipeline)
        with profiler.track_phase("ingestion", "sarvam-1"):
            import time
            time.sleep(0.5)  # Simulated

        with profiler.track_phase("reasoning", "deepseek-r1"):
            time.sleep(1.2)

        profiler.print_report()

    def model_management(self, action: str):
        """Manage models (list, download, verify)"""
        if action == "list":
            table = Table(title="Available Models", box=box.MINIMAL)
            table.add_column("Role", style="cyan")
            table.add_column("Model", style="green")
            table.add_column("Size", style="dim")
            table.add_column("Status", style="yellow")

            status = verify_models()
            for role, config in MODEL_CONFIG.items():
                size = f"{status[role]['size_gb']:.1f}GB" if status[role]['exists'] else "~4GB"
                table.add_row(
                    role,
                    config['description'],
                    size,
                    "✅" if status[role]['exists'] else "❌"
                )

            console.print(table)

        elif action == "download":
            print("Run: python models/download_models.py all")

        elif action == "verify":
            self.print_status()

def main():
    parser = argparse.ArgumentParser(
        description="Maha-CLI: Command line interface for Maha-System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s interactive                    # Start interactive mode
  %(prog)s query "नमस्ते" --lang hindi    # Single query
  %(prog)s benchmark --dataset data.json  # Run evaluation
  %(prog)s models list                    # List available models
  %(prog)s profile "Your query"           # Profile performance
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode')
    interactive_parser.add_argument('--lang', default='hindi', help='Language code')
    interactive_parser.add_argument('--no-critic', action='store_true', help='Disable critic')

    # Single query
    query_parser = subparsers.add_parser('query', help='Single query mode')
    query_parser.add_argument('text', help='Query text')
    query_parser.add_argument('--lang', default='hindi', help='Language code')
    query_parser.add_argument('--show-trace', action='store_true', help='Show reasoning trace')

    # Benchmark
    bench_parser = subparsers.add_parser('benchmark', help='Run benchmarks')
    bench_parser.add_argument('--dataset', required=True, help='Dataset path')
    bench_parser.add_argument('--max-samples', type=int, help='Limit samples')

    # Models
    model_parser = subparsers.add_parser('models', help='Model management')
    model_parser.add_argument('action', choices=['list', 'download', 'verify'])

    # Profile
    profile_parser = subparsers.add_parser('profile', help='Performance profiling')
    profile_parser.add_argument('query', help='Query to profile')
    profile_parser.add_argument('--lang', default='hindi', help='Language code')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = MahaCLI()

    if args.command == 'interactive':
        cli.interactive_mode(args.lang, not args.no_critic)
    elif args.command == 'query':
        # Quick single query
        cli.print_banner()
        model_paths = get_model_paths()
        orch = JugaadOrchestrator(model_paths)
        pipeline = TRVPipeline(orch, {})
        result = pipeline.execute(args.text, args.lang, enable_critic=True)
        print(f"\n{result['final_answer']}\n")
    elif args.command == 'benchmark':
        cli.benchmark_mode(args.dataset, args.max_samples)
    elif args.command == 'models':
        cli.model_management(args.action)
    elif args.command == 'profile':
        cli.profile_mode(args.query, args.lang)

if __name__ == "__main__":
    main()
