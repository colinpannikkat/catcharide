import numpy as np
from collections import defaultdict
from heapq import nsmallest
from dotenv import load_dotenv
import os
from pprint import pprint
from sample_data import ride_offers1, ride_requests1, ride_offers2, ride_requests2
import requests
import json
from scipy.optimize import linear_sum_assignment

load_dotenv()
GOOGLE_API_KEY = os.getenv("REACT_APP_GOOGLE_MAPS_API_KEY")

class Node:
    def __init__(self, data):
        self.data = data

class DriverNode(Node):
    def __init__(self, data):
        super().__init__(data)

class RiderNode(Node):
    def __init__(self, data):
        super().__init__(data)

class Matcher:
    def __init__(self):
        self._graph = defaultdict(set) # key is DriverNode, values are RiderNode
        self._revgraph = defaultdict(set) # key is RiderNode, values are DriverNode 
        self.locations = [] # stored as place_ids
        self.distance_matrix = None # stores both distance in meters and duration in seconds between locations
                                    # this is a symmetric matrix

    def add_location(self, location, update=False):
        """
        Adds a new location to the list of locations. Optionally updates the 
        distance matrix if the `update` parameter is set to True.

        Args:
            location (Any): The location to be added.
            update (bool, optional): If True, updates the distance matrix with 
                the new location. Defaults to False.

        Returns:
            None
        """
        if len(self.locations) == 1:
            self.locations.append(location)
            return
        if location not in self.locations:
            if (update):
                self.update_distance_matrix(location)
            self.locations.append(location)
    
    def add_rider(self, node: RiderNode):
        """
        Adds a new rider node to the graph and establishes connections with existing drivers.

        Args:
            node (RiderNode): The rider node to be added to the graph.

        Behavior:
            - For each driver in the graph, calculates the cost between the driver and the new rider.
            - Updates the graph (`_graph`) by adding the rider node and the calculated cost to the driver's adjacency list.
            - Updates the reverse graph (`_revgraph`) by adding the driver and the calculated cost to the rider's adjacency list.

        Note:
            The `calc_cost` method is used to compute the cost between the rider and the driver.
            Ensure that the `calc_cost` method is implemented with the appropriate logic for cost calculation.
        """
        # Ensure the driver is added to the graph even if there are no riders
        if node not in self._graph:
            self._revgraph[node] = set()

        for driver in self._graph.keys():
            # Calculate cost between the driver and the new rider
            cost = self.calc_cost(node, driver)  # Replace with actual cost calculation logic
            self._graph[driver].add((node, cost))
            self._revgraph[node].add((driver, cost))

    def add_driver(self, node: DriverNode):
        """
        Adds a driver node to the graph and calculates costs between the driver 
        and existing riders.
        This method ensures that the driver node is added to the graph even if 
        there are no riders. It also computes the cost between the new driver 
        and all existing riders, updating both the forward graph (`_graph`) 
        and the reverse graph (`_revgraph`) with the calculated costs.
        Args:
            node (DriverNode): The driver node to be added to the graph.
        Side Effects:
            - Updates `_graph` to include the driver node and its connections 
              to riders with associated costs.
            - Updates `_revgraph` to include connections from riders to the 
              driver node with associated costs.
        """
        # Ensure the driver is added to the graph even if there are no riders
        if node not in self._graph:
            self._graph[node] = set()
        
        # Calculate costs between the new driver and existing riders
        for rider in self._revgraph.keys():
            cost = self.calc_cost(rider, node)  # Calculate cost between rider and driver
            self._graph[node].add((rider, cost))
            self._revgraph[rider].add((node, cost))

    def add_with_location(self, node):
        """
        Adds a node (DriverNode or RiderNode) to the system along with its associated locations.

        Depending on the type of the node, this method performs the following:
        - For a DriverNode:
            - Adds the origin location of the driver.
            - Adds the destination location of the driver and updates it.
            - Registers the driver node in the system.
        - For a RiderNode:
            - Adds the origin location of the rider.
            - Adds the destination location of the rider and updates it.
            - Registers the rider node in the system.

        Args:
            node (DriverNode or RiderNode): The node to be added, containing data about
                the origin and destination locations.

        Raises:
            TypeError: If the provided node is not an instance of DriverNode or RiderNode.
        """
        if isinstance(node, DriverNode):
            self.add_location(node.data['origin'])
            self.add_location(node.data['destination'], update=True)
            self.add_driver(node)
        elif isinstance(node, RiderNode):
            self.add_location(node.data['origin'])
            self.add_location(node.data['destination'], update=True)
            self.add_rider(node)

    def calc_initial_distance_matrix(self):
        """
        Calculates the initial distance matrix for the given locations using the Google Distance Matrix API.
        This method sends a request to the Google Distance Matrix API to compute the distances and durations
        between all pairs of locations. The results are stored in a 2D numpy array `self.distance_matrix`, 
        where each element is a tuple containing the distance in meters and the duration in seconds.
        Raises:
            Exception: If the API request fails (non-200 status code), an exception is raised with the error details.
        Attributes:
            self.distance_matrix (numpy.ndarray): A 2D array where each element is a tuple (distance, duration).
                - distance (int): The distance in meters between the origin and destination.
                - duration (int): The duration in seconds between the origin and destination.
        Notes:
            - The API key for the Google Distance Matrix API must be set in the `GOOGLE_API_KEY` variable.
            - The `self.locations` attribute must be a list of location identifiers (e.g., place IDs).
            - The API request uses the "TRAFFIC_AWARE" routing preference and "DRIVE" travel mode.
        """
        locs = [{"waypoint": {"placeId": loc}} for loc in self.locations]

        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,duration"
        }
        body = {
            "origins": locs,
            "destinations": locs,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE"
        }
        
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        
        res = response.json()

        # Parse the result to build a 2D array of distances
        self.distance_matrix = np.zeros((len(self.locations), len(self.locations)), dtype=tuple)
        for route_matrix_element in res:
            dest_idx = route_matrix_element['destinationIndex']
            orig_idx = route_matrix_element['originIndex']
            dur = int(route_matrix_element['duration'].split("s")[0])
            dist = 0
            if dur != 0:
                dist = route_matrix_element['distanceMeters']
            self.distance_matrix[dest_idx][orig_idx] = (dist, dur)

    def update_distance_matrix(self, location):
        """
        Updates the distance matrix with the distances and durations between a new location 
        and the existing locations.

        This method sends a request to the Google Distance Matrix API to compute the distances 
        and durations between the new location and all existing locations. The results are then 
        used to update the internal distance matrix.

        Args:
            location (str): The place ID of the new location to be added to the distance matrix.

        Raises:
            Exception: If the API request fails with a non-200 status code.

        Notes:
            - The distance matrix is represented as a NumPy array where each element is a tuple 
              containing the distance in meters and the duration in seconds.
            - The diagonal elements of the distance matrix represent the distance and duration 
              from a location to itself, which are set to (0, 0).
        """
        loc = {"waypoint": {"placeId": location}}
        existing_locs = [{"waypoint": {"placeId": loc}} for loc in self.locations if loc != location]

        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": "originIndex,destinationIndex,distanceMeters,duration"
        }
        body = {
            "origins": [loc],
            "destinations": existing_locs,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE"
        }

        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")

        res = response.json()

        # Update the distance matrix with new distances
        new_row = np.zeros((len(self.locations),), dtype=tuple)
        for route_matrix_element in res:
            dest_idx = route_matrix_element['destinationIndex']
            dur = int(route_matrix_element['duration'].split("s")[0])
            dist = 0
            if dur != 0:
                dist = route_matrix_element['distanceMeters']
                new_row[dest_idx] = (dist, dur)

        # Add the new row and column to the distance matrix
        if self.distance_matrix is None:
            self.distance_matrix = np.zeros((1, 1), dtype=tuple)
            self.distance_matrix[0][0] = new_row[0]
        else:
            self.distance_matrix = np.vstack((self.distance_matrix, new_row[:-1]))
            new_col = np.append(new_row[:-1], (0, 0))  # Add (0, 0) for the diagonal element
            self.distance_matrix = np.column_stack((self.distance_matrix, new_col))

    def calc_cost(self, rider: RiderNode, driver: DriverNode):
        """
        Calculate the cost and excess travel time for a driver to pick up and drop off a rider.

        Args:
            rider (RiderNode): The rider node containing data about the rider's origin and destination.
            driver (DriverNode): The driver node containing data about the driver's origin and destination.

        Returns:
            tuple: A tuple containing:
                - total (float): The total cost, which includes detour time from the driver's source 
                  to the rider's source, detour time from the rider's destination to the driver's 
                  destination, and the excess travel time caused by picking up and dropping off the rider.
                - excess_travel_time (float): The additional travel time incurred by the driver due to 
                  picking up and dropping off the rider.
        """
        rider_src, rider_dest = rider.data['origin'], rider.data['destination']
        driver_src, driver_dest = driver.data['origin'], driver.data['destination']

        driver_src_to_rider_src = self.distance_matrix[self.locations.index(driver_src)][self.locations.index(rider_src)][1]
        driver_src_to_driver_dest = self.distance_matrix[self.locations.index(driver_src)][self.locations.index(driver_dest)][1]
        rider_src_to_rider_dest = self.distance_matrix[self.locations.index(rider_src)][self.locations.index(rider_dest)][1]
        rider_dest_to_driver_dest = self.distance_matrix[self.locations.index(rider_dest)][self.locations.index(driver_dest)][1]

        detour_from_src = driver_src_to_rider_src/60
        detour_from_dest = rider_dest_to_driver_dest/60
        total_with_rider = driver_src_to_rider_src + rider_src_to_rider_dest + rider_dest_to_driver_dest
        excess_travel_time = (total_with_rider - driver_src_to_driver_dest) / 60

        total = detour_from_src + detour_from_dest + excess_travel_time

        return (total, excess_travel_time)

    def sort_listings(self, node: Node, n: int):
        """
        Sorts and retrieves the top `n` listings connected to the given node 
        based on their associated weights in ascending order.

        Args:
            node (Node): The node for which the connected listings are to be sorted.
            n (int): The number of top listings to retrieve.

        Returns:
            list: A list of the top `n` listings connected to the given node, 
                  sorted by their weights in ascending order. Each listing is 
                  represented as a tuple (listing, weight).
        """
        top = nsmallest(n, self._revgraph[node], key=lambda x: x[1])
        return top
    
