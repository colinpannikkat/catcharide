import psycopg
from dataclasses import dataclass
from psycopg.rows import class_row

connection_params = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'catcharide',
    'connect_timeout': 10,
}

@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    is_verified: bool

@dataclass
class RideOffer:
    id: int
    driver_id: int
    origin: str
    destination: str
    departure_time: str
    available_seats: int
    description: str

@dataclass
class RideRequest:
    id: int
    rider_id: int
    origin: str
    destination: str
    departure_time: str

@dataclass
class RideMatch:
    id: int
    ride_offer_id: int
    ride_request_id: int
    pending: bool
    confirmed: bool

class DatabaseDriver:

    def __init__(self, connection_params):
        self.conn = psycopg.connect(**connection_params)

    def reset(self):
        print("resetting tables")
        with self.conn.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS ride_matches;
                DROP TABLE IF EXISTS ride_requests;
                DROP TABLE IF EXISTS ride_offers;
                DROP TABLE IF EXISTS users;
            """)
            self.conn.commit()

    def init_tables(self):
        # import schema.sql and execute it
        with self.conn.cursor() as cur:
            with open('database/schema.sql', 'r') as f:
                cur.execute(f.read())
            self.conn.commit()
    
    # Users CRUD
    def create_user(self, first_name, last_name, email, phone_number, is_verified=False):
        sql = "INSERT INTO users (first_name, last_name, email, phone_number, is_verified) VALUES (%s, %s, %s, %s, %s) RETURNING id, first_name, last_name, email, phone_number, is_verified"
        try:
            with self.conn.cursor(row_factory=class_row(User)) as cur:
                cur.execute(sql, (first_name, last_name, email, phone_number, is_verified))
                user = cur.fetchone()
                self.conn.commit()
            return user
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_user(self, user_id):
        sql = "SELECT id, first_name, last_name, email, phone_number, is_verified FROM users WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchone()
        
    def get_user_by_email(self, email):
        sql = "SELECT id, first_name, last_name, email, phone_number, is_verified FROM users WHERE email = %s"
        with self.conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute(sql, (email,))
            return cur.fetchone()
        
    def update_user(self, user_id, **kwargs):
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        try:
            with self.conn.cursor(row_factory=class_row(User)) as cur:
                cur.execute(sql, tuple(values))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_user(self, user_id):
        sql = "DELETE FROM users WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(User)) as cur:
            cur.execute(sql, (user_id,))
            self.conn.commit()
            return cur.rowcount > 0

    # Ride offers CRUD
    def create_ride_offer(self, origin, destination, departure_time, available_seats, description=None):
        sql = "INSERT INTO ride_offers (origin, destination, departure_time, available_seats, description) VALUES (%s, %s, %s, %s, %s) RETURNING id, driver_id, origin, destination, departure_time, available_seats, description"
        try:
            with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
                cur.execute(sql, (origin, destination, departure_time, available_seats, description))
                ride_offer = cur.fetchone()
                self.conn.commit()
            return ride_offer
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_ride_offer(self, ride_offer_id):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
            cur.execute(sql, (ride_offer_id,))
            return cur.fetchone()
        
    def get_ride_offers_by_driver(self, driver_id):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE driver_id = %s"
        with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
            cur.execute(sql, (driver_id,))
            return cur.fetchall()
        
    def get_ride_offers_by_departure_date(self, departure_date):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE departure_time::date = %s"
        with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
            cur.execute(sql, (departure_date,))
            return cur.fetchall()
        
    def update_ride_offer(self, ride_offer_id, **kwargs):
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(ride_offer_id)
        sql = f"UPDATE ride_offers SET {', '.join(fields)} WHERE id = %s"
        try:
            with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
                cur.execute(sql, tuple(values))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_ride_offer(self, ride_offer_id):
        sql = "DELETE FROM ride_offers WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideOffer)) as cur:
            cur.execute(sql, (ride_offer_id,))
            self.conn.commit()
            return cur.rowcount > 0

    # Ride requests CRUD
    def create_ride_request(self, rider_id, origin, destination, departure_time):
        sql = "INSERT INTO ride_requests (rider_id, origin, destination, departure_time) VALUES (%s, %s, %s, %s) RETURNING id, rider_id, origin, destination, departure_time"
        try:
            with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
                cur.execute(sql, (rider_id, origin, destination, departure_time))
                ride_request = cur.fetchone()
                self.conn.commit()
            return ride_request
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_ride_request(self, ride_request_id):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
            cur.execute(sql, (ride_request_id,))
            return cur.fetchone()
    
    def get_ride_requests_by_rider(self, rider_id):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE rider_id = %s"
        with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
            cur.execute(sql, (rider_id,))
            return cur.fetchall()
        
    def get_rider_ride_requests_by_departure_date(self, rider_id, departure_date):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE rider_id = %s AND departure_time::date = %s"
        with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
            cur.execute(sql, (rider_id, departure_date))
            return cur.fetchall()

    def update_ride_request(self, ride_request_id, **kwargs):
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(ride_request_id)
        sql = f"UPDATE ride_requests SET {', '.join(fields)} WHERE id = %s"
        try:
            with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
                cur.execute(sql, tuple(values))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_ride_request(self, ride_request_id):
        sql = "DELETE FROM ride_requests WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideRequest)) as cur:
            cur.execute(sql, (ride_request_id,))
            self.conn.commit()
            return cur.rowcount > 0

    # Ride matches CRUD
    def create_ride_match(self, ride_offer_id, ride_request_id, pending=True, confirmed=False):
        sql = "INSERT INTO ride_matches (ride_offer_id, ride_request_id, pending, confirmed) VALUES (%s, %s, %s, %s) RETURNING id, ride_offer_id, ride_request_id, pending, confirmed"
        try:
            with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
                cur.execute(sql, (ride_offer_id, ride_request_id, pending, confirmed))
                ride_match = cur.fetchone()
                self.conn.commit()
            return ride_match
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_ride_match(self, ride_match_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
            cur.execute(sql, (ride_match_id,))
            return cur.fetchone()
        
    def get_ride_matches_by_ride_offer(self, ride_offer_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE ride_offer_id = %s"
        with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
            cur.execute(sql, (ride_offer_id,))
            return cur.fetchall()
        
    def get_ride_matches_by_ride_request(self, ride_request_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE ride_request_id = %s"
        with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
            cur.execute(sql, (ride_request_id,))
            return cur.fetchall()

    def update_ride_match(self, ride_match_id, **kwargs):
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(ride_match_id)
        sql = f"UPDATE ride_matches SET {', '.join(fields)} WHERE id = %s"
        try:
            with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
                cur.execute(sql, tuple(values))
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            raise e

    def delete_ride_match(self, ride_match_id):
        sql = "DELETE FROM ride_matches WHERE id = %s"
        with self.conn.cursor(row_factory=class_row(RideMatch)) as cur:
            cur.execute(sql, (ride_match_id,))
            self.conn.commit()
            return cur.rowcount > 0

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseDriver(connection_params)
    db.reset( )
    db.init_tables()
    
    # Create a user
    user = db.create_user(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        is_verified=True
    )
    print(f"Created user with ID: {user}")

    # Get a user
    user = db.get_user(user.id)
    print(f"Retrieved user: {user}")

    # Delete the user
    db.delete_user(user.id)
    print(f"Deleted user with ID: {user.id}")

    # Close the database connection
    db.close()