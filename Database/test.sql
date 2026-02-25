-- Insert test users
INSERT INTO users (full_name, email, phone)
VALUES 
('Daniel Natal', 'daniel@example.com', '9876543210'),
('Rahul Sharma', 'rahul@example.com', '9123456780');

-- Insert test venues
INSERT INTO venues (name, city, rating, price, capacity)
VALUES 
('Royal Palace Hall', 'Dehradun', 4.5, 150000, 300),
('Sunset Banquet', 'Dehradun', 4.2, 100000, 200);

-- Insert test vendors
INSERT INTO vendors (name, service_type, city, rating, price)
VALUES 
('Elite Catering', 'Catering', 'Dehradun', 4.7, 80000),
('DJ Thunder', 'Entertainment', 'Dehradun', 4.3, 30000);

-- Insert venue availability
INSERT INTO venue_availability (venue_id, available_date, is_available)
VALUES 
(1, '2026-03-10', TRUE),
(2, '2026-03-10', TRUE);

-- Insert vendor availability
INSERT INTO vendor_availability (vendor_id, available_date, is_available)
VALUES 
(1, '2026-03-10', TRUE),
(2, '2026-03-10', TRUE);

-- Insert test event
INSERT INTO events (user_id, venue_id, event_date, guest_count)
VALUES 
(1, 1, '2026-03-10', 250);

-- Insert booking
INSERT INTO bookings (user_id, venue_id, booking_date, total_price, status)
VALUES 
(1, 1, '2026-03-10', 150000, 'confirmed');

-- Map vendor to event
INSERT INTO event_vendor_mapping (event_id, vendor_id)
VALUES 
(1, 1),
(1, 2);

INSERT INTO events (user_id, venue_id, event_date, guest_count)
VALUES (999, 1, '2026-04-01', 100);
INSERT INTO venue_availability (venue_id, available_date)
VALUES (1, '2026-03-10');

DELETE FROM users WHERE user_id = 1;