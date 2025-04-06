from dotenv import load_dotenv
import os
import requests

load_dotenv()

google_maps_api_key = os.getenv("REACT_APP_GOOGLE_MAPS_API_KEY")

def get_place_id(location, api_key):
    response = requests.post(
        'https://places.googleapis.com/v1/places:searchText',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.id'
        },
        json={
            'textQuery': location
        }
    )
    place_id = response.json().get('places', [{}])[0].get('id')
    return place_id

def get_formatted_address(place_id, api_key):
    response = requests.get(
        f'https://places.googleapis.com/v1/places/{place_id}',
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'id,formattedAddress'
        }
    )
    location_details = response.json()
    return location_details.get('formattedAddress')

# get the time estimate between two locations using place id using the route api
def get_time_estimate(origin_place_id, destination_place_id, api_key):
    response = requests.post(
        f"https://routes.googleapis.com/directions/v2:computeRoutes",
        headers={
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'routes.duration'
        },
        json={
            'origin': {
                'placeId': origin_place_id
            },
            'destination': {
                'placeId': destination_place_id
            },
            'travelMode': 'DRIVE'
        }
    )
    duration = response.json().get('routes', [{}])[0].get('duration')
    return duration

# Example usage
origin = "Corvallis, OR"
destination = "Portland, OR"
origin_place_id = get_place_id(origin, google_maps_api_key)
destination_place_id = get_place_id(destination, google_maps_api_key)
duration = get_time_estimate(origin_place_id, destination_place_id, google_maps_api_key)

print(f"Estimated travel time from {origin} to {destination} is {duration} seconds.")