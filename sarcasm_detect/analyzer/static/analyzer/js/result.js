// result.js — Chart.js radar chart for modality scores + ablation loader

document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('radarChart');
  if (!ctx || typeof scores === 'undefined') return;

  const COLORS = {
    text:   '#4361ee',
    image:  '#7209b7',
    emoji:  '#f8961e',
  };

  const labels = Object.keys(scores).map(k => k.charAt(0).toUpperCase() + k.slice(1));
  const values = Object.values(scores).map(v => Math.round(v * 100));
  const bgColors = Object.keys(scores).map(k => COLORS[k] || '#888');

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Sarcasm Score (%)',
        data: values,
        backgroundColor: 'rgba(255, 214, 10, 0.15)',
        borderColor: '#ffd60a',
        borderWidth: 2,
        pointBackgroundColor: bgColors,
        pointBorderColor: '#fff',
        pointRadius: 6,
        pointHoverRadius: 8,
      }]
    },
    options: {
      responsive: true,
      scales: {
        r: {
          min: 0, max: 100,
          ticks: { color: '#888', backdropColor: 'transparent', stepSize: 25 },
          grid: { color: '#2a2d4a' },
          pointLabels: { color: '#ccc', font: { size: 14, weight: '500' } },
          angleLines: { color: '#2a2d4a' },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e2030',
          borderColor: '#ffd60a',
          borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.formattedValue}% sarcasm signal`
          }
        }
      }
    }
  });
});

// ── Ablation loader ──────────────────────────────────────────────────────────
async function loadAblation(analysisId) {
  const section = document.getElementById('ablationSection');
  const content = document.getElementById('ablationContent');
  section.classList.remove('d-none');
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const resp = await fetch(`/api/ablation/${analysisId}/`);
    const data = await resp.json();
    if (!resp.ok) throw new Error('Failed to load ablation data.');

    const modScores = data.modality_scores;
    const ablation = data.ablation;

    let html = `<h6 class="text-muted mb-3"><i class="fa fa-chart-bar me-1"></i>Individual Modality Scores</h6>
    <table class="table table-dark table-sm ablation-table mb-4">
      <thead><tr><th>Modality</th><th>Score</th><th>Signal</th></tr></thead><tbody>`;
    for (const [mod, score] of Object.entries(modScores)) {
      if (mod === 'claude') continue;
      const pct = Math.round(score * 100);
      const color = score > 0.5 ? 'danger' : 'success';
      html += `<tr>
        <td class="text-capitalize fw-semibold">${mod}</td>
        <td><div class="progress" style="width:140px;height:10px;display:inline-flex;">
          <div class="progress-bar bg-${color}" style="width:${pct}%"></div></div>
          <span class="ms-2 fw-semibold">${pct}%</span></td>
        <td><span class="badge bg-${color} px-3">${score > 0.5 ? '🎭 Sarcastic' : '✅ Non-Sarcastic'}</span></td>
      </tr>`;
    }
    html += `</tbody></table>`;

    html += `<h6 class="text-muted mb-3"><i class="fa fa-flask me-1"></i>Without Each Modality (Ablation)</h6>
    <table class="table table-dark table-sm ablation-table">
      <thead><tr><th>Condition</th><th>Verdict</th><th>Confidence</th></tr></thead><tbody>`;
    for (const [key, val] of Object.entries(ablation)) {
      if (key.includes('claude')) continue;
      const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      const badge = val.is_sarcastic ? 'danger' : 'success';
      const icon = val.is_sarcastic ? '🎭' : '✅';
      html += `<tr>
        <td>${label}</td>
        <td><span class="badge bg-${badge} px-3">${icon} ${val.is_sarcastic ? 'Sarcastic' : 'Non-Sarcastic'}</span></td>
        <td class="fw-semibold">${val.confidence.toFixed(1)}%</td>
      </tr>`;
    }
    html += `</tbody></table>`;
    content.innerHTML = html;
  } catch (err) {
    content.innerHTML = `<div class="alert alert-danger"><i class="fa fa-exclamation-triangle me-1"></i>Error: ${err.message}</div>`;
  }
}
