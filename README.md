# AURA-Code: Agentic Code Intelligence & AST-Graph Navigator

> 🌐 **Live Demo:** https://aura-code-intelligence.onrender.com  
> 📊 **API Docs:** https://aura-code-intelligence.onrender.com/docs  
> 💻 **Local:** `bash run.sh` → http://localhost:8000


### Samsung PRISM GenAI Hackathon 3.0 (2026–27) | Theme 01: Agentic Code Intelligence
**Release Tag:** `PRISM_GENAI_HACKATHON_Y2026`  
**Hardware Profile:** 100% CPU Optimized | Zero GPU Dependency | Pure Local Inference

[![Engine Tests](https://img.shields.io/badge/Pytest-18%2F18%20Passed-brightgreen.svg)](tests/)
[![Precision@1](https://img.shields.io/badge/Precision%401-93.3%25-blue.svg)](engine/benchmark_results.json)
[![Mean Latency](https://img.shields.io/badge/Latency-0.64ms%20(CPU)-success.svg)](engine/benchmark_results.json)
[![Docker Ready](https://img.shields.io/badge/Docker-Multi--Platform-2496ED.svg)](Dockerfile)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 🌟 Executive Summary

Modern voice assistant ecosystems (such as Samsung Bixby and Galaxy AI) comprise multi-agent distributed architectures, asynchronous tool dispatch pipelines, and hundreds of hardware deeplinks spanning over 100,000 lines of JavaScript.

When developers query this codebase:
- *"Which files call tool `requestPermissions` before tool `launchDeeplink`?"* (Structural Sequence)
- *"Where is the Bluetooth-settings deeplink used?"* (Deep Link / Symbol Discovery)
- *"Where does the assistant handle media playback interruptions?"* (Conceptual Plain-English)

**Standard Vector RAG fails completely.** Dense vector embeddings are **order-blind** (cosine similarity cannot distinguish whether tool A preceded tool B in a function), and feeding entire repositories into massive LLM context windows incurs quadratic latency (>2,500ms), prohibitive token costs, and catastrophic hallucinations.

**AURA-Code** solves this through a **Neuro-Symbolic Agentic Architecture**:
1. **Symbolic Program Layer:** Tree-sitter C-speed AST parsing and NetworkX Code Property Graphs (CPG) providing deterministic intra-procedural call sequence verification and inverted literal indexing.
2. **Neural-Lexical Layer:** Subword CamelCase/snake_case TF-IDF vectorization with concept-coverage boosting for conceptual semantic retrieval.
3. **Autonomous ReAct Controller:** A 4-step **Plan → Search → Read → Refine** agentic retrieval loop that navigates codebases exceeding LLM context windows.
4. **Voice Assistant CodePath Optimizer (Brownie Points Bonus):** Static analyzer that detects async waterfall bottlenecks (consecutive serial `await` calls) and suggests concurrent `Promise.all` diffs, cutting voice turn response times by **90–180ms**.

---

## 📊 Benchmark & Performance Metrics

Evaluated on a standardized 15-query ground-truth benchmark across structural sequences, deeplinks, and conceptual questions on standard consumer CPU hardware:

| Evaluation Metric | AURA-Code (Ours) | Standard Vector RAG (Dense) | Full-Context LLM Stuffing |
| :--- | :---: | :---: | :---: |
| **Precision@1** | **93.33%** | 33.3% (Fails on sequence) | 73.3% |
| **Precision@3** | **77.78%** | 40.0% | 66.7% |
| **Mean Recall** | **93.33%** | 46.7% | 80.0% |
| **Mean Query Latency (CPU)** | **0.64 ms** | 120 ms | 2,850 ms |
| **P95 Latency (CPU)** | **1.73 ms** | 210 ms | 4,200 ms |
| **Cold Repository Indexing** | **11.1 ms** | ~45,000 ms (Embeddings) | N/A |
| **Hardware Required** | **100% CPU (0 VRAM)** | High RAM / GPU Recommended | High-End GPU Cluster |
| **Code Privacy** | **100% Local / Offline** | Cloud Embeddings API | External LLM API ($$$) |

*Full evaluation metrics and query breakdowns are stored in [`engine/benchmark_results.json`](engine/benchmark_results.json).*

---

## 🏛️ System Architecture

```
                                 User Query
                       (NL / Sequence / Deeplink)
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │             AURA-Code Agentic Controller               │
       │         [Intent Classification & ReAct Loop]           │
       └────────────────────────────┬───────────────────────────┘
                                    │
           ┌────────────────────────┴────────────────────────┐
           ▼                                                 ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│        Symbolic Engine       │          │     Neural-Lexical Engine    │
│  Tree-sitter (0.26) AST      │          │ Subword CamelCase Tokenizer  │
│  NetworkX Code Property Graph│          │ Sublinear TF-IDF Vectorizer  │
│  - Intra-procedural Sequence │          │ Concept Coverage Multiplier  │
│  - Inverted Deeplink Index   │          │                              │
└──────────────┬───────────────┘          └──────────────┬───────────────┘
               │                                         │
               └────────────────────┬────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                Bounded Code Window Reader              │
       │         Extracts Exact Line Spans & AST Scopes         │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │         Bonus Feature: CodePath Optimizer              │
       │  - Serial Await Waterfall Detection (Promise.all diff) │
       │  - Unprotected Deeplink Dispatch Warning               │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                Synthesis & Delivery                    │
       │    Interactive Web Dashboard (SVG Graph) | Terminal CLI │
       └────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### Option 1: Native Local Run (macOS / Linux)

Ensure Python 3.11+ is installed.

```bash
# Clone the repository
git clone https://github.com/aadityabansal/aura-code-intelligence.git
cd aura-code-intelligence

# Make runner executable and run the pre-flight verification + server
chmod +x run.sh
./run.sh
```
*The interactive dashboard will be live at **http://localhost:8000**.*

---

### Option 2: Docker Containerization (One-Command Startup)

```bash
# Build and run containerized service
docker compose up --build
```
*Open **http://localhost:8000** in your browser.*

---

### Option 3: Terminal CLI Mode

Run instant queries directly from your shell:

```bash
# 1. Structural Sequence Query
./run.sh search "which files call tool requestPermissions before tool launchDeeplink"

# 2. Deep Link & Constant Query
./run.sh search "where is the bluetooth settings deeplink used"

# 3. Conceptual Semantic Query
./run.sh search "where does the assistant handle media playback interruptions"

# 4. Run the 15-Query Evaluation Benchmark
./run.sh benchmark

# 5. Run the Automated Test Suite (18 tests)
./run.sh test
```

---

## 💡 Key Features & Differentiators

### 1. Intra-Procedural Call Sequence Solver (A before B)
Evaluates execution order within function bodies using Tree-sitter statement line indices:
```bash
$ ./run.sh search "which files call tool requestPermissions before tool launchDeeplink"
```
**Output:**
```
[1] File: agents/navigation_agent.js | Lines 21-28
    -> Calls 'permissionTool.requestPermissions' (L21) before 'deviceTool.launchDeeplink' (L28)
[2] File: agents/settings_agent.js | Lines 22-28
    -> Calls 'permissionTool.requestPermissions' (L22) before 'deviceTool.launchDeeplink' (L28)
```

---

### 2. Brownie Points: Voice Assistant CodePath Optimizer
AURA-Code automatically inspects execution paths for voice turn anti-patterns:
- **Async Waterfall Bottlenecks:** Consecutive `await` calls that can be parallelized:
  ```diff
  - const permissionStatus = await permissionTool.checkPermissions('INTERNET');
  - const networkStatus = await networkTool.checkConnectivity();
  + const [permissionStatus, networkStatus] = await Promise.all([
  +     permissionTool.checkPermissions('INTERNET'),
  +     networkTool.checkConnectivity()
  + ]);
  ```
  *Estimated latency reduction:* **~90ms to 180ms per voice turn.**
- **Unprotected Deeplink Dispatch:** Automatically flags missing `try/catch` fallbacks to prevent voice crashes on uninstalled apps.

---

### 3. Interactive Web Dashboard
- **Glassmorphic Modern UI:** High-contrast dark theme with animated glowing gradients.
- **Interactive SVG Graph:** Real-time visual network of files, functions, and tool dependencies.
- **ReAct Step Visualizer:** Transparent visibility into the agent's plan, tool dispatches, and observations.
- **Diff & Snippet Viewer:** Integrated side-by-side optimization diffs.

---

## 🛠️ REST API Reference

FastAPI exposes full OpenAPI documentation at `https://aura-code-intelligence.onrender.com/docs`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Engine health status, indexing state, and graph node counts. |
| `POST` | `/api/query` | Executes agentic Plan-Search-Read-Refine loop for any query. |
| `GET` | `/api/graph` | Returns nodes and edges formatted for D3/SVG visualization. |
| `GET` | `/api/benchmark` | Returns latest benchmark metrics (Precision@k, Latency, Recall). |
| `POST` | `/api/index` | Re-indexes target codebase directory dynamically. |

---

## 📁 Repository Structure

```
aura-code-intelligence/
├── cli/
│   └── aura.py                    # Terminal CLI with rich ASCII formatting
├── engine/
│   ├── ast_parser.py              # Tree-sitter JS AST parser & call extractor
│   ├── graph_store.py             # NetworkX Code Property Graph & sequence solver
│   ├── vector_lexical_store.py    # Subword TF-IDF + BM25 CPU-optimized vectorizer
│   ├── agent_controller.py        # ReAct agentic retrieval loop (Plan-Search-Read-Refine)
│   ├── codepath_optimizer.py      # Voice assistant waterfall & deeplink optimizer
│   ├── benchmark.py               # 15-query ground-truth benchmark suite
│   ├── benchmark_results.json     # Stored benchmark metrics
│   └── server.py                  # FastAPI REST API & static UI mount
├── sample_voice_assistant/        # Realistic 14-file JS voice assistant codebase
│   ├── agents/                    # navigation_agent.js, media_agent.js, etc.
│   ├── tools/                     # device_tool.js, permission_tool.js, etc.
│   ├── config/                    # deeplinks.js, constants.js
│   └── test.js                    # Node.js end-to-end integration test
├── submission/
│   ├── CollegeName_TeamName_Submission.pptx # 12-slide official presentation
│   ├── LangAI3.0_AI_Disclosure.docx         # Official AI Usage Disclosure Form
│   └── DEMO_VIDEO_SCRIPT.md                 # 5-minute minute-by-minute demo script
├── tests/
│   └── test_engine.py             # 18 automated unit tests (Pytest)
├── ui/
│   ├── index.html                 # Web dashboard markup
│   ├── styles.css                 # Glassmorphic dark design system
│   └── app.js                     # SVG graph renderer & ReAct visualizer
├── Dockerfile                     # Production container spec
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Pinned Python dependencies
├── run.sh                         # Unified startup & verification script
└── README.md                      # Comprehensive documentation
```

---

## 📋 Hackathon Deliverables Checklist

- [x] **Working Prototype Code:** Public repository with full source (`https://github.com/AadityaBansal01/aura-code-intelligence`).
- [x] **Reproducible Setup:** Verified via `./run.sh` and `docker compose up --build`.
- [x] **100% CPU Execution:** Strictly zero GPU dependencies and zero cloud API keys.
- [x] **Benchmark Report:** Precision@1 (93.3%), Recall (93.3%), Latency (0.64ms on CPU).
- [x] **Demo Video Script:** 5-minute minute-by-minute script in [`submission/DEMO_VIDEO_SCRIPT.md`](submission/DEMO_VIDEO_SCRIPT.md).
- [x] **Presentation Deck:** Completed 12 slides in [`Thapar_TeamAURA_Submission.pptx`](Thapar_TeamAURA_Submission.pptx) and [`submission/Thapar_TeamAURA_Submission.pptx`](submission/Thapar_TeamAURA_Submission.pptx).
- [x] **AI Disclosure Form:** Completed in [`LangAI3.0_AI_Disclosure.docx`](LangAI3.0_AI_Disclosure.docx) and [`submission/LangAI3.0_AI_Disclosure.docx`](submission/LangAI3.0_AI_Disclosure.docx).
- [x] **Dependencies File:** Provided as both [`requirements.txt`](requirements.txt) and [`requirement.txt`](requirement.txt).
- [x] **Git Release Tag:** Committed and tagged with `PRISM_GENAI_HACKATHON_Y2026`.

---

## 👥 Team & Institution Details

**Team Name:** Team AURA  
**Hackathon Theme:** Theme 01 - Agentic Code Intelligence (Samsung PRISM GenAI Hackathon 3.0, 2026–27)  
**Institution:** Thapar Institute of Engineering and Technology (TIET), Patiala  
- **Aaditya Bansal** — Team Lead & Systems Architect (`aadityabansal740@gmail.com` | GitHub: [@AadityaBansal01](https://github.com/AadityaBansal01))  
- **Team AURA Engineers** — Program Analysis, AST Graph, & Benchmark Verification  

---

## 🎥 5-Minute Demo Video Walkthrough

- **Detailed Minute-by-Minute Script & Storyboard:** [`submission/DEMO_VIDEO_SCRIPT.md`](submission/DEMO_VIDEO_SCRIPT.md)
- **Demo Video Access:** [Watch 5-Minute Technical Demo on Google Drive / YouTube](https://drive.google.com/drive/folders/1g7H44ecwxfv7TPTFvQU14duMuGexMIQU) *(Recorded following the exact script in `submission/DEMO_VIDEO_SCRIPT.md`)*

