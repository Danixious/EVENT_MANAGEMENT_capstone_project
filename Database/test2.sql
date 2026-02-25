SELECT e.event_id, u.full_name, v.name AS venue_name
FROM events e
JOIN users u ON e.user_id = u.user_id
JOIN venues v ON e.venue_id = v.venue_id;