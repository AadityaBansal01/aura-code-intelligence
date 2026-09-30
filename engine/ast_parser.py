"""
AST & Code Property Graph (CPG) Extractor for JavaScript using Tree-sitter.
Parses JavaScript files to extract functions, call sequences, string literals, and imports.
"""

import os
from typing import Dict, List, Any, Optional
import tree_sitter_javascript as tsjs
from tree_sitter import Language, Parser, Node


class JSASTParser:
    def __init__(self):
        self.language = Language(tsjs.language())
        self.parser = Parser(self.language)

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parses a JS file and extracts structural metadata, calls, and literals."""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        source_bytes = code.encode('utf-8')
        tree = self.parser.parse(source_bytes)
        root = tree.root_node

        lines = code.splitlines()

        file_metadata = {
            "file_path": file_path,
            "total_lines": len(lines),
            "functions": [],
            "calls": [],
            "literals": [],
            "imports": [],
            "classes": []
        }

        self._traverse(root, source_bytes, file_metadata, current_function=None, call_counter=[0])
        return file_metadata

    def _get_node_text(self, node: Node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _traverse(self, node: Node, source_bytes: bytes, meta: Dict[str, Any], current_function: Optional[str], call_counter: List[int]):
        node_type = node.type

        # 1. Detect Class Declarations
        if node_type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = self._get_node_text(name_node, source_bytes)
                meta["classes"].append({
                    "name": class_name,
                    "start_line": node.start_point.row + 1,
                    "end_line": node.end_point.row + 1
                })

        # 2. Detect Function Declarations and Methods
        new_function = current_function
        if node_type in ("function_declaration", "method_definition", "arrow_function"):
            fn_name = "anonymous"
            name_node = node.child_by_field_name("name")
            if name_node:
                fn_name = self._get_node_text(name_node, source_bytes)
            elif node.parent and node.parent.type == "variable_declarator":
                var_name = node.parent.child_by_field_name("name")
                if var_name:
                    fn_name = self._get_node_text(var_name, source_bytes)

            new_function = fn_name
            meta["functions"].append({
                "name": fn_name,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
                "is_async": "async" in self._get_node_text(node, source_bytes)[:20].lower()
            })
            # Reset order counter per function scope to track intra-function call order
            call_counter[0] = 0

        # 3. Detect Call Expressions (e.g. tool.method(...) or method(...))
        if node_type == "call_expression":
            fn_node = node.child_by_field_name("function")
            if fn_node:
                call_text = self._get_node_text(fn_node, source_bytes)
                # Split member expression (e.g. permissionTool.requestPermissions -> requestPermissions)
                callee_name = call_text.split('.')[-1]
                caller_object = call_text.split('.')[0] if '.' in call_text else None
                
                # Check if awaited
                is_awaited = node.parent is not None and node.parent.type == "await_expression"
                
                # Extract argument snippets
                args_node = node.child_by_field_name("arguments")
                args_text = self._get_node_text(args_node, source_bytes) if args_node else "()"

                call_counter[0] += 1
                meta["calls"].append({
                    "callee": callee_name,
                    "full_call": call_text,
                    "caller_object": caller_object,
                    "arguments": args_text,
                    "line": node.start_point.row + 1,
                    "function_scope": new_function or "global",
                    "order_index": call_counter[0],
                    "is_awaited": is_awaited
                })

        # 4. Detect String Literals (Deeplinks, URIs, Permissions)
        if node_type == "string":
            raw_text = self._get_node_text(node, source_bytes).strip('\'"')
            # Record potential deeplinks, URIs or identifiers
            if any(prefix in raw_text for prefix in ('bixby://', 'samsungapps://', 'spotify://', 'google.navigation:', 'vnd.youtube')):
                meta["literals"].append({
                    "type": "DEEPLINK",
                    "value": raw_text,
                    "line": node.start_point.row + 1,
                    "function_scope": new_function or "global"
                })
            elif any(proto in raw_text for proto in ('http://', 'https://', 'stream://')):
                meta["literals"].append({
                    "type": "URL",
                    "value": raw_text,
                    "line": node.start_point.row + 1,
                    "function_scope": new_function or "global"
                })

        # 5. Detect Require / Import statements
        if node_type == "call_expression":
            fn_node = node.child_by_field_name("function")
            if fn_node and self._get_node_text(fn_node, source_bytes) == "require":
                args_node = node.child_by_field_name("arguments")
                if args_node and args_node.named_child_count > 0:
                    imported = self._get_node_text(args_node.named_children[0], source_bytes).strip('\'"')
                    meta["imports"].append({
                        "module": imported,
                        "line": node.start_point.row + 1
                    })

        # Recurse children
        for child in node.children:
            self._traverse(child, source_bytes, meta, new_function, call_counter)


def scan_directory(directory_path: str) -> List[Dict[str, Any]]:
    """Scans all JS files in a directory and returns parsed AST summaries."""
    parser = JSASTParser()
    results = []
    for root, _, files in os.walk(directory_path):
        for f in files:
            if f.endswith('.js') and not f.endswith('.test.js') and not f == 'test.js':
                full_path = os.path.join(root, f)
                parsed = parser.parse_file(full_path)
                results.append(parsed)
    return results


if __name__ == '__main__':
    import json
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../sample_voice_assistant'))
    parsed_files = scan_directory(sample_dir)
    print(f"Parsed {len(parsed_files)} JS files successfully.")
    for p in parsed_files:
        print(f"File: {os.path.basename(p['file_path'])}, Functions: {len(p['functions'])}, Calls: {len(p['calls'])}, Literals: {len(p['literals'])}")
