"""
AURA-Code Developer CLI.
Terminal utility for instant Agentic Code Intelligence, Structural Search,
and Optimization Analysis.
"""

import sys
import os
import argparse
import json

from engine.agent_controller import AgenticCodeNavigator
from engine.benchmark import BenchmarkHarness
from engine.codepath_optimizer import CodePathOptimizer


def print_banner():
    banner = r"""
   █████╗ ██╗   ██╗██████╗  █████╗       ██████╗ ██████╗ ██████╗ ███████╗
  ██╔══██╗██║   ██║██╔══██╗██╔══██╗     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ███████║██║   ██║██████╔╝███████║     ██║     ██║   ██║██║  ██║█████╗  
  ██╔══██║██║   ██║██╔══██╗██╔══██║     ██║     ██║   ██║██║  ██║██╔══╝  
  ██║  ██║╚██████╔╝██║  ██║██║  ██║     ╚██████╗╚██████╔╝██████╔╝███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
  Agentic Code Intelligence & AST-Graph Engine (Samsung PRISM Hackathon 3.0)
    """
    print(banner)


def main():
    parser = argparse.ArgumentParser(description="AURA-Code Terminal Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Search Command
    search_parser = subparsers.add_parser("search", help="Execute agentic code search")
    search_parser.add_argument("query", type=str, help="Natural language or structural sequence query")
    search_parser.add_argument("--codebase", type=str, default="sample_voice_assistant", help="Path to codebase")

    # Benchmark Command
    bench_parser = subparsers.add_parser("benchmark", help="Run full evaluation harness")
    bench_parser.add_argument("--codebase", type=str, default="sample_voice_assistant", help="Path to codebase")

    # Optimize Command
    opt_parser = subparsers.add_parser("optimize", help="Analyze code file for async waterfalls and anti-patterns")
    opt_parser.add_argument("file", type=str, help="Path to JavaScript file to optimize")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.command == "search":
        codebase_path = os.path.join(base_dir, args.codebase)
        nav = AgenticCodeNavigator(codebase_path)
        nav.index_codebase()

        print_banner()
        print(f"[*] Query: \"{args.query}\"\n")
        res = nav.query(args.query)

        print(f"[+] Query Intent: {res['query_type']} (Resolved in {res['latency_ms']}ms on CPU)")
        print("\n--- AGENTIC REASONING PLAN ---")
        for step in res["plan_steps"]:
            print(f"  Step {step['step']}: {step['action']}")
            print(f"         Observation: {step['observation']}")

        print(f"\n--- MATCHED LOCATIONS ({len(res['matches'])} found) ---")
        for idx, m in enumerate(res["matches"], start=1):
            print(f"\n[{idx}] File: {m['file']} | Lines {m['line_start']}-{m['line_end']} (Score: {m['confidence']})")
            print(f"    Function Context: {m.get('function', 'N/A')}")
            print("    " + "-" * 50)
            for line in m["snippet"].splitlines()[:6]:
                print(f"    | {line}")
            if len(m["snippet"].splitlines()) > 6:
                print("    | ...")

        if res.get("optimizations"):
            print(f"\n--- BONUS CODEPATH OPTIMIZATIONS ({len(res['optimizations'])} detected) ---")
            for opt in res["optimizations"]:
                print(f"\n[!] [{opt['severity']}] {opt['title']}")
                print(f"    Impact: {opt['estimated_impact']}")
                print("    Suggested Fix:")
                for l in opt["optimized_code"].splitlines():
                    print(f"    + {l}")

    elif args.command == "benchmark":
        codebase_path = os.path.join(base_dir, args.codebase)
        print_banner()
        harness = BenchmarkHarness(codebase_path)
        harness.run_full_benchmark()

    elif args.command == "optimize":
        target_file = os.path.abspath(args.file)
        if not os.path.exists(target_file):
            target_file = os.path.join(base_dir, args.file)
        
        if not os.path.exists(target_file):
            print(f"Error: File not found: {args.file}")
            return

        with open(target_file, 'r', encoding='utf-8') as f:
            code = f.read()

        optimizer = CodePathOptimizer()
        opts = optimizer.analyze_snippet(target_file, code)

        print_banner()
        print(f"[*] Analyzing '{os.path.relpath(target_file, base_dir)}' for Voice Assistant Anti-Patterns...")
        if not opts:
            print("[+] No anti-patterns detected. Clean execution path!")
        else:
            print(f"[!] Discovered {len(opts)} optimization opportunity(ies):\n")
            for o in opts:
                print(f"------------------------------------------------------------")
                print(f"Severity: {o['severity']} | Category: {o['category']}")
                print(f"Title:    {o['title']}")
                print(f"Impact:   {o['estimated_impact']}")
                print(f"\nOriginal Code:\n{o['original_code']}")
                print(f"\nOptimized Proposal:\n{o['optimized_code']}")


if __name__ == '__main__':
    main()
