from flask import Flask, jsonify, Response
from flask_pydantic import validate
from pydantic import BaseModel, ValidationError
from database.driver import DatabaseDriver
import json
import argparse
from matching.route import RouteOptimization
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()
PROJECT_ID = os.getenv('PROJECT_ID')
OAUTH_TOKEN = os.getenv('OAUTH_TOKEN')

route_optimizer = RouteOptimization(PROJECT_ID, OAUTH_TOKEN)

db = DatabaseDriver({
    'host': 'localhost',
    'port': 5432,
    'dbname': 'catcharide',
    'connect_timeout': 10,
})

class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    is_verified: bool | None

class RideOffer(BaseModel):
    origin: str
    destination: str
    departure_time: str
    available_seats: int
    description: str

class RideRequest(BaseModel):
    origin: str
    destination: str
    departure_time: str

class RideMatch(BaseModel):
    ride_request_id: int
    pending: bool | None
    confirmed: bool | None

@app.get('/api')
def home():
    return jsonify({"message": "Welcome to the CatchARide API!"})

@app.get('/api/status')
def status():
    return jsonify({"status": "Server is running!"})

@app.post("/api/create_user")
@validate(body=User)
def create_user(body: User):
    try:
        db.create_user(**json.loads(body.model_dump_json()))
        return Response(status=201, response="User created successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to create user.")

@app.get('/api/users/<int:user_id>')
def get_user(user_id: int):
    try:
        user = db.get_user(user_id)
        if user:
            return jsonify(user.__dict__)
        return Response(status=404, response="User not found.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve user.")

@app.put('/api/users/<int:user_id>')
@validate(body=User)
def update_user(user_id: int, body: User):
    try:
        rows_affected = db.update_user(user_id, **json.loads(body.model_dump_json()))
        if not rows_affected:
            raise(Exception("No rows affected by update"))
        return Response(status=200, response="User updated successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to update user.")

@app.delete('/api/users/<int:user_id>')
def delete_user(user_id: int):
    try:
        rows_affected = db.delete_user(user_id)
        if not rows_affected:
            raise(Exception("No rows affected by deletion"))
        return Response(status=200, response="User deleted successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to delete user.")

@app.post('/api/ride_offers')
@validate(body=RideOffer)
def create_ride_offer(body: RideOffer):
    try:
        ride_offer = db.create_ride_offer(**json.loads(body.model_dump_json()))
        return jsonify(ride_offer.__dict__), 201
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to create ride offer.")

@app.get('/api/ride_offers/<int:ride_offer_id>')
def get_ride_offer(ride_offer_id: int):
    try:
        ride_offer = db.get_ride_offer(ride_offer_id)
        if ride_offer:
            return jsonify(ride_offer.__dict__)
        return Response(status=404, response="Ride offer not found.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride offer.")
    
@app.put('/api/ride_offers/<int:ride_offer_id>')
@validate(body=RideOffer)
def update_ride_offer(ride_offer_id: int, body: RideOffer):
    try:
        rows_affected = db.update_ride_offer(ride_offer_id, **json.loads(body.model_dump_json()))
        if not rows_affected:
            raise(Exception("No rows affected by update"))
        return Response(status=200, response="Ride offer updated successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to update ride offer.")

@app.delete('/api/ride_offers/<int:ride_offer_id>')
def delete_ride_offer(ride_offer_id: int):
    try:
        rows_affected = db.delete_ride_offer(ride_offer_id)
        if not rows_affected:
            raise(Exception("No rows affected by deletion"))
        return Response(status=200, response="Ride offer deleted successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to delete ride offer.")

@app.get('/api/ride_offers/driver/<int:driver_id>')
def get_ride_offers_by_driver(driver_id: int):
    try:
        ride_offers = db.get_ride_offers_by_driver(driver_id)
        return jsonify([offer.__dict__ for offer in ride_offers])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride offers by driver.")

@app.get('/api/ride_offers/departure_date/<string:departure_date>')
def get_ride_offers_by_departure_date(departure_date: str):
    try:
        ride_offers = db.get_ride_offers_by_departure_date(departure_date)
        return jsonify([offer.__dict__ for offer in ride_offers])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride offers by departure date.")

