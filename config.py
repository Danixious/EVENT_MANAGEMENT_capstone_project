import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'eventiq-doon-secret-2024')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': Config,
    'default': DevelopmentConfig
}

# All Dehradun localities with profiling data
DEHRADUN_LOCALITIES = [
    {"name": "Rajpur Road",      "type": "upscale",     "vibe": "premium",    "traffic": "moderate"},
    {"name": "Sahastradhara",    "type": "scenic",      "vibe": "leisure",    "traffic": "low"},
    {"name": "Mussoorie Road",   "type": "scenic",      "vibe": "resort",     "traffic": "moderate"},
    {"name": "Clement Town",     "type": "residential", "vibe": "community",  "traffic": "low"},
    {"name": "Prem Nagar",       "type": "residential", "vibe": "community",  "traffic": "low"},
    {"name": "Vasant Vihar",     "type": "upscale",     "vibe": "premium",    "traffic": "low"},
    {"name": "Ballupur",         "type": "commercial",  "vibe": "mixed",      "traffic": "moderate"},
    {"name": "ISBT Area",        "type": "transit",     "vibe": "accessible", "traffic": "high"},
    {"name": "Paltan Bazaar",    "type": "commercial",  "vibe": "busy",       "traffic": "high"},
    {"name": "Clock Tower",      "type": "central",     "vibe": "heritage",   "traffic": "high"},
    {"name": "Race Course",      "type": "upscale",     "vibe": "spacious",   "traffic": "low"},
    {"name": "GMS Road",         "type": "commercial",  "vibe": "modern",     "traffic": "moderate"},
    {"name": "Haridwar Road",    "type": "highway",     "vibe": "accessible", "traffic": "high"},
    {"name": "Dalanwala",        "type": "central",     "vibe": "heritage",   "traffic": "moderate"},
    {"name": "Chakrata Road",    "type": "semi-rural",  "vibe": "open",       "traffic": "low"},
]

# Venues mapped to localities
VENUES = {
    "Rajpur Road": [
        {"name": "Pacific Hotel Banquet Hall",    "capacity": 500, "cost_per_head": 1200, "indoor": True,  "rating": 4.5},
        {"name": "Maa Shakumbhari Marriage Lawn", "capacity": 1000,"cost_per_head": 800,  "indoor": False, "rating": 4.2},
        {"name": "Hotel Madhuban Convention",     "capacity": 300, "cost_per_head": 1500, "indoor": True,  "rating": 4.7},
    ],
    "Vasant Vihar": [
        {"name": "Aman Palace Banquet",           "capacity": 700, "cost_per_head": 1400, "indoor": True,  "rating": 4.6},
        {"name": "Green Valley Lawn",             "capacity": 1200,"cost_per_head": 700,  "indoor": False, "rating": 4.1},
    ],
    "Sahastradhara": [
        {"name": "Sahastradhara Resort Hall",     "capacity": 400, "cost_per_head": 1100, "indoor": True,  "rating": 4.3},
        {"name": "Nature's Retreat Lawn",         "capacity": 600, "cost_per_head": 750,  "indoor": False, "rating": 4.0},
    ],
    "Mussoorie Road": [
        {"name": "Sterling Resort Convention",    "capacity": 300, "cost_per_head": 1800, "indoor": True,  "rating": 4.8},
        {"name": "Ananda Spa Banquet Wing",       "capacity": 250, "cost_per_head": 2200, "indoor": True,  "rating": 4.9},
    ],
    "Clement Town": [
        {"name": "DDA Community Centre",          "capacity": 300, "cost_per_head": 400,  "indoor": True,  "rating": 3.8},
        {"name": "Timber Trail Lawn",             "capacity": 500, "cost_per_head": 600,  "indoor": False, "rating": 3.9},
    ],
    "Prem Nagar": [
        {"name": "Shiva Palace Banquet",          "capacity": 400, "cost_per_head": 550,  "indoor": False, "rating": 3.9},
        {"name": "Prem Nagar Community Hall",     "capacity": 200, "cost_per_head": 350,  "indoor": True,  "rating": 3.7},
    ],
    "Ballupur": [
        {"name": "Ballupur Club House",           "capacity": 350, "cost_per_head": 900,  "indoor": True,  "rating": 4.1},
        {"name": "City Greens Lawn",              "capacity": 600, "cost_per_head": 650,  "indoor": False, "rating": 3.8},
    ],
    "ISBT Area": [
        {"name": "Hotel Srinagar Palace Hall",    "capacity": 400, "cost_per_head": 600,  "indoor": True,  "rating": 3.9},
        {"name": "Shri Ram Marriage Garden",      "capacity": 1500,"cost_per_head": 500,  "indoor": False, "rating": 3.7},
    ],
    "Race Course": [
        {"name": "Grand Legacy Banquet",          "capacity": 600, "cost_per_head": 1100, "indoor": True,  "rating": 4.5},
        {"name": "Osho Resort Convention Wing",   "capacity": 800, "cost_per_head": 1000, "indoor": True,  "rating": 4.4},
    ],
    "GMS Road": [
        {"name": "City Centre Banquet Hall",      "capacity": 500, "cost_per_head": 900,  "indoor": True,  "rating": 4.2},
        {"name": "Fun Valley Event Lawn",         "capacity": 800, "cost_per_head": 600,  "indoor": False, "rating": 3.9},
    ],
    "Haridwar Road": [
        {"name": "Hotel Dreamland Convention",    "capacity": 600, "cost_per_head": 800,  "indoor": True,  "rating": 4.0},
        {"name": "Royal Garden Marriage Lawn",    "capacity": 2000,"cost_per_head": 450,  "indoor": False, "rating": 3.8},
    ],
    "Clock Tower": [
        {"name": "Drona Hotel Banquet",           "capacity": 400, "cost_per_head": 1300, "indoor": True,  "rating": 4.4},
        {"name": "Survey Chowk Hall",             "capacity": 200, "cost_per_head": 500,  "indoor": True,  "rating": 3.6},
    ],
    "Dalanwala": [
        {"name": "Old Doon Club Ballroom",        "capacity": 300, "cost_per_head": 900,  "indoor": True,  "rating": 4.3},
    ],
    "Chakrata Road": [
        {"name": "Nature's Nest Farmhouse",       "capacity": 300, "cost_per_head": 800,  "indoor": False, "rating": 4.1},
    ],
    "Paltan Bazaar": [
        {"name": "Kwality Restaurant Banquet",    "capacity": 150, "cost_per_head": 700,  "indoor": True,  "rating": 3.8},
    ],
}

