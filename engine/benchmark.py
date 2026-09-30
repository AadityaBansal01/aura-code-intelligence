"""
Automated Benchmarking & Evaluation Suite for AURA-Code.
Evaluates Precision@k, Recall, Latency, and Indexing Cost across
Structural, Usage, and Semantic test suites.
Generates JSON and Markdown outputs for the competition presentation and reports.
"""

import os
import time
import json
import statistics
from typing import Dict, List, Any
from engine.agent_controller import AgenticCodeNavigator


BENCHMARK_GROUND_TRUTH = [
    # 1. Structural Queries (AST Sequence & Call Flow)
    {
        "id": "SEQ-01",
        "category": "Structural Sequence",
        "query": "which files call tool requestPermissions before tool launchDeeplink?",
        "expected_files": ["agents/navigation_agent.js", "agents/settings_agent.js"]
    },
    {
        "id": "SEQ-02",
        "category": "Structural Sequence",
        "query": "where is checkConnectivity called before fetchEndpoint?",
        "expected_files": ["agents/smarthome_agent.js"]
    },
    {
        "id": "SEQ-03",
        "category": "Structural Sequence",
        "query": "which files invoke checkPermissions before requestPermissions?",
        "expected_files": ["agents/settings_agent.js", "agents/navigation_agent.js"]
    },
    {
        "id": "SEQ-04",
        "category": "Structural Sequence",
        "query": "where does the code call duckAudioStream before any playback?",
        "expected_files": ["agents/media_agent.js"]
    },
    {
        "id": "SEQ-05",
        "category": "Structural Sequence",
        "query": "which agents call scanNearbyDevices before pairDevice?",
        "expected_files": ["agents/settings_agent.js"]
    },

    # 2. Usage & Deeplink Queries
    {
        "id": "USE-01",
        "category": "Usage & Deeplink",
        "query": "where is the Bluetooth-settings deeplink used?",
        "expected_files": ["config/deeplinks.js", "agents/settings_agent.js", "tools/device_tool.js"]
    },
    {
        "id": "USE-02",
        "category": "Usage & Deeplink",
        "query": "find references to NAVIGATION_NAVIGATE_HOME deeplink",
        "expected_files": ["config/deeplinks.js", "agents/navigation_agent.js"]
    },
    {
        "id": "USE-03",
        "category": "Usage & Deeplink",
        "query": "where is BATTERY_SAVER_SETTINGS deeplink referenced?",
        "expected_files": ["config/deeplinks.js", "agents/system_agent.js"]
    },
    {
        "id": "USE-04",
        "category": "Usage & Deeplink",
        "query": "where is launchDeeplink method defined?",
        "expected_files": ["tools/device_tool.js"]
    },
    {
        "id": "USE-05",
        "category": "Usage & Deeplink",
        "query": "find usage of BLUETOOTH_PAIRING_DIALOG deeplink",
        "expected_files": ["config/deeplinks.js", "agents/settings_agent.js"]
    },

    # 3. Conceptual & Natural Language Queries
    {
        "id": "SEM-01",
        "category": "Conceptual Semantic",
        "query": "where does the assistant handle media playback interruptions?",
        "expected_files": ["agents/media_agent.js", "tools/audio_tool.js"]
    },
    {
        "id": "SEM-02",
        "category": "Conceptual Semantic",
        "query": "how are smart lights toggled in IoT devices?",
        "expected_files": ["agents/smarthome_agent.js"]
    },
    {
        "id": "SEM-03",
        "category": "Conceptual Semantic",
        "query": "where is speech recognition timeout configured?",
        "expected_files": ["config/constants.js"]
    },
    {
        "id": "SEM-04",
        "category": "Conceptual Semantic",
        "query": "how does the system optimize battery consumption when low?",
        "expected_files": ["agents/system_agent.js"]
    },
    {
        "id": "SEM-05",
        "category": "Conceptual Semantic",
        "query": "where are incoming voice speech intents routed to agents?",
        "expected_files": ["agents/voice_dispatcher.js"]
    }
]


