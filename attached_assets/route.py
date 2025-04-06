import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json

load_dotenv()

def get_oauth_token():
    service_info = json.load(open('server/catcharide-456005-b017707003cb.json'))
    credentials = service_account.Credentials.from_service_account_info(
        service_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    request_obj = Request()
    credentials.refresh(request_obj)
    os.environ["OAUTH_TOKEN"] = credentials.token
    return credentials.token

def refresh_oauth_token():
    """
    This function uses the stored refresh token along with your client credentials
    to obtain a fresh OAuth access token from Google.
    """

    # Create a Credentials object with no current token but with a refresh token.
    service_info = json.load(open('server/catcharide-456005-b017707003cb.json'))
    creds = service_account.Credentials.from_service_account_info(
        service_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    try:
        # Refresh the credentials. This sends a request to Google's token endpoint.
        creds.refresh(Request())
        new_token = creds.token

        # Update the environment variable with the new token.
        os.environ["OAUTH_TOKEN"] = new_token
        # print("Refreshed OAuth token:", new_token)
    except Exception as e:
        print("Failed to refresh token:", e)

class RouteOptimization:
    def __init__(self, project_id, oauth_token):
        self.project_id = project_id
        self.oauth_token = oauth_token

    def add_one_day(self, timestamp_str):
        print(timestamp_str)
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        new_timestamp = timestamp + timedelta(days=2)
        return new_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def optimize_tours(self, vehicle_waypoint, shipment_waypoints, start_time):
        vehicle = {
            "startWaypoint": {"placeId": vehicle_waypoint[0]},
            "endWaypoint": {"placeId": vehicle_waypoint[1]},
            "travelMode": "DRIVING"
        }
        
        shipments = []
        for pickup, delivery in shipment_waypoints:
            shipments.append({
                "pickups": [
                    {"arrivalWaypoint": {"placeId": pickup}}
                ],
                "deliveries": [
                    {"arrivalWaypoint": {"placeId": delivery}}
                ]
            })
        
        end_time = self.add_one_day(start_time)
        
        shipment_model = {
            "shipments": shipments,
            "vehicles": [vehicle],
            "globalStartTime": start_time,
            "globalEndTime": end_time
        }
        
        optimization_request = {
            "model": shipment_model,
            "considerRoadTraffic": True,
            "populatePolylines": True
        }
        
        url = f"https://routeoptimization.googleapis.com/v1/projects/{self.project_id}:optimizeTours"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth_token}"
        }
        
        response = requests.post(url, json=optimization_request, headers=headers)
        
        if response.status_code != 200:
            refresh_oauth_token()
            self.oauth_token = os.getenv("OAUTH_TOKEN")
            headers["Authorization"] = f"Bearer {self.oauth_token}"
            response = requests.post(url, json=optimization_request, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        
        response = response.json()
        total_duration = response["metrics"]["aggregatedRouteMetrics"]["totalDuration"]
        total_distance = response["metrics"]["aggregatedRouteMetrics"]["travelDistanceMeters"]
        polyline = response["routes"][0]["routePolyline"]["points"]

        total_duration = int(total_duration[:-1])
        total_distance = int(total_distance)

        output = {
            "total_duration": total_duration,
            "total_distance": total_distance,
            "polyline": polyline
        }

        return output
    
if __name__ == "__main__":    
    vehicle_waypoint = ("ChIJfdcUqp1AwFQRvsC9Io-ADdc", "ChIJJ3SpfQsLlVQRkYXR9ua5Nhw")
    shipment_waypoints = [
        ("ChIJv0fYEV4XwFQRAKdgafDZ1R8", "ChIJY5xLvPz-v1QRwlcDj-ApNPk"),
        ("ChIJ3VwciHg3wFQR1iwHMt0kbkY", "ChIJeeW8Vl8FlVQRhu0zaob_KX0")
    ]
    start_time = "2025-04-06T08:00:00Z"

    refresh_oauth_token()

    project_id = os.getenv("PROJECT_ID")
    oauth_token = os.getenv("OAUTH_TOKEN")

    route_optimizer = RouteOptimization(project_id, oauth_token)
    result = route_optimizer.optimize_tours(vehicle_waypoint, shipment_waypoints, start_time)
    print(result)