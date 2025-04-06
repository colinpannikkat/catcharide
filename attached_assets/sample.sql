INSERT INTO users (first_name, last_name, email, phone_number, is_verified) VALUES
    ('John', 'Doe', 'john.doe@example.com', '+1234567890', TRUE),
    ('Jane', 'Smith', 'jane.smith@example.com', '+2345678901', TRUE),
    ('Alice', 'Brown', 'alice.brown@example.com', '+3456789012', TRUE),
    ('Sam', 'Wilson', 'sam.wilson@example.com', '+4567890123', TRUE),
    ('Emily', 'Davis', 'emily.davis@example.com', '+5678901234', TRUE),
    ('Michael', 'Johnson', 'michael.johnson@example.com', '+6789012345', TRUE),
    ('Chris', 'Evans', 'chris.evans@example.com', '+7890123456', TRUE);

INSERT INTO ride_offers (driver_id, origin, destination, departure_time, available_seats, description) VALUES
    (1, 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', 'ChIJGRlQrLAZwVQRTYlDSolh7Fc', '2025-04-19T08:00:00Z', 3, 'Morning ride down I-5 to Eugene, coffee stops welcome.'), --Portland to Eugene
    (1, 'ChIJUdLTpf_AuFQRtNEgx6zniBA', 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', '2025-04-19T09:00:00Z', 2, 'Heading to Portland, pet-friendly ride.'), --Bend to Portland
    (2, 'ChIJGRlQrLAZwVQRTYlDSolh7Fc', 'ChIJY5xLvPz-v1QRwlcDj-ApNPk', '2025-04-19T10:00:00Z', 4, 'Quick trip to the capital, AC and good music.'), --Eugene to Salem
    (2, 'ChIJY5xLvPz-v1QRwlcDj-ApNPk', 'ChIJfdcUqp1AwFQRvsC9Io-ADdc', '2025-04-19T11:45:00Z', 3, 'Afternoon chill ride to Corvallis.'), --Salem to Corvallis
    (3, 'ChIJu1GMTtTUuFQRGHlrwGDSOJQ', 'ChIJUdLTpf_AuFQRtNEgx6zniBA', '2025-04-19T07:30:00Z', 2, 'Short morning hop to Bend. On time guaranteed!'), --Eugene to Portland
    (3, 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', 'ChIJUdLTpf_AuFQRtNEgx6zniBA', '2025-04-19T10:30:00Z', 4, 'Quick trip to Bend, AC and good music.'), --Eugene to Salem
    (1, 'ChIJUdLTpf_AuFQRtNEgx6zniBA', 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', '2025-04-19T09:15:00Z', 2, 'Cruising back to PDX, pet-friendly ride.'), --Bend to Portland
    (2, 'ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', '2025-04-19T12:00:00Z', 3, 'Afternoon ride to Portland, coffee stops welcome.'); --Corvallis to Portland

INSERT INTO ride_requests (rider_id, origin, destination, departure_time) VALUES
    (4, 'ChIJGRlQrLAZwVQRTYlDSolh7Fc', 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', '2025-04-19T14:00:00Z'), --Eugene to Portland
    (5, 'ChIJY5xLvPz-v1QRwlcDj-ApNPk', 'ChIJUdLTpf_AuFQRtNEgx6zniBA', '2025-04-19T13:30:00Z'), --Salem to Bend
    (6, 'ChIJJ3SpfQsLlVQRkYXR9ua5Nhw', 'ChIJfdcUqp1AwFQRvsC9Io-ADdc', '2025-04-19T12:15:00Z'), --Portland to Corvallis
    (7, 'ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'ChIJUdLTpf_AuFQRtNEgx6zniBA', '2025-04-19T11:00:00Z'); --Corvallis to Bend

INSERT INTO ride_matches (ride_offer_id, ride_request_id, pending, confirmed) VALUES
    (5, 1, FALSE, TRUE),
    (5, 2, FALSE, TRUE),
    (1, 3, FALSE, TRUE),
    (7, 4, FALSE, TRUE);