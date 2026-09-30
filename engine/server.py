"""
FastAPI Server for AURA-Code Intelligence Platform.
Exposes RESTful endpoints for Agentic Code Search, Graph Visualization,
CodePath Optimizations, and Benchmark Reporting.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional

from engine.agent_controller import AgenticCodeNavigator
from engine.benchmark import BenchmarkHarness


app = FastAPI(
    title="AURA-Code Intelligence API",
    description="Agentic Code Intelligence & AST-Graph Navigator (Samsung PRISM Hackathon 3.0)",
    version="1.0.0"
)

# Enable CORS for local UI development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Navigator on default sample codebase
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CODEBASE = os.path.join(BASE_DIR, "sample_voice_assistant")
navigator = AgenticCodeNavigator(SAMPLE_CODEBASE)
navigator.index_codebase()

# Pre-index on startup (idempotent)
@app.on_event("startup")
def startup_event():
    if not navigator.is_indexed:
        navigator.index_codebase()


class QueryRequest(BaseModel):
    query: str
    codebase_path: Optional[str] = None


class IndexRequest(BaseModel):
    codebase_path: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "AURA-Code Neuro-Symbolic Engine",
        "version": "1.0.0",
        "hardware": "CPU (Optimized)",
        "indexed": navigator.is_indexed,
        "files_indexed": len(navigator.cpg.files_meta),
        "nodes_count": navigator.cpg.graph.number_of_nodes(),
        "edges_count": navigator.cpg.graph.number_of_edges(),
        "chunks_count": len(navigator.hybrid_index.chunks)
    }


@app.post("/api/index")
def reindex_codebase(req: IndexRequest = None):
    target_path = req.codebase_path if req and req.codebase_path else SAMPLE_CODEBASE
    if not os.path.exists(target_path):
        raise HTTPException(status_code=400, detail=f"Path does not exist: {target_path}")

    global navigator
    navigator = AgenticCodeNavigator(target_path)
    metrics = navigator.index_codebase()
    return metrics


@app.post("/api/query")
def execute_query(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = navigator.query(req.query.strip())
    return result


@app.get("/api/graph")
def get_graph():
    return navigator.cpg.get_graph_visualization_data()


@app.get("/api/benchmark")
def get_benchmark():
    json_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    if os.path.exists(json_path):
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        harness = BenchmarkHarness(SAMPLE_CODEBASE)
        return harness.run_full_benchmark()


# Mount UI static files if directory exists
UI_DIR = os.path.join(BASE_DIR, "ui")
if os.path.exists(UI_DIR):
    app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("engine.server:app", host="0.0.0.0", port=8000, reload=True)
