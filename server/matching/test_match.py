import pytest
from match import Matcher, DriverNode, RiderNode

@pytest.fixture
def matcher():
    return Matcher()

def test_add_location(matcher):
    matcher.add_location("place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc")
    assert "place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc" in matcher.locations

def test_add_driver(matcher):
    driver = DriverNode({'origin': 'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'destination': 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'})
    matcher.add_driver(driver)
    assert driver in matcher._graph

def test_add_rider(matcher):
    rider = RiderNode({'origin': 'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8', 'destination': 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ'})
    matcher.add_rider(rider)
    assert rider in matcher._revgraph

def test_add_with_location_driver(matcher):
    driver = DriverNode({'origin': 'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'destination': 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'})
    matcher.add_with_location(driver)
    assert driver in matcher._graph
    assert 'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc' in matcher.locations
    assert 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw' in matcher.locations

def test_add_with_location_rider(matcher):
    rider = RiderNode({'origin': 'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8', 'destination': 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ'})
    matcher.add_with_location(rider)
    print(matcher._revgraph)
    assert rider in matcher._revgraph
    assert 'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8' in matcher.locations
    assert 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ' in matcher.locations

def test_calc_cost(matcher):
    matcher.locations = [
        'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc',
        'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8',
        'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ',
        'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'
    ]
    matcher.distance_matrix = [
        [(0, 0), (1000, 600), (2000, 1200), (3000, 1800)],
        [(1000, 600), (0, 0), (1500, 900), (2500, 1500)],
        [(2000, 1200), (1500, 900), (0, 0), (1000, 600)],
        [(3000, 1800), (2500, 1500), (1000, 600), (0, 0)]
    ]
    rider = RiderNode({'origin': 'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8', 'destination': 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ'})
    driver = DriverNode({'origin': 'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'destination': 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'})
    cost, excess_travel_time = matcher.calc_cost(rider, driver)
    assert cost > 0
    assert excess_travel_time > 0

def test_sort_listings(matcher):
    rider = RiderNode({'origin': 'place_id:ChIJv0fYEV4XwFQRAKdgafDZ1R8', 'destination': 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ'})
    driver1 = DriverNode({'origin': 'place_id:ChIJfdcUqp1AwFQRvsC9Io-ADdc', 'destination': 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'})
    driver2 = DriverNode({'origin': 'place_id:ChIJ-RRZyGOvlVQR8-ORLBHVVoQ', 'destination': 'place_id:ChIJJ3SpfQsLlVQRkYXR9ua5Nhw'})
    matcher._revgraph[rider] = {(driver1, (10, 9)), (driver2, (5, 3))}
    top_listings = matcher.sort_listings(rider, 1)
    assert len(top_listings) == 1
    assert top_listings[0][0] == driver2