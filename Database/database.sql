CREATE DATABASE event_management;
\c event_management;

CREATE TABLE venues(
    venue_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    image_link TEXT,
    location TEXT,
    listing_type TEXT,
    rating NUMERIC(2,1),
    price NUMERIC,
    description TEXT,
    venue_space_type TEXT,
    city TEXT,
    initial_price NUMERIC
);

CREATE TABLE vendors (
    vendor_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    image_link TEXT,
    location TEXT,
    listing_type TEXT,
    rating NUMERIC(2,1),
    price NUMERIC,
    description TEXT,
    service_type TEXT,
    city TEXT,
    initial_price NUMERIC
);