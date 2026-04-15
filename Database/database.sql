-- Reset database
DROP DATABASE IF EXISTS event_management;
CREATE DATABASE event_management;

\c event_management;

-- USERS
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EVENTS
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    event_type TEXT,
    event_date DATE,
    guest_count INTEGER,
    min_budget NUMERIC,
    max_budget NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EVENT PLANS
CREATE TABLE event_plans (
    plan_id SERIAL PRIMARY KEY,
    event_id INTEGER,
    plan_type TEXT,
    total_cost NUMERIC,
    remaining_budget NUMERIC,
    optimization_score NUMERIC
);

-- PLAN DETAILS
CREATE TABLE plan_details (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER,
    vendor_id INTEGER,
    allocated_budget NUMERIC,
    selection_score NUMERIC
);

-- VENDORS (FINAL WITH GEO)
CREATE TABLE vendors (
    vendor_id SERIAL PRIMARY KEY,
    name TEXT,
    location TEXT,
    locality TEXT,
    service_type TEXT,
    rating NUMERIC,
    base_price NUMERIC,
    min_capacity INTEGER,
    max_capacity INTEGER,
    description TEXT,

    -- GEO + ML SUPPORT
    latitude NUMERIC,
    longitude NUMERIC,
    search_keyword TEXT,
    capacity INTEGER
);

-- RAW DATA
CREATE TABLE vendors_raw (
    place_id TEXT,
    name TEXT,
    rating NUMERIC,
    review_count INTEGER,
    business_status TEXT,
    open_now BOOLEAN,
    address TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    types TEXT,
    photo_reference TEXT,
    photo_url TEXT,
    category TEXT,
    search_keyword TEXT,
    search_area TEXT,
    phone TEXT,
    website TEXT,
    google_maps_url TEXT,
    photo_urls TEXT,
    has_images BOOLEAN,
    rating_missing BOOLEAN,
    review_missing BOOLEAN,
    estimated_price NUMERIC,
    capacity INTEGER,
    description TEXT,
    rating_score NUMERIC,
    review_score NUMERIC,
    price_score NUMERIC,
    capacity_score NUMERIC,
    vendor_score NUMERIC,
    price_per_guest NUMERIC,
    image_score NUMERIC
);

-- VENDOR SCORES
CREATE TABLE vendor_scores (
    vendor_id INTEGER PRIMARY KEY,
    score NUMERIC,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- VENDOR AVAILABILITY
CREATE TABLE vendor_availability (
    availability_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    available_month INTEGER,
    is_available BOOLEAN,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- REVIEWS
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    rating NUMERIC,
    comment TEXT
);