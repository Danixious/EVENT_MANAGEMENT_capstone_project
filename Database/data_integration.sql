-- Clean everything
TRUNCATE vendors_raw, vendors, vendor_scores, vendor_availability RESTART IDENTITY CASCADE;

-- Load CSV
COPY vendors_raw
FROM 'D:/EM_38/data/cleaned_vendor_dataset_fixed.csv'
DELIMITER ','
CSV HEADER
ENCODING 'LATIN1';

-- Insert into vendors
INSERT INTO vendors (
    name,
    location,
    locality,
    service_type,
    category,
    rating,
    base_price,
    min_capacity,
    max_capacity,
    description,
    latitude,
    longitude,
    search_keyword,
    capacity
)
SELECT 
    name,
    address,
    search_area,
    search_keyword,   
    category,         
    rating,
    estimated_price,
    capacity * 0.5,
    capacity,
    description,
    latitude,
    longitude,
    search_keyword,
    capacity
FROM vendors_raw;

-- Insert scores
INSERT INTO vendor_scores (vendor_id, score)
SELECT v.vendor_id, r.vendor_score
FROM vendors v
JOIN vendors_raw r ON v.name = r.name
ON CONFLICT DO NOTHING;

-- Insert availability
INSERT INTO vendor_availability (vendor_id, available_month, is_available)
SELECT vendor_id, (RANDOM()*11+1)::int, TRUE
FROM vendors
ON CONFLICT DO NOTHING;