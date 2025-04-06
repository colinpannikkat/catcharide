import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json
import logging

logger = logging.getLogger(__name__)
load_dotenv()

def get_oauth_token():
    """Get a fresh OAuth token from Google using service account credentials."""
    try:
        # First check if there's a token already in environment
        oauth_token = os.environ.get("OAUTH_TOKEN")
        if oauth_token:
            return oauth_token
            
        # Check if service account credentials are available in environment
        credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if credentials_json:
            # Use credentials from environment variable
            service_info = json.loads(credentials_json)
        else:
            # Fallback to file-based credentials if available
            credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", 'catcharide-456005-b017707003cb.json')
            with open(credentials_file, 'r') as f:
                service_info = json.load(f)
        
        credentials = service_account.Credentials.from_service_account_info(
            service_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        request_obj = Request()
        credentials.refresh(request_obj)
        os.environ["OAUTH_TOKEN"] = credentials.token
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get OAuth token: {e}")
        return None

def refresh_oauth_token():
    """Refresh the OAuth token when needed."""
    try:
        # Check for an existing token in the environment variables first
        oauth_token = os.environ.get("OAUTH_TOKEN")
        
        # Check if service account credentials are available in environment
        credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if credentials_json:
            # Use credentials from environment variable
            service_info = json.loads(credentials_json)
        else:
            # Fallback to file-based credentials if available
            credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", 'catcharide-456005-b017707003cb.json')
            with open(credentials_file, 'r') as f:
                service_info = json.load(f)
        
        creds = service_account.Credentials.from_service_account_info(
            service_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        
        # Refresh the credentials
        creds.refresh(Request())
        new_token = creds.token
        
        # Update the environment variable with the new token
        os.environ["OAUTH_TOKEN"] = new_token
        return new_token
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        # If refresh fails but we have an existing token, return it
        if oauth_token:
            logger.info("Using existing OAuth token from environment")
            return oauth_token
        return None

class RouteOptimization:
    def __init__(self, project_id, oauth_token=None):
        self.project_id = project_id
        self.oauth_token = oauth_token or get_oauth_token()
    
    def add_one_day(self, timestamp_str):
        """Add one day to the given timestamp string."""
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        new_timestamp = timestamp + timedelta(days=2)
        return new_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def optimize_tours(self, vehicle_waypoint, shipment_waypoints, start_time):
        """
        Optimize a tour using Google's Route Optimization API.
        
        Args:
            vehicle_waypoint: Tuple of (origin, destination) for the vehicle
            shipment_waypoints: List of (pickup, delivery) tuples for shipments
            start_time: ISO 8601 format timestamp string for the start time
            
        Returns:
            Dictionary with total_duration, total_distance, and polyline
        """
        # Check if token is available, if not, get a new one
        if not self.oauth_token:
            self.oauth_token = get_oauth_token()
            if not self.oauth_token:
                raise Exception("Failed to obtain OAuth token")
        
        # Define the vehicle
        vehicle = {
            "startWaypoint": {"placeId": vehicle_waypoint[0]},
            "endWaypoint": {"placeId": vehicle_waypoint[1]},
            "travelMode": "DRIVING"
        }
        
        # Define the shipments (pickups and deliveries)
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
        
        # Set the end time (2 days after start time)
        end_time = self.add_one_day(start_time)
        
        # Create the shipment model
        shipment_model = {
            "shipments": shipments,
            "vehicles": [vehicle],
            "globalStartTime": start_time,
            "globalEndTime": end_time
        }
        
        # Create the optimization request
        optimization_request = {
            "model": shipment_model,
            "considerRoadTraffic": True,
            "populatePolylines": True
        }
        
        # API endpoint URL
        url = f"https://routeoptimization.googleapis.com/v1/projects/{self.project_id}:optimizeTours"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth_token}"
        }
        
        # Send the request to the API
        response = requests.post(url, json=optimization_request, headers=headers)
        
        # If request fails, refresh the token and try again
        if response.status_code != 200:
            logger.warning(f"API request failed with status {response.status_code}, refreshing token and retrying")
            self.oauth_token = refresh_oauth_token()
            headers["Authorization"] = f"Bearer {self.oauth_token}"
            response = requests.post(url, json=optimization_request, headers=headers)
            
            # If it still fails, raise an exception
            if response.status_code != 200:
                error_details = response.text
                logger.error(f"API request failed: {error_details}")
                raise Exception(f"Error: {response.status_code}, {error_details}")
        
        # Parse the response
        response_data = response.json()
        
        # Extract relevant information
        total_duration = response_data["metrics"]["aggregatedRouteMetrics"]["totalDuration"]
        total_distance = response_data["metrics"]["aggregatedRouteMetrics"]["travelDistanceMeters"]
        polyline = response_data["routes"][0]["routePolyline"]["points"]

        # Convert duration string to integer (remove 's' suffix)
        total_duration = int(total_duration[:-1])
        # Convert distance to integer
        total_distance = int(total_distance)

        # Return the optimized route data
        output = {
            "total_duration": total_duration,
            "total_distance": total_distance,
            "polyline": polyline
        }
        
        return output
