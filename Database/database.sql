-- Drop and recreate database
DROP DATABASE IF EXISTS event_management;
CREATE DATABASE event_management;

-- Connect to database
\c event_management;

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY, -- Unique user ID
    full_name VARCHAR(150) NOT NULL, -- User full name
    email VARCHAR(150) UNIQUE NOT NULL, -- User email
    phone VARCHAR(15), -- Contact number
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Creation time
);

-- Raw venues table (from API/CSV)
CREATE TABLE venues_raw (
    venue_id SERIAL PRIMARY KEY, -- Unique venue ID
    name TEXT, -- Venue name
    location TEXT, -- Address
    city VARCHAR(100), -- City
    rating NUMERIC(2,1), -- Raw rating
    price NUMERIC, -- Raw price
    capacity INTEGER, -- Raw capacity
    source VARCHAR(100), -- Data source
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Scrape timestamp
);

-- Raw vendors table (from API/CSV)
CREATE TABLE vendors_raw (
    vendor_id SERIAL PRIMARY KEY, -- Unique vendor ID
    name TEXT, -- Vendor name
    location TEXT, -- Address
    city VARCHAR(100), -- City
    service_type VARCHAR(100), -- Vendor type
    rating NUMERIC(2,1), -- Raw rating
    price NUMERIC, -- Raw price
    capacity INTEGER, -- Raw capacity
    source VARCHAR(100), -- Data source
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Scrape timestamp
);

-- Cleaned venues table
CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY, -- Unique venue ID
    name VARCHAR(255) NOT NULL, -- Venue name
    location TEXT, -- Address
    city VARCHAR(100), -- City
    venue_space_type VARCHAR(100), -- Indoor/outdoor
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5), -- Clean rating
    rating_count INTEGER DEFAULT 0, -- Number of reviews
    price NUMERIC, -- Clean price
    price_type VARCHAR(50) DEFAULT 'per_event', -- Pricing model
    capacity INTEGER CHECK (capacity > 0), -- Capacity
    description TEXT, -- Description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Creation time
);

-- Cleaned vendors table
CREATE TABLE vendors (
    vendor_id SERIAL PRIMARY KEY, -- Unique vendor ID
    name VARCHAR(255) NOT NULL, -- Vendor name
    location TEXT, -- Address
    city VARCHAR(100), -- City
    service_type VARCHAR(100), -- Vendor type
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5), -- Clean rating
    rating_count INTEGER DEFAULT 0, -- Number of reviews
    price NUMERIC, -- Clean price
    price_type VARCHAR(50) DEFAULT 'per_event', -- Pricing model
    capacity INTEGER, -- Capacity
    description TEXT, -- Description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Creation time
);

-- Processed vendor features (feature store for ML)
CREATE TABLE processed_vendors (
    vendor_id INTEGER PRIMARY KEY, -- Linked vendor
    normalized_price NUMERIC, -- Normalized price
    demand_score NUMERIC, -- Demand score
    locality_score NUMERIC, -- Locality score
    reliability_score NUMERIC, -- Reliability score
    final_score NUMERIC, -- Final ML score
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Last update
    CONSTRAINT fk_processed_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- Locality statistics table
CREATE TABLE locality_stats (
    locality VARCHAR(150) PRIMARY KEY, -- Locality name
    avg_price NUMERIC, -- Average price
    vendor_count INTEGER, -- Number of vendors
    demand_index NUMERIC, -- Demand score
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Last update
);

-- Events table
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY, -- Unique event ID
    user_id INTEGER NOT NULL, -- Linked user
    venue_id INTEGER, -- Optional venue
    event_type VARCHAR(100), -- Event type
    event_date DATE NOT NULL, -- Event date
    guest_count INTEGER CHECK (guest_count > 0), -- Guests
    budget NUMERIC, -- Budget
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time
    CONSTRAINT fk_event_user FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_event_venue FOREIGN KEY(venue_id) REFERENCES venues(venue_id) ON DELETE SET NULL
);

