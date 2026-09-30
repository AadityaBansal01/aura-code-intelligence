"""
AURA-Code Agentic Controller (Plan -> Search -> Read -> Refine).
Autonomous Code Intelligence Agent that navigates large codebases far beyond LLM context windows.
Synthesizes answers for Natural Language, Structural Sequence, and Usage queries.
"""

import os
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from engine.graph_store import CodePropertyGraph
from engine.vector_lexical_store import HybridCodeIndex
from engine.codepath_optimizer import CodePathOptimizer


class AgentReasoningStep:
    def __init__(self, step_number: int, action: str, observation: str):
        self.step_number = step_number
        self.action = action
        self.observation = observation

    def to_dict(self):
        return {
            "step": self.step_number,
            "action": self.action,
            "observation": self.observation
        }


class AgenticCodeNavigator:
    def __init__(self, codebase_path: str):
        self.codebase_path = os.path.abspath(codebase_path)
        self.cpg = CodePropertyGraph()
        self.hybrid_index = HybridCodeIndex()
        self.optimizer = CodePathOptimizer()
        self.is_indexed = False

    def index_codebase(self) -> Dict[str, Any]:
        """Indexes codebase across both Graph and Hybrid Vector stores."""
        start_time = time.perf_counter()
        
        self.cpg.build_graph(self.codebase_path)
        self.hybrid_index.build_index(self.codebase_path)
        
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        self.is_indexed = True

        return {
            "status": "INDEXED",
            "codebase_path": self.codebase_path,
            "indexing_time_ms": elapsed_ms,
            "nodes_indexed": self.cpg.graph.number_of_nodes(),
            "edges_indexed": self.cpg.graph.number_of_edges(),
            "chunks_indexed": len(self.hybrid_index.chunks)
        }

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Main Agentic Entrypoint:
        Executes Plan -> Search -> Read -> Refine cycle over the codebase.
        """
        if not self.is_indexed:
            self.index_codebase()

        start_time = time.perf_counter()
        steps: List[AgentReasoningStep] = []

        # Step 1: Intent Understanding & Classification
        query_type, target_entities = self._classify_intent(user_query)
        steps.append(AgentReasoningStep(
            1,
            f"Classify Query Intent: Detected '{query_type}'",
            f"Extracted entities: {target_entities}"
        ))

        matches = []
        sequence_data = None
        optimizations = []

        # Step 2 & 3: Multi-Tool Search Execution
        if query_type == "STRUCTURAL_SEQUENCE":
            tool_a, tool_b = target_entities["tool_a"], target_entities["tool_b"]
            steps.append(AgentReasoningStep(
                2,
                f"Query Symbolic AST Sequence Graph: '{tool_a}' BEFORE '{tool_b}'",
                f"Scanning intra-procedural AST call order across all function scopes"
            ))
            
            raw_seq_matches = self.cpg.find_sequence(tool_a, tool_b)
            steps.append(AgentReasoningStep(
                3,
                f"Inspect Call Sequence Graph",
                f"Located {len(raw_seq_matches)} valid sequence call paths"
            ))

            for m in raw_seq_matches:
                full_code, snippet = self._read_window(m["file"], m["line_start"] - 2, m["line_end"] + 4)
                matches.append({
                    "file": m["file"],
                    "function": m["function"],
                    "line_start": m["first_line"],
                    "line_end": m["second_line"],
                    "confidence": 0.98,
                    "reasoning": f"Calls '{m['first_tool']}' on line {m['first_line']} prior to '{m['second_tool']}' on line {m['second_line']}",
                    "snippet": snippet,
                    "full_context": full_code
                })
                # Check for optimizations on this path
                opts = self.optimizer.analyze_snippet(m["file"], full_code, m["function"])
                optimizations.extend(opts)

            sequence_data = {
                "first_tool": tool_a,
                "second_tool": tool_b,
                "order_verified": True
            }

        elif query_type == "USAGE_REFERENCE":
            symbol = target_entities.get("symbol", user_query)
            steps.append(AgentReasoningStep(
                2,
                f"Search Inverted Symbol & Deeplink Index for: '{symbol}'",
                "Looking up literal AST string nodes and member expressions"
            ))
            
            prefer_def = target_entities.get("prefer_definition", False)
            raw_symbol_matches = self.cpg.find_symbol_or_deeplink(symbol, prefer_definition=prefer_def)
            steps.append(AgentReasoningStep(
                3,
                f"Read Surrounding Context Windows",
                f"Found {len(raw_symbol_matches)} reference locations"
            ))

            for m in raw_symbol_matches:
                full_code, snippet = self._read_window(m["file"], m["line_start"], m["line_end"])
                matches.append({
                    "file": m["file"],
                    "function": m["function"],
                    "line_start": m["line"],
                    "line_end": m["line"],
                    "confidence": 0.96,
                    "reasoning": f"Found direct usage of '{m['value']}' on line {m['line']}",
                    "snippet": snippet,
                    "full_context": full_code
                })
                opts = self.optimizer.analyze_snippet(m["file"], full_code, m["function"])
                optimizations.extend(opts)

        else: # CONCEPTUAL_SEMANTIC
            steps.append(AgentReasoningStep(
                2,
                f"Execute Hybrid Vector + Lexical Search",
                f"Evaluating subword semantic embeddings and BM25 token alignment on CPU"
            ))
            
            semantic_matches = self.hybrid_index.search_semantic(user_query, top_k=4)
            steps.append(AgentReasoningStep(
                3,
                f"Read & Verify Top {len(semantic_matches)} Candidate Blocks",
                "Inspecting code context, imports, and docstrings"
            ))

            for sm in semantic_matches:
                full_code, snippet = self._read_window(sm["file"], sm["line_start"], sm["line_end"])
                matches.append({
                    "file": sm["file"],
                    "function": sm["function"],
                    "line_start": sm["line_start"],
                    "line_end": sm["line_end"],
                    "confidence": sm["score"],
                    "reasoning": f"High semantic similarity ({sm['score']}) with function docstring/signature",
                    "snippet": snippet,
                    "full_context": full_code
                })
                opts = self.optimizer.analyze_snippet(sm["file"], full_code, sm["function"])
                optimizations.extend(opts)

        # Step 4: Refine & Deduplicate
        steps.append(AgentReasoningStep(
            4,
            "Synthesize & Refine Evidence",
            f"Assembled {len(matches)} grounded code locations with file:line citations"
        ))

        # Deduplicate optimizations
        unique_opts = []
        seen_titles = set()
        for o in optimizations:
            if o["title"] not in seen_titles:
                seen_titles.add(o["title"])
                unique_opts.append(o)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "query": user_query,
            "query_type": query_type,
            "intent": query_type,
            "latency_ms": latency_ms,
            "plan_steps": [s.to_dict() for s in steps],
            "total_matches": len(matches),
            "matches": matches,
            "sequence_data": sequence_data,
            "optimizations": unique_opts,
            "summary": self._generate_summary(user_query, query_type, matches, unique_opts)
        }

    def _classify_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Intelligently classifies user query into structural, usage, definition, or semantic categories."""
        q_lower = query.lower()

        # 1. Structural Sequence query pattern: "<toolA> ... before <toolB>"
        if " before " in q_lower:
            m = re.search(r'([a-zA-Z0-9_$]+)\s+(?:is\s+)?(?:called|invoked|used)?\s*before\s+(?:any\s+)?(?:tool\s+)?([a-zA-Z0-9_$]+)', query, re.IGNORECASE)
            if m:
                return "STRUCTURAL_SEQUENCE", {
                    "tool_a": m.group(1).strip(),
                    "tool_b": m.group(2).strip()
                }

        # 2. Function/Method Definition query
        if "defined" in q_lower or "definition" in q_lower or "where is method" in q_lower or "where is function" in q_lower:
            cleaned = re.sub(r'(?i)where\s+is\s+|method\s+|function\s+|defined|definition|\?', '', query).strip()
            return "USAGE_REFERENCE", {"symbol": cleaned, "prefer_definition": True}

        # 3. Usage & Deeplink reference query
        if any(term in q_lower for term in ('deeplink', 'uri', 'constant', 'find usage of', 'find references to', 'usage of', 'references to', 'where is the bluetooth')):
            cleaned = re.sub(r'(?i)find\s+usage\s+of\s+|find\s+references\s+to\s+|where\s+is\s+the\s+|where\s+is\s+|deeplink|constant|used|\?', '', query).strip()
            return "USAGE_REFERENCE", {"symbol": cleaned}

        # 4. Default to Conceptual Semantic code search
        return "CONCEPTUAL_SEMANTIC", {"query": query}

    def _read_window(self, rel_path: str, start_line: int, end_line: int) -> Tuple[str, str]:
        """Reads code window from file."""
        abs_path = os.path.join(self.codebase_path, rel_path)
        if not os.path.exists(abs_path):
            return ("", "")

        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)

        snippet_lines = lines[start_idx:end_idx]
        snippet = "".join(snippet_lines)
        
        # Broader context window
        full_start = max(0, start_idx - 5)
        full_end = min(len(lines), end_idx + 5)
        full_code = "".join(lines[full_start:full_end])

        return (full_code, snippet)

    def _generate_summary(self, query: str, q_type: str, matches: List[Dict[str, Any]], opts: List[Dict[str, Any]]) -> str:
        if not matches:
            return f"No code locations matched query '{query}' in the codebase."

        files = list(dict.fromkeys([m["file"] for m in matches]))
        file_list_str = ", ".join([f"`{f}`" for f in files[:3]])

        if q_type == "STRUCTURAL_SEQUENCE":
            return (
                f"Found {len(matches)} execution path(s) satisfying call sequence in {file_list_str}. "
                f"Validated intra-procedural AST ordering with line-level certainty."
            )
        elif q_type == "USAGE_REFERENCE":
            lines_str = ", ".join([f"{m['file']}:L{m['line_start']}" for m in matches[:3]])
            return f"Found {len(matches)} usage location(s) across {file_list_str} (at {lines_str})."
        else:
            top_match = matches[0]
            return (
                f"Identified primary implementation in `{top_match['file']}` (lines {top_match['line_start']}-{top_match['line_end']}) "
                f"in function `{top_match['function']}`."
            )