@app.post('/api/ride_requests')
@validate(body=RideRequest)
def create_ride_request(body: RideRequest):
    try:
        ride_request = db.create_ride_request(**json.loads(body.model_dump_json()))
        return jsonify(ride_request.__dict__), 201
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to create ride request.")

@app.get('/api/ride_requests/<int:ride_request_id>')
def get_ride_request(ride_request_id: int):
    try:
        ride_request = db.get_ride_request(ride_request_id)
        if ride_request:
            return jsonify(ride_request.__dict__)
        return Response(status=404, response="Ride request not found.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride request.")

@app.get('/api/ride_requests/rider/<int:rider_id>')
def get_ride_requests_by_rider(rider_id: int):
    try:
        ride_requests = db.get_ride_requests_by_rider(rider_id)
        return jsonify([request.__dict__ for request in ride_requests])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride requests by rider.")

@app.get('/api/ride_requests/rider/<int:rider_id>/departure_date/<string:departure_date>')
def get_rider_ride_requests_by_departure_date(rider_id: int, departure_date: str):
    try:
        ride_requests = db.get_rider_ride_requests_by_departure_date(rider_id, departure_date)
        return jsonify([request.__dict__ for request in ride_requests])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride requests by departure date.")

@app.put('/api/ride_requests/<int:ride_request_id>')
@validate(body=RideRequest)
def update_ride_request(ride_request_id: int, body: RideRequest):
    try:
        rows_affected = db.update_ride_request(ride_request_id, **json.loads(body.model_dump_json()))
        if not rows_affected:
            raise(Exception("No rows affected by update"))
        return Response(status=200, response="Ride request updated successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to update ride request.")

@app.delete('/api/ride_requests/<int:ride_request_id>')
def delete_ride_request(ride_request_id: int):
    try:
        rows_affected = db.delete_ride_request(ride_request_id)
        if not rows_affected:
            raise(Exception("No rows affected by deletion"))
        return Response(status=200, response="Ride request deleted successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to delete ride request.")

@app.post('/api/ride_matches')
@validate(body=RideMatch)
def create_ride_match(body: RideMatch):
    try:
        ride_match = db.create_ride_match(**json.loads(body.model_dump_json()))
        return jsonify(ride_match.__dict__), 201
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to create ride match.")

@app.get('/api/ride_matches/<int:ride_match_id>')
def get_ride_match(ride_match_id: int):
    try:
        ride_match = db.get_ride_match(ride_match_id)
        if ride_match:
            return jsonify(ride_match.__dict__)
        return Response(status=404, response="Ride match not found.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride match.")

@app.get('/api/ride_matches/ride_offer/<int:ride_offer_id>')
def get_ride_matches_by_ride_offer(ride_offer_id: int):
    try:
        ride_matches = db.get_ride_matches_by_ride_offer(ride_offer_id)
        return jsonify([match.__dict__ for match in ride_matches])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride matches by ride offer.")

@app.get('/api/ride_matches/ride_request/<int:ride_request_id>')
def get_ride_matches_by_ride_request(ride_request_id: int):
    try:
        ride_matches = db.get_ride_matches_by_ride_request(ride_request_id)
        return jsonify([match.__dict__ for match in ride_matches])
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to retrieve ride matches by ride request.")

@app.put('/api/ride_matches/<int:ride_match_id>')
@validate(body=RideMatch)
def update_ride_match(ride_match_id: int, body: RideMatch):
    try:
        rows_affected = db.update_ride_match(ride_match_id, **json.loads(body.model_dump_json()))
        if not rows_affected:
            raise(Exception("No rows affected by update"))
        return Response(status=200, response="Ride match updated successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to update ride match.")

@app.delete('/api/ride_matches/<int:ride_match_id>')
def delete_ride_match(ride_match_id: int):
    try:
        rows_affected = db.delete_ride_match(ride_match_id)
        if not rows_affected:
            raise(Exception("No rows affected by deletion"))
        return Response(status=200, response="Ride match deleted successfully.")
    except Exception as e:
        print(e)
        return Response(status=500, response="Failed to delete ride match.")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", action="store_true", help="Reset the database")
    args = parser.parse_args()
    if (args.r):
        db.reset()
        db.init_tables('database/schema.sql')

    app.run(debug=True, port=8000)