-- Vendor availability table
CREATE TABLE vendor_availability (
    availability_id SERIAL PRIMARY KEY, -- Unique ID
    vendor_id INTEGER NOT NULL, -- Vendor reference
    available_date DATE NOT NULL, -- Available date
    is_available BOOLEAN DEFAULT TRUE, -- Availability flag
    CONSTRAINT fk_vendor_availability FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    CONSTRAINT unique_vendor_date UNIQUE (vendor_id, available_date)
);

-- Venue availability table
CREATE TABLE venue_availability (
    availability_id SERIAL PRIMARY KEY, -- Unique ID
    venue_id INTEGER NOT NULL, -- Venue reference
    available_date DATE NOT NULL, -- Available date
    is_available BOOLEAN DEFAULT TRUE, -- Availability flag
    CONSTRAINT fk_venue_availability FOREIGN KEY (venue_id) REFERENCES venues(venue_id) ON DELETE CASCADE,
    CONSTRAINT unique_venue_date UNIQUE (venue_id, available_date)
);

-- Event-Vendor mapping
CREATE TABLE event_vendor_mapping (
    id SERIAL PRIMARY KEY, -- Mapping ID
    event_id INTEGER NOT NULL, -- Event reference
    vendor_id INTEGER NOT NULL, -- Vendor reference
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Assignment time
    CONSTRAINT fk_event_mapping FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    CONSTRAINT fk_vendor_mapping FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    CONSTRAINT unique_event_vendor UNIQUE (event_id, vendor_id)
);

-- Bookings table
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY, -- Booking ID
    event_id INTEGER NOT NULL, -- Event reference
    vendor_id INTEGER, -- Vendor reference
    venue_id INTEGER, -- Venue reference
    booking_date DATE NOT NULL, -- Booking date
    final_price NUMERIC, -- Final price
    status VARCHAR(50) DEFAULT 'pending', -- Booking status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time
    CONSTRAINT fk_booking_event FOREIGN KEY(event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    CONSTRAINT fk_booking_vendor FOREIGN KEY(vendor_id) REFERENCES vendors(vendor_id) ON DELETE SET NULL,
    CONSTRAINT fk_booking_venue FOREIGN KEY(venue_id) REFERENCES venues(venue_id) ON DELETE SET NULL
);

-- Reviews table
CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY, -- Review ID
    user_id INTEGER NOT NULL, -- User reference
    venue_id INTEGER, -- Venue reference
    vendor_id INTEGER, -- Vendor reference
    rating NUMERIC(2,1), -- Rating
    comment TEXT, -- Review text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time
    CONSTRAINT fk_review_user FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_venue FOREIGN KEY(venue_id) REFERENCES venues(venue_id) ON DELETE CASCADE,
    CONSTRAINT fk_review_vendor FOREIGN KEY(vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- Vendor scoring table (ML output)
CREATE TABLE vendor_scores (
    vendor_id INTEGER PRIMARY KEY, -- Vendor reference
    score NUMERIC, -- ML score
    tier VARCHAR(50), -- Budget/mid/premium
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Last update
    CONSTRAINT fk_vendor_score FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- Event plans (AI generated plans)
CREATE TABLE event_plans (
    plan_id SERIAL PRIMARY KEY, -- Plan ID
    event_id INTEGER NOT NULL, -- Event reference
    plan_type VARCHAR(50), -- Budget/mid/premium
    total_cost NUMERIC, -- Total cost
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time
    CONSTRAINT fk_plan_event FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
);

-- Plan details (vendors inside a plan)
CREATE TABLE plan_details (
    id SERIAL PRIMARY KEY, -- Unique ID
    plan_id INTEGER NOT NULL, -- Plan reference
    vendor_id INTEGER NOT NULL, -- Vendor reference
    allocated_budget NUMERIC, -- Allocated budget
    CONSTRAINT fk_plan FOREIGN KEY (plan_id) REFERENCES event_plans(plan_id) ON DELETE CASCADE,
    CONSTRAINT fk_plan_vendor FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_vendors_city ON vendors(city);
CREATE INDEX idx_vendors_service ON vendors(service_type);
CREATE INDEX idx_venues_city ON venues(city);
CREATE INDEX idx_events_date ON events(event_date);