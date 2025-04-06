import requests
from datetime import datetime, timedelta

class RouteOptimization:
    def __init__(self, project_id, oauth_token):
        self.project_id = project_id
        self.oauth_token = oauth_token

    def add_one_day(self, timestamp_str):
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