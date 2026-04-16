
# FETCH FILTERED VENDORS
FETCH_VENDORS_QUERY = """
SELECT 
    v.place_id AS vendor_id,
    v.name,
    v.category AS service_type,
    v.search_area AS locality,
    
    -- Dynamic price calculation
    COALESCE(v.estimated_price, v.price_per_guest * %s, 10000) AS base_price,
    
    v.rating,
    v.latitude,
    v.longitude,
    v.search_keyword,
    v.capacity,
    v.vendor_score AS score,
    v.address,
    v.google_maps_url,
    v.phone,
    v.website
FROM vendors v
WHERE 
    LOWER(v.search_keyword) = ANY(%s)
    AND LOWER(v.search_area) = ANY(%s)
    AND v.capacity >= %s
LIMIT %s;
"""


# INSERT EVENT
INSERT_EVENT_QUERY = """
INSERT INTO events (user_id, event_type, event_date, guest_count, min_budget, max_budget)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING event_id;
"""


#INSERT PLAN
INSERT_PLAN_QUERY = """
INSERT INTO event_plans (event_id, plan_type, total_cost, remaining_budget, optimization_score)
VALUES (%s, %s, %s, %s, %s)
RETURNING plan_id;
"""


#  INSERT PLAN DETAILS
INSERT_PLAN_DETAILS_QUERY = """
INSERT INTO plan_details (plan_id, vendor_id, allocated_budget, selection_score)
VALUES (%s, %s, %s, %s);
"""