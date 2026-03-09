from flask import Flask, render_template, request, jsonify, session
import json
import math
from config import config, DEHRADUN_LOCALITIES, VENUES, SEASONAL_DATA, EVENT_TYPES

app = Flask(__name__)
app.config.from_object(config['development'])


# ── Venue Recommender ─────────────────────────────────────────────────────────
def get_recommended_venues(locality, budget, guests):
    """Return up to 3 suitable venues for the locality that fit within 40% of budget."""
    all_venues = VENUES.get(locality, [])
    if not all_venues:
        # Fallback: grab from the closest available key
        all_venues = list(VENUES.values())[0]

    results = []
    for v in all_venues:
        estimated = v["cost_per_head"] * guests
        pct = round((estimated / budget) * 100, 1) if budget else 0
        entry = {**v, "estimated_cost": estimated, "budget_pct": pct, "fits_budget": estimated <= budget * 0.45}
        results.append(entry)

    # Sort: budget-friendly first, then by rating
    results.sort(key=lambda x: (not x["fits_budget"], -x["rating"]))
    return results[:3]


# ── Budget Breakdown ──────────────────────────────────────────────────────────
def calculate_budget_breakdown(event_type, total_budget):
    """Split total budget across categories based on event-type norms."""
    split = EVENT_TYPES.get(event_type, EVENT_TYPES["Cultural Program"])["budget_split"]
    return {
        label: {
            "percent": pct,
            "amount": math.floor((pct / 100) * total_budget)
        }
        for label, pct in split.items()
    }


# ── Attendance Predictor ──────────────────────────────────────────────────────
def predict_attendance(guests_invited, event_type, month, locality_type):
    """Simple heuristic model combining seasonal, event-type, and locality factors."""
    seasonal   = SEASONAL_DATA.get(month, {})
    crowd_fac  = seasonal.get("crowd_factor", 0.85)

    type_fac = {
        "Wedding / Reception":     0.95,
        "Corporate Conference":    0.80,
        "College Fest":            0.72,
        "Birthday Party":          0.90,
        "Cultural Program":        0.78,
        "Sports Event":            0.68,
        "Exhibition / Trade Fair": 0.60,
        "Seminar / Workshop":      0.85,
    }.get(event_type, 0.80)

    loc_fac = {
        "upscale": 0.94, "scenic": 0.88, "residential": 0.92,
        "commercial": 0.85, "central": 0.87, "transit": 0.90,
        "highway": 0.82, "semi-rural": 0.75,
    }.get(locality_type, 0.85)

    predicted   = math.floor(guests_invited * crowd_fac * type_fac * loc_fac)
    confidence  = round(crowd_fac * type_fac * 100)
    no_show_pct = round((1 - (predicted / guests_invited)) * 100) if guests_invited else 0
    return predicted, min(confidence, 98), no_show_pct


# ── Risk Engine ───────────────────────────────────────────────────────────────
def identify_risks(event_type, month, budget, guests, locality):
    risks = []
    seasonal = SEASONAL_DATA.get(month, {})

    # Weather risk
    w_risk = seasonal.get("risk", "low")
    if w_risk in ("high", "medium"):
        risks.append({
            "level": w_risk,
            "category": "Weather",
            "icon": "🌧️",
            "issue": f"{seasonal['weather']} conditions expected in {month}.",
            "fix": "Book an indoor venue or arrange professional waterproof canopy setup."
        })

    # Budget tightness
    min_b = EVENT_TYPES.get(event_type, {}).get("min_budget", 0)
    if budget < min_b * 1.15:
        risks.append({
            "level": "medium",
            "category": "Budget",
            "icon": "💸",
            "issue": "Budget is close to the minimum recommended for this event type.",
            "fix": "Reduce guest count, simplify décor, or consider a community hall over premium venue."
        })

    # Crowd management
    if guests > 500:
        risks.append({
            "level": "medium",
            "category": "Crowd Management",
            "icon": "👥",
            "issue": "Large gatherings (500+) require dedicated security & parking planning.",
            "fix": "Hire licensed security personnel and pre-book a parking area nearby."
        })

    # Peak season booking
    if month in ["October", "November", "February", "March", "December"]:
        risks.append({
            "level": "low",
            "category": "Booking Urgency",
            "icon": "📅",
            "issue": f"{month} is peak event season in Dehradun. Venues fill up fast.",
            "fix": "Secure venue booking at least 6–8 weeks in advance with a written agreement."
        })

    # Traffic / accessibility
    locality_info = next((l for l in DEHRADUN_LOCALITIES if l["name"] == locality), {})
    if locality_info.get("traffic") == "high":
        risks.append({
            "level": "low",
            "category": "Traffic & Access",
            "icon": "🚦",
            "issue": f"{locality} experiences heavy traffic, especially on weekends.",
            "fix": "Share Google Maps pin with guests early and communicate alternate entry routes."
        })

    return risks


