/**
 * SmartAttend - Chart.js Visual Analytics Engine
 * Subject-wise breakdown, Regular vs Medical, Doughnut, Monthly Trends
 */

let subjectBarChart = null;
let doughnutChart = null;
let trendChart = null;
let comparisonChart = null;

document.addEventListener('DOMContentLoaded', () => {
  // Only initialize if chart canvases exist on the page
  if (document.getElementById('subjectAttendanceChart') || document.getElementById('overallDoughnutChart')) {
    loadChartAnalytics();
  }

  // Handle dynamic theme changes
  window.addEventListener('themeChanged', () => {
    if (document.getElementById('subjectAttendanceChart')) {
      loadChartAnalytics();
    }
  });
});

async function loadChartAnalytics() {
  try {
    const response = await fetch('/api/chart-data');
    if (!response.ok) return;
    const json = await response.json();
    if (!json.success) return;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';

    // 1. Subject-wise Attendance Bar Chart
    const barCanvas = document.getElementById('subjectAttendanceChart');
    if (barCanvas) {
      if (subjectBarChart) subjectBarChart.destroy();
      const ctx = barCanvas.getContext('2d');

      subjectBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: json.subject_bar.labels,
          datasets: [
            {
              label: 'Regular Attendance %',
              data: json.subject_bar.regular,
              backgroundColor: 'rgba(79, 70, 229, 0.85)',
              borderRadius: 6,
              barPercentage: 0.65,
            },
            {
              label: 'Medical Benefit %',
              data: json.subject_bar.medical,
              backgroundColor: 'rgba(6, 182, 212, 0.85)',
              borderRadius: 6,
              barPercentage: 0.65,
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: { color: textColor, font: { family: 'Inter', weight: '500' } }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: ${context.raw}%`;
                }
              }
            }
          },
          scales: {
            x: {
              stacked: true,
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Inter' } }
            },
            y: {
              stacked: true,
              max: 100,
              min: 0,
              grid: { color: gridColor },
              ticks: {
                color: textColor,
                callback: function(val) { return val + '%'; }
              }
            }
          }
        }
      });
    }

    // 2. Overall Attendance Doughnut Chart
    const doughnutCanvas = document.getElementById('overallDoughnutChart');
    if (doughnutCanvas) {
      if (doughnutChart) doughnutChart.destroy();
      const ctx = doughnutCanvas.getContext('2d');

      doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: json.doughnut.labels,
          datasets: [{
            data: json.doughnut.data,
            backgroundColor: [
              '#4f46e5', // Attended (Indigo)
              '#06b6d4', // Medical Approved (Cyan)
              '#ef4444'  // Missed (Red)
            ],
            borderWidth: 2,
            borderColor: isDark ? '#111827' : '#ffffff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: textColor, padding: 14, font: { family: 'Inter' } }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const total = context.dataset.data.reduce((a, b) => a + b, 0);
                  const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                  return `${context.label}: ${context.raw} classes (${pct}%)`;
                }
              }
            }
          },
          cutout: '72%'
        }
      });
    }

    // 3. Monthly Attendance Trends (Line Chart)
    const trendCanvas = document.getElementById('monthlyTrendChart');
    if (trendCanvas) {
      if (trendChart) trendChart.destroy();
      const ctx = trendCanvas.getContext('2d');

      trendChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: json.monthly_trend.months,
          datasets: [{
            label: 'Overall Attendance Trend %',
            data: json.monthly_trend.percentages,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#4f46e5',
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(ctx) { return `Attendance: ${ctx.raw}%`; }
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: textColor }
            },
            y: {
              min: 40,
              max: 100,
              grid: { color: gridColor },
              ticks: {
                color: textColor,
                callback: function(v) { return v + '%'; }
              }
            }
          }
        }
      });
    }

    // 4. Regular vs Medical Comparison Chart
    const compCanvas = document.getElementById('regularVsMedicalChart');
    if (compCanvas) {
      if (comparisonChart) comparisonChart.destroy();
      const ctx = compCanvas.getContext('2d');

      comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: json.subject_bar.labels,
          datasets: [
            {
              label: 'Regular Attendance %',
              data: json.subject_bar.regular,
              backgroundColor: '#4f46e5',
              borderRadius: 4
            },
            {
              label: 'Final Attendance (With Medical) %',
              data: json.subject_bar.final,
              backgroundColor: '#10b981',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: { color: textColor }
            }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: textColor } },
            y: {
              min: 0,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: textColor, callback: v => v + '%' }
            }
          }
        }
      });
    }

  } catch (err) {
    console.error('Failed to load chart analytics:', err);
  }
}
