// Live Dashboard Charts for Loan Default System
Chart.defaults.color = 'rgba(255, 255, 255, 0.5)';
Chart.defaults.font.family = "'Inter', 'Poppins', sans-serif";

document.addEventListener('DOMContentLoaded', function () {

    // 1. Initialize empty charts with styling
    const riskCtx = document.getElementById('riskPieChart');
    let riskChart;
    if (riskCtx) {
        riskChart = new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)', // Success/Low
                        'rgba(245, 158, 11, 0.8)', // Warning/Medium
                        'rgba(239, 68, 68, 0.8)'   // Danger/High
                    ],
                    borderColor: ['#020a2b', '#020a2b', '#020a2b'],
                    borderWidth: 2,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 10, padding: 20, color: '#94a3b8', font: { size: 11 } } },
                    tooltip: { backgroundColor: '#0f172a', titleColor: '#fff', bodyColor: '#94a3b8', padding: 12, cornerRadius: 8 }
                },
                cutout: '78%'
            }
        });
    }

    const trendCtx = document.getElementById('loanTrendChart');
    let trendChart;
    if (trendCtx) {
        const grad = trendCtx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        grad.addColorStop(0, 'rgba(139, 92, 246, 0.2)');
        grad.addColorStop(1, 'rgba(139, 92, 246, 0)');

        trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Applications',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: grad,
                    borderWidth: 3,
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: 'rgba(255,255,255,0.1)',
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }

    // 2. NEW Forecast Chart
    const forecastCtx = document.getElementById('forecastChart');
    let forecastChart;
    if (forecastCtx) {
        forecastChart = new Chart(forecastCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Actual Delinquency',
                        data: [],
                        borderColor: '#06b6d4',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 4
                    },
                    {
                        label: 'AI Projection',
                        data: [],
                        borderColor: '#06b6d4',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: '#94a3b8', font: { size: 11 } } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }

    // 3. Fetch Live Data
    const fetchDashboardData = async () => {
        try {
            // Summary Data
            const summaryRes = await fetch('/api/dashboard/summary');
            const summaryData = await summaryRes.json();
            
            if (riskChart) {
                riskChart.data.datasets[0].data = [summaryData.low, summaryData.medium, summaryData.high];
                riskChart.update();
            }

            // Trend Data
            const trendRes = await fetch('/api/dashboard/trend');
            const trendData = await trendRes.json();
            
            if (trendChart) {
                trendChart.data.labels = trendData.labels;
                trendChart.data.datasets[0].data = trendData.data;
                trendChart.update();
            }

            // Forecast Data
            const forecastRes = await fetch('/api/portfolio/forecast');
            const forecastData = await forecastRes.json();
            
            if (forecastChart) {
                forecastChart.data.labels = forecastData.labels;
                forecastChart.data.datasets[0].data = forecastData.actual;
                forecastChart.data.datasets[1].data = forecastData.forecast;
                forecastChart.update();
            }

            // Update UI Counters
            updateCounter('metric-total', summaryData.total);
            updateCounter('metric-default-rate', summaryData.default_rate, '%');
            updateCounter('metric-defaulted', summaryData.high);
            
            // Sync Risk Scorer Gauge
            const riskGaugeValue = Math.round((summaryData.high / (summaryData.total || 1)) * 100);
            const scoreEl = document.getElementById('live-risk-score');
            if (scoreEl) {
                animateValue(scoreEl, parseInt(scoreEl.innerText) || 0, riskGaugeValue, 1000, '%');
            }
            
            // Decision Logic
            const decisionEl = document.getElementById('logic-decision');
            if (decisionEl) {
                if (riskGaugeValue > 70) {
                    decisionEl.innerText = "CRITICAL RISK";
                    decisionEl.style.color = "#ef4444";
                } else if (riskGaugeValue > 40) {
                    decisionEl.innerText = "ELEVATED RISK";
                    decisionEl.style.color = "#f59e0b";
                } else {
                    decisionEl.innerText = "OPTIMAL";
                    decisionEl.style.color = "#00f2fe";
                }
            }

        } catch (error) {
            console.error('Dashboard Live Sync Error:', error);
        }
    };

    const updateCounter = (id, value, suffix = '') => {
        const el = document.getElementById(id);
        if (el) {
            const current = parseFloat(el.innerText) || 0;
            animateValue(el, current, value, 1000, suffix);
        }
    };

    function animateValue(obj, start, end, duration, suffix) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const currentVal = progress * (end - start) + start;
            obj.innerHTML = (suffix === '%' ? currentVal.toFixed(1) : Math.floor(currentVal)) + suffix;
            if (progress < 1) window.requestAnimationFrame(step);
            else obj.innerHTML = (suffix === '%' ? end.toFixed(1) : Math.floor(end)) + suffix;
        };
        window.requestAnimationFrame(step);
    }

    // Initial Load
    fetchDashboardData();

    // Refresh every 30 seconds for "Live" feel
    setInterval(fetchDashboardData, 30000);
});
