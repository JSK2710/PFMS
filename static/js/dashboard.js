// ─────────────────────────────────────────
// PIE CHART — Expense by Category
// ─────────────────────────────────────────

function renderPieChart(labels, values) {
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;

    if (!labels.length) {
        ctx.parentElement.innerHTML = `
            <div class="empty-chart">
                <i class="bi bi-pie-chart"></i>
                <p>No expense data yet</p>
            </div>`;
        return;
    }

    const colors = [
        '#ef476f', '#f78c6b', '#ffd166',
        '#06d6a0', '#4cc9f0', '#4361ee',
        '#b5179e', '#7209b7', '#560bad',
        '#480ca8'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: 'rgba(255,255,255,0.05)',
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255,255,255,0.6)',
                        padding: 16,
                        font: { size: 11 },
                        boxWidth: 12,
                        borderRadius: 4
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.parsed / total) * 100).toFixed(1);
                            return ` ₹${context.parsed.toLocaleString()} (${pct}%)`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}


// ─────────────────────────────────────────
// BAR CHART — Monthly Income vs Expense
// ─────────────────────────────────────────

function renderBarChart(labels, incomeData, expenseData) {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;

    if (!labels.length) {
        ctx.parentElement.innerHTML = `
            <div class="empty-chart">
                <i class="bi bi-bar-chart"></i>
                <p>No monthly data yet</p>
            </div>`;
        return;
    }

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    backgroundColor: 'rgba(6, 214, 160, 0.7)',
                    borderColor: '#06d6a0',
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'Expense',
                    data: expenseData,
                    backgroundColor: 'rgba(239, 71, 111, 0.7)',
                    borderColor: '#ef476f',
                    borderWidth: 1,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'rgba(255,255,255,0.6)',
                        font: { size: 11 },
                        boxWidth: 12,
                        borderRadius: 4
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ₹${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: 'rgba(255,255,255,0.5)', font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: {
                        color: 'rgba(255,255,255,0.5)',
                        font: { size: 11 },
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}


// ─────────────────────────────────────────
// AUTO DISMISS ALERTS
// ─────────────────────────────────────────

setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.classList.remove('show');
    });
}, 4000);