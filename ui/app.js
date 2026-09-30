/**
 * AURA-Code Frontend Controller
 * Connects UI with FastAPI backend for real-time Agentic Investigation,
 * SVG Graph Visualization, and Benchmark telemetry.
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const queryInput = document.getElementById('query-input');
    const searchBtn = document.getElementById('search-btn');
    const pillBtns = document.querySelectorAll('.pill-btn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    const agentPlanCard = document.getElementById('agent-plan-card');
    const intentBadge = document.getElementById('intent-badge');
    const latencyText = document.getElementById('query-latency-text');
    const stepsContainer = document.getElementById('steps-container');
    const optimizerContainer = document.getElementById('optimizer-container');
    const matchesContainer = document.getElementById('matches-container');

    const statNodes = document.getElementById('stat-nodes');
    const statEdges = document.getElementById('stat-edges');
    const statLatency = document.getElementById('stat-latency');

    // 1. Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.add('hidden'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.remove('hidden');

            if (targetId === 'tab-graph') {
                loadGraphVisualization();
            } else if (targetId === 'tab-benchmark') {
                loadBenchmarkReport();
            }
        });
    });

    // 2. Quick Query Pill Buttons
    pillBtns.forEach(pill => {
        pill.addEventListener('click', () => {
            queryInput.value = pill.getAttribute('data-query');
            executeQuery(queryInput.value);
        });
    });

    // 3. Search Action
    searchBtn.addEventListener('click', () => {
        if (queryInput.value.trim()) {
            executeQuery(queryInput.value.trim());
        }
    });

    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && queryInput.value.trim()) {
            executeQuery(queryInput.value.trim());
        }
    });

    // Initial Health & Stats Check
    fetchSystemStats();

    // Query Execution Function
    async function executeQuery(query) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<span>Thinking...</span>';

        // Switch to Investigation tab if not active
        document.querySelector('[data-tab="tab-investigation"]').click();

        try {
            const resp = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            if (!resp.ok) {
                throw new Error(`API Error: ${resp.status}`);
            }

            const data = await resp.json();
            renderInvestigationResults(data);
        } catch (err) {
            console.error('Query failed:', err);
            matchesContainer.innerHTML = `
                <div class="empty-state">
                    <h3 style="color: var(--accent-rose);">Investigation Failed</h3>
                    <p>${err.message}. Ensure backend engine server is running.</p>
                </div>
            `;
        } finally {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<span>Investigate</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
        }
    }

    function renderInvestigationResults(data) {
        // Show Plan & Steps
        agentPlanCard.classList.remove('hidden');
        intentBadge.textContent = data.query_type;
        latencyText.textContent = `${data.latency_ms}ms (CPU)`;

        stepsContainer.innerHTML = '';
        data.plan_steps.forEach(s => {
            const stepEl = document.createElement('div');
            stepEl.className = 'step-item';
            stepEl.innerHTML = `
                <div class="step-badge">${s.step}</div>
                <div class="step-content">
                    <h4>${escapeHtml(s.action)}</h4>
                    <p>${escapeHtml(s.observation)}</p>
                </div>
            `;
            stepsContainer.appendChild(stepEl);
        });

        // Show Bonus Optimizations
        optimizerContainer.innerHTML = '';
        if (data.optimizations && data.optimizations.length > 0) {
            optimizerContainer.classList.remove('hidden');
            data.optimizations.forEach(opt => {
                const optEl = document.createElement('div');
                optEl.className = 'optimizer-card';
                optEl.innerHTML = `
                    <div class="optimizer-header">
                        <span class="optimizer-tag">${opt.category}</span>
                        <span style="font-size: 11px; font-weight: 600; color: var(--accent-emerald);">Bonus Optimization</span>
                    </div>
                    <h3 style="font-size: 16px; margin-bottom: 6px;">${escapeHtml(opt.title)}</h3>
                    <p style="font-size: 13px; color: var(--text-muted);">${escapeHtml(opt.description)}</p>
                    <div style="font-size: 12px; color: var(--accent-emerald); font-weight: 600; margin-top: 6px;">
                        ⚡ Estimated Benefit: ${escapeHtml(opt.estimated_impact)}
                    </div>
                    <div class="diff-grid">
                        <div class="diff-box">
                            <div class="diff-title"><span>Original Code (Serial Waterfall)</span> <span style="color: var(--accent-rose);">- bottleneck</span></div>
                            <pre><code>${escapeHtml(opt.original_code)}</code></pre>
                        </div>
                        <div class="diff-box">
                            <div class="diff-title"><span>Optimized Proposal</span> <span style="color: var(--accent-emerald);">+ parallel</span></div>
                            <pre><code>${escapeHtml(opt.optimized_code)}</code></pre>
                        </div>
                    </div>
                `;
                optimizerContainer.appendChild(optEl);
            });
        } else {
            optimizerContainer.classList.add('hidden');
        }

        // Show Code Matches
        matchesContainer.innerHTML = '';
        if (!data.matches || data.matches.length === 0) {
            matchesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No Direct Match Found</h3>
                    <p>No code block met threshold criteria for '${escapeHtml(data.query)}'.</p>
                </div>
            `;
            return;
        }

        data.matches.forEach((m, idx) => {
            const matchCard = document.createElement('div');
            matchCard.className = 'match-card';
            matchCard.innerHTML = `
                <div class="match-header">
                    <div class="match-file-title">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
                        ${escapeHtml(m.file)}
                        <span class="match-lines">Lines ${m.line_start}–${m.line_end}</span>
                    </div>
                    <div class="match-confidence">Match Confidence: ${Math.round(m.confidence * 100)}%</div>
                </div>
                <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 10px;">${escapeHtml(m.reasoning)}</p>
                <div class="code-container">
                    <pre><code>${escapeHtml(m.full_context || m.snippet)}</code></pre>
                </div>
            `;
            matchesContainer.appendChild(matchCard);
        });
    }

    // System Stats Loader
    async function fetchSystemStats() {
        try {
            const resp = await fetch('/api/health');
            if (resp.ok) {
                const health = await resp.json();
                statNodes.textContent = `${health.nodes_count} AST Nodes`;
                statEdges.textContent = `${health.edges_count} Graph Edges`;
                statLatency.textContent = `< 1ms CPU Latency`;
            }
        } catch (e) {
            console.log('Using default system stats');
        }
    }

    // SVG Code Property Graph Visualizer
    async function loadGraphVisualization() {
        const svg = document.getElementById('cpg-svg');
        svg.innerHTML = '';

        try {
            const resp = await fetch('/api/graph');
            const data = await resp.json();

            // Simple responsive SVG force/radial visualization layout
            const width = svg.clientWidth || 900;
            const height = 520;
            const centerX = width / 2;
            const centerY = height / 2;

            // Group nodes by file
            const fileNodes = data.nodes.filter(n => n.type === 'FILE');
            const fnNodes = data.nodes.filter(n => n.type === 'FUNCTION');
            const toolNodes = data.nodes.filter(n => n.type === 'CALLEE');

            // Draw center hub
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

            // Connect files in circle
            const radius = Math.min(width, height) * 0.38;
            const fileCoords = {};

            fileNodes.forEach((fn, idx) => {
                const angle = (idx / fileNodes.length) * 2 * Math.PI;
                const x = centerX + radius * Math.cos(angle);
                const y = centerY + radius * Math.sin(angle);
                fileCoords[fn.id] = { x, y };

                // Draw node circle
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', x);
                circle.setAttribute('cy', y);
                circle.setAttribute('r', '8');
                circle.setAttribute('fill', '#6366f1');
                circle.setAttribute('stroke', '#a855f7');
                circle.setAttribute('stroke-width', '2');
                g.appendChild(circle);

                // Label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x + 12);
                text.setAttribute('y', y + 4);
                text.setAttribute('fill', '#94a3b8');
                text.setAttribute('font-size', '11');
                text.setAttribute('font-family', 'var(--font-mono)');
                text.textContent = fn.label.replace('.js', '');
                g.appendChild(text);
            });

            // Draw connections between adjacent modules
            for (let i = 0; i < fileNodes.length; i++) {
                const p1 = fileCoords[fileNodes[i].id];
                const p2 = fileCoords[fileNodes[(i + 1) % fileNodes.length].id];
                if (p1 && p2) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', p1.x);
                    line.setAttribute('y1', p1.y);
                    line.setAttribute('x2', p2.x);
                    line.setAttribute('y2', p2.y);
                    line.setAttribute('stroke', 'rgba(99, 102, 241, 0.25)');
                    line.setAttribute('stroke-width', '1.5');
                    line.setAttribute('stroke-dasharray', '4,4');
                    g.appendChild(line);
                }
            }

            // Draw center Core Node
            const coreCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            coreCircle.setAttribute('cx', centerX);
            coreCircle.setAttribute('cy', centerY);
            coreCircle.setAttribute('r', '20');
            coreCircle.setAttribute('fill', 'url(#hubGradient)');
            coreCircle.setAttribute('stroke', '#818cf8');
            coreCircle.setAttribute('stroke-width', '3');
            g.appendChild(coreCircle);

            const coreText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            coreText.setAttribute('x', centerX);
            coreText.setAttribute('y', centerY + 4);
            coreText.setAttribute('text-anchor', 'middle');
            coreText.setAttribute('fill', '#fff');
            coreText.setAttribute('font-size', '10');
            coreText.setAttribute('font-weight', 'bold');
            coreText.setAttribute('font-family', 'var(--font-sans)');
            coreText.textContent = 'CPG';
            g.appendChild(coreText);

            svg.appendChild(g);
        } catch (e) {
            console.error('Graph visualization load error:', e);
        }
    }

    // Benchmark Report Loader
    async function loadBenchmarkReport() {
        try {
            const resp = await fetch('/api/benchmark');
            const data = await resp.json();

            document.getElementById('kpi-p1').textContent = `${data.metrics.precision_at_1}%`;
            document.getElementById('kpi-recall').textContent = `${data.metrics.mean_recall}%`;
            document.getElementById('kpi-lat').textContent = `${data.metrics.mean_latency_ms} ms`;
            document.getElementById('kpi-index').textContent = `${data.indexing_cost.indexing_time_ms} ms`;

            const tbody = document.getElementById('benchmark-tbody');
            tbody.innerHTML = '';

            data.test_cases.forEach(tc => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-family: var(--font-mono); color: var(--primary-light);">${tc.id}</td>
                    <td><span style="font-size: 11px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.06);">${tc.category}</span></td>
                    <td style="font-weight: 500; color: #fff;">${escapeHtml(tc.query)}</td>
                    <td style="font-family: var(--font-mono); font-size: 11px;">${tc.expected.map(f => `<code>${f}</code>`).join(', ')}</td>
                    <td style="font-family: var(--font-mono); font-weight: 600; color: ${tc['p@1'] === 1 ? 'var(--accent-emerald)' : 'var(--accent-amber)'}">${tc['p@1'] === 1 ? '100%' : '0%'}</td>
                    <td style="font-family: var(--font-mono); font-weight: 600; color: var(--accent-emerald);">${Math.round(tc.recall * 100)}%</td>
                    <td style="font-family: var(--font-mono); color: var(--accent-cyan);">${tc.latency_ms}ms</td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Failed to load benchmark report:', err);
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
