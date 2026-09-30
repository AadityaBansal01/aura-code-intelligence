# AURA-Code: 5-Minute Product Demo Video Script
**Samsung PRISM GenAI Hackathon 3.0 (Theme 01: Agentic Code Intelligence)**  
**Target Video Duration:** 04:55 (Max 5:00)  
**Presenter:** Team AURA (Aaditya Bansal & Team)

---

## Storyboard & Timeline Breakdown

```
[00:00 - 00:45] 1. The Monorepo Dilemma: Why Standard RAG Fails on Code
[00:45 - 01:45] 2. Our Architecture: The Neuro-Symbolic Agentic Dual-Engine
[01:45 - 03:00] 3. Live Product Walkthrough: Web Dashboard & CLI in Action
[03:00 - 03:55] 4. Brownie Points Bonus: Automated Voice Assistant CodePath Optimizer
[03:55 - 04:35] 5. Benchmark Results: Sub-Millisecond Speed on 100% CPU
[04:35 - 04:55] 6. Summary & GitHub Artifacts
```

---

### [00:00 - 00:45] Minute 1: The Monorepo Dilemma — Why Standard RAG Fails on Code

**[VISUAL: Screen recording showing a massive voice assistant repository with hundreds of JS files; overlay showing standard vector search failing on a sequence query.]**

> **SPEAKER:**  
> "Hello everyone! Welcome to our submission for Samsung PRISM GenAI Hackathon 3.0, Theme 01: Agentic Code Intelligence.
> 
> Imagine you are an engineer working on Samsung’s voice assistant ecosystem—navigating over 100,000 lines of complex, asynchronous JavaScript across dozens of agents and device tools.
> 
> When you ask standard AI code tools a structural question like:  
> *'Which files call tool `requestPermissions` before tool `launchDeeplink`?'*  
> ...standard Vector RAG fails completely.
> 
> Why? Because dense vector embeddings are order-blind! To cosine similarity, calling A before B produces almost the identical embedding as calling B before A. And feeding entire codebases into 1M-token LLMs is slow, costs money, and causes 'lost-in-the-middle' hallucinations.
> 
> We built **AURA-Code** to solve this permanently."

---

### [00:45 - 01:45] Minute 2: The Architecture — Neuro-Symbolic Agentic Dual-Engine

**[VISUAL: Clean architecture diagram showing: Layer 1 (Tree-sitter AST & NetworkX Code Property Graph), Layer 2 (Subword Vector/Lexical Engine), Layer 3 (ReAct Agentic Controller), and Layer 4 (CodePath Optimizer).]**

> **SPEAKER:**  
> "AURA-Code is a neuro-symbolic, autonomous code intelligence engine designed from the ground up to run **100% on CPU with zero cloud dependencies**.
> 
> It unites three powerful layers:
> 
> 1. **The Symbolic Program Layer:** Built on Tree-sitter for deterministic C-speed AST parsing and NetworkX for our Code Property Graph. It maps intra-procedural function scopes, exact call execution indices, and inverted deep link indices.
> 2. **The Neural-Lexical Layer:** A CPU-optimized subword vectorizer with CamelCase and snake_case tokenization, scoring both semantic similarity and concept coverage.
> 3. **The Autonomous ReAct Controller:** An agentic retrieval loop that executes **Plan → Search → Read → Refine**, dynamically routing structural queries to the AST graph and conceptual questions to the lexical engine.
> 
> Let's see it in action!"

---

### [01:45 - 03:00] Minute 3: Live Product Walkthrough (Dashboard & CLI)

**[VISUAL: Switch to browser at `http://localhost:8000`. Clean, dark glassmorphic dashboard with live KPIs, search bar, and interactive SVG call graph.]**

