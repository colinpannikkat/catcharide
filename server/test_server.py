import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_home_endpoint():
    response = requests.get(f"{BASE_URL}")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the CatchARide API!"}

def test_status_endpoint():
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    assert response.json() == {"status": "Server is running!"}

def test_create_user_success():
    url = f"{BASE_URL}/create_user"
    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "phone_number": "1234567890",
        "is_verified": True
    }
    response = requests.post(url, json=user_data)
    assert response.status_code == 201
    assert response.text == "User created successfully."

def test_create_user_failure():
    url = f"{BASE_URL}/create_user"
    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "invalid-email",
        "phone_number": "1234567890",
        "is_verified": True
    }
    response = requests.post(url, json=user_data)
    assert response.status_code == 500
    assert response.text == "Failed to create user."

def test_get_user_success():
    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 200
    assert "first_name" in response.json()
    assert "last_name" in response.json()

def test_get_user_not_found():
    user_id = 9999
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 404
    assert response.text == "User not found."

def test_update_user_success():
    user_id = 1
    url = f"{BASE_URL}/users/{user_id}"
    user_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "email": "bob.johnson@example.com",
        "phone_number": "9876543210",
        "is_verified": False
    }
    response = requests.put(url, json=user_data)
    assert response.status_code == 200
    assert response.text == "User updated successfully."

def test_update_user_failure():
    user_id = 9999
    url = f"{BASE_URL}/users/{user_id}"
    user_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "email": "bob.johnson@example.com",
        "phone_number": "9876543210",
        "is_verified": False
    }
    response = requests.put(url, json=user_data)
    assert response.status_code == 500
    assert response.text == "Failed to update user."

def test_delete_user_success():
    user_id = 1
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 200
    assert response.text == "User deleted successfully."

def test_delete_user_failure():
    user_id = 9999
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 500
    assert response.text == "Failed to delete user."

def test_create_ride_offer_success():
    url = f"{BASE_URL}/ride_offers"
    ride_offer_data = {
        "driver_id": 1,
        "origin": "City A",
        "destination": "City B",
        "departure_time": "2023-10-10T10:00:00",
        "available_seats": 3,
        "description": "Comfortable ride"
    }
    response = requests.post(url, json=ride_offer_data)
    assert response.status_code == 201
    assert "driver_id" in response.json()

def test_get_ride_offer_success():
    ride_offer_id = 1
    response = requests.get(f"{BASE_URL}/ride_offers/{ride_offer_id}")
    assert response.status_code == 200
    assert "origin" in response.json()
    assert "destination" in response.json()

def test_get_ride_offer_not_found():
    ride_offer_id = 9999
    response = requests.get(f"{BASE_URL}/ride_offers/{ride_offer_id}")
    assert response.status_code == 404
    assert response.text == "Ride offer not found."

def test_delete_ride_offer_success():
    ride_offer_id = 1
    response = requests.delete(f"{BASE_URL}/ride_offers/{ride_offer_id}")
    assert response.status_code == 200
    assert response.text == "Ride offer deleted successfully."

def test_delete_ride_offer_failure():
    ride_offer_id = 9999
    response = requests.delete(f"{BASE_URL}/ride_offers/{ride_offer_id}")
    assert response.status_code == 500
    assert response.text == "Failed to delete ride offer."
