FETCH_VENDORS_QUERY = """
SELECT DISTINCT ON (v.vendor_id)
    v.vendor_id,
    v.name,
    v.service_type,
    v.locality,
    v.base_price,
    v.min_capacity,
    v.max_capacity,
    v.rating,
    v.description,
    v.latitude,
    v.longitude,
    v.search_keyword,
    v.capacity,
    vs.score
FROM vendors v
JOIN vendor_scores vs ON v.vendor_id = vs.vendor_id
JOIN vendor_availability va ON v.vendor_id = va.vendor_id
WHERE 
    v.search_keyword = ANY(%s)
    AND LOWER(v.locality) = ANY(%s)
    AND v.capacity >= %s
    AND va.is_available = TRUE
LIMIT %s;
"""

INSERT_EVENT_QUERY = """
INSERT INTO events (user_id, event_type, event_date, guest_count, min_budget, max_budget)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING event_id;
"""

INSERT_PLAN_QUERY = """
INSERT INTO event_plans (event_id, plan_type, total_cost, remaining_budget, optimization_score)
VALUES (%s, %s, %s, %s, %s)
RETURNING plan_id;
"""

INSERT_PLAN_DETAILS_QUERY = """
INSERT INTO plan_details (plan_id, vendor_id, allocated_budget, selection_score)
VALUES (%s, %s, %s, %s);
"""