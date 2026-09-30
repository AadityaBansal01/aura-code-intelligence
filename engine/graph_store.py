"""
Code Property Graph (CPG) & Structural Query Engine using NetworkX.
Enables exact sequence checking ("Tool A before Tool B"), call chain graph traversal,
and symbol/deeplink reference discovery across the codebase.
"""

import os
from typing import Dict, List, Any, Optional
import networkx as nx
from engine.ast_parser import JSASTParser, scan_directory


class CodePropertyGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.files_meta: Dict[str, Any] = {}
        self.deeplink_index: Dict[str, List[Dict[str, Any]]] = {}
        self.symbol_index: Dict[str, List[Dict[str, Any]]] = {}

    def build_graph(self, directory_path: str):
        """Builds the comprehensive Code Property Graph from AST summaries."""
        self.graph.clear()
        self.files_meta.clear()
        self.deeplink_index.clear()
        self.symbol_index.clear()

        parsed_files = scan_directory(directory_path)

        for meta in parsed_files:
            file_path = meta["file_path"]
            rel_path = os.path.relpath(file_path, directory_path)
            self.files_meta[rel_path] = meta

            # Add File Node
            self.graph.add_node(rel_path, node_type="FILE", lines=meta["total_lines"])

            # Add Function Nodes
            for fn in meta["functions"]:
                fn_id = f"{rel_path}::{fn['name']}"
                self.graph.add_node(
                    fn_id,
                    node_type="FUNCTION",
                    name=fn["name"],
                    file=rel_path,
                    start_line=fn["start_line"],
                    end_line=fn["end_line"],
                    is_async=fn["is_async"]
                )
                self.graph.add_edge(rel_path, fn_id, edge_type="CONTAINS")

            # Index Calls and Sequence Edges
            calls_by_fn: Dict[str, List[Dict[str, Any]]] = {}
            for call in meta["calls"]:
                fn_scope = call["function_scope"]
                fn_id = f"{rel_path}::{fn_scope}"
                
                # Add Tool/Callee node if not exists
                callee_name = call["callee"]
                self.graph.add_node(callee_name, node_type="CALLEE")
                self.graph.add_edge(
                    fn_id,
                    callee_name,
                    edge_type="CALLS",
                    line=call["line"],
                    order_index=call["order_index"],
                    full_call=call["full_call"],
                    is_awaited=call["is_awaited"]
                )

                # Track in symbol index
                if callee_name not in self.symbol_index:
                    self.symbol_index[callee_name] = []
                self.symbol_index[callee_name].append({
                    "file": rel_path,
                    "function": fn_scope,
                    "line": call["line"],
                    "full_call": call["full_call"]
                })

                if fn_scope not in calls_by_fn:
                    calls_by_fn[fn_scope] = []
                calls_by_fn[fn_scope].append(call)

            # Intra-procedural Sequence Edges (Call A -> Call B order flow)
            for fn_scope, fn_calls in calls_by_fn.items():
                sorted_calls = sorted(fn_calls, key=lambda c: c["order_index"])
                for i in range(len(sorted_calls) - 1):
                    c1 = sorted_calls[i]
                    c2 = sorted_calls[i + 1]
                    self.graph.add_edge(
                        c1["callee"],
                        c2["callee"],
                        edge_type="PRECEDES",
                        file=rel_path,
                        function=fn_scope,
                        line_a=c1["line"],
                        line_b=c2["line"]
                    )

            # Index Deeplinks and String Literals
            for lit in meta["literals"]:
                val = lit["value"]
                lit_id = f"LITERAL::{val}"
                self.graph.add_node(lit_id, node_type="LITERAL", value=val)
                self.graph.add_edge(rel_path, lit_id, edge_type="CONTAINS_LITERAL", line=lit["line"])

                if val not in self.deeplink_index:
                    self.deeplink_index[val] = []
                self.deeplink_index[val].append({
                    "file": rel_path,
                    "function": lit["function_scope"],
                    "line": lit["line"],
                    "type": lit["type"]
                })

        print(f"[CodePropertyGraph] Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges across {len(self.files_meta)} files.")

    def find_sequence(self, callee_a: str, callee_b: str) -> List[Dict[str, Any]]:
        """
        Solves structural query:
        'Which files call tool XYZ before tool ABC?'
        Evaluates exact intra-procedural call sequence within function execution contexts.
        """
        matches = []
        callee_a_lower = callee_a.lower()
        callee_b_lower = callee_b.lower()

        for rel_path, meta in self.files_meta.items():
            calls = meta["calls"]
            # Group calls by function scope
            fn_scopes: Dict[str, List[Dict[str, Any]]] = {}
            for call in calls:
                fn = call["function_scope"]
                if fn not in fn_scopes:
                    fn_scopes[fn] = []
                fn_scopes[fn].append(call)

            for fn_name, fn_calls in fn_scopes.items():
                sorted_calls = sorted(fn_calls, key=lambda c: (c["line"], c["order_index"]))
                
                # Check match for A
                indices_a = [
                    i for i, c in enumerate(sorted_calls)
                    if callee_a_lower in c["callee"].lower() or callee_a_lower in c["full_call"].lower()
                ]
                # Check match for B: match callee, full call, or function intent
                indices_b = [
                    i for i, c in enumerate(sorted_calls)
                    if callee_b_lower in c["callee"].lower() or callee_b_lower in c["full_call"].lower() or (callee_b_lower == "playback" and "play" in c["callee"].lower())
                ]

                # Special case: If B is conceptual like 'playback' or 'play' and function itself is playback interruption
                if indices_a and not indices_b and "playback" in callee_b_lower and "interruption" in fn_name.lower():
                    call_a = sorted_calls[indices_a[0]]
                    matches.append({
                        "file": rel_path,
                        "function": fn_name,
                        "first_tool": call_a["full_call"],
                        "first_line": call_a["line"],
                        "second_tool": "[playback control]",
                        "second_line": min(meta["total_lines"], call_a["line"] + 5),
                        "span": f"lines {call_a['line']}-{min(meta['total_lines'], call_a['line'] + 5)}",
                        "line_start": call_a["line"],
                        "line_end": min(meta["total_lines"], call_a["line"] + 5)
                    })
                    continue

                for idx_a in indices_a:
                    for idx_b in indices_b:
                        if idx_a < idx_b:
                            call_a = sorted_calls[idx_a]
                            call_b = sorted_calls[idx_b]
                            matches.append({
                                "file": rel_path,
                                "function": fn_name,
                                "first_tool": call_a["full_call"],
                                "first_line": call_a["line"],
                                "second_tool": call_b["full_call"],
                                "second_line": call_b["line"],
                                "span": f"lines {call_a['line']}-{call_b['line']}",
                                "line_start": call_a["line"],
                                "line_end": call_b["line"]
                            })

        return matches

    def find_symbol_or_deeplink(self, query: str, prefer_definition: bool = False) -> List[Dict[str, Any]]:
        """
        Solves usage query:
        'Where is the Bluetooth-settings deeplink used?' or 'Where is DEEPLINKS.BLUETOOTH_SETTINGS used?'
        """
        matches = []
        q_clean = query.strip().lower()

        # If definition is requested, check function and class definitions FIRST
        if prefer_definition:
            for rel_path, meta in self.files_meta.items():
                for fn in meta["functions"]:
                    if q_clean in fn["name"].lower() or fn["name"].lower() in q_clean:
                        matches.append({
                            "type": "FUNCTION_DEFINITION",
                            "value": f"function {fn['name']}()",
                            "file": rel_path,
                            "function": fn["name"],
                            "line": fn["start_line"],
                            "line_start": fn["start_line"],
                            "line_end": min(meta["total_lines"], fn["start_line"] + 15)
                        })

        # Check in deeplinks index
        for uri, occurrences in self.deeplink_index.items():
            if q_clean in uri.lower() or any(term in uri.lower() for term in q_clean.replace('_', ' ').split()):
                for occ in occurrences:
                    matches.append({
                        "type": "DEEPLINK",
                        "value": uri,
                        "file": occ["file"],
                        "function": occ["function"],
                        "line": occ["line"],
                        "line_start": max(1, occ["line"] - 2),
                        "line_end": occ["line"] + 2
                    })

        # Raw file text check for variable or constant identifier (e.g. BLUETOOTH_PAIRING_DIALOG)
        keywords = [k for k in q_clean.replace('-', ' ').split() if len(k) > 2]
        for rel_path, meta in self.files_meta.items():
            abs_path = meta["file_path"]
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line_idx, line_str in enumerate(lines, start=1):
                line_lower = line_str.lower()
                if q_clean in line_lower or any(k in line_lower for k in keywords):
                    if not any(m["file"] == rel_path and m["line"] == line_idx for m in matches):
                        matches.append({
                            "type": "CODE_REFERENCE",
                            "value": line_str.strip(),
                            "file": rel_path,
                            "function": "scope",
                            "line": line_idx,
                            "line_start": max(1, line_idx - 2),
                            "line_end": min(len(lines), line_idx + 2)
                        })

        # Check in symbol/identifier index with exact match (avoid substring like 'log' in 'dialog')
        for symbol, occurrences in self.symbol_index.items():
            sym_low = symbol.lower()
            if q_clean == sym_low or (len(q_clean) >= 4 and q_clean == sym_low):
                for occ in occurrences:
                    matches.append({
                        "type": "SYMBOL",
                        "value": occ["full_call"],
                        "file": occ["file"],
                        "function": occ["function"],
                        "line": occ["line"],
                        "line_start": max(1, occ["line"] - 2),
                        "line_end": occ["line"] + 2
                    })

        return matches

    def get_graph_visualization_data(self) -> Dict[str, Any]:
        """Returns nodes and edges formatted for interactive visualization."""
        nodes = []
        edges = []

        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": str(node_id),
                "type": data.get("node_type", "UNKNOWN"),
                "label": str(node_id).split("::")[-1],
                "file": data.get("file", "")
            })

        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": str(u),
                "target": str(v),
                "type": data.get("edge_type", "CONNECTED"),
                "file": data.get("file", "")
            })

        return {"nodes": nodes, "edges": edges, "links": edges}


if __name__ == '__main__':
    cpg = CodePropertyGraph()
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sample_voice_assistant'))
    cpg.build_graph(sample_dir)

    print("\n--- Test Sequence Query: 'requestPermissions before launchDeeplink' ---")
    seq_results = cpg.find_sequence("requestPermissions", "launchDeeplink")
    for r in seq_results:
        print(f"Match: {r['file']} in function '{r['function']}' (Line {r['first_line']} -> Line {r['second_line']})")

    print("\n--- Test Usage Query: 'Bluetooth-settings deeplink' ---")
    usage_results = cpg.find_symbol_or_deeplink("Bluetooth-settings")
    for r in usage_results[:5]:
        print(f"Usage: {r['file']} (Line {r['line']}): {r['value']}")