# ── Recommendations ───────────────────────────────────────────────────────────
def build_recommendations(event_type, locality, month, budget, guests, audience):
    tips = []
    seasonal = SEASONAL_DATA.get(month, {})

    tips.append({"icon": "🌦️", "title": "Seasonal Insight",
                 "body": seasonal.get("tip", "Plan well ahead.")})

    if event_type in ["Wedding / Reception", "Birthday Party", "Cultural Program"]:
        palette = "marigold garlands, mogra strings and warm amber lighting" if month in ["Oct","Nov","Mar","Apr"] else "fairy lights, pastel drapes and floral centrepieces"
        tips.append({"icon": "🎨", "title": "Décor Tip",
                     "body": f"Trending décor in Dehradun for {month}: {palette}. Local suppliers on Rajpur Road offer good wholesale rates."})

    if "student" in audience.lower() or event_type == "College Fest":
        tips.append({"icon": "📣", "title": "Marketing Channel",
                     "body": "Promote on Instagram Reels, WhatsApp broadcast lists, and put up posters at DIT University, UPES, and Graphic Era campuses."})
    elif "professional" in audience.lower() or "corporate" in event_type.lower():
        tips.append({"icon": "📣", "title": "Marketing Channel",
                     "body": "Use LinkedIn events, Uttarakhand Chamber of Commerce channels, and email newsletters to local business communities."})
    else:
        tips.append({"icon": "📣", "title": "Marketing Channel",
                     "body": "Dainik Jagran / Amar Ujala local inserts and Dehradun WhatsApp community groups deliver excellent local reach."})

    tips.append({"icon": "🍽️", "title": "Catering Partners",
                 "body": "Well-regarded caterers: Sanjha Chulha, Garhwali Rasoi, and Punjabi Zaika offer bulk booking discounts with quality Uttarakhand cuisine."})

    tips.append({"icon": "📋", "title": "Checklist",
                 "body": "Lock venue → confirm caterer → book sound/lighting → send invites → arrange transport → day-of coordinator. Start at least 6 weeks out."})

    return tips


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plan')
def plan():
    localities  = [l["name"] for l in DEHRADUN_LOCALITIES]
    event_types = list(EVENT_TYPES.keys())
    months      = list(SEASONAL_DATA.keys())
    return render_template('plan.html', localities=localities, event_types=event_types, months=months)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True)

    event_name = data.get('event_name', 'My Event').strip() or 'My Event'
    event_type = data.get('event_type', 'Cultural Program')
    locality   = data.get('locality', 'Rajpur Road')
    month      = data.get('month', 'March')
    guests     = max(1, int(data.get('guests', 100)))
    budget     = max(1000, int(data.get('budget', 100000)))
    audience   = data.get('audience', 'General Public')
    organizer  = data.get('organizer', 'Individual')

    loc_info   = next((l for l in DEHRADUN_LOCALITIES if l["name"] == locality),
                      {"type": "commercial", "vibe": "mixed", "traffic": "moderate"})
    seasonal   = SEASONAL_DATA.get(month, {})
    ev_info    = EVENT_TYPES.get(event_type, {})

    venues         = get_recommended_venues(locality, budget, guests)
    budget_bd      = calculate_budget_breakdown(event_type, budget)
    predicted, confidence, no_show = predict_attendance(guests, event_type, month, loc_info["type"])
    risks          = identify_risks(event_type, month, budget, guests, locality)
    recs           = build_recommendations(event_type, locality, month, budget, guests, audience)

    # Feasibility score (0–100)
    min_budget   = ev_info.get("min_budget", 1)
    budget_score = min(100, int((budget / min_budget) * 55))
    season_score = int(seasonal.get("crowd_factor", 0.8) * 30)
    risk_penalty = sum(15 if r["level"] == "high" else 8 if r["level"] == "medium" else 3 for r in risks)
    feasibility  = max(20, min(100, budget_score + season_score - risk_penalty))

    result = {
        "event_name":     event_name,
        "event_type":     event_type,
        "event_emoji":    ev_info.get("emoji", "🎉"),
        "locality":       locality,
        "locality_vibe":  loc_info.get("vibe", "mixed"),
        "month":          month,
        "guests":         guests,
        "budget":         budget,
        "audience":       audience,
        "organizer":      organizer,
        "weather":        seasonal.get("weather", "N/A"),
        "weather_risk":   seasonal.get("risk", "low"),
        "seasonal_tip":   seasonal.get("tip", ""),
        "venues":         venues,
        "budget_breakdown": budget_bd,
        "predicted_attendance":  predicted,
        "attendance_confidence": confidence,
        "no_show_pct":    no_show,
        "risks":          risks,
        "recommendations": recs,
        "feasibility_score": feasibility,
        "duration_days":  ev_info.get("avg_duration_days", 1),
        "cost_per_head":  round(budget / guests),
        "ideal_audience": ev_info.get("ideal_audience", "General"),
    }

    session['last_result'] = json.dumps(result)
    return jsonify({"ok": True, "data": result})


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/api/localities')
def api_localities():
    return jsonify(DEHRADUN_LOCALITIES)


@app.errorhandler(404)
def page_not_found(_):
    return render_template('index.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)