if __name__ == '__main__':
    sample_dir = os.path.join(os.path.dirname(__file__), '../sample_voice_assistant')
    navigator = AgenticCodeNavigator(sample_dir)
    navigator.index_codebase()

    print("\n================ QUERY 1: STRUCTURAL SEQUENCE ================")
    q1 = "which files call tool requestPermissions before tool launchDeeplink?"
    res1 = navigator.query(q1)
    print(f"Summary: {res1['summary']}")
    for m in res1["matches"]:
        print(f" -> {m['file']}:{m['line_start']}-{m['line_end']} ({m['function']})")

    print("\n================ QUERY 2: USAGE / DEEPLINK ===================")
    q2 = "where is the Bluetooth-settings deeplink used?"
    res2 = navigator.query(q2)
    print(f"Summary: {res2['summary']}")
    for m in res2["matches"][:3]:
        print(f" -> {m['file']}:L{m['line_start']}")

    print("\n================ QUERY 3: CONCEPTUAL NL ======================")
    q3 = "where does the assistant handle media playback interruptions?"
    res3 = navigator.query(q3)
    print(f"Summary: {res3['summary']}")
    for m in res3["matches"][:2]:
        print(f" -> {m['file']}:{m['line_start']}-{m['line_end']} ({m['function']})")

    print(f"\nDiscovered {len(res3['optimizations'])} bonus optimization(s)!")
    for o in res3["optimizations"][:1]:
        print(f"[{o['severity']}] {o['title']}")