> **SPEAKER:**  
> "Here is the AURA-Code interactive dashboard. Notice our pre-flight healthcheck: 14 files indexed in just 11 milliseconds on pure CPU.
> 
> **Query 1: Structural Sequence Verification.**  
> Let's click the sample query: *'which files call tool requestPermissions before tool launchDeeplink?'*  
> Hit search.
> 
> Look at the speed: **0.58 milliseconds**!  
> Notice the step-by-step ReAct thought trace:  
> 1. Intent classified as `STRUCTURAL_SEQUENCE`.  
> 2. Extracted entities: `requestPermissions` before `launchDeeplink`.  
> 3. Scanned intra-procedural AST call order.  
> 4. Verified and synthesized exact line spans.
> 
> Look at the matches:  
> - `navigation_agent.js` lines 21 to 28 (verifying `ACCESS_FINE_LOCATION` before GPS deeplink).  
> - `settings_agent.js` lines 22 to 28 (verifying `BLUETOOTH_CONNECT` before settings deeplink).  
> In both cases, intra-procedural order is mathematically verified.
> 
> **Query 2: Deep Link Discovery.**  
> Now let's ask: *'where is the bluetooth settings deeplink used?'*  
> In **0.42 milliseconds**, it pinpoints the direct dispatch on line 28 of `settings_agent.js` and the URI definition in `config/deeplinks.js`.
> 
> **Query 3: Terminal CLI Execution.**  
> Everything you see in the UI is also available in our developer CLI.  
> Let's switch to terminal and run:  
> `./run.sh search "where does the assistant handle media playback interruptions"`  
> Boom! Instant ANSI-colored output surfacing `media_agent.js` lines 17-25 with context lines and zero hallucination."

---

### [03:00 - 03:55] Minute 4: Brownie Points Bonus — Automated CodePath Optimizer

**[VISUAL: Zoom in on the 'Bonus CodePath Optimizations' section of the dashboard showing the unified before/after diff card.]**

> **SPEAKER:**  
> "Now, for our hackathon brownie points feature: the **AURA-Code CodePath Optimizer**.
> 
> AURA-Code doesn't just passively find code—it actively optimizes the execution paths it discovers for voice assistants!
> 
> Look at this surfaced optimization card:  
> In `agents/media_agent.js`, the optimizer detected an **Async Waterfall Bottleneck**—sequential `await` statements fetching permissions and network state independently before playing a track.
> 
> AURA-Code automatically generated a drop-in code diff replacing the serial awaits with `Promise.all`:
> ```javascript
> const [permissionStatus, networkStatus] = await Promise.all([
>     permissionTool.checkPermissions('INTERNET'),
>     networkTool.checkConnectivity()
> ]);
> ```
> This single optimization slashes Voice-Turn-Around (VTA) latency by an estimated **90 to 180 milliseconds**, making voice interactions feel noticeably snappier to end users.
> 
> Furthermore, it flagged an **Unprotected Deeplink Dispatch** warning, suggesting a try/catch fallback to prevent assistant crashes on unsupported devices."

---

### [03:55 - 04:35] Minute 5: Evaluation Benchmark & Zero GPU Constraint

**[VISUAL: Switch to Benchmark tab or terminal showing `./run.sh benchmark` output table.]**

> **SPEAKER:**  
> "Let's review our formal evaluation results. We built a standardized benchmark harness with 15 ground-truth evaluation queries across all categories:
> 
> - **Precision@1:** **93.33%**
> - **Mean Recall:** **93.33%**
> - **Mean Inference Latency:** **0.64 milliseconds on CPU**
> - **P95 Latency:** **1.73 milliseconds**
> - **Cold Indexing Time:** **11.1 milliseconds**
> 
> Crucially, AURA-Code adheres 100% to the hackathon constraint: **it runs entirely on CPU**. It requires zero GPUs, zero cloud API keys, and has zero operational token costs. Your code stays completely private and secure."

---

### [04:35 - 04:55] Minute 6: Wrap-up & Deliverables Checklist

**[VISUAL: Showing GitHub repository with tagged release `PRISM_GENAI_HACKATHON_Y2026`, Docker setup, populated presentation, and AI disclosure form.]**

> **SPEAKER:**  
> "To summarize our deliverables:
> 1. Complete working prototype with interactive Web UI and CLI.
> 2. Full Docker containerization (`docker compose up --build`).
> 3. 18 automated unit tests passing 100% (`./run.sh test`).
> 4. Completed 12-slide presentation (`CollegeName_TeamName_Submission.pptx`).
> 5. Completed AI Usage Disclosure Form (`LangAI3.0_AI_Disclosure.docx`).
> 6. Release tag `PRISM_GENAI_HACKATHON_Y2026` published on Git.
> 
> AURA-Code demonstrates that neuro-symbolic agentic intelligence is the future of software engineering at scale.
> 
> Thank you to the Samsung PRISM and Language AI teams!"

---
*End of Script (Target: 4 mins 55 secs)*
