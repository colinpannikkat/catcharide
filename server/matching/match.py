import numpy as np
from collections import defaultdict

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
        self._graph = defaultdict(set) # vertex key is DriverNode, vertex values are RiderNode 

    def add_rider(self, rider_data):
        node = RiderNode(rider_data)

        for driver in self._graph.keys():
            # Calculate cost between the driver and the new rider
            cost = self.calc_cost(node, driver)  # Replace with actual cost calculation logic
            self._graph[driver].add((node, cost))

    def add_driver(self, driver_data):
        node = DriverNode(driver_data)
        self._graph[node] = set()

    def calc_cost(self, rider: RiderNode, driver: DriverNode):
        pass

    def sort_listings(self, node: Node):
        pass