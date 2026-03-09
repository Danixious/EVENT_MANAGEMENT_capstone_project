// form-handler.js — EventIQ plan form logic

const SEASONAL_TIPS = {
    "January":   { weather: "Cold & Foggy",      risk: "high",   tip: "Dense fog can disrupt travel. Indoor heated venues strongly recommended." },
    "February":  { weather: "Cold but Clearing",  risk: "medium", tip: "Valentine's season — book venues at least 5 weeks early. Weather improving." },
    "March":     { weather: "Warm & Pleasant",    risk: "low",    tip: "Peak outdoor month! Ideal for lawns and open spaces in Dehradun." },
    "April":     { weather: "Warm & Dry",         risk: "low",    tip: "Excellent for outdoor events. Evening slots preferred to avoid afternoon heat." },
    "May":       { weather: "Hot & Dusty",        risk: "medium", tip: "Tourist influx from plains. Book early. Morning or evening events only." },
    "June":      { weather: "Pre-Monsoon Humid",  risk: "medium", tip: "Unpredictable showers begin. Keep an indoor backup plan ready." },
    "July":      { weather: "Heavy Monsoon",      risk: "high",   tip: "Avoid outdoor events entirely. Heavy rain and possible flooding." },
    "August":    { weather: "Monsoon Continues",  risk: "high",   tip: "Independence Day events popular but rain remains persistent." },
    "September": { weather: "Post-Monsoon Damp",  risk: "medium", tip: "Rains taper off late in the month. Good for last-week events." },
    "October":   { weather: "Pleasant & Clear",   risk: "low",    tip: "Peak event season! Navratri & Dussehra. Book venues 8 weeks ahead." },
    "November":  { weather: "Cool & Crisp",       risk: "low",    tip: "Diwali season — possibly the best month for events in Dehradun." },
    "December":  { weather: "Cold, Clear Skies",  risk: "medium", tip: "Christmas & New Year rush. Expect 20-30% price premium on venues." },
};

const EVENT_INFO = {
    "Wedding / Reception":    { min: 200000, audience: "Family & Guests",        emoji: "💍" },
    "Corporate Conference":   { min: 80000,  audience: "Working Professionals",  emoji: "💼" },
    "College Fest":           { min: 40000,  audience: "Students & Youth",        emoji: "🎓" },
    "Birthday Party":         { min: 15000,  audience: "Friends & Family",        emoji: "🎂" },
    "Cultural Program":       { min: 25000,  audience: "General Public",          emoji: "🎭" },
    "Sports Event":           { min: 20000,  audience: "Youth & Athletes",        emoji: "⚽" },
    "Exhibition / Trade Fair":{ min: 120000, audience: "General Public",          emoji: "🛍️" },
    "Seminar / Workshop":     { min: 12000,  audience: "Students & Professionals",emoji: "📚" },
};

