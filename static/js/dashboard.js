// Cloud Cost Monitoring Dashboard JavaScript

let monthlyTrendsChart, serviceBreakdownChart, regionAnalysisChart;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadAllData();
    updateLastUpdateTime();
    
    // Refresh data every 5 minutes
    setInterval(loadAllData, 300000);
});

// Initialize dashboard
function initializeDashboard() {
    console.log('Initializing Cloud Cost Monitoring Dashboard...');
}

// Load all dashboard data
async function loadAllData() {
    try {
        await Promise.all([
            loadMonthlyTrends(),
            loadServiceBreakdown(),
            loadRegionAnalysis(),
            loadIdleResources(),
            loadRecommendations(),
            updateKPIs()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load monthly cost trends
async function loadMonthlyTrends() {
    try {
        const response = await fetch('/api/monthly-trends');
        const data = await response.json();
        
        const ctx = document.getElementById('monthlyTrendsChart').getContext('2d');
        
        if (monthlyTrendsChart) {
            monthlyTrendsChart.destroy();
        }
        
        monthlyTrendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.months,
                datasets: [{
                    label: 'Monthly Cost ($)',
                    data: data.costs,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Cost: $' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading monthly trends:', error);
    }
}

// Load service breakdown
async function loadServiceBreakdown() {
    try {
        const response = await fetch('/api/service-breakdown');
        const data = await response.json();
        
        const ctx = document.getElementById('serviceBreakdownChart').getContext('2d');
        
        if (serviceBreakdownChart) {
            serviceBreakdownChart.destroy();
        }
        
        serviceBreakdownChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.services,
                datasets: [{
                    data: data.costs,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                        '#FF6384',
                        '#C9CBCF',
                        '#4BC0C0',
                        '#FF6384'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': $' + context.parsed.toLocaleString() + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading service breakdown:', error);
    }
}

// Load region analysis
async function loadRegionAnalysis() {
    try {
        const response = await fetch('/api/region-analysis');
        const data = await response.json();
        
        const ctx = document.getElementById('regionAnalysisChart').getContext('2d');
        
        if (regionAnalysisChart) {
            regionAnalysisChart.destroy();
        }
        
        regionAnalysisChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.regions,
                datasets: [{
                    label: 'Cost by Region ($)',
                    data: data.costs,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Cost: $' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading region analysis:', error);
    }
}

// Load idle resources
async function loadIdleResources() {
    try {
        const response = await fetch('/api/idle-resources');
        const data = await response.json();
        
        const container = document.getElementById('idleResourcesList');
        
        if (data.length === 0) {
            container.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> No idle resources detected!</div>';
            return;
        }
        
        let html = '';
        data.forEach(resource => {
            html += `
                <div class="idle-resource-item">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>${resource.service}</strong> in ${resource.region}
                    <span class="badge bg-warning float-end">${resource.count} resources</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading idle resources:', error);
        document.getElementById('idleResourcesList').innerHTML = '<div class="alert alert-danger">Error loading idle resources data</div>';
    }
}

// Load optimization recommendations
async function loadRecommendations() {
    try {
        const response = await fetch('/api/recommendations');
        const data = await response.json();
        
        const container = document.getElementById('recommendationsList');
        
        if (data.length === 0) {
            container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle"></i> No optimization recommendations at this time.</div>';
            return;
        }
        
        let html = '';
        data.forEach(rec => {
            const priorityClass = `priority-${rec.priority}`;
            html += `
                <div class="recommendation-item ${rec.priority}-priority">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6><i class="fas fa-lightbulb"></i> ${rec.description}</h6>
                            <p class="mb-1"><strong>Service:</strong> ${rec.service} | <strong>Region:</strong> ${rec.region}</p>
                            <p class="mb-0"><strong>Potential Savings:</strong> <span class="text-success">$${rec.potential_savings.toLocaleString()}</span></p>
                        </div>
                        <div class="ms-3">
                            <span class="priority-badge ${priorityClass}">${rec.priority.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading recommendations:', error);
        document.getElementById('recommendationsList').innerHTML = '<div class="alert alert-danger">Error loading recommendations data</div>';
    }
}

// Update KPI cards
async function updateKPIs() {
    try {
        // Get monthly trends data for total cost
        const trendsResponse = await fetch('/api/monthly-trends');
        const trendsData = await trendsResponse.json();
        
        const totalCost = trendsData.costs.length > 0 ? 
            trendsData.costs[trendsData.costs.length - 1] : 0;
        
        // Get service breakdown for active services
        const serviceResponse = await fetch('/api/service-breakdown');
        const serviceData = await serviceResponse.json();
        
        const activeServices = serviceData.services.length;
        
        // Get idle resources count
        const idleResponse = await fetch('/api/idle-resources');
        const idleData = await idleResponse.json();
        
        const idleResources = idleData.reduce((total, resource) => total + resource.count, 0);
        
        // Get recommendations for potential savings
        const recResponse = await fetch('/api/recommendations');
        const recData = await recResponse.json();
        
        const potentialSavings = recData.reduce((total, rec) => total + rec.potential_savings, 0);
        
        // Update DOM
        document.getElementById('totalCost').textContent = '$' + totalCost.toLocaleString();
        document.getElementById('activeServices').textContent = activeServices;
        document.getElementById('idleResources').textContent = idleResources;
        document.getElementById('potentialSavings').textContent = '$' + potentialSavings.toLocaleString();
        
    } catch (error) {
        console.error('Error updating KPIs:', error);
    }
}

// Update last update time
function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleString();
    document.getElementById('lastUpdated').textContent = timeString;
}

// Export data to CSV
function exportToCSV() {
    // This function can be implemented to export dashboard data to CSV
    console.log('Export to CSV functionality to be implemented');
}

// Generate PDF report
function generatePDFReport() {
    // This function can be implemented to generate PDF reports
    console.log('PDF report generation functionality to be implemented');
}

// Refresh dashboard data
function refreshDashboard() {
    loadAllData();
    updateLastUpdateTime();
}

// Download PDF Report
function downloadPDFReport() {
    try {
        // Show loading indicator
        const button = event.target;
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        button.disabled = true;
        
        // Create download link
        const link = document.createElement('a');
        link.href = '/api/download-report';
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Restore button after a short delay
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Error downloading PDF report:', error);
        alert('Error generating PDF report. Please try again.');
        
        // Restore button
        const button = event.target;
        button.innerHTML = '<i class="fas fa-file-pdf"></i> Download Report';
        button.disabled = false;
    }
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format percentage
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value);
}