if __name__ == "__main__":
    match = Matcher()

    # match.locations = ["place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc",
    #                    "place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8",
    #                    "place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ",
    #                    "place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw"] # Corvallis, OR; Albany, OR, Vancouver, WA; Portland, OR

    # match.calc_distance_matrix()
    # pprint(match.distance_matrix)

    # rider = RiderNode({'origin':'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8', 'destination':'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ'}) # ALB -> VAN
    # driver = DriverNode({'origin':'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'destination':'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'}) # COR -> PORT

    # match.add_driver(driver)
    # match.add_rider(rider)

    ride_offers = ride_offers2
    ride_requests = ride_requests2

    for ride_offer in ride_offers:
        match.add_location(ride_offer['origin'])
        match.add_location(ride_offer['destination'])

    for ride_request in ride_requests:
        match.add_location(ride_request['origin'])
        match.add_location(ride_request['destination'])

    match.calc_initial_distance_matrix()

    for ride_offer in ride_offers:
        node = DriverNode(ride_offer)
        match.add_driver(node)

    for ride_request in ride_requests:
        node = RiderNode(ride_request)
        match.add_rider(node)

    match.add_with_location(node=RiderNode({
        "id": 4,
        "rider_id": 404,
        "origin": "ChIJJ3SpfQsLlVQRkYXR9ua5Nhw",  # Portland, OR
        "destination": "ChIJGRlQrLAZwVQRTYlDSolh7Fc",  # Eugene, OR
        "departure_time": "2025-04-19T12:15:00"
    }))

    for rider in match._revgraph:
        print("Rider: ", rider.data)
        best = match.sort_listings(rider, 2)
        for d, w in best:
            print(d.data, w)

    # rider 1: Eugene -> Portland
    # rider 2: Salem -> Bend
    # rider 3: Portland -> Corvallis