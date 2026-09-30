import pytest
import os
import json
from engine.ast_parser import JSASTParser, scan_directory
from engine.graph_store import CodePropertyGraph
from engine.vector_lexical_store import HybridCodeIndex
from engine.codepath_optimizer import CodePathOptimizer
from engine.agent_controller import AgenticCodeNavigator
from fastapi.testclient import TestClient
from engine.server import app

SAMPLE_CODEBASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_voice_assistant"))

@pytest.fixture(scope="module")
def parsed_files():
    return scan_directory(SAMPLE_CODEBASE)

@pytest.fixture(scope="module")
def graph_and_index():
    cpg = CodePropertyGraph()
    cpg.build_graph(SAMPLE_CODEBASE)
    
    hybrid_index = HybridCodeIndex()
    hybrid_index.build_index(SAMPLE_CODEBASE)
    
    return cpg, hybrid_index

@pytest.fixture(scope="module")
def navigator():
    nav = AgenticCodeNavigator(SAMPLE_CODEBASE)
    nav.index_codebase()
    return nav

@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)

# ----------------- AST Parser Tests -----------------
def test_ast_parser_files_found(parsed_files):
    assert len(parsed_files) == 14
    file_names = [os.path.basename(p["file_path"]) for p in parsed_files]
    assert "navigation_agent.js" in file_names
    assert "settings_agent.js" in file_names
    assert "deeplinks.js" in file_names

def test_ast_parser_functions_and_calls(parsed_files):
    nav_file = next(p for p in parsed_files if "navigation_agent.js" in p["file_path"])
    fn_names = [f["name"] for f in nav_file["functions"]]
    assert "navigateToSavedLocation" in fn_names
    
    calls = nav_file["calls"]
    req_call = next((c for c in calls if c["callee"] == "requestPermissions"), None)
    deep_call = next((c for c in calls if c["callee"] == "launchDeeplink"), None)
    assert req_call is not None
    assert deep_call is not None
    assert req_call["order_index"] < deep_call["order_index"]

def test_ast_parser_deeplink_literals(parsed_files):
    deeplink_file = next(p for p in parsed_files if "deeplinks.js" in p["file_path"])
    literals = [lit["value"] for lit in deeplink_file["literals"]]
    assert any("bixby://settings/bluetooth" in lit for lit in literals)

# ----------------- Code Property Graph Tests -----------------
def test_cpg_graph_structure(graph_and_index):
    cpg, _ = graph_and_index
    assert cpg.graph.number_of_nodes() > 50
    assert cpg.graph.number_of_edges() > 50

def test_cpg_sequence_query(graph_and_index):
    cpg, _ = graph_and_index
    results = cpg.find_sequence("requestPermissions", "launchDeeplink")
    assert len(results) >= 2
    files = [r["file"] for r in results]
    assert "agents/navigation_agent.js" in files
    assert "agents/settings_agent.js" in files

def test_cpg_symbol_deeplink_search(graph_and_index):
    cpg, _ = graph_and_index
    results = cpg.find_symbol_or_deeplink("bixby://settings/bluetooth")
    assert len(results) >= 1
    assert any("deeplinks.js" in r["file"] for r in results)

# ----------------- Vector Lexical Store Tests -----------------
def test_hybrid_index_camelcase_splitting(graph_and_index):
    _, hybrid_index = graph_and_index
    tokens = hybrid_index._tokenize("navigateToSavedLocation")
    assert "navigate" in tokens
    assert "saved" in tokens
    assert "location" in tokens

def test_hybrid_index_semantic_search(graph_and_index):
    _, hybrid_index = graph_and_index
    results = hybrid_index.search("where is voice recognition timeout configured", top_k=5)
    assert len(results) > 0
    top_file = results[0]["file"]
    assert "constants.js" in top_file

# ----------------- CodePath Optimizer Tests -----------------
def test_codepath_optimizer_waterfall():
    sample_code = """
    async function playTrack(query) {
        const p1 = await permissionTool.checkPermissions('INTERNET');
        const p2 = await networkTool.checkConnectivity();
        return await deviceTool.launchDeeplink('spotify://');
    }
    """
    optimizer = CodePathOptimizer()
    optimizations = optimizer.analyze_snippet("agents/media_agent.js", sample_code, "playTrack")
    assert len(optimizations) >= 1
    types = [opt["type"] for opt in optimizations]
    assert "ASYNC_WATERFALL_BOTTLENECK" in types
    waterfall = next(opt for opt in optimizations if opt["type"] == "ASYNC_WATERFALL_BOTTLENECK")
    assert "Promise.all" in waterfall["optimized_code"]

def test_codepath_optimizer_unprotected_deeplink():
    sample_code = """
    async function openUri(uri) {
        await deviceTool.launchDeeplink(uri);
    }
    """
    optimizer = CodePathOptimizer()
    optimizations = optimizer.analyze_snippet("agents/settings_agent.js", sample_code, "openUri")
    assert len(optimizations) >= 1
    types = [opt["type"] for opt in optimizations]
    assert "FAULT_TOLERANCE_WARNING" in types

# ----------------- Agentic Controller Tests -----------------
def test_agent_controller_sequence_query(navigator):
    res = navigator.query("which files call tool requestPermissions before tool launchDeeplink")
    assert res["query_type"] == "STRUCTURAL_SEQUENCE"
    assert res["intent"] == "STRUCTURAL_SEQUENCE"
    assert len(res["matches"]) >= 2
    files = [m["file"] for m in res["matches"]]
    assert "agents/navigation_agent.js" in files
    assert "agents/settings_agent.js" in files
    assert len(res["plan_steps"]) >= 3

def test_agent_controller_deeplink_query(navigator):
    res = navigator.query("where is the bluetooth settings deeplink defined or used")
    assert res["query_type"] == "USAGE_REFERENCE"
    assert len(res["matches"]) >= 1
    assert any("settings_agent.js" in m["file"] or "deeplinks.js" in m["file"] for m in res["matches"])

def test_agent_controller_semantic_query(navigator):
    res = navigator.query("how does the voice assistant handle user permission denials")
    assert len(res["matches"]) >= 1
    assert any("permission" in m["snippet"].lower() or "denied" in m["snippet"].lower() for m in res["matches"])

def test_agent_controller_latency_under_50ms(navigator):
    # Test CPU inference latency constraint (Hackathon requirement: fast CPU execution)
    res = navigator.query("where is speech recognition timeout configured")
    assert res["latency_ms"] < 50.0  # Under 50ms on CPU (typical is < 3ms)

# ----------------- Server API Tests -----------------
def test_api_health(api_client):
    res = api_client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["files_indexed"] == 14
    assert data["nodes_count"] > 50

def test_api_query_sequence(api_client):
    res = api_client.post("/api/query", json={"query": "which files call tool requestPermissions before tool launchDeeplink"})
    assert res.status_code == 200
    data = res.json()
    assert data["query_type"] == "STRUCTURAL_SEQUENCE"
    assert len(data["matches"]) >= 2

def test_api_graph_export(api_client):
    res = api_client.get("/api/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) > 0

def test_api_benchmark_endpoint(api_client):
    res = api_client.get("/api/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert data["metrics"]["precision_at_1"] > 0.85
