CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE ride_offers (
    id SERIAL PRIMARY KEY,
    driver_id INT REFERENCES users(id),
    origin VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    departure_time TIMESTAMP NOT NULL,
    available_seats INT NOT NULL,
    description TEXT
);

CREATE TABLE ride_requests (
    id SERIAL PRIMARY KEY,
    rider_id INT REFERENCES users(id),
    origin VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    departure_time TIMESTAMP NOT NULL
);

CREATE TABLE ride_matches (
    id SERIAL PRIMARY KEY,
    ride_offer_id INT REFERENCES ride_offers(id),
    ride_request_id INT REFERENCES ride_requests(id),
    pending BOOLEAN DEFAULT TRUE,
    confirmed BOOLEAN DEFAULT FALSE
);