class BenchmarkHarness:
    def __init__(self, codebase_path: str):
        self.navigator = AgenticCodeNavigator(codebase_path)

    def run_full_benchmark(self) -> Dict[str, Any]:
        print("[Benchmark] Starting full evaluation suite...")
        
        # 1. Measure Indexing Metrics
        index_metrics = self.navigator.index_codebase()

        latencies_ms = []
        p_at_1_scores = []
        p_at_3_scores = []
        p_at_5_scores = []
        recall_scores = []
        category_breakdown = {}

        detailed_results = []

        # 2. Execute Test Cases
        for tc in BENCHMARK_GROUND_TRUTH:
            t0 = time.perf_counter()
            response = self.navigator.query(tc["query"])
            latency = round((time.perf_counter() - t0) * 1000, 2)
            latencies_ms.append(latency)

            retrieved_files = [m["file"] for m in response.get("matches", [])]
            expected = set(tc["expected_files"])

            # Compute Precision@1
            top_1 = retrieved_files[:1]
            p1 = 1.0 if any(f in expected for f in top_1) else 0.0
            p_at_1_scores.append(p1)

            # Compute Precision@3
            top_3 = retrieved_files[:3]
            hits_3 = sum(1 for f in top_3 if f in expected)
            p3 = hits_3 / min(len(top_3), 3) if top_3 else 0.0
            p_at_3_scores.append(p3)

            # Compute Precision@5
            top_5 = retrieved_files[:5]
            hits_5 = sum(1 for f in top_5 if f in expected)
            p5 = hits_5 / min(len(top_5), 5) if top_5 else 0.0
            p_at_5_scores.append(p5)

            # Compute Recall
            retrieved_set = set(retrieved_files)
            found_expected = expected.intersection(retrieved_set)
            rec = len(found_expected) / len(expected) if expected else 1.0
            recall_scores.append(rec)

            cat = tc["category"]
            if cat not in category_breakdown:
                category_breakdown[cat] = {"p1": [], "rec": [], "lat": []}
            category_breakdown[cat]["p1"].append(p1)
            category_breakdown[cat]["rec"].append(rec)
            category_breakdown[cat]["lat"].append(latency)

            detailed_results.append({
                "id": tc["id"],
                "category": cat,
                "query": tc["query"],
                "expected": list(expected),
                "retrieved": retrieved_files[:3],
                "p@1": p1,
                "recall": round(rec, 2),
                "latency_ms": latency
            })

        latencies_ms.sort()
        p95_idx = int(len(latencies_ms) * 0.95)
        p95_latency = latencies_ms[p95_idx] if latencies_ms else 0.0

        summary = {
            "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_queries_tested": len(BENCHMARK_GROUND_TRUTH),
            "metrics": {
                "precision_at_1": round(statistics.mean(p_at_1_scores) * 100, 2),
                "precision_at_3": round(statistics.mean(p_at_3_scores) * 100, 2),
                "precision_at_5": round(statistics.mean(p_at_5_scores) * 100, 2),
                "mean_recall": round(statistics.mean(recall_scores) * 100, 2),
                "mean_latency_ms": round(statistics.mean(latencies_ms), 2),
                "median_latency_ms": round(statistics.median(latencies_ms), 2),
                "p95_latency_ms": round(p95_latency, 2)
            },
            "indexing_cost": {
                "indexing_time_ms": index_metrics["indexing_time_ms"],
                "graph_nodes": index_metrics["nodes_indexed"],
                "graph_edges": index_metrics["edges_indexed"],
                "code_chunks": index_metrics["chunks_indexed"],
                "hardware_platform": "CPU (Zero GPU required)"
            },
            "category_metrics": {
                cat: {
                    "precision_at_1": round(statistics.mean(data["p1"]) * 100, 2),
                    "mean_recall": round(statistics.mean(data["rec"]) * 100, 2),
                    "mean_latency_ms": round(statistics.mean(data["lat"]), 2)
                }
                for cat, data in category_breakdown.items()
            },
            "test_cases": detailed_results
        }

        # Save to benchmark_results.json
        output_dir = os.path.dirname(__file__)
        json_path = os.path.join(output_dir, "benchmark_results.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"\n[Benchmark] Completed. Saved results to {json_path}")
        self._print_markdown_table(summary)
        return summary

    def _print_markdown_table(self, summary: Dict[str, Any]):
        m = summary["metrics"]
        ic = summary["indexing_cost"]
        print("\n" + "=" * 60)
        print("          AURA-Code OFFICIAL BENCHMARK REPORT          ")
        print("=" * 60)
        print(f"| Metric                      | Result                 |")
        print(f"|-----------------------------|------------------------|")
        print(f"| Precision@1                 | {m['precision_at_1']}%                 |")
        print(f"| Precision@3                 | {m['precision_at_3']}%                 |")
        print(f"| Precision@5                 | {m['precision_at_5']}%                 |")
        print(f"| Mean Recall                 | {m['mean_recall']}%                 |")
        print(f"| Mean Latency (CPU)          | {m['mean_latency_ms']} ms               |")
        print(f"| P95 Latency (CPU)           | {m['p95_latency_ms']} ms               |")
        print(f"| Cold Indexing Time          | {ic['indexing_time_ms']} ms               |")
        print(f"| Hardware Resource           | {ic['hardware_platform']} |")
        print("=" * 60)


if __name__ == '__main__':
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sample_voice_assistant'))
    harness = BenchmarkHarness(sample_dir)
    harness.run_full_benchmark()
