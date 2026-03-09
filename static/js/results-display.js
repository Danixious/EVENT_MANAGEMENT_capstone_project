// results-display.js — EventIQ result page renderer

document.addEventListener('DOMContentLoaded', () => {

    const root    = document.getElementById('resultRoot');
    const loading = document.getElementById('resultLoading');
    const raw     = sessionStorage.getItem('eventiq_result');

    if (!raw) {
        // No data — redirect to plan page
        window.location.href = '/plan';
        return;
    }

    const d = JSON.parse(raw);

    // ── Helpers ────────────────────────────────────────────────────────────
    function fmt(n) {
        if (n >= 10000000) return '₹' + (n / 10000000).toFixed(2) + ' Cr';
        if (n >= 100000)   return '₹' + (n / 100000).toFixed(2) + ' L';
        if (n >= 1000)     return '₹' + (n / 1000).toFixed(1) + 'K';
        return '₹' + Number(n).toLocaleString('en-IN');
    }

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    const riskColors = { high: '#b8412e', medium: '#c47b20', low: '#3d7a5e' };

    // ── Build result HTML ──────────────────────────────────────────────────
    function buildHTML() {

        // ── Header ──
        const feasBg = d.feasibility_score >= 70 ? '#3d7a5e' : d.feasibility_score >= 45 ? '#c47b20' : '#b8412e';
        const header = `
        <div class="result-header">
          <div class="result-header-inner">
            <a href="/plan" class="back-link" style="color:rgba(255,255,255,.45);margin-bottom:1.25rem;display:inline-flex;align-items:center;gap:.4rem;font-size:.875rem">← Plan Another Event</a>
            <h1 class="result-title">${esc(d.event_emoji)} ${esc(d.event_name)}</h1>
            <div class="result-meta">
              <span class="result-tag">📋 ${esc(d.event_type)}</span>
              <span class="result-tag">📍 ${esc(d.locality)}, Dehradun</span>
              <span class="result-tag">📅 ${esc(d.month)}</span>
              <span class="result-tag">👥 ${Number(d.guests).toLocaleString('en-IN')} Guests</span>
              <span class="result-tag">💰 ${fmt(d.budget)}</span>
            </div>
            <div class="feasibility-wrap">
              <div class="feasibility-label">
                <span>Event Feasibility Score</span>
                <strong id="feasNum" data-target="${d.feasibility_score}" style="color:${feasBg}">${d.feasibility_score}/100</strong>
              </div>
              <div class="feasibility-bar-bg">
                <div class="feasibility-bar-fill" id="feasBar" style="width:0%;background:${feasBg}"></div>
              </div>
            </div>
          </div>
        </div>`;

        // ── Venues ──
        let venueCards = '';
        if (d.venues && d.venues.length) {
            d.venues.forEach((v, i) => {
                const indoorTag = v.indoor ? '🏛️ Indoor' : '🌿 Outdoor';
                const fitBadge  = v.fits_budget
                    ? '<span class="badge-fit">✓ Fits Budget</span>'
                    : '<span class="badge-over">Over 45%</span>';
                venueCards += `
                <div class="venue-card ${i === 0 ? 'best-fit' : ''}">
                  <div class="venue-icon">${v.indoor ? '🏛️' : '🌿'}</div>
                  <div class="venue-info">
                    <div class="venue-name">${esc(v.name)} ${i === 0 ? '<span style="font-size:.75rem;color:var(--gold);margin-left:.4rem">★ Top Pick</span>' : ''}</div>
                    <div class="venue-details">
                      <span class="venue-detail">⭐ ${v.rating}</span>
                      <span class="venue-detail">👥 Up to ${Number(v.capacity).toLocaleString('en-IN')}</span>
                      <span class="venue-detail">${indoorTag}</span>
                      <span class="venue-detail">₹${v.cost_per_head}/head</span>
                    </div>
                    ${fitBadge}
                  </div>
                  <div class="venue-cost">${fmt(v.estimated_cost)}<br><span style="font-size:.78rem;font-weight:500;color:var(--ink-muted)">${v.budget_pct}% of budget</span></div>
                </div>`;
            });
        } else {
            venueCards = '<p style="color:var(--ink-muted);font-size:.9rem">No specific venues found for this locality. Try adjusting your guest count or budget.</p>';
        }

        // ── Budget breakdown ──
        let budgetRows = '';
        const colors = ['#c9913a','#6ab187','#7fabd4','#b98eca','#e07a5f','#52b788'];
        let ci = 0;
        for (const [label, obj] of Object.entries(d.budget_breakdown)) {
            const clr = colors[ci++ % colors.length];
            budgetRows += `
            <div class="budget-row">
              <span class="budget-label">${esc(label)}</span>
              <span class="budget-pct-tag">${obj.percent}%</span>
              <span class="budget-amount">${fmt(obj.amount)}</span>
            </div>
            <div class="budget-bar-full">
              <div class="budget-bar-inner" style="width:${obj.percent}%;background:${clr}"></div>
            </div>`;
        }

        // ── Attendance ──
        const attend = `
        <div class="attend-card">
          <div class="attend-big" data-counter="${d.predicted_attendance}">${Number(d.predicted_attendance).toLocaleString('en-IN')}</div>
          <div class="attend-invited">Predicted out of ${Number(d.guests).toLocaleString('en-IN')} invited</div>
          <div class="attend-stats">
            <div class="attend-stat">
              <strong>${d.attendance_confidence}%</strong>
              <span>Confidence</span>
            </div>
            <div class="attend-stat">
              <strong>${d.no_show_pct}%</strong>
              <span>No-show est.</span>
            </div>
            <div class="attend-stat">
              <strong>${fmt(d.cost_per_head)}</strong>
              <span>Cost/head</span>
            </div>
          </div>
        </div>`;

        // ── Risks ──
        let riskHTML = '';
        if (d.risks && d.risks.length) {
            d.risks.forEach(r => {
                riskHTML += `
                <div class="risk-item risk-${r.level}">
                  <div class="risk-top">
                    <span class="risk-icon">${r.icon}</span>
                    <span class="risk-cat">${esc(r.category)}</span>
                    <span style="font-size:.75rem;color:${riskColors[r.level]};font-weight:600;text-transform:uppercase;letter-spacing:.06em">${r.level} risk</span>
                  </div>
                  <div class="risk-issue">${esc(r.issue)}</div>
                  <div class="risk-fix">💡 ${esc(r.fix)}</div>
                </div>`;
            });
        } else {
            riskHTML = '<div class="risk-item risk-low"><div class="risk-fix">✅ No significant risks identified for this event plan. Good to go!</div></div>';
        }

        // ── Recommendations ──
        let recHTML = '';
        if (d.recommendations) {
            d.recommendations.forEach(rec => {
                recHTML += `
                <div class="rec-card">
                  <div class="rec-icon">${rec.icon}</div>
                  <div>
                    <div class="rec-title">${esc(rec.title)}</div>
                    <div class="rec-body">${esc(rec.body)}</div>
                  </div>
                </div>`;
            });
        }

        // ── Sidebar stats ──
        const sidebar = `
        <div class="result-sidebar">
          <div class="stats-panel">
            <h4>📊 Event Summary</h4>
            <div class="stat-row"><span>Event Type</span><strong>${esc(d.event_type)}</strong></div>
            <div class="stat-row"><span>Locality</span><strong>${esc(d.locality)}</strong></div>
            <div class="stat-row"><span>Month</span><strong>${esc(d.month)}</strong></div>
            <div class="stat-row"><span>Weather</span><strong>${esc(d.weather)}</strong></div>
            <div class="stat-row"><span>Guests Invited</span><strong>${Number(d.guests).toLocaleString('en-IN')}</strong></div>
            <div class="stat-row"><span>Total Budget</span><strong>${fmt(d.budget)}</strong></div>
            <div class="stat-row"><span>Cost/Head</span><strong>${fmt(d.cost_per_head)}</strong></div>
            <div class="stat-row"><span>Duration</span><strong>${d.duration_days} day${d.duration_days > 1 ? 's' : ''}</strong></div>
            <div class="stat-row"><span>Organiser</span><strong>${esc(d.organizer)}</strong></div>
            <div class="stat-row"><span>Audience</span><strong>${esc(d.audience)}</strong></div>
          </div>

          <div style="background:var(--cream);border:1.5px solid rgba(201,145,58,.18);border-radius:14px;padding:1.5rem">
            <h4 style="font-family:'Fraunces',serif;font-size:1rem;font-weight:700;color:var(--ink);margin-bottom:.75rem">🌦️ Seasonal Insight</h4>
            <p style="font-size:.875rem;color:var(--ink-soft);line-height:1.65">${esc(d.seasonal_tip)}</p>
          </div>

          <button class="plan-again-btn" onclick="window.location.href='/plan'">
            ← Plan Another Event
          </button>

          <button class="plan-again-btn" onclick="window.print()" style="background:var(--warm-off);color:var(--ink);font-weight:600">
            🖨️ Print / Save as PDF
          </button>
        </div>`;

        return `
        ${header}
        <div class="result-body">
          <div class="result-main">

            <div class="result-section">
              <h2 class="result-section-title">Recommended Venues</h2>
              <div class="venue-grid">${venueCards}</div>
            </div>

            <div class="result-section">
              <h2 class="result-section-title">Budget Distribution</h2>
              <div style="background:var(--cream);border:1.5px solid rgba(201,145,58,.18);border-radius:14px;padding:2rem">
                <div class="budget-breakdown-grid">${budgetRows}</div>
                <p style="margin-top:1.25rem;font-size:.82rem;color:var(--ink-muted)">
                  Total: <strong style="color:var(--ink)">${fmt(d.budget)}</strong> across ${Object.keys(d.budget_breakdown).length} categories
                </p>
              </div>
            </div>

            <div class="result-section">
              <h2 class="result-section-title">Predicted Attendance</h2>
              ${attend}
            </div>

            <div class="result-section">
              <h2 class="result-section-title">Risk Assessment</h2>
              <div class="risk-list">${riskHTML}</div>
            </div>

            <div class="result-section">
              <h2 class="result-section-title">Expert Recommendations</h2>
              <div class="rec-grid">${recHTML}</div>
            </div>

          </div>
          ${sidebar}
        </div>`;
    }

    // ── Render ─────────────────────────────────────────────────────────────
    if (loading) loading.remove();
    root.innerHTML = buildHTML();

    // ── Animate feasibility bar ────────────────────────────────────────────
    requestAnimationFrame(() => {
        setTimeout(() => {
            const bar = document.getElementById('feasBar');
            if (bar) bar.style.width = d.feasibility_score + '%';
        }, 200);
    });

    // ── Counter animations ─────────────────────────────────────────────────
    document.querySelectorAll('[data-counter]').forEach(el => {
        const target = parseInt(el.dataset.counter, 10);
        const start  = performance.now();
        const dur    = 1200;
        const tick   = (now) => {
            const t = Math.min((now - start) / dur, 1);
            const ease = 1 - Math.pow(1 - t, 3);
            el.textContent = Math.round(target * ease).toLocaleString('en-IN');
            if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    });

});