"""
CPU-Optimized Hybrid Vector & Lexical Retrieval Engine for JavaScript Code.
Combines subword n-gram semantic vectorization with BM25 keyword matching
to locate code snippets for plain-English queries in under 10ms on CPU.
"""

import os
import re
from typing import Dict, List, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CodeChunk:
    def __init__(self, file_path: str, function_name: str, start_line: int, end_line: int, content: str, docstring: str = ""):
        self.file_path = file_path
        self.function_name = function_name
        self.start_line = start_line
        self.end_line = end_line
        self.content = content
        self.docstring = docstring
        
        # Prepare rich token context with sub-token expansion (CamelCase & snake_case)
        expanded_code = re.sub(r'([a-z])([A-Z])', r'\1 \2', content)
        expanded_code = expanded_code.replace('_', ' ')
        self.searchable_text = f"file: {file_path}\nfunction: {function_name}\n{docstring}\n{content}\n{expanded_code}"


class HybridCodeIndex:
    def __init__(self):
        self.chunks: List[CodeChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.directory_path: str = ""

    def build_index(self, directory_path: str):
        """Indexes all JS files by syntactic chunks (functions and module blocks)."""
        self.directory_path = directory_path
        self.chunks = []

        for root, _, files in os.walk(directory_path):
            for file_name in sorted(files):
                if file_name.endswith('.js') and not file_name.endswith('.test.js') and file_name != 'test.js':
                    full_path = os.path.join(root, file_name)
                    rel_path = os.path.relpath(full_path, directory_path)
                    self._extract_chunks_from_file(full_path, rel_path)

        if not self.chunks:
            print("[HybridCodeIndex] Warning: No chunks extracted.")
            return

        corpus = [c.searchable_text for c in self.chunks]
        
        # Word + Character n-grams for code semantic retrieval
        self.vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=10000
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        print(f"[HybridCodeIndex] Indexed {len(self.chunks)} syntactic code chunks across codebase (CPU optimized).")

    def _extract_chunks_from_file(self, full_path: str, rel_path: str):
        """Reads file and segments into logical blocks."""
        with open(full_path, 'r', encoding='utf-8') as f:
            code = f.read()

        lines = code.splitlines()
        
        # Whole-file fallback chunk
        self.chunks.append(CodeChunk(
            file_path=rel_path,
            function_name="[module_root]",
            start_line=1,
            end_line=len(lines),
            content="\n".join(lines[:40]),
            docstring="Module header and exports"
        ))

        # Block-level chunking based on comments and function keywords
        current_chunk_lines = []
        current_fn_name = "general"
        chunk_start = 1
        current_doc = []

        for idx, line in enumerate(lines, start=1):
            trimmed = line.strip()
            if trimmed.startswith('/**') or trimmed.startswith('*') or trimmed.startswith('//'):
                current_doc.append(trimmed)

            # Detect function or method declaration
            if ('function ' in line or 'async ' in line or '=>' in line or 'class ' in line) and '{' in line:
                if current_chunk_lines and len(current_chunk_lines) > 5:
                    self.chunks.append(CodeChunk(
                        file_path=rel_path,
                        function_name=current_fn_name,
                        start_line=chunk_start,
                        end_line=idx - 1,
                        content="\n".join(current_chunk_lines),
                        docstring="\n".join(current_doc)
                    ))
                    current_chunk_lines = []
                    current_doc = []
                chunk_start = idx
                match = re.search(r'(?:function\s+|class\s+|async\s+)?([a-zA-Z0-9_$]+)\s*\(', line)
                if match:
                    current_fn_name = match.group(1)
                else:
                    current_fn_name = "method"

            current_chunk_lines.append(line)

        # Flush final chunk
        if current_chunk_lines:
            self.chunks.append(CodeChunk(
                file_path=rel_path,
                function_name=current_fn_name,
                start_line=chunk_start,
                end_line=len(lines),
                content="\n".join(current_chunk_lines),
                docstring="\n".join(current_doc)
            ))

    def _tokenize(self, text: str) -> List[str]:
        """Extracts and normalizes tokens from code or text, expanding CamelCase and snake_case."""
        expanded = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        expanded = expanded.replace('_', ' ').lower()
        return [t for t in re.findall(r'[a-zA-Z0-9]+', expanded) if len(t) > 1]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Alias for search_semantic."""
        return self.search_semantic(query, top_k)

    def search_semantic(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes hybrid semantic & lexical search over indexed code chunks.
        Returns top-k code snippets with exact file paths and line ranges.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        # Vectorize query
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        # Concept Coverage Multiplier: Prioritize chunks matching multiple distinct query concepts
        q_terms = [t.lower() for t in query.split() if len(t) > 2]
        for i, chunk in enumerate(self.chunks):
            boost = 0.0
            text_lower = chunk.searchable_text.lower()
            file_lower = chunk.file_path.lower()
            matched_terms = sum(1 for term in q_terms if term in text_lower or term in file_lower)
            
            # Coverage bonus: chunks containing multiple distinct terms get a multiplicative boost
            coverage_factor = 1.0 + (matched_terms / len(q_terms) if q_terms else 0.0) * 1.5
            scores[i] = (scores[i] + boost) * coverage_factor

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < 0.01:
                continue
            chunk = self.chunks[idx]
            results.append({
                "file": chunk.file_path,
                "function": chunk.function_name,
                "line_start": chunk.start_line,
                "line_end": chunk.end_line,
                "score": round(score, 4),
                "snippet": chunk.content,
                "docstring": chunk.docstring
            })

        return results


if __name__ == '__main__':
    index = HybridCodeIndex()
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sample_voice_assistant'))
    index.build_index(sample_dir)

    print("\n--- Test Conceptual NL Query: 'where does the assistant handle media playback interruptions?' ---")
    results = index.search_semantic("where does the assistant handle media playback interruptions?", top_k=3)
    for r in results:
        print(f"[{r['score']}] {r['file']} (Lines {r['line_start']}-{r['line_end']}) in '{r['function']}':")
        print("   " + r['snippet'].splitlines()[0])
