/**
 * AdaptiveAI Frontend Interactive UI Script (Monochrome B&W Edition)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Tab Switching
    const tabs = document.querySelectorAll('.nav-tab');
    const tabPages = document.querySelectorAll('.tab-page');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            tabPages.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (target === 'tab-analytics') {
                loadMetricsAndCharts();
            } else if (target === 'tab-episodes') {
                loadEpisodesTable();
            } else if (target === 'tab-semantic') {
                loadSemanticKB();
            }
        });
    });

    // 2. Sample Prompt Chips
    const promptChips = document.querySelectorAll('.chip-prompt');
    const goalInput = document.getElementById('goal-input');

    promptChips.forEach(chip => {
        chip.addEventListener('click', () => {
            goalInput.value = chip.dataset.prompt;
        });
    });

    // 3. Task Execution Studio
    const btnExecute = document.getElementById('btn-execute');
    const strategyOverride = document.getElementById('strategy-override');
    const visualizerContent = document.getElementById('visualizer-content');
    const executionBadge = document.getElementById('execution-badge');

    btnExecute.addEventListener('click', async () => {
        const goal = goalInput.value.trim();
        if (!goal) {
            alert('Please enter a goal prompt before running task execution.');
            return;
        }

        const forceStrategy = strategyOverride.value || null;

        // Update UI state to Running
        btnExecute.disabled = true;
        btnExecute.querySelector('span').textContent = 'Executing...';
        executionBadge.className = 'badge badge-running';
        executionBadge.textContent = 'Running';

        visualizerContent.innerHTML = `
            <div class="step-card">
                <div class="step-card-header">
                    <span class="step-title">Phase 1: Task Analysis & Feature Extraction</span>
                    <span class="badge badge-running">Processing</span>
                </div>
                <p>Analyzing intent, token count, complexity score, and domain classification for: <em>"${escapeHtml(goal)}"</em></p>
            </div>
        `;

        try {
            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_goal: goal,
                    force_strategy: forceStrategy
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Task execution failed.');
            }

            const data = await response.json();
            renderExecutionVisualizer(data);

            executionBadge.className = 'badge badge-success';
            executionBadge.textContent = 'Completed';

            // Refresh analytics metrics in background
            loadMetricsAndCharts();
        } catch (err) {
            visualizerContent.innerHTML += `
                <div class="step-card" style="border-color: #71717A;">
                    <div class="step-card-header">
                        <span class="step-title" style="color: #A1A1AA;">Execution Failed</span>
                        <span class="badge badge-error">Error</span>
                    </div>
                    <p style="color: #A1A1AA;">${escapeHtml(err.message)}</p>
                </div>
            `;
            executionBadge.className = 'badge badge-error';
            executionBadge.textContent = 'Error';
        } finally {
            btnExecute.disabled = false;
            btnExecute.querySelector('span').textContent = 'Run Task';
        }
    });

    // 4. Render Step-by-Step Learning Visualizer (Monochrome)
    function renderExecutionVisualizer(data) {
        let html = '';

        // Step 1: Feature Extraction
        const feats = data.features;
        html += `
            <div class="step-card">
                <div class="step-card-header">
                    <span class="step-title">Phase 1: Task Understanding & Feature Vector</span>
                    <span class="badge badge-success">Domain: ${data.domain_category}</span>
                </div>
                <p><strong>Goal:</strong> ${escapeHtml(data.user_goal)}</p>
                <div style="margin-top: 6px; font-size: 0.85rem; color: #A1A1AA;">
                    Complexity: <strong>${data.complexity_score}</strong> | Tokens: <strong>${feats.token_count}</strong> |
                    Code: <strong>${feats.has_code_requirement}</strong> | Math: <strong>${feats.has_math_requirement}</strong>
                </div>
                <div class="code-block">Dense Vector: [${feats.feature_vector.join(', ')}]</div>
            </div>
        `;

        // Step 2: Strategy Selector (ML + Bandit)
        const candidateScores = data.candidate_scores;
        let scoreRows = '';
        for (const [strat, score] of Object.entries(candidateScores)) {
            const isChosen = strat === data.strategy_chosen;
            scoreRows += `
                <tr style="${isChosen ? 'color: #FFFFFF; font-weight: 700; background: #18181B;' : ''}">
                    <td>${strat} ${isChosen ? '★ Chosen' : ''}</td>
                    <td>${(score * 100).toFixed(1)}%</td>
                </tr>
            `;
        }

        html += `
            <div class="step-card">
                <div class="step-card-header">
                    <span class="step-title">Phase 2: Strategy Selection (ML Predictor + Bandit UCB1)</span>
                    <span class="badge badge-running">Mode: ${data.selection_mode}</span>
                </div>
                <p>Selected Strategy: <strong style="color: #FFFFFF; font-size: 1.05rem;">${data.strategy_chosen}</strong></p>
                <table class="data-table" style="margin-top: 10px;">
                    <thead>
                        <tr><th>Candidate Strategy</th><th>Predicted Probability / Score</th></tr>
                    </thead>
                    <tbody>${scoreRows}</tbody>
                </table>
            </div>
        `;

        // Step 3: Step-by-Step Tool Execution
        const stepResults = data.execution.step_results;
        let stepsHtml = '';
        stepResults.forEach(step => {
            stepsHtml += `
                <div style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #27272A;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>Step ${step.step_number}: ${escapeHtml(step.step_name)}</strong>
                        <span class="badge ${step.success ? 'badge-success' : 'badge-error'}">${step.tool_used ? 'Tool: ' + step.tool_used : 'Direct Reasoning'}</span>
                    </div>
                    <div class="code-block">${escapeHtml(step.output || step.error || 'No output')}</div>
                </div>
            `;
        });

        html += `
            <div class="step-card">
                <div class="step-card-header">
                    <span class="step-title">Phase 3: Subtask Plan & Execution Engine</span>
                    <span class="badge badge-success">${data.execution.step_count} Steps</span>
                </div>
                ${stepsHtml}
            </div>
        `;

        // Step 4: Result Evaluator & Experience Storage
        const evalRes = data.evaluation;
        html += `
            <div class="step-card" style="border-color: #FFFFFF;">
                <div class="step-card-header">
                    <span class="step-title" style="color: #FFFFFF;">Phase 4: Result Evaluator & Learning Store</span>
                    <span class="badge badge-success">Task ID: ${data.task_id}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 10px;">
                    <div>Success: <strong>${evalRes.success ? 'YES' : 'NO'}</strong></div>
                    <div>Quality Score: <strong>${evalRes.quality_score}</strong></div>
                    <div>Scalar Reward: <strong style="color: #FFFFFF; font-size: 1.1rem;">${evalRes.reward_score}</strong></div>
                </div>
                <p style="font-size: 0.85rem; color: #A1A1AA;">
                    Logged episode into Episodic Memory. ${data.auto_retrained ? 'Auto-retrained ML Model accuracy bump!' : 'Bandit stats updated.'}
                </p>
            </div>
        `;

        visualizerContent.innerHTML = html;
    }

    // 5. Chart.js Learning Analytics Dashboard (Monochrome Black & White)
    let chartLearningCurve = null;
    let chartStrategyDist = null;

    async function loadMetricsAndCharts() {
        try {
            const res = await fetch('/api/metrics');
            const data = await res.json();

            document.getElementById('kpi-total-tasks').textContent = data.total_tasks || 0;
            document.getElementById('kpi-success-rate').textContent = `${((data.overall_success_rate || 0) * 100).toFixed(1)}%`;
            document.getElementById('kpi-mean-reward').textContent = (data.mean_reward || 0).toFixed(2);

            const mlStatus = data.ml_model_status || {};
            document.getElementById('kpi-ml-status').textContent = mlStatus.status || 'Active';
            document.getElementById('kpi-ml-accuracy').textContent = `Accuracy: ${((mlStatus.accuracy || 0.85) * 100).toFixed(1)}% (${mlStatus.samples_count || 0} samples)`;

            // Render Learning Curve
            const curveData = data.learning_curve || [];
            const labels = curveData.map(c => `Task #${c.task_index}`);
            const successRates = curveData.map(c => c.window_success_rate * 100);
            const rewards = curveData.map(c => c.window_mean_reward);

            const ctx1 = document.getElementById('chart-learning-curve').getContext('2d');
            if (chartLearningCurve) chartLearningCurve.destroy();

            chartLearningCurve = new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Success Rate (%)',
                            data: successRates,
                            borderColor: '#FFFFFF',
                            backgroundColor: 'rgba(255, 255, 255, 0.08)',
                            fill: true,
                            tension: 0.2
                        },
                        {
                            label: 'Mean Reward',
                            data: rewards,
                            borderColor: '#A1A1AA',
                            backgroundColor: 'transparent',
                            borderDash: [4, 4],
                            tension: 0.2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { grid: { color: '#18181B' }, ticks: { color: '#A1A1AA' } },
                        x: { grid: { color: '#18181B' }, ticks: { color: '#A1A1AA' } }
                    },
                    plugins: { legend: { labels: { color: '#FFFFFF' } } }
                }
            });

            // Render Strategy Distribution (Monochrome grayscale slices)
            const stratDist = data.strategy_distribution || {};
            const stratLabels = Object.keys(stratDist);
            const stratCounts = Object.values(stratDist);

            const ctx2 = document.getElementById('chart-strategy-dist').getContext('2d');
            if (chartStrategyDist) chartStrategyDist.destroy();

            chartStrategyDist = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: stratLabels.length ? stratLabels : ['DirectExecution', 'ToolHeavyPipeline', 'ReActReasoning'],
                    datasets: [{
                        data: stratCounts.length ? stratCounts : [3, 5, 2],
                        backgroundColor: ['#FFFFFF', '#D4D4D8', '#A1A1AA', '#71717A', '#3F3F46'],
                        borderColor: '#000000'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: '#FFFFFF' } } }
                }
            });
        } catch (err) {
            console.error('Metrics loading error:', err);
        }
    }

    // 6. Episodic Memory Table & User Feedback
    async function loadEpisodesTable() {
        const tbody = document.getElementById('episodes-table-body');
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">Fetching episodic records...</td></tr>';

        try {
            const res = await fetch('/api/episodes?limit=50');
            const episodes = await res.json();

            if (!episodes || episodes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="10" class="text-center">No episodic records stored yet. Execute tasks to populate experience memory.</td></tr>';
                return;
            }

            let html = '';
            episodes.forEach(ep => {
                const stars = [1, 2, 3, 4, 5].map(s => {
                    const filled = (ep.feedback_rating || 0) >= s;
                    return `<span class="star ${filled ? 'filled' : ''}" data-taskid="${ep.task_id}" data-rating="${s}">★</span>`;
                }).join('');

                html += `
                    <tr>
                        <td><code>${ep.task_id}</code></td>
                        <td>${escapeHtml(ep.user_goal)}</td>
                        <td><span class="badge badge-idle">${ep.domain_category}</span></td>
                        <td>${ep.complexity_score}</td>
                        <td><strong>${ep.strategy_chosen}</strong></td>
                        <td>${ep.selection_mode}</td>
                        <td><span class="badge ${ep.success ? 'badge-success' : 'badge-error'}">${ep.success ? 'Success' : 'Failed'}</span></td>
                        <td>${ep.execution_time}s</td>
                        <td style="color: #FFFFFF; font-weight: 600;">${ep.reward_score}</td>
                        <td><div class="star-rating">${stars}</div></td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;

            // Attach Feedback Star Click Handlers
            document.querySelectorAll('.star-rating .star').forEach(star => {
                star.addEventListener('click', async (e) => {
                    const taskId = e.target.dataset.taskid;
                    const rating = parseInt(e.target.dataset.rating, 10);

                    try {
                        await fetch('/api/feedback', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ task_id: taskId, rating: rating })
                        });
                        loadEpisodesTable();
                    } catch (err) {
                        console.error('Feedback submit error:', err);
                    }
                });
            });
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="10" class="text-center" style="color: #A1A1AA;">Error loading episodes: ${escapeHtml(err.message)}</td></tr>`;
        }
    }

    document.getElementById('btn-refresh-episodes').addEventListener('click', loadEpisodesTable);

    // 7. Semantic Memory KB Search
    async function loadSemanticKB(query = '') {
        const container = document.getElementById('semantic-kb-container');
        container.innerHTML = '<p class="text-center" style="grid-column: 1/-1;">Loading semantic knowledge base...</p>';

        try {
            const url = query ? `/api/semantic-memory?query=${encodeURIComponent(query)}` : '/api/semantic-memory';
            const res = await fetch(url);
            const items = await res.json();

            if (!items || items.length === 0) {
                container.innerHTML = '<p class="text-center" style="grid-column: 1/-1;">No semantic templates matched.</p>';
                return;
            }

            let html = '';
            items.forEach(item => {
                html += `
                    <div class="semantic-card">
                        <div class="semantic-title">${item.id || 'Template'}: Domain [${item.domain}]</div>
                        <div class="semantic-meta">
                            <span>Recommended Strategy: <strong style="color: #FFFFFF;">${item.strategy || item.recommended_strategy}</strong></span>
                            ${item.similarity_score ? `<span>Match: <strong>${(item.similarity_score * 100).toFixed(0)}%</strong></span>` : ''}
                        </div>
                        <div class="code-block">${escapeHtml(item.template || item.solution_template)}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        } catch (err) {
            container.innerHTML = `<p style="color: #A1A1AA; grid-column: 1/-1;">Error loading KB: ${escapeHtml(err.message)}</p>`;
        }
    }

    document.getElementById('btn-semantic-search').addEventListener('click', () => {
        const q = document.getElementById('semantic-search-input').value.trim();
        loadSemanticKB(q);
    });

    // 8. Trigger Manual ML Model Retraining
    document.getElementById('btn-trigger-retrain').addEventListener('click', async () => {
        const btn = document.getElementById('btn-trigger-retrain');
        btn.disabled = true;
        btn.textContent = 'Training ML Model...';

        try {
            const res = await fetch('/api/retrain', { method: 'POST' });
            const data = await res.json();
            alert(`ML Model Retrain Results:\nStatus: ${data.status}\nSamples Trained: ${data.samples_count}\nAccuracy: ${(data.accuracy * 100).toFixed(1)}%\nClasses: ${data.classes_trained.join(', ')}`);
            loadMetricsAndCharts();
        } catch (err) {
            alert('Retrain error: ' + err.message);
        } finally {
            btn.disabled = false;
            btn.textContent = 'Retrain ML Model';
        }
    });

    // Utility HTML Escaper
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Initial load
    loadMetricsAndCharts();
});
