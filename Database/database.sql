DROP DATABASE IF EXISTS event_management;
CREATE DATABASE event_management;

\c event_management;


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_link TEXT,
    location TEXT,
    listing_type VARCHAR(100),
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
    price NUMERIC,
    description TEXT,
    venue_space_type VARCHAR(100),
    city VARCHAR(100),
    initial_price NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_venues_city ON venues(city);
CREATE INDEX idx_venues_rating ON venues(rating);


CREATE TABLE vendors (
    vendor_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_link TEXT,
    location TEXT,
    listing_type VARCHAR(100),
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
    price NUMERIC,
    description TEXT,
    service_type VARCHAR(100),
    city VARCHAR(100),
    initial_price NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendors_city ON vendors(city);


CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    guest_count INTEGER CHECK (guest_count > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_event_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_event_venue
        FOREIGN KEY(venue_id)
        REFERENCES venues(venue_id)
        ON DELETE CASCADE
);

CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    booking_date DATE NOT NULL,
    total_price NUMERIC,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_booking_venue
        FOREIGN KEY(venue_id)
        REFERENCES venues(venue_id)
        ON DELETE CASCADE
);


CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    rating NUMERIC(2,1) CHECK (rating >= 0 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_review_venue
        FOREIGN KEY(venue_id)
        REFERENCES venues(venue_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_reviews_venue ON reviews(venue_id);

-- Add capacity directly to venues
ALTER TABLE venues
ADD COLUMN capacity INTEGER CHECK (capacity > 0);

-- Venue availability table
CREATE TABLE venue_availability (
    availability_id SERIAL PRIMARY KEY,
    venue_id INTEGER NOT NULL,
    available_date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venue_availability
        FOREIGN KEY (venue_id)
        REFERENCES venues(venue_id)
        ON DELETE CASCADE,
    CONSTRAINT unique_venue_date UNIQUE (venue_id, available_date)
);

-- Vendor availability table
CREATE TABLE vendor_availability (
    availability_id SERIAL PRIMARY KEY,
    vendor_id INTEGER NOT NULL,
    available_date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vendor_availability
        FOREIGN KEY (vendor_id)
        REFERENCES vendors(vendor_id)
        ON DELETE CASCADE,
    CONSTRAINT unique_vendor_date UNIQUE (vendor_id, available_date)
);

-- Event vendor mapping table (many-to-many)
CREATE TABLE event_vendor_mapping (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_event_mapping
        FOREIGN KEY (event_id)
        REFERENCES events(event_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_vendor_mapping
        FOREIGN KEY (vendor_id)
        REFERENCES vendors(vendor_id)
        ON DELETE CASCADE,
    CONSTRAINT unique_event_vendor UNIQUE (event_id, vendor_id)
);