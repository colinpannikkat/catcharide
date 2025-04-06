import psycopg
import psycopg.rows

connection_params = {
    'host': 'localhost',
    'port': 6969,
    'dbname': 'catcharide',
    'connect_timeout': 10,
}

class DatabaseDriver:

    def __init__(self, connection_params):
        self.conn = psycopg.connect(**connection_params, row_factory=psycopg.rows.dict_row)
    
    # Users CRUD
    def create_user(self, first_name, last_name, email, phone_number, is_verified=False):
        sql = "INSERT INTO users (first_name, last_name, email, phone_number, is_verified) VALUES (%s, %s, %s, %s, %s) RETURNING id"
        with self.conn.cursor() as cur:
            cur.execute(sql, (first_name, last_name, email, phone_number, is_verified))
            user_id = cur.fetchone()[0]
            self.conn.commit()
        return user_id

    def get_user(self, user_id):
        sql = "SELECT id, first_name, last_name, email, phone_number, is_verified FROM users WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchone()
        
    def get_user_by_email(self, email):
        sql = "SELECT id, first_name, last_name, email, phone_number, is_verified FROM users WHERE email = %s"
        with self.conn.cursor() as cur:
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
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            self.conn.commit()

    def delete_user(self, user_id):
        sql = "DELETE FROM users WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            self.conn.commit()

    # Ride offers CRUD
    def create_ride_offer(self, driver_id, origin, destination, departure_time, available_seats, description=None):
        sql = "INSERT INTO ride_offers (driver_id, origin, destination, departure_time, available_seats, description) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
        with self.conn.cursor() as cur:
            cur.execute(sql, (driver_id, origin, destination, departure_time, available_seats, description))
            ride_offer_id = cur.fetchone()[0]
            self.conn.commit()
        return ride_offer_id

    def get_ride_offer(self, ride_offer_id):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_offer_id,))
            return cur.fetchone()
        
    def get_ride_offers_by_driver(self, driver_id):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE driver_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (driver_id,))
            return cur.fetchall()
        
    def get_ride_offers_by_departure_date(self, departure_date):
        sql = "SELECT id, driver_id, origin, destination, departure_time, available_seats, description FROM ride_offers WHERE departure_time::date = %s"
        with self.conn.cursor() as cur:
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
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            self.conn.commit()

    def delete_ride_offer(self, ride_offer_id):
        sql = "DELETE FROM ride_offers WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_offer_id,))
            self.conn.commit()

    # Ride requests CRUD
    def create_ride_request(self, rider_id, origin, destination, departure_time):
        sql = "INSERT INTO ride_requests (rider_id, origin, destination, departure_time) VALUES (%s, %s, %s, %s) RETURNING id"
        with self.conn.cursor() as cur:
            cur.execute(sql, (rider_id, origin, destination, departure_time))
            ride_request_id = cur.fetchone()[0]
            self.conn.commit()
        return ride_request_id

    def get_ride_request(self, ride_request_id):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_request_id,))
            return cur.fetchone()
    
    def get_ride_requests_by_rider(self, rider_id):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE rider_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (rider_id,))
            return cur.fetchall()
        
    def get_rider_ride_requests_by_departure_date(self, rider_id, departure_date):
        sql = "SELECT id, rider_id, origin, destination, departure_time FROM ride_requests WHERE rider_id = %s AND departure_time::date = %s"
        with self.conn.cursor() as cur:
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
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            self.conn.commit()

    def delete_ride_request(self, ride_request_id):
        sql = "DELETE FROM ride_requests WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_request_id,))
            self.conn.commit()

    # Ride matches CRUD
    def create_ride_match(self, ride_offer_id, ride_request_id, pending=True, confirmed=False):
        sql = "INSERT INTO ride_matches (ride_offer_id, ride_request_id, pending, confirmed) VALUES (%s, %s, %s, %s) RETURNING id"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_offer_id, ride_request_id, pending, confirmed))
            ride_match_id = cur.fetchone()[0]
            self.conn.commit()
        return ride_match_id

    def get_ride_match(self, ride_match_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_match_id,))
            return cur.fetchone()
        
    def get_ride_matches_by_ride_offer(self, ride_offer_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE ride_offer_id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_offer_id,))
            return cur.fetchall()
        
    def get_ride_matches_by_ride_request(self, ride_request_id):
        sql = "SELECT id, ride_offer_id, ride_request_id, pending, confirmed FROM ride_matches WHERE ride_request_id = %s"
        with self.conn.cursor() as cur:
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
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            self.conn.commit()

    def delete_ride_match(self, ride_match_id):
        sql = "DELETE FROM ride_matches WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (ride_match_id,))
            self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    pass