document.addEventListener('DOMContentLoaded', () => {

    const form         = document.getElementById('eventForm');
    const budgetInput  = document.getElementById('budget');
    const budgetDisplay= document.getElementById('budgetDisplay');
    const monthSelect  = document.getElementById('month');
    const eventSelect  = document.getElementById('event_type');
    const submitBtn    = document.getElementById('submitBtn');
    const submitText   = document.getElementById('submitText');
    const submitSpinner= document.getElementById('submitSpinner');
    const seasonTip    = document.getElementById('sidebarSeasonTip');
    const eventInfo    = document.getElementById('sidebarEventInfo');

    if (!form) return;

    // ── Budget display ─────────────────────────────────────────────────────
    function updateBudgetDisplay() {
        const val = parseInt(budgetInput.value, 10);
        if (!val || val < 0) { budgetDisplay.textContent = ''; return; }
        budgetDisplay.textContent = '≈ ' + formatINR(val);
    }

    function formatINR(n) {
        if (n >= 10000000) return '₹' + (n / 10000000).toFixed(2) + ' Crore';
        if (n >= 100000)   return '₹' + (n / 100000).toFixed(2) + ' Lakh';
        if (n >= 1000)     return '₹' + (n / 1000).toFixed(1) + 'K';
        return '₹' + n.toLocaleString('en-IN');
    }

    budgetInput.addEventListener('input', updateBudgetDisplay);

    // ── Budget presets ─────────────────────────────────────────────────────
    document.querySelectorAll('.bp-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.bp-btn').forEach(b => b.classList.remove('is-active'));
            btn.classList.add('is-active');
            budgetInput.value = btn.dataset.val;
            updateBudgetDisplay();
            clearError('budget');
        });
    });

    // ── Month → seasonal sidebar ───────────────────────────────────────────
    monthSelect.addEventListener('change', () => {
        const month = monthSelect.value;
        const data  = SEASONAL_TIPS[month];
        if (!data || !seasonTip) return;

        const riskColor = { low: '#3d7a5e', medium: '#c47b20', high: '#b8412e' }[data.risk] || '#888';
        const riskLabel = { low: '✅ Low Risk', medium: '⚠️ Medium Risk', high: '🚨 High Risk' }[data.risk] || '';

        seasonTip.innerHTML = `
            <strong style="color:var(--ink)">${month} — ${data.weather}</strong><br>
            <span style="color:${riskColor};font-weight:600;font-size:.82rem">${riskLabel}</span><br><br>
            ${data.tip}
        `;
    });

    // ── Event type → info sidebar ─────────────────────────────────────────
    eventSelect.addEventListener('change', () => {
        const et = eventSelect.value;
        const info = EVENT_INFO[et];
        if (!info || !eventInfo) return;
        eventInfo.innerHTML = `
            <h4>${info.emoji} ${et}</h4>
            <p style="margin-bottom:.6rem">
                <strong>Recommended minimum budget:</strong><br>
                <span style="color:var(--green);font-size:1.1rem;font-weight:700">${formatINR(info.min)}</span>
            </p>
            <p>
                <strong>Ideal for:</strong> ${info.audience}
            </p>
        `;
    });

    // ── Validation ─────────────────────────────────────────────────────────
    function setError(field, msg) {
        const el = document.getElementById('err_' + field);
        if (el) el.textContent = msg;
        const input = document.getElementById(field);
        if (input) input.style.borderColor = 'var(--red)';
    }

    function clearError(field) {
        const el = document.getElementById('err_' + field);
        if (el) el.textContent = '';
        const input = document.getElementById(field);
        if (input) input.style.borderColor = '';
    }

    function validateForm() {
        let valid = true;
        const fields = [
            { id: 'event_name', msg: 'Please enter an event name.' },
            { id: 'event_type', msg: 'Please select an event type.' },
            { id: 'locality',   msg: 'Please select a locality.' },
            { id: 'month',      msg: 'Please select a month.' },
            { id: 'audience',   msg: 'Please select an audience type.' },
        ];

        fields.forEach(f => {
            const el = document.getElementById(f.id);
            if (!el || !el.value.trim()) { setError(f.id, f.msg); valid = false; }
            else clearError(f.id);
        });

        const guests = parseInt(document.getElementById('guests').value, 10);
        if (!guests || guests < 10) {
            setError('guests', 'Please enter at least 10 guests.'); valid = false;
        } else if (guests > 5000) {
            setError('guests', 'Maximum 5000 guests supported.'); valid = false;
        } else {
            clearError('guests');
        }

        const budget = parseInt(document.getElementById('budget').value, 10);
        if (!budget || budget < 5000) {
            setError('budget', 'Minimum budget is ₹5,000.'); valid = false;
        } else {
            clearError('budget');
        }

        return valid;
    }

    // ── Form submit ────────────────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        // UI: loading state
        submitBtn.disabled = true;
        submitText.classList.add('hidden');
        submitSpinner.classList.remove('hidden');

        const payload = {
            event_name: document.getElementById('event_name').value.trim(),
            event_type: document.getElementById('event_type').value,
            locality:   document.getElementById('locality').value,
            month:      document.getElementById('month').value,
            guests:     parseInt(document.getElementById('guests').value, 10),
            budget:     parseInt(document.getElementById('budget').value, 10),
            audience:   document.getElementById('audience').value,
            organizer:  document.getElementById('organizer').value,
        };

        try {
            const res  = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const json = await res.json();

            if (!res.ok || !json.ok) {
                throw new Error(json.error || 'Server error. Please try again.');
            }

            // Persist to sessionStorage, navigate to result
            sessionStorage.setItem('eventiq_result', JSON.stringify(json.data));
            window.location.href = '/result';

        } catch (err) {
            alert('Error: ' + err.message);
            submitBtn.disabled = false;
            submitText.classList.remove('hidden');
            submitSpinner.classList.add('hidden');
        }
    });

    // ── Live validation on blur ───────────────────────────────────────────
    ['event_name','event_type','locality','month','guests','budget','audience'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('blur', () => validateForm());
    });

});