# Seasonal analysis for Dehradun
SEASONAL_DATA = {
    "January":   {"weather": "Cold & Foggy",       "risk": "high",   "crowd_factor": 0.70, "tip": "Dense fog can disrupt travel. Use indoor heated venues only."},
    "February":  {"weather": "Cold but Clearing",  "risk": "medium", "crowd_factor": 0.80, "tip": "Valentine's season — book venues at least 5 weeks early."},
    "March":     {"weather": "Warm & Pleasant",    "risk": "low",    "crowd_factor": 1.00, "tip": "Peak outdoor month. Holi dates may affect availability."},
    "April":     {"weather": "Warm & Dry",         "risk": "low",    "crowd_factor": 0.95, "tip": "Excellent for outdoor lawns. Evening slots preferred."},
    "May":       {"weather": "Hot & Dusty",        "risk": "medium", "crowd_factor": 0.85, "tip": "Tourist influx from plains. Early morning or evening slots only."},
    "June":      {"weather": "Pre-Monsoon Humid",  "risk": "medium", "crowd_factor": 0.75, "tip": "Unpredictable showers begin. Keep indoor backup ready."},
    "July":      {"weather": "Heavy Monsoon",      "risk": "high",   "crowd_factor": 0.60, "tip": "Avoid outdoor events entirely. Flooding risk on Haridwar Road."},
    "August":    {"weather": "Monsoon Continues",  "risk": "high",   "crowd_factor": 0.65, "tip": "Independence Day events popular but rain remains heavy."},
    "September": {"weather": "Post-Monsoon Damp",  "risk": "medium", "crowd_factor": 0.80, "tip": "Rains taper off late-month. Good for last-week events."},
    "October":   {"weather": "Pleasant & Clear",   "risk": "low",    "crowd_factor": 1.00, "tip": "Navratri & Dussehra season — extremely high demand. Book early!"},
    "November":  {"weather": "Cool & Crisp",       "risk": "low",    "crowd_factor": 0.95, "tip": "Diwali season. Possibly the best month for events in Dehradun."},
    "December":  {"weather": "Cold, Clear Skies",  "risk": "medium", "crowd_factor": 0.85, "tip": "Christmas & New Year — premium demand. Expect 20–30% price surge."},
}

# Event types with budget distribution & metadata
EVENT_TYPES = {
    "Wedding / Reception": {
        "budget_split": {"Venue & Stay": 30, "Catering": 35, "Decoration": 15, "Entertainment": 10, "Logistics & Misc": 10},
        "min_budget": 200000,
        "ideal_audience": "Family & Guests",
        "avg_duration_days": 2,
        "emoji": "💍",
    },
    "Corporate Conference": {
        "budget_split": {"Venue": 35, "Catering": 25, "AV & Tech": 20, "Branding": 10, "Logistics": 10},
        "min_budget": 80000,
        "ideal_audience": "Professionals",
        "avg_duration_days": 1,
        "emoji": "💼",
    },
    "College Fest": {
        "budget_split": {"Venue": 25, "Performers & Shows": 30, "Food Stalls": 20, "Decoration": 15, "Misc": 10},
        "min_budget": 40000,
        "ideal_audience": "Students",
        "avg_duration_days": 2,
        "emoji": "🎓",
    },
    "Birthday Party": {
        "budget_split": {"Venue": 30, "Catering & Cake": 30, "Decoration": 20, "Entertainment": 15, "Misc": 5},
        "min_budget": 15000,
        "ideal_audience": "Friends & Family",
        "avg_duration_days": 1,
        "emoji": "🎂",
    },
    "Cultural Program": {
        "budget_split": {"Venue": 30, "Performers": 35, "Sound & Lighting": 20, "Decoration": 10, "Misc": 5},
        "min_budget": 25000,
        "ideal_audience": "General Public",
        "avg_duration_days": 1,
        "emoji": "🎭",
    },
    "Sports Event": {
        "budget_split": {"Ground / Venue": 25, "Equipment": 20, "Prize Money": 25, "Refreshments": 20, "Misc": 10},
        "min_budget": 20000,
        "ideal_audience": "Youth / Athletes",
        "avg_duration_days": 1,
        "emoji": "⚽",
    },
    "Exhibition / Trade Fair": {
        "budget_split": {"Venue": 35, "Stall Setup": 30, "Marketing": 20, "Catering": 10, "Misc": 5},
        "min_budget": 120000,
        "ideal_audience": "General Public",
        "avg_duration_days": 3,
        "emoji": "🛍️",
    },
    "Seminar / Workshop": {
        "budget_split": {"Venue": 35, "Speakers & Trainers": 30, "Catering": 20, "Materials": 10, "Misc": 5},
        "min_budget": 12000,
        "ideal_audience": "Students / Professionals",
        "avg_duration_days": 1,
        "emoji": "📚",
    },
}